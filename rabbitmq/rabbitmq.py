#!/usr/bin/python
# -*- coding:utf-8 -*-

"""
https://www.cnblogs.com/shenh/p/10497244.html


模式一：fanout
这种模式下，传递到 exchange 的消息将会转发到所有与其绑定的 queue 上。
不需要指定 routing_key ，即使指定了也是无效。
需要提前将 exchange 和 queue 绑定，一个 exchange 可以绑定多个 queue，一个queue可以绑定多个exchange。
需要先启动 订阅者，此模式下的队列是 consumer 随机生成的，发布者 仅仅发布消息到 exchange ，由 exchange 转发消息至 queue。


模式二：direct
这种工作模式的原理是 消息发送至 exchange，exchange 根据 路由键（routing_key）转发到相对应的 queue 上。
 可以使用默认 exchange =' ' ，也可以自定义 exchange
这种模式下不需要将 exchange 和 任何进行绑定，当然绑定也是可以的。可以将 exchange 和 queue ，routing_key 和 queue 进行绑定
传递或接受消息时 需要 指定 routing_key
需要先启动 订阅者，此模式下的队列是 consumer 随机生成的，发布者 仅仅发布消息到 exchange ，由 exchange 转发消息至 queue。
"""
import time
import pika
from pika.exceptions import ChannelClosed, ConnectionClosed

import sys
sys.path.append("..")

import conf
CONF = conf.CONF
from scheduler.main.host_state import hoststate


# 消息队列基类
class RabbitMQServer(object):
    def __init__(self, mode="fanout"):
        self.host = CONF.rabbitmq.hostname      # 主机
        self.port = CONF.rabbitmq.port          # 端口
        self.username = CONF.rabbitmq.username  # 用户名
        self.password = CONF.rabbitmq.password  # 密码
        self.vhost = CONF.rabbitmq.vhost        # 虚拟主机，VirtualHost之间相互隔离

        self.mode = mode
        self.connection = None
        self.channel = None

        if self.mode == "fanout":
            self.exchange = CONF.rabbitmq.fanout_exchange        # 交换机
            self.queue = CONF.rabbitmq.fanout_queue              # 队列
            self.routing_key = CONF.rabbitmq.fanout_routing_key  # 交换机和队列的绑定
        elif self.mode == "direct":
            self.exchange = CONF.rabbitmq.direct_exchange        # 交换机
            self.queue = CONF.rabbitmq.direct_queue              # 队列
            self.routing_key = CONF.rabbitmq.direct_routing_key  # 交换机和队列的绑定

    def reconnect(self, heartbeat=True):
        try:
            # 关闭旧的连接
            if self.connection and not self.connection.is_closed:
                self.connection.close()

            # 构造登录参数
            credentials = pika.PlainCredentials(self.username, self.password)
            parameters = pika.ConnectionParameters(self.host, self.port, self.vhost, credentials)

            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()

            # 声明交换机
            # 声明exchange，由exchange指定消息在哪个队列传递，如不存在，则创建。durable = True 代表exchange持久化存储，False 非持久化存储
            self.channel.exchange_declare(exchange=self.exchange, exchange_type=self.mode, durable=False)

            if self.mode == "fanout":
                # 消费者实例
                if isinstance(self, RabbitComsumer):
                    # 声明消息队列，消息将在这个队列传递，如不存在，则创建。durable = True 代表消息队列持久化存储，False 非持久化存储
                    # 创建临时队列,队列名传空字符，consumer关闭后，队列自动删除
                    result = self.channel.queue_declare(queue=self.queue, exclusive=False, durable=False)
                    # 绑定队列，fnout不需要queue
                    self.channel.queue_bind(exchange=self.exchange, queue=self.queue)
                    # 表明最大阻塞未ack的消息数量
                    self.channel.basic_qos(prefetch_count=1)
                    # # no_ack 设置成 False，在调用callback函数时，未收到确认标识，消息会重回队列。True，无论调用callback成功与否，消息都被消费掉
                    self.channel.basic_consume(on_message_callback=self.consumer_callback, queue=self.queue,
                                               auto_ack=False)
                # 生产者实例
                elif isinstance(self, RabbitPublisher):
                    # 声明
                    pass

            elif self.mode == "direct":
                # 消费者实例
                if isinstance(self, RabbitComsumer):
                    # 声明消息队列，消息将在这个队列传递，如不存在，则创建。durable = True 代表消息队列持久化存储，False 非持久化存储
                    self.channel.queue_declare(queue=self.queue, exclusive=False, durable=False)
                    # 绑定队列
                    self.channel.queue_bind(exchange=self.exchange, queue=self.queue, routing_key=self.routing_key)
                    # 表明最大阻塞未ack的消息数量
                    self.channel.basic_qos(prefetch_count=1)
                    # # no_ack 设置成 False，在调用callback函数时，未收到确认标识，消息会重回队列。True，无论调用callback成功与否，消息都被消费掉
                    self.channel.basic_consume(on_message_callback=self.consumer_callback, queue=self.queue, auto_ack=False)
                # 生产者实例
                elif isinstance(self, RabbitPublisher):
                    # 声明消息队列，消息将在这个队列传递，如不存在，则创建。durable = True 代表消息队列持久化存储，False 非持久化存储
                    self.channel.queue_declare(queue=self.queue, exclusive=False, durable=False)

        except Exception as e:
            print(e)


