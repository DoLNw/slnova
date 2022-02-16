# -*- coding: utf-8 -*-

# import requests
# import json
#
# # [使用Python调用Nessus 接口实现自动化扫描](https://cloud.tencent.com/developer/article/1581977)
#
#
# def get_token(ip, port, username, password):
#     url = "https://{0}:{1}/session".format(ip, port)
#     post_data = {
#         'username': username,
#         'password': password
#     }
#
#     response = requests.post(url, data=post_data, verify=False)
#     if response.status_code == 200:
#         data = json.loads(response.text)
#         return data["token"]
#
# # # 第一种请求方式，使用token
# # def get_scan_list(ip, port, username, password):
# #     # 这里ip和port可以从配置文件中读取或者从数据库读取，这里我省略了获取这些配置值得操作
# #     url = "https://{0}:{1}/scans".format(ip, port)
# #     token = get_token(ip, port, username, password)
# #     if token:
# #         header = {
# #             "X-Cookie": "token={0}".format(token),
# #             "Content-Type": "application/json"
# #         }
# #         response = requests.get(url, headers=header, verify=False)
# #         if response.status_code == 200:
# #             result = json.loads(response.text)
# #             return result
#
# accessKey = "194cfc85ede189f1c048c50d5e102acb9ea0b2b5be5ee99d2380fb4e2d721fd0"  # 此处填入真实的内容
# secretKey = "feaaec80726c645eb78744e464dbcc0626eec2973792da275677421206e73a60"  # 此处填入真实内容
#
# # 第二种请求方式，使用accessKey和secretKey
# def get_scan_list(ip, port, username, password):
#     url = "https://{0}:{1}/scans".format(ip, port)
#     token = get_token(ip, port, username, password)
#     if token:
#         header = {
#             'X-ApiKeys': 'accessKey={accesskey};secretKey={secretkey}'.format(accesskey=accessKey, secretkey=secretKey),
#             "Content-Type": "application/json"
#         }
#         response = requests.get(url, headers=header, verify=False)
#         if response.status_code == 200:
#             result = json.loads(response.text)
#             return result
#
#
# # 获取策略模板uuid的方法，主要思路是获取系统中所有模板，然后根据模板名称返回对应的uuid值，默认用"advanced策略模版"
# def get_nessus_template_uuid(ip, port, template_name="advanced"):
#     header = {
#         'X-ApiKeys': 'accessKey={accesskey};secretKey={secretkey}'.format(accesskey=accessKey,
#                                                                           secretkey=secretKey),
#         'Content-type': 'application/json',
#         'Accept': 'text/plain'}
#
#     api = "https://{ip}:{port}/editor/scan/templates".format(ip=ip, port=port)
#     response = requests.get(api, headers=header, verify=False)
#     templates = json.loads(response.text)['templates']
#
#     for template in templates:
#         if template['name'] == template_name:
#             return template['uuid']
#     return None
#
#
# # # 创建扫描策略模版实例
# # def create_template(ip, port, **kwargs):  # kwargs 作为可选参数，用来配置settings和其他项
# #     header = {
# #         "X-ApiKeys": "accessKey={accesskey};secretKey={secretkey}".format(accesskey=accessKey,
# #                                                                           secretkey=secretKey),
# #         "Content-Type": "application/json",
# #         "Accept": "text/plain"
# #     }
# #     policys = {}
# #
# #     # 这里 grouppolicy_set 存储的是策略模板中各个脚本名称以及脚本是否启用的信息
# #     for policy in grouppolicy_set:
# #         enabled = "enabled" if policy.enable else "disabled"
# #         policys[policy.name] = {
# #             "status": enabled
# #     }
# #
# #     # settings里面的各小项必须得带上，否则会创建不成功
# #     # 弱口令文件需要事先上传，后面会提到上传文件接口
# #     settings = {
# #         "name": template.name,
# #         "watchguard_offline_configs": "",
# #         "unixfileanalysis_disable_xdev": "no",
# #         "unixfileanalysis_include_paths": "",
# #         "unixfileanalysis_exclude_paths": "",
# #         "unixfileanalysis_file_extensions": "",
# #         "unixfileanalysis_max_size": "",
# #         "unixfileanalysis_max_cumulative_size": "",
# #         "unixfileanalysis_max_depth": "",
# #         "unix_docker_scan_scope": "host",
# #         "sonicos_offline_configs": "",
# #         "netapp_offline_configs": "",
# #         "junos_offline_configs": "",
# #         "huawei_offline_configs": "",
# #         "procurve_offline_configs": "",
# #         "procurve_config_to_audit": "Saved/(show config)",
# #         "fortios_offline_configs": "",
# #         "fireeye_offline_configs": "",
# #         "extremeos_offline_configs": "",
# #         "dell_f10_offline_configs": "",
# #         "cisco_offline_configs": "",
# #         "cisco_config_to_audit": "Saved/(show config)",
# #         "checkpoint_gaia_offline_configs": "",
# #         "brocade_offline_configs": "",
# #         "bluecoat_proxysg_offline_configs": "",
# #         "arista_offline_configs": "",
# #         "alcatel_timos_offline_configs": "",
# #         "adtran_aos_offline_configs": "",
# #         "patch_audit_over_telnet": "no",
# #         "patch_audit_over_rsh": "no",
# #         "patch_audit_over_rexec": "no",
# #         "snmp_port": "161",
# #         "additional_snmp_port1": "161",
# #         "additional_snmp_port2": "161",
# #         "additional_snmp_port3": "161",
# #         "http_login_method": "POST",
# #         "http_reauth_delay": "",
# #         "http_login_max_redir": "0",
# #         "http_login_invert_auth_regex": "no",
# #         "http_login_auth_regex_on_headers": "no",
# #         "http_login_auth_regex_nocase": "no",
# #         "never_send_win_creds_in_the_clear": "yes" if kwargs["never_send_win_creds_in_the_clear"] else "no",
# #         "dont_use_ntlmv1": "yes" if kwargs["dont_use_ntlmv1"] else "no",
# #         "start_remote_registry": "yes" if kwargs["start_remote_registry"] else "no",
# #         "enable_admin_shares": "yes" if kwargs["enable_admin_shares"] else "no",
# #         "ssh_known_hosts": "",
# #         "ssh_port": kwargs["ssh_port"],
# #         "ssh_client_banner": "OpenSSH_5.0",
# #         "attempt_least_privilege": "no",
# #         "region_dfw_pref_name": "yes",
# #         "region_ord_pref_name": "yes",
# #         "region_iad_pref_name": "yes",
# #         "region_lon_pref_name": "yes",
# #         "region_syd_pref_name": "yes",
# #         "region_hkg_pref_name": "yes",
# #         "microsoft_azure_subscriptions_ids": "",
# #         "aws_ui_region_type": "Rest of the World",
# #         "aws_us_east_1": "",
# #         "aws_us_east_2": "",
# #         "aws_us_west_1": "",
# #         "aws_us_west_2": "",
# #         "aws_ca_central_1": "",
# #         "aws_eu_west_1": "",
# #         "aws_eu_west_2": "",
# #         "aws_eu_west_3": "",
# #         "aws_eu_central_1": "",
# #         "aws_eu_north_1": "",
# #         "aws_ap_east_1": "",
# #         "aws_ap_northeast_1": "",
# #         "aws_ap_northeast_2": "",
# #         "aws_ap_northeast_3": "",
# #         "aws_ap_southeast_1": "",
# #         "aws_ap_southeast_2": "",
# #         "aws_ap_south_1": "",
# #         "aws_me_south_1": "",
# #         "aws_sa_east_1": "",
# #         "aws_use_https": "yes",
# #         "aws_verify_ssl": "yes",
# #         "log_whole_attack": "no",
# #         "enable_plugin_debugging": "no",
# #         "audit_trail": "use_scanner_default",
# #         "include_kb": "use_scanner_default",
# #         "enable_plugin_list": "no",
# #         "custom_find_filepath_exclusions": "",
# #         "custom_find_filesystem_exclusions": "",
# #         "reduce_connections_on_congestion": "no",
# #         "network_receive_timeout": "5",
# #         "max_checks_per_host": "5",
# #         "max_hosts_per_scan": "100",
# #         "max_simult_tcp_sessions_per_host": "",
# #         "max_simult_tcp_sessions_per_scan": "",
# #         "safe_checks": "yes",
# #         "stop_scan_on_disconnect": "no",
# #         "slice_network_addresses": "no",
# #         "allow_post_scan_editing": "yes",
# #         "reverse_lookup": "no",
# #         "log_live_hosts": "no",
# #         "display_unreachable_hosts": "no",
# #         "report_verbosity": "Normal",
# #         "report_superseded_patches": "yes",
# #         "silent_dependencies": "yes",
# #         "scan_malware": "no",
# #         "samr_enumeration": "yes",
# #         "adsi_query": "yes",
# #         "wmi_query": "yes",
# #         "rid_brute_forcing": "no",
# #         "request_windows_domain_info": "no",
# #         "scan_webapps": "no",
# #         "start_cotp_tsap": "8",
# #         "stop_cotp_tsap": "8",
# #         "modbus_start_reg": "0",
# #         "modbus_end_reg": "16",
# #         "hydra_always_enable": "yes" if kwargs["hydra_always_enable"] else "no",
# #         "hydra_logins_file": "" if kwargs["hydra_logins_file"] else kwargs["hydra_logins_file"],
# #         "hydra_passwords_file": "" if kwargs["hydra_passwords_file"] else kwargs["hydra_passwords_file"],
# #         "hydra_parallel_tasks": "16",
# #         "hydra_timeout": "30",
# #         "hydra_empty_passwords": "yes",
# #         "hydra_login_as_pw": "yes",
# #         "hydra_exit_on_success": "no",
# #         "hydra_add_other_accounts": "yes",
# #         "hydra_postgresql_db_name": "",
# #         "hydra_client_id": "",
# #         "hydra_win_account_type": "Local accounts",
# #         "hydra_win_pw_as_hash": "no",
# #         "hydra_cisco_logon_pw": "",
# #         "hydra_web_page": "",
# #         "hydra_proxy_test_site": "",
# #         "hydra_ldap_dn": "",
# #         "test_default_oracle_accounts": "no",
# #         "provided_creds_only": "yes",
# #         "smtp_domain": "example.com",
# #         "smtp_from": "nobody@example.com",
# #         "smtp_to": "postmaster@[AUTO_REPLACED_IP]",
# #         "av_grace_period": "0",
# #         "report_paranoia": "Normal",
# #         "thorough_tests": "no",
# #         "detect_ssl": "yes",
# #         "tcp_scanner": "no",
# #         "tcp_firewall_detection": "Automatic (normal)",
# #         "syn_scanner": "yes",
# #         "syn_firewall_detection": "Automatic (normal)",
# #         "wol_mac_addresses": "",
# #         "wol_wait_time": "5",
# #         "scan_network_printers": "no",
# #         "scan_netware_hosts": "no",
# #         "scan_ot_devices": "no",
# #         "ping_the_remote_host": "yes",
# #         "tcp_ping": "yes",
# #         "icmp_unreach_means_host_down": "no",
# #         "test_local_nessus_host": "yes",
# #         "fast_network_discovery": "no",
# #
# #         "arp_ping": "yes" if kwargs["arp_ping"] else "no",
# #         "tcp_ping_dest_ports": kwargs["tcp_ping_dest_ports"],
# #         "icmp_ping": "yes" if kwargs["icmp_ping"] else "no",
# #         "icmp_ping_retries": kwargs["icmp_ping_retries"],
# #         "udp_ping": "yes" if kwargs["udp_ping"] else "no",
# #         "unscanned_closed": "yes" if kwargs["unscanned_closed"] else "no",
# #         "portscan_range": kwargs["portscan_range"],
# #         "ssh_netstat_scanner": "yes" if kwargs["ssh_netstat_scanner"] else "no",
# #         "wmi_netstat_scanner": "yes" if kwargs["wmi_netstat_scanner"] else "no",
# #         "snmp_scanner": "yes" if kwargs["snmp_scanner"] else "no",
# #         "only_portscan_if_enum_failed": "yes" if kwargs["only_portscan_if_enum_failed"] else "no",
# #         "verify_open_ports": "yes" if kwargs["verify_open_ports"] else "no",
# #         "udp_scanner": "yes" if kwargs["udp_scanner"] else "no",
# #         "svc_detection_on_all_ports": "yes" if kwargs["svc_detection_on_all_ports"] else "no",
# #         "ssl_prob_ports": "Known SSL ports" if kwargs["ssl_prob_ports"] else "All ports",
# #         "cert_expiry_warning_days": kwargs["cert_expiry_warning_days"],
# #         "enumerate_all_ciphers": "yes" if kwargs["enumerate_all_ciphers"] else "no",
# #         "check_crl": "yes" if kwargs["check_crl"] else "no",
# #     }
# #
# #     credentials = {
# #         "add": {
# #             "Host": {
# #                 "SSH": [],
# #                 "SNMPv3": [],
# #                 "Windows": [],
# #             },
# #             "Plaintext Authentication": {
# #                 "telnet/rsh/rexec": []
# #             }
# #         }
# #     }
# #     try:
# #         if kwargs["snmpv3_username"] and kwargs["snmpv3_port"] and kwargs["snmpv3_level"]:
# #             level = kwargs["snmpv3_level"]
# #             print("asdasd")
# #             print(level)
# #             if level == NessusSettings.LOW:
# #                 credentials["add"]["Host"]["SNMPv3"].append({
# #                     "security_level": "No authentication and no privacy",
# #                     "username": kwargs["snmpv3_username"],
# #                     "port": kwargs["snmpv3_port"]
# #                 })
# #             elif level == NessusSettings.MID:
# #                 credentials["add"]["Host"]["SNMPv3"].append({
# #                     "security_level": "Authentication without privacy",
# #                     "username": kwargs["snmpv3_username"],
# #                     "port": kwargs["snmpv3_port"],
# #                     "auth_algorithm": NessusSettings.AUTH_ALG[kwargs["snmpv3_auth"][1]],
# #                     "auth_password": kwargs["snmpv3_auth_psd"]
# #                 })
# #             elif level == NessusSettings.HIGH:
# #                 credentials["add"]["Host"]["SNMPv3"].append({
# #                     "security_level": "Authentication and privacy",
# #                     "username": kwargs["snmpv3_username"],
# #                     "port": kwargs["snmpv3_port"],
# #                     "auth_algorithm": NessusSettings.AUTH_ALG[kwargs["snmpv3_auth"]][1],
# #                     "auth_password": kwargs["snmpv3_auth_psd"],
# #                     "privacy_algorithm": NessusSettings.PPIVACY_ALG[kwargs["snmpv3_hide"]][1],
# #                     "privacy_password": kwargs["snmpv3_hide_psd"]
# #                 })
# #
# #         if kwargs["ssh_username"] and kwargs["ssh_psd"]:
# #             credentials["add"]["Host"]["SSH"].append(
# #                 {
# #                     "auth_method": "password",
# #                     "username": kwargs["ssh_username"],
# #                     "password": kwargs["ssh_psd"],
# #                     "elevate_privileges_with": "Nothing",
# #                     "custom_password_prompt": "",
# #                 })
# #
# #         if kwargs["windows_username"] and kwargs["windows_psd"]:
# #             credentials["add"]["Host"]["Windows"].append({
# #                 "auth_method": "Password",
# #                 "username": kwargs["windows_username"],
# #                 "password": kwargs["windows_psd"],
# #                 "domain": kwargs["ssh_host"]
# #             })
# #
# #         if kwargs["telnet_username"] and kwargs["telnet_password"]:
# #             credentials["add"]["Plaintext Authentication"]["telnet/rsh/rexec"].append({
# #                 "username": kwargs["telnet_username"],
# #                 "password": kwargs["telnet_password"]
# #             })
# #
# #
# #     data = {
# #         "uuid": get_nessus_template_uuid(ip, port, "advanced"),
# #         "settings": settings,
# #         "plugins": policys,
# #         "credentials": credentials
# #     }
# #
# #     api = "https://{0}:{1}/policies".format(ip, port)
# #     response = requests.post(api, headers=header, data=json.dumps(data, ensure_ascii=False).encode("utf-8"),
# #                              # 这里做一个转码防止在nessus端发生中文乱码
# #                              verify=False)
# #     if response.status_code == 200:
# #         data = json.loads(response.text)
# #         return data["policy_id"]  # 返回策略模板的id，后续可以在创建任务时使用
# #     else:
# #         return None
#
#
#
# """
# 创建任务重要的参数如下说明如下:
# 1. uuid: 创建任务时使用的模板id，这个id同样是我们上面说的系统自带的模板id
# 2. name：任务名称
# 3. policy_id：策略模板ID，这个是可选的，如果要使用上面我们自己定义的扫描模板，需要使用这个参数来指定，并且设置上面的uuid为 custom 的uuid，
#    这个值表示使用用户自定义模板；当然如果就想使用系统提供的，这个字段可以不填
# 4. text_targets：扫描目标地址，这个参数是一个数组，可以填入多个目标地址，用来一次扫描多个主机
# """
# def create_task(task_name, hosts, ip, port, policy_id={}):  # host 是一个列表，存放的是需要扫描的多台主机
#     # uuid = get_nessus_template_uuid(ip, port, "custom")  # 获取自定义策略的uuid
#     uuid = get_nessus_template_uuid(ip, port, "advanced")  # 获取自定义策略的uuid
#     if uuid is None:
#         return False
#
#     data = {"uuid": uuid, "settings": {
#         "name": task_name,
#         "policy_id": policy_id,
#         "enabled": True,
#         "text_targets": hosts,
#         "agent_group_id": []
#     }}
#
#     header = {
#         'X-ApiKeys': 'accessKey={accesskey};secretKey={secretkey}'.format(accesskey=accessKey,
#                                                                           secretkey=secretKey),
#         'Content-type': 'application/json',
#         'Accept': 'text/plain'}
#
#     api = "https://{ip}:{port}/scans".format(ip=ip, port=port)
#     response = requests.post(api, headers=header, data=json.dumps(data, ensure_ascii=False).encode("utf-8"),
#                              verify=False)
#     if response.status_code == 200:
#         data = json.loads(response.text)
#         if data["scan"] is not None:
#             scan = data["scan"]
#             # 新增任务扩展信息记录
#
#             return scan["id"]  # 返回任务id
#
# # 启动任务
# def start_task(task_id, hosts):
#     header = {
#         'X-ApiKeys': 'accessKey={accesskey};secretKey={secretkey}'.format(accesskey=accessKey,
#                                                                           secretkey=secretKey),
#         'Content-type': 'application/json',
#         'Accept': 'text/plain'}
#
#     data = {
#         "alt_targets": [hosts]  # 重新指定扫描地址
#     }
#
#     api = "https://{ip}:{port}/scans/{scan_id}/launch".format(ip=ip, port=port, scan_id=scan_id)
#     response = requests.post(api, data=data, verify=False, headers=header)
#     if response.status_code != 200:
#         return False
#     else:
#         return True
#
# # # 停止任务
# # def stop_task(task_id):
# #     header = {
# #         'X-ApiKeys': 'accessKey={accesskey};secretKey={secretkey}'.format(accesskey=terminal.reserved1,
# #                                                                           secretkey=terminal.reserved2),
# #         'Content-type': 'application/json',
# #         'Accept': 'text/plain'}
# #
# #     api = "https://{ip}:{port}/scans/{scan_id}/stop".format(ip=ip, port=port, task_id)
# #     response = requests.post(api, headers=header, verify=False)
# #     if response.status_code == 200 or response.status_code == 409:  # 根据nessus api文档可以知道409 表示任务已结束
# #         return True
#
#     # return
#
# #
#
# def get_host_vulnerabilities(scan_id, host_id, ip, port):
#     header = {
#         "X-ApiKeys": "accessKey={accesskey};secretKey={secretkey}".format(accesskey=accessKey,
#                                                                           secretkey=secretKey),
#         "Content-Type": "application/json",
#         "Accept": "text/plain"
#     }
#
#     # scan_history = ScanHistory.objects.get(id=scan_id)
#     api = "https://{ip}:{port}/scans/{task_id}/hosts/{host_id}".format(ip=ip, port=port, task_id=scan_id, host_id=host_id)
#     response = requests.get(api, headers=header, verify=False)
#     print(response)
#     if response.status_code != 200:
#         return 2, "Data Error"
#
#     data = json.loads(response.text)
#     vulns = data["vulnerabilities"]
#
#     for vuln in vulns:
#         vuln_name = vuln["plugin_name"]
#         plugin_id = vuln["plugin_id"] #插件id，可以获取更详细信息，包括插件自身信息和扫描到漏洞的解决方案等信息
#         #保存漏洞信息
#
#     return vulns
#
# print(get_host_vulnerabilities("116.62.233.27-2", "116.62.233.27", "116.62.233.27", 8834))
#
# # 获取任务状态
# def get_task_status(task_id):
#     header = {
#         "X-ApiKeys": "accessKey={accesskey};secretKey={secretkey}".format(accesskey=accessKey,
#                                                                           secretkey=secretKey),
#         "Content-Type": "application/json",
#         "Accept": "text/plain"
#     }
#
#     api = "https://{ip}:{port}/scans/{task_id}".format(ip=ip, port=port,
#                                                        task_id=task_id)
#     response = requests.get(api, headers=header, verify=False)
#     if response.status_code != 200:
#         return 2, "Data Error"
#
#     data = json.loads(response.text)
#     hosts = data["hosts"]
#     for host in hosts:
#         get_host_vulnerabilities(scan_id, host["host_id"]) # 按主机获取漏洞信息
#
#     if data["info"]["status"] == "completed" or data["info"]["status"] =='canceled':
#         # 已完成,此时更新本地任务状态
#         return 1, "OK"
#
# def get_vuln_detail(scan_id, host_id, plugin_id):
#     header = {
#         "X-ApiKeys": "accessKey={accesskey};secretKey={secretkey}".format(accesskey=accessKey,
#                                                                           secretkey=secretKeyey),
#         "Content-Type": "application/json",
#         "Accept": "text/plain"
#     }
#
#     api = "https://{ip}:{port}/scans/{scan_id}/hosts/{host_id}/plugins/{plugin_id}".format(ip=ip, port=port, scan_id=scan_id, host_id=host_id, plugin_id=plugin_id)
#     response = requests.get(api, headers=header, verify=False)
#     data = json.loads(response.text)
#     outputs = data["outputs"]
#     return outputs
#
# if __name__ == "__main__":
#     # task_id = create_task(task_name="test111", hosts=["116.62.233.27"], ip="116.62.233.27", port=8834)
#     # print(task_id)
#     # res = get_scan_list("116.62.233.27", 8834, "jcwang", "971707")
#     # print(res)
#
#     print("hello world")

