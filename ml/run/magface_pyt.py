#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from ml.dataloader import dataloader
from ml.models import magface
from ml.utils import utils
import numpy as np
from collections import OrderedDict
from termcolor import cprint
from torchvision import datasets
from torchvision import transforms
import torch.backends.cudnn as cudnn
import torch.multiprocessing as mp
import torch.nn.functional as F
import torch.nn as nn
import torchvision
import torch
import argparse
import random
import warnings
import time
import pprint
import os

from db.mysql import upload_ml_info, upload_is_training_status, upload_initial_ml_info

import conf
CONF = conf.CONF

modelDir = CONF.magface.pth_save_fold
dataDir = CONF.magface.train_list

current_dir_name = os.path.dirname(__file__)
modelDir = current_dir_name + "/" + modelDir
dataDir = current_dir_name + "/" + dataDir

max_epochs = CONF.magface.epoch



"""
../swarm-learning/bin/run-sl --name $TRAINING_NODE-sl --network $EXAMPLE-net
 --host-ip $TRAINING_NODE-sl --sn-ip node-sn -e MAX_EPOCHS=5 --apls-ip $APLS_IP
 --serverAddress node-spire -genJoinToken
 --data-dir $WORKSPACE_DIR/ws-$EXAMPLE/$TRAINING_NODE/app-data
 --model-dir $WORKSPACE_DIR/ws-$EXAMPLE/$TRAINING_NODE/model
 --model-program mnist_pyt.py --sl-platform PYT
"""


os.system("mkdir -p %s/vis/" % modelDir)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")



# 本py文件就不用argparse.ArgumentParser了，创建个类代替得了
class Args(object):
    """docstring for args"""
    def __init__(self):
        super(Args, self).__init__()

        self.pth_save_fold = modelDir
        self.train_list = dataDir

        self.arch = 'iresnet100'
        self.workers = 8
        # 显示的时候从0开始，存储的时候，是从1开始存储的，因为训练的时候26，101这样，为了每5次存储时首位都存储
        self.epochs = max_epochs
        self.start_epoch = 0
        self.batch_size = 512
        self.embedding_size = 512
        self.last_fc_size = 85742
        self.arc_scale = 64
        self.lr = 0.1
        self.momentum = 0.9
        self.weight_decay = 5e-4
        self.lr_drop_epoch = [10, 18, 22]
        self.lr_drop_ratio = 0.1
        self.print_freq = 100
        self.pth_save_epoch = self.epochs // 5   # 注意两个//的相除，才是返回整数，向下取整
        self.l_a = 10
        self.u_a = 110
        self.l_margin = 0.45
        self.u_margin = 0.8
        self.lambda_g = 35
        self.vis_mag = 1


args = Args()


warnings.filterwarnings("ignore")


def main(args):
    # check the feasible of the lambda g
    s = 64
    k = (args.u_margin-args.l_margin)/(args.u_a-args.l_a)
    min_lambda = s*k*args.u_a**2*args.l_a**2/(args.u_a**2-args.l_a**2)
    color_lambda = 'red' if args.lambda_g < min_lambda else 'green'
    cprint('min lambda g is {}, currrent lambda is {}'.format(
        min_lambda, args.lambda_g), color_lambda)

    cprint('=> torch version : {}'.format(torch.__version__), 'green')
    ngpus_per_node = torch.cuda.device_count()
    cprint('=> ngpus : {}'.format(ngpus_per_node), 'green')

    main_worker(ngpus_per_node, args)


def main_worker(ngpus_per_node, args):
    global best_acc1

    cprint('=> modeling the network ...', 'green')
    model = magface.builder(args)
    # print("model = magface.builder(args)")
    # print(model)
    model = torch.nn.DataParallel(model)
    model = model.to(device)

    # for name, param in model.named_parameters():
    #     cprint(' : layer name and parameter size - {} - {}'.format(name, param.size()), 'green')

    cprint('=> building the oprimizer ...', 'green')
    optimizer = torch.optim.SGD(
        filter(lambda p: p.requires_grad, model.parameters()),
        args.lr,
        momentum=args.momentum,
        weight_decay=args.weight_decay)
    pprint.pprint(optimizer)

    cprint('=> building the dataloader ...', 'green')
    train_loader = dataloader.train_loader(args)





    cprint('=> building the criterion ...', 'green')
    criterion = magface.MagLoss(
        args.l_a, args.u_a, args.l_margin, args.u_margin)


    global iters
    iters = 0

    cprint('=> starting training engine ...', 'green')
    for epoch in range(args.start_epoch, args.epochs):

        global current_lr
        current_lr = utils.adjust_learning_rate(optimizer, epoch, args)

        # train for one epoch
        # 保存了loss和准确率
        loss, acc = do_train(train_loader, model, criterion, optimizer, epoch, args)




        # save pth
        # 此处取余的时候，是从0开始计算的
        if epoch % args.pth_save_epoch == 0:
            state_dict = model.state_dict()

            # cprint('pth_save_fold: {}'.format(args.pth_save_fold))
            # 第二种方式存储，所以取出来的时候没有网络结构
            utils.save_checkpoint({
                'epoch': epoch + 1,
                'arch': args.arch,
                'state_dict': state_dict,
                'optimizer': optimizer.state_dict(),
            }, False,
                filename=os.path.join(
                args.pth_save_fold, '{}.pth'.format(
                    str(epoch+1).zfill(5))
            ))

            cprint(' : save pth for epoch {}'.format(epoch+1))

        # 这个是需要每一个epoch都打印的
        # 存储的模型是从1开始计算的，
        # 比如epoch是17，这个时候没存储,最近存储的是16.pth（epoch=15）的时候，所以此处求的modesize是16.pth这个，用下面的公式没问题
        upload_ml_info(loss, acc, epoch,
                       os.path.join(args.pth_save_fold, '{}.pth'.format(str((epoch + 1) - (epoch % 5)).zfill(5))))




    # 训练结束
    upload_is_training_status(False)


