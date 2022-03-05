from oslo_config import cfg

rabbitmq_group = cfg.OptGroup(name="rabbitmq", title="rabbitmq options")

rabbitmq_opts = [
    cfg.StrOpt("hostname", default="116.62.233.27"),
    cfg.IntOpt("port", default=5672),
    cfg.StrOpt("vhost", default="vhost"),
    cfg.StrOpt("username", default="rabbit",),
    cfg.StrOpt("password", default="password"),

    cfg.StrOpt("fanout_exchange", default="ml_fanout_exchange"),
    cfg.StrOpt("fanout_queue", default=""),
    cfg.StrOpt("fanout_routing_key", default=""),

    cfg.StrOpt("direct_exchange", default="ml_direct_exchange"),
    cfg.StrOpt("direct_queue", default="ml_direct_ququq"),
    cfg.StrOpt("direct_routing_key", default="ml_direct_routing_key"),
]


def register_opts(conf):
    conf.register_group(rabbitmq_group)
    conf.register_opts(rabbitmq_opts, group=rabbitmq_group)


def list_opts():
    return {rabbitmq_group: rabbitmq_opts}



