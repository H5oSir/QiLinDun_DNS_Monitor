"""
@Name: run.py
@Auth: H5osir
@Email: H5osir@outlook.com
@Date: 2024/5/4-15:50
@Desc: 
@Ver : 0.0.0
"""
import time
from threading import Thread

import requests

from dnspod import DnsPod
from config import Config
from log import Log

config = Config.get_config_json()
log = Log.get_logger()


def cdn_ip_is_alive(url, ip, flag) -> tuple:
    headers = {
        'Host': url.split('://')[1].split('/')[0],  # 提取域名部分作为Host
        'User-Agent': 'QiLinDun-Monitor-v2.0'
    }
    proxies = {
        'http': f'http://{ip}',
        # 'https': f'https://{ip}'
    }
    time_out_count = 0
    while True:
        try:
            if time_out_count >= config.max_time_out_count:
                msg = f"监控节点名称 {config.check_node_name} ,监控节点IP {config.check_node_ip} , CDN 节点 {ip} 访问失败，尝试访问节点超时{config.max_time_out_count}次"
                return False, msg
            # 发送请求
            response = requests.get(url, headers=headers, proxies=proxies, timeout=5)
            # 检查响应状态码
            if response.status_code == 200 and flag in response.content.decode() or response.status_code == 502:
                msg = f"CDN 节点 {ip} 存活，状态码为: {response.status_code}，响应内容为：{response.content.decode()}"
                log.info(msg)
                return True, msg
            else:
                msg = f"监控节点名称 {config.check_node_name} ,监控节点IP {config.check_node_ip} , CDN 节点 {ip} 访问失败，状态码为: {response.status_code}，响应内容为：{response.content.decode()}"
                log.info(msg)
                return False, msg
        # 捕获time_out 异常
        except requests.exceptions.ConnectTimeout as e:
            time_out_count = time_out_count + 1
            msg = f"监控节点名称 {config.check_node_name} ,监控节点IP {config.check_node_ip} , CDN 节点 {ip} 访问失败，尝试访问节点超时第{config.max_time_out_count}次，错误信息：{e}"
            log.info(msg)
        except requests.exceptions.Timeout as e:
            time_out_count = time_out_count + 1
            msg = f"监控节点名称 {config.check_node_name} ,监控节点IP {config.check_node_ip} , CDN 节点 {ip} 访问失败，尝试访问节点超时第{config.max_time_out_count}次，错误信息：{e}"
            log.info(msg)
        except requests.exceptions.ProxyError as e:
            time_out_count = time_out_count + 1
            msg = f"监控节点名称 {config.check_node_name} ,监控节点IP {config.check_node_ip} , CDN 节点 {ip} 访问失败，尝试访问节点超时第{config.max_time_out_count}次，错误信息：{e}"
            log.info(msg)
        except Exception as e:
            msg = f"监控节点名称 {config.check_node_name} ,监控节点IP {config.check_node_ip} , CDN 节点 {ip} 请求异常，错误信息：{e}"
            log.info(msg)
            return False, msg


def monitor(name: str, ip: str, url: str, flag: str, domain: str, subdomain: str) -> None:
    dns = DnsPod(config.secret_id, config.secret_ket)
    count = 0
    delay_time = 0
    while True:

        try:
            start_time = time.time()
            # 开启Debug
            if config.debug:
                if count > 0:
                    break
                else:
                    count = count + 1
            # 判断CDN节点是否存活。
            alive, msg = cdn_ip_is_alive(url, ip, flag)
            records = dns.get_record_by_domain_and_subdomain_and_value(domain=domain, subdomain=subdomain, value=ip)
            # 如果节点是活的并且解析记录存在
            if alive and records:
                for record in records:
                    if record.Status == "DISABLE":
                        # 启用解析
                        record.Status = "ENABLE"
                        dns.modify_record(record=record, domain=domain)
                        log.warning(
                            f"监控节点名称 {config.check_node_name} ,监控节点IP {config.check_node_ip} , CDN 节点 {ip} 开启解析记录，域名 {record.Name}.{domain} ，线路 {record.Line}，详细信息 {msg}")

            # 如果节点是活的并且解析记录不存在
            elif alive and not records:
                # dns.create_record(domain=domain, subdomain=subdomain, ip=ip)
                log.warning(f"CDN 节点 {ip} 是活的，域名 {subdomain}.{domain} 解析不存在，详细信息 {msg}")
                # 添加解析记录
            # 如果节点是死的并且解析记录存在
            elif not alive and records:
                for record in records:
                    if record.Status == "ENABLE":
                        # 关闭解析
                        record.Status = "DISABLE"
                        dns.modify_record(record=record, domain=domain)
                        log.warning(
                            f"监控节点名称 {config.check_node_name} ,监控节点IP {config.check_node_ip} , CDN 节点 {ip} 关闭解析记录，域名 {record.Name}.{domain} ，线路 {record.Line}，详细信息 {msg}")

            # 如果节点是死的并且解析记录不存在
            elif not alive and not records:
                # 不需要操作
                pass
            # 计算间隔时间，然后睡眠，保证1秒钟一次监控。
            end_time = time.time()
            delay_time = config.rate_sec - (end_time - start_time)
            if delay_time > 0:
                time.sleep(delay_time)
        except Exception as err:
            log.info("产生异常：" + str(err))


def main_chck_ip():
    node_ips = ["156.238.229.154", "156.238.242.34", "45.85.77.8", "222.186.48.167", "222.186.48.168"]
    url = "http://test-hw.qilindun.com/"
    flag = "www.qilindun.com"
    t_list = []
    for ip in node_ips:
        t = Thread(target=cdn_ip_is_alive, name="check-" + str(ip), args=(url, ip, flag),
                   daemon=True)
        t_list.append(t)
        t.start()

        print("启动线程成功：", t.native_id)
    for t in t_list:
        t.join()
    print("所有线程执行完毕")


def main_loop():
    msg = f"监控节点名称 {config.check_node_name} ,监控节点IP {config.check_node_ip} , 已启动完成！"
    log.warning(msg)

    node_ips = config.cdn_ips
    # node_ips = ["156.238.229.154",]
    url = config.url
    flag = config.flag
    domain = config.domain
    subdomain = config.sud_domain

    t_list = []
    for ip in node_ips:
        t = Thread(target=monitor, name="check-" + str(ip), args=(ip, ip, url, flag, domain, subdomain),
                   daemon=True)
        t_list.append(t)
        t.start()

        log.info("启动线程成功：" + str(t.native_id))
    for t in t_list:
        t.join()
    log.info("所有线程执行完毕")


def main():
    node_ips = ["156.238.229.154", "156.238.242.34", "45.85.77.8", "222.186.48.167", "222.186.48.168"]
    url = "http://test-hw.qilindun.com/"
    flag = "www.qilindun.com"
    domain = "666cloud.cn"
    subdomain = "*.06e9de7315"
    for ip in node_ips:
        monitor(name=ip, ip=ip, url=url, flag=flag, domain=domain, subdomain=subdomain)


if __name__ == '__main__':
    # monitor(name="监控器1", ip="156.238.229.154")
    main_loop()
    # cdn_ip_is_alive(config.get_config_json().url,"45.85.77.8","www.qilindun.com")