def do_train(train_loader, model, criterion, optimizer, epoch, args, swarmCallback=None):
    batch_time = utils.AverageMeter('Time', ':6.3f')
    data_time = utils.AverageMeter('Data', ':6.3f')
    losses = utils.AverageMeter('Loss', ':.3f')
    top1 = utils.AverageMeter('Acc@1', ':6.2f')
    top5 = utils.AverageMeter('Acc@5', ':6.2f')
    learning_rate = utils.AverageMeter('LR', ':.4f')
    throughputs = utils.AverageMeter('ThroughPut', ':.2f')

    losses_id = utils.AverageMeter('L_ID', ':.3f')
    losses_mag = utils.AverageMeter('L_mag', ':.6f')
    progress_template = [batch_time, data_time, throughputs, 'images/s',
                         losses, losses_id, losses_mag, 
                         top1, top5, learning_rate]

    progress = utils.ProgressMeter(
        len(train_loader),
        progress_template,
        prefix="Epoch: [{}]".format(epoch))
    end = time.time()

    # update lr
    learning_rate.update(current_lr)

    for i, (input, target) in enumerate(train_loader):
        print(i)
        # measure data loading time
        data_time.update(time.time() - end)
        global iters
        iters += 1

        input = input.to(device, non_blocking=True)
        target = target.to(device, non_blocking=True)
        
        # compute output
        output, x_norm = model(input, target)

        loss_id, loss_g, one_hot = criterion(output, target, x_norm)
        loss = loss_id + args.lambda_g * loss_g

        # measure accuracy and record loss
        acc1, acc5 = utils.accuracy(args, output[0], target, topk=(1, 5))

        losses.update(loss.item(), input.size(0))
        top1.update(acc1[0], input.size(0))
        top5.update(acc5[0], input.size(0))

        losses_id.update(loss_id.item(), input.size(0))
        losses_mag.update(args.lambda_g*loss_g.item(), input.size(0))

        # compute gradient and do solver step
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        # measure elapsed time
        duration = time.time() - end
        batch_time.update(duration)
        end = time.time()
        throughputs.update(args.batch_size / duration)

        # cprint('Loss: {:.6f}'.format(loss.item()))
        # cprint('Acc@1: {:.6f}'.format(acc1[0]))
        # cprint('Acc@5: {:.6f}'.format(acc5[0]))

        if i % args.print_freq == 0:
            progress.display(i)
            debug_info(x_norm, args.l_a, args.u_a,
                           args.l_margin, args.u_margin)

        if args.vis_mag:
            if (i > 10000) and (i % 100 == 0):
                x_norm = x_norm.detach().cpu().numpy()
                cos_theta = torch.masked_select(
                    output[0], one_hot.bool()).detach().cpu().numpy()
                logit = torch.masked_select(
                    F.softmax(output[0]), one_hot.bool()).detach().cpu().numpy()
                np.savez('{}/vis/epoch_{}_iter{}'.format(args.pth_save_fold, epoch, i),
                         x_norm, logit, cos_theta)

        # loss和准确率
        return loss.item(), 0


def debug_info(x_norm, l_a, u_a, l_margin, u_margin):
    """
    visualize the magnitudes and magins during training.
    Note: modify the function if m(a) is not linear
    """
    mean_ = torch.mean(x_norm).detach().cpu().numpy()
    max_ = torch.max(x_norm).detach().cpu().numpy()
    min_ = torch.min(x_norm).detach().cpu().numpy()
    m_mean_ = (u_margin-l_margin)/(u_a-l_a)*(mean_-l_a) + l_margin
    m_max_ = (u_margin-l_margin)/(u_a-l_a)*(max_-l_a) + l_margin
    m_min_ = (u_margin-l_margin)/(u_a-l_a)*(min_-l_a) + l_margin
    print('  [debug info]: x_norm mean: {:.2f} min: {:.2f} max: {:.2f}'
          .format(mean_, min_, max_))
    print('  [debug info]: margin mean: {:.2f} min: {:.2f} max: {:.2f}'
          .format(m_mean_, m_min_, m_max_))



def train():
    # 训练前，初始化ml的信息
    upload_initial_ml_info()

    main(args)

if __name__ == '__main__':
    pprint.pprint(vars(args))



    train()