import requests
import json
import time
import sys

# 忽略requests证书警告
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# import sys
# sys.path.append("/Users/jc/jcall/研究实验代码")
from slnova.info import getinfo

import slnova.conf
CONF = slnova.conf.CONF

scanned_ip = CONF.nessus.scanned_ip
nessus_url = CONF.nessus.nessus_url
verify = False
token = ''
username = CONF.nessus.username
password = CONF.nessus.password
accessKey = CONF.nessus.accessKey  # 此处填入真实的内容
secretKey = CONF.nessus.secretKey  # 此处填入真实内容

headers = {
        'X-ApiKeys': 'accessKey={accesskey};secretKey={secretkey}'.format(accesskey=accessKey, secretkey=secretKey),
        'Content-type': 'application/json',
        'Accept': 'text/plain'}


def build_url(resource):
    return '{0}{1}'.format(nessus_url, resource)



def connect(method, resource, data=None):
    """
    Send a request

    Send a request to Nessus based on the specified data. If the session token
    is available add it to the request. Specify the content type as JSON and
    convert the data to JSON format.
    """




    # headers = {'X-Cookie': 'token={0}'.format(token),
    #            'content-type': 'application/json'}

    data = json.dumps(data)

    if method == 'POST':
        r = requests.post(build_url(resource), data=data, headers=headers, verify=verify)
    elif method == 'PUT':
        r = requests.put(build_url(resource), data=data, headers=headers, verify=verify)
    elif method == 'DELETE':
        r = requests.delete(build_url(resource), data=data, headers=headers, verify=verify)
    else:
        r = requests.get(build_url(resource), params=data, headers=headers, verify=verify)

    # Exit if there is an error.
    if r.status_code != 200:
        e = r.json()
        print(e['error'])
        sys.exit()

    # When downloading a scan we need the raw contents not the JSON data.
    if 'download' in resource:
        return r.content
    else:
        return r.json()


