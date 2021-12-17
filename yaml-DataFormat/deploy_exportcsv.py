# -*- coding: utf-8 -*-
# @Time     : 2021-1207
# @Author   : weibing.ma@daocloud.io
# @Filename : deploy_exportcsv.py
# @Explain  : 支持所有信息放在一个sheet表中,筛选

from openpyxl import Workbook
from openpyxl.worksheet.table import Table, TableStyleInfo
import yaml
import os

wb = Workbook()
ws = wb.active
ws.title = '应用信息'

data = []
for root, dirs, dce_file in os.walk('deployinfo', followlinks=True):
    for index in range(0, len(dce_file)):
        caas_yaml = (root + '/' + dce_file[index])
        with open(caas_yaml, 'r', encoding='gb18030', errors='ignore') as dce_yaml:
            init_yaml = yaml.safe_load(dce_yaml)
        result = []
        namespace = init_yaml['metadata']['namespace']
        deploy_name = init_yaml['metadata']['name']
        replicas = init_yaml['spec']['replicas']
        image = init_yaml['spec']['template']['spec']['containers'][0]['image']
        container_name = init_yaml['spec']['template']['spec']['containers'][0]['name']

        # requests
        if 'requests' not in init_yaml['spec']['template']['spec']['containers'][0]['resources']:
            pass
        else:
            requests_cpu = init_yaml['spec']['template']['spec']['containers'][0]['resources']['requests']['cpu']
            requests_mem = init_yaml['spec']['template']['spec']['containers'][0]['resources']['requests']['memory']

        # limits
        if 'limits' not in init_yaml['spec']['template']['spec']['containers'][0]['resources']:
            pass
        else:
            limit_cpu = init_yaml['spec']['template']['spec']['containers'][0]['resources']['limits']['cpu']
            limit_mem = init_yaml['spec']['template']['spec']['containers'][0]['resources']['limits']['memory']

        dnspolicy = init_yaml['spec']['template']['spec']['dnsPolicy']

        # dnsconfig
        if 'dnsConfig' not in init_yaml['spec']['template']['spec']:
            pass
            dnsconfig = 'None'
        else:
            dns = init_yaml['spec']['template']['spec']['dnsConfig']
            if 'nameservers' not in dns:
                pass
            else:
                dnsconfig = dns['nameservers']

        # hostAliases
        hostaliases = []
        if 'hostAliases' not in init_yaml['spec']['template']['spec']:
            pass
        else:
            # hosts is a list
            hosts = init_yaml['spec']['template']['spec']['hostAliases']
            for host in hosts:
                for value in host.values():
                    hostaliases.append(value)

        # imagespullsecret
        imagepullsecret = []
        if 'imagePullSecrets' not in init_yaml['spec']['template']['spec']:
            pass
        else:
            # imagesecrets is a list
            imagesecrets = init_yaml['spec']['template']['spec']['imagePullSecrets']
            for imagesecret in imagesecrets:
                imagepullsecret.append(imagesecret['name'])

        # zone
        if 'affinity' not in init_yaml['spec']['template']['spec']:
            pass
        else:
            zone = init_yaml['spec']['template']['spec']['affinity']['nodeAffinity'][
                'requiredDuringSchedulingIgnoredDuringExecution']['nodeSelectorTerms'][0]['matchExpressions'][0][
                'values']

        # hostpath/pvc/configmap
        volumes = []
        if 'volumes' not in init_yaml['spec']['template']['spec']:
            pass
        else:
            # volumes is a list
            volume = init_yaml['spec']['template']['spec']['volumes']
            for i in volume:
                if 'hostPath' in i:
                    x = i['hostPath']['path']
                    volumes.append(x)
                elif 'persistentVolumeClaim' in i:
                    y = i['persistentVolumeClaim']['claimName']
                    volumes.append(y)
                elif 'configMap' in i:
                    z = i['configMap']['name']
                    volumes.append(z)
                else:
                    pass
        for res in namespace, deploy_name, image, container_name, requests_cpu, requests_mem, replicas, limit_cpu, \
                   limit_mem, dnspolicy, str(dnsconfig), str(hostaliases), str(imagepullsecret), str(zone), \
                   str(volumes):
                result.append(res)
        data.append(result)

# 定义首行的列标题
ws.append(['namespace', 'deploy_name', 'image', 'container_name', 'requests_cpu', 'requests_mem', 'replicas',
           'limit_cpu', 'limit_mem', 'dnspolicy', 'dnsconfig', 'hostaliases', 'imagepullsecret', 'zone', 'volumes'])
# 导入数据
for i in data:
    ws.append(i)

# 定义表名及范围和风格
for root, dirs, dce_file in os.walk('deployinfo', followlinks=True):
    range = len(dce_file)

    tab = Table(displayName='Table1', ref='A1:O{r}'.format(r=range))
    style = TableStyleInfo(name="TableStyleMedium9", showFirstColumn=False,
                       showLastColumn=False, showRowStripes=True, showColumnStripes=True)
    tab.tableStyleInfo = style

# 添加表及保存数据
ws.add_table(tab)
wb.save('hfoak1-alldeployment.xlsx')
