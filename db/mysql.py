# -*- coding: utf-8 -*-
import pymysql
import traceback

import conf
CONF = conf.CONF

host = CONF.mysql.host
user = CONF.mysql.user
passwd = CONF.mysql.passwd
mydb = CONF.mysql.db
port = CONF.mysql.port
table = CONF.mysql.table

import threading
lock = threading.Lock()

from scheduler.main.host_state import hoststate, update_basic_info, update_model_size_mb, format_hoststate
from info.nessus import check_status_and_update, pre_scan, start_scan

# 会自动把bool转成tinyint，0是false，1是true
new_table_sql = """create table if not exists test(
                   uuid varchar(255) not null,
                   disk_allocation_ratio double not null,
                   name varchar(255) not null default 'NoneName',
                   ip varchar(255) not null default '0.0.0.0',
                   total_disk_gb  double not null,
                   total_memory_gb  double not null,
                   gpu_total_memory_gb  double not null,
                   cpu_max_freq double not null,
                   time varchar(255) not null default '1970-0-0 00:00:00',
                   cpu_percent double not null,
                   used_disk_gb double not null,
                   used_memory_gb double not null,
                   gpu_used_memory_gb double not null,
                   cpu_current_freq double not null,
                   high_vul int not null default 0,
                   medium_vul int not null default 0,
                   low_vul int not null default 0,
                   info_vul int not null default 0,
                   model_size_mb double not null null default 0.0,
                   loss double not null default 0.0,
                   accuracy double not null,
                   epoch int not null default -1,
                   is_aggregating bool not null default False,
                   is_training bool not null default False,
                   primary key(uuid))
                """


def reconnect():
    global db
    global cursor
    # 要每一次打开一下的好，因为不然的话，数据库临时关闭之后，就出错了吧？
    # 打开数据库连接
    db = pymysql.connect(host=host, user=user, passwd=passwd, db=mydb, port=port, charset='utf8')
    # db = pymysql.connect(host='127.0.0.1', user='root', passwd='971707', db='slnova', port=3306, charset='utf8')
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()

first_init = True
if first_init:
    first_init = False
    reconnect()

# 执行sql语句，下面所有的信息更新的sql语句执行，都要调用这句话
def sql_excute(upload_sql, func_name):
    query_sql = "SELECT * FROM %s where uuid = '%s'" % (table, hoststate.uuid)
    # del_sql = "delete from %s where uuid = '%s'" % (table, hoststate.uuid)
    add_sql = """INSERT INTO %s(uuid,
                 disk_allocation_ratio, 
                 name, 
                 ip, 
                 total_disk_gb, 
                 total_memory_gb, 
                 gpu_total_memory_gb, 
                 cpu_max_freq, 
                 time, 
                 cpu_percent, 
                 used_disk_gb, 
                 used_memory_gb, 
                 gpu_used_memory_gb, 
                 cpu_current_freq, 
                 high_vul, 
                 medium_vul, 
                 low_vul, 
                 info_vul, 
                 model_size_mb, 
                 loss, 
                 accuracy, 
                 epoch, 
                 is_aggregating, 
                 is_training) 
                 VALUES ('%s', %.2f, '%s', '%s', %.2f, %.2f, %.2f, %.2f, '%s', 
                 %.2f, %.2f, %.2f, %.2f, %.4f, %d, %d, %d, %d, %.2f, %.2f, %.2f, %d, %d, %d)
             """ % (table,
                    hoststate.uuid,
                    hoststate.disk_allocation_ratio,
                    hoststate.name,
                    hoststate.ip,
                    hoststate.total_disk_gb,
                    hoststate.total_memory_gb,
                    hoststate.gpu_total_memory_gb,
                    hoststate.cpu_max_freq,
                    hoststate.time,
                    hoststate.cpu_percent,
                    hoststate.used_disk_gb,
                    hoststate.used_memory_gb,
                    hoststate.gpu_used_memory_gb,
                    hoststate.cpu_current_freq,
                    hoststate.high_vul,
                    hoststate.medium_vul,
                    hoststate.low_vul,
                    hoststate.info_vul,
                    hoststate.model_size_mb,
                    hoststate.loss,
                    hoststate.accuracy,
                    hoststate.epoch,
                    hoststate.is_aggregating,
                    hoststate.is_training
                    )

    try:
        lock.acquire()
        cursor.execute(new_table_sql)  # 已经创建了我就注释掉得了，毕竟需要占用点cpu的
        cursor.execute(query_sql)
        data = cursor.fetchone()
        if data:  # data有值，那么需要更新
            cursor.execute(upload_sql)
        else:  # 否则，添加
            cursor.execute(add_sql)

        #    cursor.execute(del_sql)
        # cursor.execute(add_sql)     # 添加是一定需要的，删除的话，是需要数据库有数据的时候才删除它
        db.commit()

        # print("{} successfully".format(func_name))
    except:
        print("{} error".format(func_name))
        # 输出异常信息
        traceback.print_exc()
        # db.rollback()

        # 若是被关闭了，则重新等待链接，直接成功呗s
        reconnect()
    finally:
        lock.release()

    # # 关闭游标
    # cursor.close()
    # # 关闭数据库连接
    # db.close()