def login(usr, pwd):
    """
    Login to nessus.
    """

    login = {'username': usr, 'password': pwd}
    data = connect('POST', '/session', data=login)

    return data['token']


def logout():
    """
    Logout of nessus.
    """

    connect('DELETE', '/session')


def get_policies():
    """
    Get scan policies

    Get all of the scan policies but return only the title and the uuid of
    each policy.
    """

    data = connect('GET', '/editor/policy/templates')

    return dict((p['title'], p['uuid']) for p in data['templates'])


def get_history_ids(sid):
    """
    Get history ids

    Create a dictionary of scan uuids and history ids so we can lookup the
    history id by uuid.
    """
    data = connect('GET', '/scans/{0}'.format(sid))

    return dict((h['uuid'], h['history_id']) for h in data['history'])


def get_scan_history(sid, hid):
    """
    Scan history details

    Get the details of a particular run of a scan.
    """
    params = {'history_id': hid}
    data = connect('GET', '/scans/{0}'.format(sid), params)

    return data['info']


def add(name, desc, targets, pid):
    """
    Add a new scan

    Create a new scan using the policy_id, name, description and targets. The
    scan will be created in the default folder for the user. Return the id of
    the newly created scan.
    """

    scan = {'uuid': pid,
            'settings': {
                'name': name,
                'description': desc,
                'text_targets': targets}
            }

    data = connect('POST', '/scans', data=scan)

    return data['scan']


