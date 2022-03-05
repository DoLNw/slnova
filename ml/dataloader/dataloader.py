#!/usr/bin/env python
import sys
sys.path.append("..")

from ml.utils import cv2_trans as transforms
from termcolor import cprint
import cv2
import torchvision
import torch.utils.data as data
import torch
import random
import numpy as np
import os
import warnings

current_dir_name = os.path.dirname(__file__)

class MagTrainDataset(data.Dataset):
    def __init__(self, ann_file, transform=None):
        self.ann_file = ann_file
        self.transform = transform
        self.init()

    def init(self):
        self.weight = {}
        self.im_names = []
        self.targets = []
        self.pre_types = []
        with open(self.ann_file) as f:
            for line in f.readlines():
                data = line.strip().split(' ')
                self.im_names.append(current_dir_name + "/" + data[0])
                self.targets.append(int(data[2]))

    def __getitem__(self, index):
        im_name = self.im_names[index]
        target = self.targets[index]
        img = cv2.imread(im_name)

        img = self.transform(img)
        return img, target

    def __len__(self):
        return len(self.im_names)


def train_loader(args):
    train_trans = transforms.Compose([
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
    ])

    train_dataset = MagTrainDataset(
        args.train_list,
        transform=train_trans
    )
    train_sampler = None

    # train_loader = torch.utils.data.DataLoader(
    #     train_dataset,
    #     shuffle=(train_sampler is None),
    #     batch_size=args.batch_size,
    #     num_workers=args.workers,
    #     pin_memory=True,
    #     sampler=train_sampler,
    #     drop_last=(train_sampler is None))
    # 数据太少，drop_last为True的话，根本没有数据的
    train_loader = torch.utils.data.DataLoader(
        train_dataset,
        shuffle=(train_sampler is None),
        batch_size=args.batch_size,
        num_workers=args.workers,
        pin_memory=True,
        sampler=train_sampler,
        drop_last=False)

    return train_loader
