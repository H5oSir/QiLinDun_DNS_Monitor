"""
@Name: config.py
@Auth: H5osir
@Email: H5osir@outlook.com
@Date: 2024/5/4-23:32
@Desc: 
@Ver : 0.0.0
"""
import json


class Config(object):
    _instances = None

    def __init__(self):
        self.max_time_out_count = None
        self.rate_sec = None
        self.check_node_ip = None
        self.check_node_name = None
        self.wechat_hook_url = None
        self.debug = None
        self.secret_ket = None
        self.secret_id = None
        self.config_json = None
        self.sud_domain = None
        self.domain = None
        self.flag = None
        self.url = None
        self.cdn_ips = None
        self.load_json()

    def load_json(self):
        with open(file="config.json", mode='r') as f:
            self.config_json = json.load(f)

        self.cdn_ips = self.config_json.get('cdn_ips', [])
        self.url = self.config_json.get('url', '')
        self.flag = self.config_json.get('flag', '')
        self.domain = self.config_json.get('domain', '')
        self.sud_domain = self.config_json.get('sud_domain', '')
        self.secret_id = self.config_json.get('secret_id', '')
        self.secret_ket = self.config_json.get('secret_key', '')
        self.debug = self.config_json.get('debug', False)
        self.wechat_hook_url = self.config_json.get("wechat_hook_url", "")
        self.check_node_name = self.config_json.get("check_node_name", "")
        self.check_node_ip = self.config_json.get("check_node_ip", "")
        self.rate_sec = self.config_json.get("rate_sec", 1)
        self.max_time_out_count = self.config_json.get("max_time_out_count", 0)

    @classmethod
    def get_config_json(cls, ):
        if not cls._instances:
            cls._instances = cls()
        return cls._instances