def update(scan_id, name, desc, targets, pid=None):
    """
    Update a scan

    Update the name, description, targets, or policy of the specified scan. If
    the name and description are not set, then the policy name and description
    will be set to None after the update. In addition the targets value must
    be set or you will get an "Invalid 'targets' field" error.
    """

    scan = {}
    scan['settings'] = {}
    scan['settings']['name'] = name
    scan['settings']['desc'] = desc
    scan['settings']['text_targets'] = targets

    if pid is not None:
        scan['uuid'] = pid

    data = connect('PUT', '/scans/{0}'.format(scan_id), data=scan)

    return data


def launch(sid):
    """
    Launch a scan

    Launch the scan specified by the sid.
    """

    data = connect('POST', '/scans/{0}/launch'.format(sid))

    return data['scan_uuid']


def status(sid, hid):
    """
    Check the status of a scan run

    Get the historical information for the particular scan and hid. Return
    the status if available. If not return unknown.
    """

    d = get_scan_history(sid, hid)
    return d['status']


def export_status(sid, fid):
    """
    Check export status

    Check to see if the export is ready for download.
    """

    data = connect('GET', '/scans/{0}/export/{1}/status'.format(sid, fid))

    return data['status'] == 'ready'


def export(sid, hid):
    """
    Make an export request

    Request an export of the scan results for the specified scan and
    historical run. In this case the format is hard coded as nessus but the
    format can be any one of nessus, html, pdf, csv, or db. Once the request
    is made, we have to wait for the export to be ready.
    """

    data = {'history_id': hid,
            'format': 'nessus'}

    data = connect('POST', '/scans/{0}/export'.format(sid), data=data)

    fid = data['file']

    while export_status(sid, fid) is False:
        time.sleep(5)

    return fid


