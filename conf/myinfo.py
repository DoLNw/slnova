from oslo_config import cfg

"""
更改的地方，mysql.py中的路径需要更改一下（当然，linux中也可以直接相对路径导入包的，可以见UploadPara文件中的代码，如下：
# from slnova.scheduler.main.host_state import HostState
# from slnova.info import getinfo
from host_state import HostState
import getinfo
"""

"""
import sys
# sys.path.append("/Users/jc/jcall/研究实验代码")
from slnova.info import getinfo）
然后就是下面的需要扫描的IP
"""

nessus_group = cfg.OptGroup(name="nessus",
                           title="nessus options")

nessus_opts = [
    cfg.StrOpt("scanned_ip",
        default="116.62.233.27",
        # default="114.55.95.44",
        deprecated_group="DEFAULT",
        help="""
        扫描不同的IP时需要更改
        """),
    cfg.StrOpt("nessus_url",
        default="https://116.62.233.27:8834",
        deprecated_group="DEFAULT",
        help="""
        """),
    cfg.StrOpt("username",
        default="jcwang",
        deprecated_group="DEFAULT",
        help="""   
        """),
    cfg.StrOpt("password",
        default="971707",
        deprecated_group="DEFAULT",
        help="""
        """),
    cfg.StrOpt("accessKey",
        default="0206e24ee732c635e10964442df569e8cc3c54358aba722f25585ab35eb19294",
        deprecated_group="DEFAULT",
        help="""
        """),
    cfg.StrOpt("secretKey",
        default="8a0d597a7373a4c39d031d7f45634a7bf98afa9626c7792ccd5a06de55e7c56a",
        deprecated_group="DEFAULT",
        help="""
        """),
]

mysql_group = cfg.OptGroup(name="mysql",
                           title="mysql options")

mysql_opts = [
    cfg.StrOpt("host",
        default="116.62.233.27",
        deprecated_group="DEFAULT",
        help="""
        """),
    cfg.StrOpt("user",
        default="root",
        deprecated_group="DEFAULT",
        help="""
        """),
    cfg.StrOpt("passwd",
        default="971707",
        deprecated_group="DEFAULT",
        help="""   
        """),
    cfg.StrOpt("db",
        default="slnova",
        deprecated_group="DEFAULT",
        help="""
        """),
    cfg.IntOpt("port",
        default=3306,
        deprecated_group="DEFAULT",
        help="""
        """),
    cfg.StrOpt("table",
        default="test",
        deprecated_group="DEFAULT",
        help="""
        """),
]


def register_opts(conf):
    conf.register_group(nessus_group)
    conf.register_opts(nessus_opts, group=nessus_group)

    conf.register_group(mysql_group)
    conf.register_opts(mysql_opts, group=mysql_group)


def list_opts():
    return {nessus_group: nessus_opts,
            mysql_group: mysql_opts}

