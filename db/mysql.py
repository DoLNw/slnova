# -*- coding: utf-8 -*-
import pymysql
import traceback
import sys
# sys.path.append("/Users/jc/jcall/研究实验代码")

sys.path.append("/root")

import slnova.conf
CONF = slnova.conf.CONF

host = CONF.mysql.host
user = CONF.mysql.user
passwd = CONF.mysql.passwd
mydb = CONF.mysql.db
port = CONF.mysql.port
table = CONF.mysql.table

from slnova.scheduler.main.host_state import HostState
from slnova.info import getinfo
from slnova.info.nessus import check_status_and_update, pre_scan, start_scan

# 实现一个定期向数据库更新电脑参数数据

hoststate = HostState(isrunning=False, uuid=getinfo.get_uuid(), cpufreq=getinfo.get_cpu_freq(),
                     free_memory_mb=getinfo.get_free_memory_mb(),
                     total_usable_disk_gb=getinfo.get_total_usable_disk_gb(), disk_allocation_ratio = 1,
                     cpu_percent=getinfo.get_cpu_percent(), ip=getinfo.get_ip(), name=getinfo.get_name(),
                     free_disk_gb=getinfo.get_free_disk_gb(), time=getinfo.get_time())

def update_info():
    # 这些是需要更改的，有些参数不需要更改，我就不再更改了，比如当前IP，uuid等信息。
    hoststate.isrunning = True
    hoststate.cpufreq = getinfo.get_cpu_freq()
    hoststate.free_memory_mb = getinfo.get_free_memory_mb()
    hoststate.total_usable_disk_gb = getinfo.get_total_usable_disk_gb()
    hoststate.cpu_percent = getinfo.get_cpu_percent()
    hoststate.free_disk_gb = getinfo.get_free_disk_gb()
    hoststate.time = getinfo.get_time()

    querysql = "SELECT * FROM %s where uuid = '%s'" % (table, hoststate.uuid)
    delsql = "delete from %s where uuid = '%s'" % (table, hoststate.uuid)
    addsql = """INSERT INTO %s(uuid, isrunning, cpufreq, free_memory_mb, total_usable_disk_gb, \
               disk_allocation_ratio, cpu_percent, ip, name, free_disk_gb, time, high_vul, medium_vul, low_vul, info_vul)\
                VALUES ('%s', %d, %d, %d, %d, %.2f, %.2f, '%s', \
                '%s', %.2f, '%s', %d, %d, %d, %d)""" % \
            (table, hoststate.uuid, hoststate.isrunning, hoststate.cpufreq, hoststate.free_memory_mb,
             hoststate.total_usable_disk_gb, hoststate.disk_allocation_ratio, hoststate.cpu_percent, hoststate.ip,
             hoststate.name, hoststate.free_disk_gb, hoststate.time, hoststate.high_vul, hoststate.medium_vul,
             hoststate.low_vul, hoststate.info_vul)
    # print(addsql)

    updatesql = "UPDATE %s SET isrunning = %d, cpufreq = %d, free_memory_mb = %d, total_usable_disk_gb = %d,  \
                disk_allocation_ratio = %.2f, cpu_percent = %.2f, ip = '%s', name = '%s', free_disk_gb = %.2f, \
                time = '%s' WHERE uuid = '%s'" % (table, hoststate.isrunning, hoststate.cpufreq, hoststate.free_memory_mb,
                                                   hoststate.total_usable_disk_gb, hoststate.disk_allocation_ratio,
                                                   hoststate.cpu_percent, hoststate.ip,
                                                   hoststate.name, hoststate.free_disk_gb, hoststate.time,
                                                   hoststate.uuid)

    # 要每一次打开一下的好，因为不然的话，数据库临时关闭之后，就出错了吧？
    # 打开数据库连接
    db = pymysql.connect(host=host, user=user, passwd=passwd, db=mydb, port=port, charset='utf8')
    # db = pymysql.connect(host='127.0.0.1', user='root', passwd='971707', db='slnova', port=3306, charset='utf8')
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()

    try:
        cursor.execute(querysql)
        data = cursor.fetchone()
        if data:                     # data有值，那么需要更新
            cursor.execute(updatesql)
        else:                        # 否则，添加
            cursor.execute(addsql)
        #    cursor.execute(delsql)
        # cursor.execute(addsql)     # 添加是一定需要的，删除的话，是需要数据库有数据的时候才删除它


        db.commit()
        print("update info successfully")
    except:
        print("mysql info update error")
        # 输出异常信息
        traceback.print_exc()
        db.rollback()

    # 关闭游标
    cursor.close()
    # 关闭数据库连接
    db.close()




