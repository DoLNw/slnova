from oslo_config import cfg

MNIST_group = cfg.OptGroup(name="MNIST", title="MNIST options")

MNIST_opts = [
    cfg.StrOpt("save_aggre_model_fold_path", default="/root/autodl-nas/MNIST/model/aggre"),
    cfg.StrOpt("data_fold_path", default="/root/autodl-nas/MNIST/data"),
    cfg.StrOpt("model_save_fold", default="/root/autodl-nas/MNIST/model"),
    cfg.IntOpt("epochs", default=200, min=1),   # 五次一保存，正好第一次和最后一次也都是保存的
]


def register_opts(conf):
    conf.register_group(MNIST_group)
    conf.register_opts(MNIST_opts, group=MNIST_group)


def list_opts():
    return {MNIST_group: MNIST_opts}