def download(sid, fid):
    """
    Download the scan results

    Download the scan results stored in the export file specified by fid for
    the scan specified by sid.
    """

    data = connect('GET', '/scans/{0}/export/{1}/download'.format(sid, fid))
    filename = 'nessus_{0}_{1}.nessus'.format(sid, fid)

    print('Saving scan results to {0}.'.format(filename))
    with open(filename, 'wb') as f:
        f.write(data)


def delete(sid):
    """
    Delete a scan

    This deletes a scan and all of its associated history. The scan is not
    moved to the trash folder, it is deleted.
    """

    connect('DELETE', '/scans/{0}'.format(scan_id))


def history_delete(sid, hid):
    """
    Delete a historical scan.

    This deletes a particular run of the scan and not the scan itself. the
    scan run is defined by the history id.
    """

    connect('DELETE', '/scans/{0}/history/{1}'.format(sid, hid))



# [基于Python的nessus API简析——监听&获取扫描结果](https://blog.csdn.net/u013578500/article/details/78725295)

# 获取扫描结果（基于主机）
def get_scan_detail_baseon_host(scan_id):
    # 结果，主机漏洞字典列表
    result = []
    # 主机漏洞字典
    host_detail = {}
    # 调用
    url = '{url}/scans/{scan_id}'.format(url=nessus_url, scan_id=scan_id)
    # 发送请求
    respon = requests.get(url, headers=headers, verify=False)
    # 取出主机列表
    host_list = json.loads(respon.text)['hosts']
    # 遍历主机列表并生成结果
    # for host in host_list:
        # # IP为键名
        # host_detail[host['hostname']] = get_vul_by_host(scan_id, host['host_id'])
        # result.append(host_detail)
    for host in host_list: # 目前都只扫描了一个host
        # IP为键名
        host_detail[host['hostname']] = {"high": host["high"], "medium": host["medium"], "low": host["low"],
                                         "info": host["info"]}
        result.append(host_detail)

    return result