# 更新一些主机的基本信息
def upload_basic_info():
    update_basic_info()  # 注意，一个是upload，一个是update

    # 注意， update语句中where前面是没有逗号的，不确定的话，可以去数据库测试
    update_sql = """UPDATE %s SET time = '%s', 
                    cpu_percent = %.2f, 
                    used_disk_gb = %.2f, 
                    used_memory_gb = %.2f, 
                    gpu_used_memory_gb = %.2f, 
                    cpu_current_freq = %.4f
                    WHERE uuid = '%s'
                 """ % (table,
                        hoststate.time,
                        hoststate.cpu_percent,
                        hoststate.used_disk_gb,
                        hoststate.used_memory_gb,
                        hoststate.gpu_used_memory_gb,
                        hoststate.cpu_current_freq,
                        hoststate.uuid)

    sql_excute(update_sql, "upload_basic_info")

# 更新安全风险信息
def upload_nessus_info(high_vul=0, medium_vul=0, low_vul=0, info_vul=0):
    # 这些是需要更改的，有些参数不需要更改，我就不再更改了，比如当前IP，uuid等信息。
    hoststate.high_vul = high_vul
    hoststate.medium_vul = medium_vul
    hoststate.low_vul = low_vul
    hoststate.info_vul = info_vul

    upload_sql = "UPDATE %s SET high_vul = %d, medium_vul = %d, low_vul = %d, info_vul = %d WHERE uuid = '%s'" % \
                 (table, hoststate.high_vul, hoststate.medium_vul, hoststate.low_vul, hoststate.info_vul, hoststate.uuid)

    sql_excute(upload_sql, "upload_nessus_info")

# 更新是否在训练的信息
def upload_is_training_status(is_training):
    hoststate.is_training = is_training

    upload_sql = "UPDATE %s SET is_training = %d WHERE uuid = '%s'" % \
                 (table, hoststate.is_training, hoststate.uuid)

    sql_excute(upload_sql, "upload_is_training_status")

# 更新是否在聚合的信息
def upload_is_aggregating_status(is_aggregating):
    hoststate.is_aggregating = is_aggregating

    upload_sql = "UPDATE %s SET is_aggregating = %d WHERE uuid = '%s'" % \
                 (table, hoststate.is_aggregating, hoststate.uuid)

    sql_excute(upload_sql, "upload_is_aggregating_status")

# 更新有关机器学习方面的信息
def upload_ml_info(loss=0.0, accuracy=0.0, epoch=-1, model_path=""):
    # 这些是需要更改的，有些参数不需要更改，我就不再更改了，比如当前IP，uuid等信息。
    hoststate.loss = loss
    hoststate.accuracy = accuracy
    hoststate.epoch = epoch
    hoststate.model_size_mb = update_model_size_mb(model_path)

    upload_sql = "UPDATE %s SET model_size_mb = %.2f, loss = %.4f, accuracy = %.4f, epoch = %d WHERE uuid = '%s'" % \
                 (table, hoststate.model_size_mb, hoststate.loss, hoststate.accuracy, hoststate.epoch, hoststate.uuid)

    sql_excute(upload_sql, "update_ml_info")


