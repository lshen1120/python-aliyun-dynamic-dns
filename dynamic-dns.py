# -*- coding: utf-8 -*-
# !/usr/bin/python
import urllib2
import re
import time
from aliyunsdkcore import client
from aliyunsdkalidns.request.v20150109.UpdateDomainRecordRequest import *
from aliyunsdkalidns.request.v20150109.DescribeDomainRecordsRequest import *
from xml.dom.minidom import parse
import xml.dom.minidom
import time
# doc https://help.aliyun.com/document_detail/29740.html?spm=5176.doc29739.6.128.C0nuRG
# 需要先安装 dns-sdk
# pip install aliyun-python-sdk-alidns
keyId = ""
keySecret = ""
domain = "test.com" # 根域名
RR = "dns" #子域名
updateInterval = 600  # 间隔600s
ISOTIMEFORMAT='%Y-%m-%d %X'
def getRecordInfo(xmlStr, RR):
    domtree = xml.dom.minidom.parseString(xmlStr)
    docelem = domtree.documentElement
    records = docelem.getElementsByTagName("Record")
    for record in records:
        if record.getElementsByTagName("RR")[0].childNodes[0].data == RR:
            return {
                "RecordId": record.getElementsByTagName("RecordId")[0].childNodes[0].data,
                "Value": record.getElementsByTagName("Value")[0].childNodes[0].data
            }
    return None
rip = "\<code\>(?P<num>[\d\.]*)\</code>"
clt = client.AcsClient(keyId, keySecret, 'cn-hangzhou')
descDomainReq = DescribeDomainRecordsRequest()
descDomainReq.set_DomainName(domain)
descDomainRes = clt.do_action(descDomainReq)
recordInfo = getRecordInfo(descDomainRes, RR)
if recordInfo is None:
    raise Exception("can't find RR value " + RR)
print recordInfo
currentIP = recordInfo["Value"]
recordId = recordInfo["RecordId"]
while True:
    try:
        result = urllib2.urlopen('http://ip.cn/',timeout=3)
        text = result.read()
        ip = re.findall(rip, text)[0]
        if currentIP == ip:
            print time.strftime( ISOTIMEFORMAT, time.localtime())+" ip( %s ) is not change, sleep %ds" % (ip, updateInterval)
            time.sleep(updateInterval)
            continue
        request = UpdateDomainRecordRequest()
        request.set_Value(ip)
        request.set_Type("A")
        request.set_RecordId(recordId)
        request.set_RR(RR)
        request.set_accept_format('xml')
        result = clt.do_action(request)
        print result
        currentIP = ip
        print time.strftime( ISOTIMEFORMAT, time.localtime())+" ip( %s ) update" % ip
    except:
        None
