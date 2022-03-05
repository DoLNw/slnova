from oslo_config import cfg

magface_group = cfg.OptGroup(name="magface", title="magface options")

magface_opts = [
    cfg.StrOpt("train_list", default="../data/ms1m_train.list"),
    cfg.StrOpt("pth_save_fold", default="../saved_model"),
    cfg.IntOpt("epoch", default=26, min=1),  # 五次一保存，正好第一次和最后一次也都是保存的
]

def register_opts(conf):
    conf.register_group(magface_group)
    conf.register_opts(magface_opts, group=magface_group)

def list_opts():
    return {magface_group: magface_opts}