def update_nessus_info(high_vul=0, medium_vul=0, low_vul=0, info_vul=0):
    # 这些是需要更改的，有些参数不需要更改，我就不再更改了，比如当前IP，uuid等信息。
    hoststate.high_vul = high_vul
    hoststate.medium_vul = medium_vul
    hoststate.low_vul = low_vul
    hoststate.info_vul = info_vul

    updatesql = "UPDATE %s SET high_vul = %d, medium_vul = %d, low_vul = %d, info_vul = %d WHERE uuid = '%s'" % \
                (table, hoststate.high_vul, hoststate.medium_vul, hoststate.low_vul, hoststate.info_vul, hoststate.uuid)

    # 要每一次打开一下的好，因为不然的话，数据库临时关闭之后，就出错了吧？
    # 打开数据库连接
    db = pymysql.connect(host=host, user=user, passwd=passwd, db=mydb, port=port, charset='utf8')
    # db = pymysql.connect(host='127.0.0.1', user='root', passwd='971707', db='slnova', port=3306, charset='utf8')
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()

    try:
        cursor.execute(updatesql)   # 由于前面的更新肯定比这一条先执行，所以此处不需要判断是不是已经存在该数据

        db.commit()
        print("update nessus successfully")
    except:
        print("mysql nessus update error")
        # 输出异常信息
        traceback.print_exc()
        db.rollback()

    # 关闭游标
    cursor.close()
    # 关闭数据库连接
    db.close()


"""sched模块实现了一个时间调度程序，该程序可以通过单线程执行来处理按照时间尺度进行调度的时间。
通过调用scheduler.enter(delay,priority,func,args)函数，可以将一个任务添加到任务队列里面，当指定的时间到了，就会执行任务(func函数)。

delay：任务的间隔时间。
priority：如果几个任务被调度到相同的时间执行，将按照priority的增序执行这几个任务。
func：要执行的任务函数
args：func的参数
"""
import time
import sched
import datetime

# s = sched.scheduler(time.time, time.sleep)

# def print_time(a='default'):
#     print('Now Time:',datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),a)


# # 每inc秒运行一次，优先级别为2
# def task():
#     s.enter(0, 2, update_info, argument=())
#     s.run()
#
#
# def perform(inc):
#     s.enter(inc, 0, perform, (inc,))
#     task()
#
#
# def main(inc=3):
#     s.enter(0, 0, perform, (inc,))
#     s.run()

# 上面那个，感觉递归进去太深入了。
from apscheduler.schedulers.background import BackgroundScheduler
def otherscheTask():
    sched = BackgroundScheduler(timezone='MST')
    # 如果有多个任务序列的话可以给每个任务设置ID号，可以根据ID号选择清除对象，且remove放到start前才有效
    sched.add_job(update_info, 'interval', seconds=1, id='update_info_id')
    # sched.remove_job('update_info_id')
    sched.start()



"""
    解释一下下面这个运行，来获取漏洞信息的过程，
    首先，预处理扫描，然后第一次扫描，这样的话得到了scanid和historyid，然后可以使用定时器，来定时检查是否完成，
    如果完成，更新数据并且进行下一次扫描；如果未完成，定时器件进行下一次扫描
"""

scan_id = 0
history_id = 0

def nessus_update():
    global history_id
    (is_complete, info) = check_status_and_update(scan_id, history_id)
    if is_complete:
        update_nessus_info(info["high"], info["medium"], info["low"], info["info"])  # 数据库存储
        history_id = start_scan(scan_id)  # 进行下一次扫描


def nessus_schedulerTask():
    # 这个只需要运行一次，另一次扫描的话只要拿着这个之前的scan_id去扫描就好了
    global  scan_id
    global history_id
    scan_id = pre_scan()
    history_id = start_scan(scan_id)

    # scan_id = 24
    # history_id = 25

    sched = BackgroundScheduler(timezone='MST')
    # 如果有多个任务序列的话可以给每个任务设置ID号，可以根据ID号选择清除对象，且remove放到start前才有效
    sched.add_job(nessus_update, 'interval', seconds=10, id='update_info_id')
    # sched.add_job(nessus_update, 'interval', seconds=10, id='update_info_id', args=[scan_id, history_id])
    # sched.remove_job('update_info_id')
    sched.start()



if __name__ == '__main__':
    # 每隔1秒上传一次
    # main(1.0)
    otherscheTask()
    nessus_schedulerTask()

    # 为了使得这个程序保持运行，需要添加这个while死循环
    while(True):
        time.sleep(10)

    # update_info()
