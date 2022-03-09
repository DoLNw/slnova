# import paramiko  # 用于调用scp命令
#
# from paramiko import SSHClient
# from scp import SCPClient
#
# # 将指定目录的图片文件上传到服务器指定目录
# # remote_path远程服务器目录
# # file_path本地文件夹路径
# # img_name是file_path本地文件夹路径下面的文件名称
# def upload_file(remote_path="/toot",
#                file_path="/Users/jc/jcall/研究实验代码/slnova/rabbitmq/aaa.png"):
#     # img_name示例：07670ff76fc14ab496b0dd411a33ac95-6.webp
#     host = "116.62.233.27"  # 服务器ip地址
#     port = 22  # 端口号
#     username = "root"  # ssh 用户名
#     password = "0717wjcWJCv"  # 密码
#
#     ssh_client = paramiko.SSHClient()
#     ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
#     ssh_client.connect(host, port, username, password)
#     scpclient = SCPClient(ssh_client.get_transport(), socket_timeout=15.0)
#
#     try:
#         scpclient.put(file_path, remote_path)
#     except FileNotFoundError as e:
#         print(e)
#         print("系统找不到指定文件" + file_path)
#     else:
#         print("文件上传成功")
#     ssh_client.close()
#
# if __name__ == "__main__":
#     upload_file()


# !/usr/bin/env python
# coding=UTF-8
'''
Created on 2017年7月15日

@author: liushy
'''
import paramiko
import scpclient
import os
import socket
from contextlib import closing


class scpy(object):
    def __init__(self, host, port, username, password):
        # 服务端相关配置
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        # self.remote_filename = None

    def cli(self):
        # 输入参数：路径（默认当前路径）和pkg名
        self.path = parser.parse_args().path
        self.filename = parser.parse_args().file
        self.remote_filename = parser.parse_args().file

    def scp(self):
        # 创建ssh访问
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(self.host, self.port, self.username, self.password)
        # 创建scp
        with closing(scpclient.Write(ssh.get_transport(), '~')) as scp:
            scp.send_file(self.path + '/' + self.filename, True, remote_filename=self.remote_filename)


def start():
    scp = scpy('192.168.199.233', 22, 'liushy', 'password')
    scp.cli()
    scp.scp()


if __name__ == '__main__':
    start()


