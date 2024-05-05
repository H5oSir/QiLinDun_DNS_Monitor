"""
@Name: log.py
@Auth: H5osir
@Email: H5osir@outlook.com
@Date: 2024/5/5-00:16
@Desc: 
@Ver : 0.0.0
"""
import json
import logging

import requests

from config import Config
config =Config.get_config_json()

class Log(object):
    _instances = None

    @classmethod
    def get_logger(cls, ):
        if not cls._instances:
            log = logging.getLogger("Monitor")
            if config.debug:
                log_level=logging.INFO
            else:
                log_level=logging.WARNING
            log.setLevel(log_level)

            # 创建文件处理器，用于写入日志文件
            file_handler = logging.FileHandler('app.log', mode='a')
            file_handler.setLevel(log_level)
            file_format = logging.Formatter(
                '%(asctime)s - [%(pathname)s](%(funcName)s:%(lineno)d) - %(levelname)s - %(message)s')
            file_handler.setFormatter(file_format)

            # 设置控制台日志处理器
            console_handler = logging.StreamHandler()
            console_handler.setLevel(log_level)
            # 设置日志格式
            console_format = logging.Formatter(
                '%(asctime)s - [%(pathname)s](%(funcName)s:%(lineno)d) - %(levelname)s - %(message)s')
            console_handler.setFormatter(console_format)

            # 创建 WeChat 日志处理器
            wechat_handler = WeChatHandler(config.wechat_hook_url)
            wechat_handler.setLevel(logging.WARNING)
            wechat_format=logging.Formatter(
                '%(asctime)s - [%(pathname)s](%(funcName)s:%(lineno)d) - %(levelname)s - %(message)s')
            wechat_handler.setFormatter(wechat_format)

            # 将处理器添加到 logger 对象
            log.addHandler(console_handler)
            log.addHandler(file_handler)
            log.addHandler(wechat_handler)
            cls._instances = log

        return cls._instances


class WeChatHandler(logging.Handler):
    def __init__(self, webhook_url):
        super().__init__()
        self.webhook_url = webhook_url

    def emit(self, record):
        log_entry = self.format(record)
        payload = {
            "msgtype": "text",
            "text": {
                "content": log_entry
            }
        }
        headers = {'Content-Type': 'application/json'}
        try:
            response = requests.post(self.webhook_url, data=json.dumps(payload), headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Failed to send log entry to WeChat: {e}")