def execute(body):
    print("received message: {}".format(body))
    if body == b'start train':
        hoststate.receive_start_train_signal = True
        return True
    if body == b'next epoch':
        hoststate.receive_next_epoch_train_signal = True
        return True
    if body == b'start scheduler':
        hoststate.receive_scheduler_signal = True
        return True
    # 不返回True的话，后面不发送处理成功消息，消息会返回到队列中去
    return True
    # pass


# 消费者
class RabbitComsumer(RabbitMQServer):
    def __init__(self, mode="fanout"):
        super(RabbitComsumer, self).__init__(mode)

    def consumer_callback(self, channel, method, properties, body):
        result = execute(body)  # 模拟处理消息
        if channel.is_open:
            if result:
                channel.basic_ack(delivery_tag=method.delivery_tag)
            else:
                # 处理不成功时，发送no_ack
                channel.basic_nack(delivery_tag=method.delivery_tag, multiple=False, requeue=True)
        if not channel.is_open:
            print("Callback 接收频道关闭，无法ack")

    def start_consumer(self):
        while True:
            try:
                self.reconnect()
                # start_consuming这里就会阻塞，需要想办法起线程
                self.channel.start_consuming()
            except ConnectionClosed as e:  # 保证连接断开重连
                print("ConnectionClosed")
                self.reconnect()
                time.sleep(2)
            except ChannelClosed as e:  # 保证连接断开重连
                print("ChannelClosed")
                self.reconnect()
                time.sleep(2)
            except Exception as e:
                print("Exception")
                print(e)
                self.reconnect()
                time.sleep(2)


# coding:utf-8
# ! /bin/python
import os
import sys
import os.path
import pickle
import struct




import base64
# 生产者
class RabbitPublisher(RabbitMQServer):
    def __init__(self, mode="fanout"):
        super(RabbitPublisher, self).__init__(mode)

    def start_publish(self, message):
        self.reconnect()
        # message=json.dumps({'OrderId': i})

        try:
            # 指定 routing_key。delivery_mode = 2 声明消息在队列中持久化，delivery_mod = 1 消息非持久化
            self.channel.basic_publish(exchange=self.exchange, routing_key=self.routing_key, body=message,
                                       properties=pika.BasicProperties(delivery_mode=1))
            print("send successful")
        except ConnectionClosed as e:
            print("ConnectionClosed")
        except ChannelClosed as e:
            print("ChannelClosed")
        except Exception as e:
            print(e)
            print("Exception")


def send_fanout_signal(message):
    rabbit = RabbitPublisher("fanout")
    rabbit.start_publish(message)
    rabbit.connection.close()

if __name__ == "__main__":
    # rabbit = RabbitPublisher("direct")
    # rabbit.start_publish()

    rabbit_consumer = RabbitComsumer("fanout")
    rabbit_consumer.start_consumer()