# 更新基本信息，需要用定时器每个每隔1s执行一次
import time
from apscheduler.schedulers.background import BackgroundScheduler
def basic_info_upload_taskask():
    sched = BackgroundScheduler(timezone='MST')
    # 如果有多个任务序列的话可以给每个任务设置ID号，可以根据ID号选择清除对象，且remove放到start前才有效
    sched.add_job(upload_basic_info, 'interval', seconds=1, id='upload_basic_info_id', max_instances=7)
    # sched.remove_job('upload_basic_info_id')
    sched.start()



"""
    解释一下下面这个运行，来获取漏洞信息的过程，
    首先，预处理扫描，然后第一次扫描，这样的话得到了scanid和historyid，然后可以使用定时器，来定时检查是否完成，
    如果完成，更新数据并且进行下一次扫描；如果未完成，定时器件进行下一次扫描
"""
scan_id = 0
history_id = 0


def nessus_upload():
    global history_id
    (is_complete, info) = check_status_and_update(scan_id, history_id)
    if is_complete:
        upload_nessus_info(info["high"], info["medium"], info["low"], info["info"])  # 数据库存储
        history_id = start_scan(scan_id)  # 进行下一次扫描


def nessus_upload_task():
    # 这个只需要运行一次，另一次扫描的话只要拿着这个之前的scan_id去扫描就好了
    global  scan_id
    global history_id
    scan_id = pre_scan()
    history_id = start_scan(scan_id)

    # scan_id = 24
    # history_id = 25

    sched = BackgroundScheduler(timezone='MST')
    # 如果有多个任务序列的话可以给每个任务设置ID号，可以根据ID号选择清除对象，且remove放到start前才有效
    sched.add_job(nessus_upload, 'interval', seconds=10, id='upload_basic_info_id')
    # sched.add_job(nessus_upload, 'interval', seconds=10, id='upload_basic_info_id', args=[scan_id, history_id])
    # sched.remove_job('upload_basic_info_id')
    sched.start()



def get_all_hosts_info():
    query_sql = "SELECT * FROM %s" % (table)

    reconnect()

    try:
        lock.acquire()
        cursor.execute(query_sql)
        datas = cursor.fetchall()
        db.commit()
        # print("get_all_hosts_info successfully")
    except:
        print("get_all_hosts_info error")
        # 输出异常信息
        traceback.print_exc()
        # db.rollback()
    finally:
        lock.release()

    # # 关闭游标
    # cursor.close()
    # # 关闭数据库连接
    # db.close()

    return format_hoststate(datas)


def get_all_training_host_uuids():
    query_sql = "SELECT * FROM %s" % (table)
    reconnect()

    try:
        lock.acquire()
        cursor.execute(query_sql)
        datas = cursor.fetchall()
        db.commit()


        print("get_all_training_hosts_num successfully")
    except:
        print("get hosts' info error")
        # 输出异常信息
        traceback.print_exc()
        # db.rollback()
    finally:
        lock.release()

    # # 关闭游标
    # cursor.close()
    # # 关闭数据库连接
    # db.close()

    host_states = format_hoststate(datas)
    current_training_host_state_uuids = []

    # 假设没有别的current_training_hosts_num属性为true但是不在运行的情况
    current_training_hosts_num = 0
    for host_state in host_states:
        if host_state.is_training:
            current_training_hosts_num += 1
            current_training_host_state_uuids.append(host_state.uuid)

    return current_training_host_state_uuids


if __name__ == '__main__':
    # 每隔1秒上传一次
    # main(1.0)
    basic_info_upload_taskask()
    # nessus_upload_task()

    # 为了使得这个程序保持运行，需要添加这个while死循环
    while True:
        time.sleep(10)

    # upload_basic_info()

    #
    # a = get_all_hosts_info()
    # for b in a:
    #     print(b.description())








