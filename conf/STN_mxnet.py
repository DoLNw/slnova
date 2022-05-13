from oslo_config import cfg

STN_group = cfg.OptGroup(name="STN", title="STN options")

STN_opts = [
    cfg.StrOpt("save_aggre_model_fold_path", default="/root/autodl-nas/STN/model/aggre"),
    cfg.StrOpt("config_path", default="config/PEMS08/individual_3layer_12T.json"),
    cfg.StrOpt("model_save_fold", default="/root/autodl-nas/STN/model"),
    cfg.IntOpt("epochs", default=200, min=1),   # 五次一保存，正好第一次和最后一次也都是保存的
]


def register_opts(conf):
    conf.register_group(STN_group)
    conf.register_opts(STN_opts, group=STN_group)


def list_opts():
    return {STN_group: STN_opts}

