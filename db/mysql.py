
# sql = "INSERT INTO EMPLOYEE(FIRST_NAME, \
#        LAST_NAME, AGE, SEX, INCOME) \
#        VALUES (%s, %s, %s, %s, %s )" % \
#        ('Mac', 'Mohan', 20, 'M', 2000)

# delsql = "delete from test where uuid = %s" % '213'
# addsql = """INSERT INTO test(uuid, isrunning, cpufreq, free_disk_mb,
#          total_usable_disk_gb, disk_allocation_ratio)
#          VALUES ("213", True, 3, 4, 5, %d)""" % 100

# sql = "SELECT VERSION()"
# sql = "SELECT * FROM test"
# sql = "UPDATE test SET cpufreq=4 isrunning = True WHERE uuid = '%s'" % ('213')


# a = results = cursor.fetchall()

import pymysql
import traceback
import sys
sys.path.append("/Users/jc")

from slnova.scheduler.main.host_manager import HostState
from slnova.info import getinfo

# 实现一个定期向数据库更新电脑参数数据

def update_info():
   hoststate = HostState(isrunning=False, uuid=getinfo.get_uuid(), cpufreq=getinfo.get_cpu_freq(), \
                         free_memory_mb=getinfo.get_free_memory_mb(), \
                         total_usable_disk_gb=getinfo.get_total_usable_disk_gb(), disk_allocation_ratio = 1, \
                         cpu_percent=getinfo.get_cpu_percent())
   querysql = "SELECT * FROM test where uuid = '%s'" % hoststate.uuid
   delsql = "delete from test where uuid = '%s'" % hoststate.uuid
   addsql = """INSERT INTO test(uuid, isrunning, cpufreq, free_memory_mb, total_usable_disk_gb, \
               disk_allocation_ratio, cpu_percent) VALUES ('%s', %d, %d, %d, %d, %.2f, %f)""" % \
            (hoststate.uuid, hoststate.isrunning, hoststate.cpufreq, hoststate.free_memory_mb, \
             hoststate.total_usable_disk_gb, hoststate.disk_allocation_ratio, hoststate.cpu_percent)
   # 打开数据库连接
   db = pymysql.connect(host='116.62.233.27', user='root', passwd='971707', db='slnova', port=3306, charset='utf8')
   # 使用cursor()方法获取操作游标
   cursor = db.cursor()

   try:
      cursor.execute(querysql)
      data = cursor.fetchone()
      if data: # data有值，那么需要删除
         cursor.execute(delsql)
      cursor.execute(addsql)     # 添加是一定需要的，删除的话，是需要数据库有数据的时候才删除它

      db.commit()
      print("update successfully")
   except:
      print("mysql update error")
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

s = sched.scheduler(time.time, time.sleep)

# def print_time(a='default'):
#     print('Now Time:',datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),a)


# 每五分钟运行一次，优先级别为2
def task():
    s.enter(5, 2, update_info, argument=())
    s.run()


def perform(inc):
    s.enter(inc, 0, perform, (inc,))
    task()


def main(inc=3):
    s.enter(0, 0, perform, (inc,))
    s.run()


if __name__ == '__main__':
    main()