# 获得主机漏洞信息
def get_vul_by_host(scan_id, host_id):
    # 调用
    url = '{url}/scans/{scan_id}/hosts/{host_id}'.format(url=nessus_url, scan_id=scan_id, host_id=host_id)
    # 发送请求
    respon = requests.get(url, headers=headers, verify=False)
    return json.loads(respon.text)['vulnerabilities']


def pre_scan():
    # 这个只需要运行一次，另一次扫描的话只要拿着这个之前的scan_id去扫描就好了
    print('Login')
    token = login(username, password)
    print("token: %s" % token)
    # scan_id = 24
    # history_id = 25

    # scan_id = 27
    # history_id = 28

    print('Adding new scan...')
    policies = get_policies()
    policy_id = policies['Advanced Scan']
    # policy_id = policies['Basic Network Scan']
    print(policy_id)
    scan_data = add("{0}-{1}".format(scanned_ip, getinfo.get_time()), 'Create a new scan with API', scanned_ip, policy_id)
    scan_id = scan_data['id']
    print("scan_id: {0}".format(scan_id))  # 24, 25

    print('Updating scan with new targets...')
    update(scan_id, scan_data['name'], scan_data['description'], scanned_ip)

    return scan_id


def start_scan(scan_id):
    print('Launching scan...')
    scan_uuid = launch(scan_id)
    history_ids = get_history_ids(scan_id)
    history_id = history_ids[scan_uuid]
    print("history_id: {0}".format(history_id))

    return history_id


