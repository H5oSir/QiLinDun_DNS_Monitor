"""
@Name: dnspod.py
@Auth: H5osir
@Email: H5osir@outlook.com
@Date: 2024/5/4-14:24
@Desc:
@Ver : 0.0.0
"""
import datetime

from tencentcloud.common import credential
from tencentcloud.dnspod.v20210323 import dnspod_client, models


class DnsPod(object):

    def __init__(self, secret_id: str, secret_key: str):
        self.secret_id = secret_id
        self.secret_key = secret_key

        self.init()

    def init(self):
        self.cred = credential.Credential(self.secret_id, self.secret_key)
        self.client = dnspod_client.DnspodClient(self.cred, "ap-shanghai")

    def get_records(self, domain: str):
        """
        获取域名解析记录
        :param domain:
        :return:
        """
        req = models.DescribeRecordFilterListRequest()
        req.Domain = domain
        req.SubDomain = '*.06e9de7315'
        resp: models.DescribeRecordFilterListResponse = self.client.DescribeRecordFilterList(req)
        print(resp.to_json_string(indent=4))
        return resp.RecordList

    def get_record_id_by_domain_and_subdomain_and_value(self, domain: str, subdomain: str, value: str, ):
        """
        获取解析记录的ID，没有就返回0。
        :param domain:
        :param subdomain:
        :param value:
        :return:

        """
        req = models.DescribeRecordFilterListRequest()
        req.Domain = domain
        req.SubDomain = subdomain
        req.Limit = 3000
        resp: models.DescribeRecordFilterListResponse = self.client.DescribeRecordFilterList(req)
        record_list = resp.RecordList
        result = 0
        for record in record_list:
            if record.Value == value:
                result = record.RecordId
                return result
        return result

    def get_record_by_domain_and_subdomain_and_value(self, domain: str, subdomain: str, value: str, ):
        """
        获取解析记录的ID，没有就返回0。
        :param domain:
        :param subdomain:
        :param value:
        :return:
        {
            "RecordId": 1775910398,
            "Value": "156.238.242.34",
            "Status": "ENABLE",
            "UpdatedOn": "2024-05-04 03:54:02",
            "Name": "*.06e9de7315",
            "Line": "默认",
            "LineId": "0",
            "Type": "A",
            "Weight": null,
            "MonitorStatus": "",
            "Remark": "",
            "TTL": 1,
            "MX": 0,
            "DefaultNS": false
        }
        """
        req = models.DescribeRecordFilterListRequest()
        req.Domain = domain
        req.SubDomain = subdomain
        req.Limit = 3000
        resp: models.DescribeRecordFilterListResponse = self.client.DescribeRecordFilterList(req)
        record_list: list[models.RecordListItem] = resp.RecordList
        result = []
        for record in record_list:
            if record.Value == value:
                result .append(record)
        return result

    def modify_record(self, record: models.RecordListItem, domain):

        req = models.ModifyRecordRequest()
        req.Domain = domain
        req.SubDomain =record.Name
        req.RecordType = record.Type
        req.RecordLine = record.Line
        req.RecordId = record.RecordId
        req.Value = record.Value
        req.Remark = f"Monitor更新操作时间：{datetime.datetime.now()}"
        req.Status = record.Status
        req.TTL = 1
        resp: models.ModifyRecordResponse = self.client.ModifyRecord(req)
        return resp

    def create_record(self, domain: str, subdomain: str, ip: str, ):

        req = models.CreateRecordRequest()
        req.Domain = domain
        req.SubDomain = subdomain
        req.RecordType = 'A'
        req.RecordLine = '默认'
        req.Value = ip
        req.Status = "ENABLE"
        req.TTL = 1
        req.Remark = f"Monitor添加,时间：{datetime.datetime.now()}"
        resp: models.CreateRecordResponse = self.client.CreateRecord(req)
        return resp


if __name__ == '__main__':
    from config import Config
    config = Config.get_config_json()
    secret_id = config.secret_id
    secret_key = config.secret_key
    dns = DnsPod(secret_id, secret_key)
    # dns.get_records("666cloud.cn")
    # record = dns.get_record_by_domain_and_subdomain_and_value(domain="666cloud.cn", subdomain="*.06e9de7315",
    #                                                           value="156.238.229.154")
    # if not record:
    #     print("解析记录不存在")
    #     exit()
    # record.Status = "ENABLE"
    # resp = dns.modify_record(record=record, domain="666cloud.cn")
    # print(record)
    # print(resp)
    resp=dns.create_record(domain="666cloud.cn",subdomain="monitor-test",ip="127.0.0.1")
    print(resp)
