import paramiko  # 用于调用scp命令

from scp import SCPClient

# 将指定目录的图片文件上传到服务器指定目录
# remote_path远程服务器目录
# file_path本地文件夹路径
# img_name是file_path本地文件夹路径下面的文件名称
def upload_file(remote_path="/toot",
               file_path="/Users/jc/jcall/研究实验代码/slnova/rabbitmq/aaa.png"):
    # img_name示例：07670ff76fc14ab496b0dd411a33ac95-6.webp
    host = "116.62.233.27"  # 服务器ip地址
    port = 22  # 端口号
    username = "root"  # ssh 用户名
    password = "0717wjcWJCv"  # 密码

    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
    ssh_client.connect(host, port, username, password)
    scpclient = SCPClient(ssh_client.get_transport(), socket_timeout=15.0)

    try:
        scpclient.put(file_path, remote_path)
    except FileNotFoundError as e:
        print(e)
        print("系统找不到指定文件" + file_path)
    else:
        print("文件上传成功")
    ssh_client.close()

if __name__ == "__main__":
    upload_file()