def check_status_and_update(scan_id, history_id):
    if status(scan_id, history_id) == 'completed':  # 本次扫描已经完成
        res = get_scan_detail_baseon_host(scan_id)
        info = res[0][scanned_ip]

        return True, info
    else:
        return False, None
        # print('Exporting the completed scan.')
        # file_id = export(scan_id, history_id)
        # download(scan_id, file_id)

    # print(get_scan_detail_baseon_host(scan_id))

    # print('Deleting the scan.')
    # history_delete(scan_id, history_id)
    # delete(scan_id)
    #
    # print('Logout')
    # logout()


# if __name__ == '__main__':
#     print('Login')
#     token = login(username, password)
#     print("token: %s" % token)
#     # scan_id = 24
#     # history_id = 25
#
#     # scan_id = 27
#     # history_id = 28
#
#     print('Adding new scan...')
#     policies = get_policies()
#     policy_id = policies['Advanced Scan']
#     # policy_id = policies['Basic Network Scan']
#     print(policy_id)
#     scan_data = add("{0}-{1}".format(scanned_ip, getinfo.get_time()), 'Create a new scan with API', scanned_ip,
#                     policy_id)
#     scan_id = scan_data['id']
#     print("scan_id: {0}".format(scan_id))  # 24, 25
#
#     print('Updating scan with new targets...')
#     update(scan_id, scan_data['name'], scan_data['description'], scanned_ip)
#
#     print('Launching new scan...')
#     scan_uuid = launch(scan_id)
#     history_ids = get_history_ids(scan_id)
#     history_id = history_ids[scan_uuid]
#     print("history_id: {0}".format(history_id))
#     while status(scan_id, history_id) != 'completed':
#         print(getinfo.get_time())
#         time.sleep(5)
#
#     print('Exporting the completed scan.')
#     file_id = export(scan_id, history_id)
#     download(scan_id, file_id)
#
#     print(get_scan_detail_baseon_host(scan_id))
#
#     # print('Deleting the scan.')
#     # history_delete(scan_id, history_id)
#     # delete(scan_id)
#     #
#     # print('Logout')
#     # logout()
#
#
