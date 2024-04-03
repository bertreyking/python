# -*- coding: utf-8 -*-
# @Time     : 2024-03-16
# @Author   : weibing.ma
# @Filename : generateyaml.py
# @Explain  : 获取yaml，并删除无用字段，执行建议在 master 节点并指定 namespace

import os
import subprocess
import argparse
import yaml

"""
 获取指定 namespace 下的所有资源类型
 - deployment、statefulset、daemonset、job
 - service、ingress
 - configmap、secret
 - pvc
 - 少 ingressclass、pv、cronjob 没有对接
"""
# getkindType = subprocess.run("kubectl get deployment,statefulset,daemonset,job,service,ingress,configmap,secret,pvc -n kube-system | egrep -v 'NAME|^$' | awk -F '/' '{print $1}' | uniq", shell=True, stdout=subprocess.PIPE, text=True)
# kindTypeResult = getkindType.stdout.splitlines()

# 解析命令行参数
parser = argparse.ArgumentParser()
parser.add_argument("-n", "--namespace", help="Namespace")
args = parser.parse_args()

# 构建命令
command = "kubectl get deployment,statefulset,daemonset,job,service,ingress,configmap,secret,pvc"
if args.namespace:
    command += f" -n {args.namespace}"

# 执行命令
getkindType = subprocess.run(command + " | egrep -v 'NAME|^$' | awk -F '/' '{print $1}' | uniq", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")
kindTypeResult = getkindType.stdout.splitlines()


# 按资源类型，检索 namespace 下所有资源清单，如 deploy、sts、ds

print('导出 yaml 文件到当前 yaml 目录中......')
for kind in kindTypeResult:
    if args.namespace:
        kindtype_metadata = subprocess.run(f"kubectl get {kind} -n {args.namespace} | egrep -v 'NAME|^$'", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")
        kindlist = kindtype_metadata.stdout.splitlines()

    """
    遍历 kindlist 列表，并打印第一列，也就是资源的名称，并最后将 yaml 文件导出到当前目录
    - 文件名格式
    namespace-kind-name.yaml
    - 示例如下：
    ns-deployment-nginx-test.yaml
    """ 
    for metadata_name in kindlist:
        name = metadata_name.split()[0] # 使用 split() 方法，打印第一列,也就是 metadata.name
        if args.namespace:
            subprocess.run(f"kubectl get {kind} {name} -n {args.namespace} -o yaml > ./yaml/{args.namespace}-{kind}-{name}.yaml && echo {args.namespace}-{kind}-{name}.'yaml save success!!!'", shell=True, stderr=subprocess.PIPE, encoding="utf-8")
   

# 处理导出的 yaml 文件

print(' ')
print('重新定义 yaml 文件并保存到 new_yaml 目录中......')
"""
遍历当前目录下的 yaml 文件
"""
fileList = []
for root, dirs, files in os.walk("./"):
    if 'new_yaml' in dirs:
        dirs.remove('new_yaml')

    for file in files:
        if file.endswith(".yaml"):
            fileList.append(os.path.join(root, file))

for file in fileList:
    with open(file, 'r') as file:
        data = yaml.load(file, Loader=yaml.FullLoader)

        if "Deployment" == data['kind']:
            if "apps/v1" != data['apiVersion']:
                data['apiVersion'] = "apps/v1"
            if 'selfLink' in data['metadata']:
                del data['metadata']['selfLink']
            if 'annotations' in data['metadata']:
                del data['metadata']['annotations']
            del data['metadata']['creationTimestamp']
            del data['metadata']['generation']
            del data['metadata']['resourceVersion']
            del data['metadata']['uid']
            del data['status']        
        
            # 定义文件路径及文件名
            filename = './new_yaml/' + data['metadata']['namespace'] + '_' +data['kind'] + '_' + data['metadata']['name'] + '.yaml'
            with open(filename, 'w') as file:
                yaml.dump(data, file)
            print(filename + " " + "save success!!!")

        elif "StatefulSet" == data['kind']:
            if "apps/v1" != data['apiVersion']:
                data['apiVersion'] = "apps/v1"
            if 'annotations' in data['metadata']:
                del data['metadata']['annotations']
            if 'selfLink' in data['metadata']:
                del data['metadata']['selfLink']
            del data['metadata']['creationTimestamp']
            del data['metadata']['generation']
            del data['metadata']['resourceVersion']
            del data['metadata']['uid']
            del data['status']

            # 定义文件路径及文件名
            filename = './new_yaml/' + data['metadata']['namespace'] + '_' +data['kind'] + '_' + data['metadata']['name'] + '.yaml'
            with open(filename, 'w') as file:
                yaml.dump(data, file)
            print(filename + " " + "save success!!!")

        elif "DaemonSet" == data['kind']:
            if "apps/v1" != data['apiVersion']:
                data['apiVersion'] = "apps/v1"
            if 'annotations' in data['metadata']:
                del data['metadata']['annotations']
            if 'selfLink' in data['metadata']:
                del data['metadata']['selfLink']
            del data['metadata']['creationTimestamp']
            del data['metadata']['generation']
            del data['metadata']['resourceVersion']
            del data['metadata']['uid']
            del data['status']

            # 定义文件路径及文件名
            filename = './new_yaml/' + data['metadata']['namespace'] + '_' +data['kind'] + '_' + data['metadata']['name'] + '.yaml'
            with open(filename, 'w') as file:
                yaml.dump(data, file)
            print(filename + " " + "save success!!!")

        elif "Job" == data['kind']:
            if "batch/v1" != data['apiVersion']:
                data['apiVersion'] = "batch/v1"
            if 'annotations' in data['metadata']:
                del data['metadata']['annotations']
            if 'selfLink' in data['metadata']:
                del data['metadata']['selfLink']
            del data['metadata']['creationTimestamp']
            if 'generation' in data['metadata']:
                del data['metadata']['generation']
            del data['metadata']['resourceVersion']
            del data['metadata']['uid']
            del data['spec']['selector']
            del data['spec']['template']['metadata']['labels']['controller-uid']
            del data['status']

            # 定义文件路径及文件名
            filename = './new_yaml/' + data['metadata']['namespace'] + '_' +data['kind'] + '_' + data['metadata']['name'] + '.yaml'
            with open(filename, 'w') as file:
                yaml.dump(data, file)
            print(filename + " " + "save success!!!")

        elif "Service" == data['kind']:
            if "v1" != data['apiVersion']:
                data['apiVersion'] = "v1"
            if 'annotations' in data['metadata']:
                del data['metadata']['annotations']
            if 'selfLink' in data['metadata']:
                del data['metadata']['selfLink']
            del data['metadata']['creationTimestamp']
            if 'generation' in data['metadata']:
                del data['metadata']['generation']
            del data['metadata']['resourceVersion']
            del data['metadata']['uid']
            del data['spec']['clusterIP']
            if 'clusterIPs' in data['spec']:
                del data['spec']['clusterIPs']
            del data['status']
            if 'NodePort' == data['spec']['type'] or 'LoadBalancer' ==  data['spec']['type']:
                ports_dict = data['spec']['ports'][0]
                del ports_dict['nodePort']
            
            # 定义文件路径及文件名
            filename = './new_yaml/' + data['metadata']['namespace'] + '_' +data['kind'] + '_' + data['metadata']['name'] + '.yaml'
            with open(filename, 'w') as file:
                yaml.dump(data, file)
            print(filename + " " + "save success!!!")

        elif "Ingress" == data['kind']:
            if "networking.k8s.io/v1" != data['apiVersion']:
                data['apiVersion'] = "networking.k8s.io/v1"
            # if 'annotations' in data['metadata']:
            #     del data['metadata']['annotations']
            if 'selfLink' in data['metadata']:
                del data['metadata']['selfLink']
            del data['metadata']['creationTimestamp']
            if 'generation' in data['metadata']:
                del data['metadata']['generation']
            del data['metadata']['resourceVersion']
            del data['metadata']['uid']
            del data['status']

            # 定义文件路径及文件名
            filename = './new_yaml/' + data['metadata']['namespace'] + '_' +data['kind'] + '_' + data['metadata']['name'] + '.yaml'
            with open(filename, 'w') as file:
                yaml.dump(data, file)
            print(filename + " " + "save success!!!, please check ingress's annotations and ingressclass!!!")

        elif "ConfigMap" == data['kind']:
            if "v1" != data['apiVersion']:
                data['apiVersion'] = "v1"
            if 'annotations' in data['metadata']:
                del data['metadata']['annotations']
            if 'selfLink' in data['metadata']:
                del data['metadata']['selfLink']
            del data['metadata']['creationTimestamp']
            del data['metadata']['resourceVersion']
            del data['metadata']['uid']

            # 定义文件路径及文件名
            filename = './new_yaml/' + data['metadata']['namespace'] + '_' +data['kind'] + '_' + data['metadata']['name'] + '.yaml'
            with open(filename, 'w') as file:
                yaml.dump(data, file)
            print(filename + " " + "save success!!!")

        elif "Secret" == data['kind']:
            if "v1" != data['apiVersion']:
                data['apiVersion'] = "v1"
            if 'generateName' in data['metadata']:
                del data['metadata']['generateName']
            if 'selfLink' in data['metadata']:
                del data['metadata']['selfLink']
            del data['metadata']['creationTimestamp']
            del data['metadata']['resourceVersion']
            del data['metadata']['uid']

            # 定义文件路径及文件名
            filename = './new_yaml/' + data['metadata']['namespace'] + '_' +data['kind'] + '_' + data['metadata']['name'] + '.yaml'
            with open(filename, 'w') as file:
                yaml.dump(data, file)
            print(filename+"save success!!!")

        elif "PersistentVolumeClaim" == data['kind']:
            if "v1" != data['apiVersion']:
                data['apiVersion'] = "v1"
            if 'annotations' in data['metadata']:
                del data['metadata']['annotations']
            if 'selfLink' in data['metadata']:
                del data['metadata']['selfLink']
            del data['metadata']['creationTimestamp']
            del data['metadata']['finalizers']
            del data['metadata']['resourceVersion']
            del data['metadata']['uid']
            del data['status']

            # 定义文件路径及文件名
            filename = './new_yaml/' + data['metadata']['namespace'] + '_' +data['kind'] + '_' + data['metadata']['name'] + '.yaml'
            with open(filename, 'w') as file:
                yaml.dump(data, file)
            print(filename + " " + "save success!!!")
        
        # elif "PersistentVolume" == data['kind']:
        #     if f"{args.namespace}" == data['spec']['claimRef']['namespace']:
        #         if "v1" != data['apiVersion']:
        #             data['apiVersion'] = "v1"
        #         if 'annotations' in data['metadata']:
        #             del data['metadata']['annotations']
        #         if 'selfLink' in data['metadata']:
        #             del data['metadata']['selfLink']
        #         del data['metadata']['creationTimestamp']
        #         del data['metadata']['finalizers']
        #         del data['metadata']['resourceVersion']
        #         del data['metadata']['uid']
        #         del data['spec']['claimRef']['uid']
        #         del data['spec']['claimRef']['resourceVersion']
        #         del data['status']

        #     # 定义文件路径及文件名
        #     filename = './new_yaml/' + f"{args.namespace}" + '_' +data['kind'] + '_' + data['metadata']['name'] + '.yaml'
        #     with open(filename, 'w') as file:
        #         yaml.dump(data, file)
        #     print(filename+"save success, please check pv_type(nfs or other) and storageclasss!!!")
