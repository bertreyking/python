#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/08/02 17:10
# @Author  : weibing.ma@daocloud.io

from flask import Flask, request, jsonify
import docker
import requests
import os
import re

client = docker.DockerClient(base_url='tcp://10.6.203.60:2375')
# client = docker.DockerClient(base_url='unix://var/run/docker.sock')
app = Flask(__name__)


@app.route("/push_image", methods=['POST'])
def push_image():

    """1. 定义 ip_result 列表，主要存储返回信息。"""
    ips_result = []
    """判断请求类型是否是 post，并将请求 body 存储在 post_request_info,并判断其是否为字典"""
    if request.method == 'POST':
        if not request.form:
            return 'POST 请求表单为空'
        post_request_info = request.form
        if isinstance(post_request_info, dict):
            jfrog_registry_url = post_request_info.get('jfrog_registry_url')
            jfrog_registry_name = post_request_info.get('jfrog_registry_name')
            jfrog_image_name = post_request_info.get('jfrog_image_name')
            jfrog_image_tag = post_request_info.get('jfrog_image_tag')
            juser = post_request_info.get('jfrog_username')
            jpasswd = post_request_info.get('jfrog_password')
            prod_registry_url = post_request_info.get('prod_registry_url')
            prod_registry_name = post_request_info.get('prod_registry_name')

            """校验变量 values"""
            check_result = []
            for check_ip in jfrog_registry_url, prod_registry_url:
                if check_ip is None:
                    pass
                else:
                    if not re.match(
                            r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$",
                                check_ip):
                        check_result.append({'result': '{ip} IP address Invalid'.format(ip=check_ip)})

            for check_name in jfrog_registry_name, jfrog_image_name, prod_registry_name:
                if check_name is None:
                    pass
                else:
                    if '/' in check_name:
                        check_result.append({'result': '{name} Format is Error'.format(name=check_name)})

            if check_result:
                return jsonify(check_result)
            else:
                """判断登陆是否成功，失败抛出异常，并根据上面字典中变量，拼接镜像地址如：x.x.x.x/busybox/busybox:1.1"""
                try:
                    client.login(username='{u}'.format(u=juser), password='{p}'.format(p=jpasswd),
                                 registry='{jurl}'.format(jurl=jfrog_registry_url))
                except Exception as jlogin_err:
                    return {'Response': 500, 'Info': 'JfrogLoginFailed',
                            'Result': jlogin_err.__dict__.get('explanation')}

                jfrogImginfo = '{jfrogUrl}/{jfrogReg}/{prodRegName}/{jfrogImg}:{jfrogTag}'.format(jfrogUrl=jfrog_registry_url,
                                                                                                  jfrogReg=jfrog_registry_name,
                                                                                                  jfrogImg=jfrog_image_name,
                                                                                                  jfrogTag=jfrog_image_tag,
                                                                                                  prodRegName=prod_registry_name)

                """判断镜像是否 pull 成功，失败抛出异常"""
                try:
                    client.images.pull(jfrogImginfo)
                except Exception as e:
                    return {'Response': 404, 'Info': 'ImageNotFound', 'Result': e.__dict__.get('explanation')}

                """ 
                1. 定义 tmp_env_ips, prod_registry_ips 列表,主要用于获取和存储生产镜像仓库IP
                2. prod_registry_url 变量存在则执行 else 部分仅 push 到指定的仓库, 如果不存在，push到 prod_registry_ips 列表中所有仓库
                """
                tmp_env_ips = []
                prod_registry_ips = []
                env = dict(os.environ)
                for i in range(1, 31):
                    env_ips = env.get('REG_IP' + str(i))
                    tmp_env_ips.append(env_ips)
                for ip in tmp_env_ips:
                    if ip is None:
                        pass
                    else:
                        prod_registry_ips.append(ip)

                if prod_registry_url is None:
                    for ip_index in range(0, len(prod_registry_ips)):
                        prodimagetag = '{url}/{prodReg}/{prodImg}'.format(url=prod_registry_ips[ip_index],
                                                                          prodReg=prod_registry_name,
                                                                          prodImg=jfrog_image_name)
                        if client.api.tag(jfrogImginfo, repository='{prodImg}'.format(prodImg=prodimagetag),
                                          tag='{img_tag}'.format(img_tag=jfrog_image_tag)):
                            client.login(username='jfrog', password='Daocloud@1234',
                                         registry='{curl}'.format(curl=prod_registry_ips[ip_index]))

                            """判断镜像空间/镜像文件/镜像版本是否存在，存在返回异常，不存在 push 到指定镜像空间"""
                            auth = ('jfrog', 'Daocloud@1234')
                            reg_list = requests.get(
                                'http://{url}/dce/registries/buildin-registry/namespaces'.format(
                                    url=prod_registry_ips[ip_index]), auth=auth).json()
                            prod_registry_name_list = []
                            for reg_index in range(0, len(reg_list)):
                                if isinstance(reg_list[reg_index], dict):
                                    prod_registry_name_list.append(reg_list[reg_index]['Name'])
                            if prod_registry_name in prod_registry_name_list:
                                imgtag_list = requests.get(
                                    'http://{url}/dce/registries/buildin-registry/repositories/{reg_name}/{img_name}/tags'.format(
                                        url=prod_registry_ips[ip_index], reg_name=prod_registry_name,
                                        img_name=jfrog_image_name), auth=auth).json()
                                img_tags = []
                                for img_tag in range(0, len(imgtag_list)):
                                    img_tags.append(imgtag_list[img_tag]['Name'])
                                if img_tags:
                                    if jfrog_image_tag in img_tags:
                                        ips_result.append({'Response': 200, 'Info': 'DceRegistryImageVersionExist',
                                                           'ip': prod_registry_ips[ip_index]})
                                    else:
                                        if client.api.push(
                                                '{prod_img}:{img_tag}'.format(prod_img=prodimagetag,
                                                                              img_tag=jfrog_image_tag)):
                                            ips_result.append({'Response': 200, 'Info': 'PushFinished',
                                                               'ip': prod_registry_ips[ip_index]})
                                        else:
                                            ips_result.append(
                                                {'Response': 404, 'Info': 'PushFailed',
                                                 'ip': prod_registry_ips[ip_index]})
                                else:
                                    if client.api.push(
                                            '{prod_img}:{img_tag}'.format(prod_img=prodimagetag,
                                                                          img_tag=jfrog_image_tag)):
                                        ips_result.append({'Response': 200, 'Info': 'PushFinished',
                                                           'ip': prod_registry_ips[ip_index]})
                                    else:
                                        ips_result.append(
                                            {'Response': 404, 'Info': 'PushFailed',
                                             'ip': prod_registry_ips[ip_index]})
                            else:
                                ips_result.append(
                                    {'Response': 404, 'Info': 'DceRegistryNorFound',
                                     'ip': prod_registry_ips[ip_index]})
                else:
                    prodimagetag = '{url}/{prodReg}/{prodImg}'.format(url=prod_registry_url,
                                                                      prodReg=prod_registry_name,
                                                                      prodImg=jfrog_image_name)
                    if client.api.tag(jfrogImginfo, repository='{prodImg}'.format(prodImg=prodimagetag),
                                      tag='{img_tag}'.format(img_tag=jfrog_image_tag)):
                        client.login(username='jfrog', password='Daocloud@1234',
                                     registry='{curl}'.format(curl=prod_registry_url))
                        auth = ('jfrog', 'Daocloud@1234')
                        reg_list = requests.get(
                            'http://{url}/dce/registries/buildin-registry/namespaces'.format(
                                url=prod_registry_url), auth=auth).json()
                        prod_registry_name_list = []
                        for reg_index in range(0, len(reg_list)):
                            if isinstance(reg_list[reg_index], dict):
                                prod_registry_name_list.append(reg_list[reg_index]['Name'])
                        if prod_registry_name in prod_registry_name_list:
                            imgtag_list = requests.get(
                                'http://{url}/dce/registries/buildin-registry/repositories/{reg_name}/{img_name}/tags'.format(
                                    url=prod_registry_url, reg_name=prod_registry_name,
                                    img_name=jfrog_image_name), auth=auth).json()
                            img_tags = []
                            for img_tag in range(0, len(imgtag_list)):
                                img_tags.append(imgtag_list[img_tag]['Name'])
                            if img_tags:
                                if jfrog_image_tag in img_tags:
                                    ips_result.append({'Response': 200, 'Info': 'DceRegistryImageVersionExist',
                                                       'ip': prod_registry_url})
                                else:
                                    if client.api.push(
                                            '{prod_img}:{img_tag}'.format(prod_img=prodimagetag,
                                                                          img_tag=jfrog_image_tag)):
                                        ips_result.append({'Response': 200, 'Info': 'PushFinished',
                                                           'ip': prod_registry_url})
                                    else:
                                        ips_result.append(
                                            {'Response': 404, 'Info': 'PushFailed',
                                             'ip': prod_registry_url})
                            else:
                                if client.api.push(
                                        '{prod_img}:{img_tag}'.format(prod_img=prodimagetag,
                                                                      img_tag=jfrog_image_tag)):
                                    ips_result.append({'Response': 200, 'Info': 'PushFinished',
                                                       'ip': prod_registry_url})
                                else:
                                    ips_result.append(
                                        {'Response': 404, 'Info': 'PushFailed',
                                         'ip': prod_registry_url})
                        else:
                            ips_result.append(
                                {'Response': 404, 'Info': 'DceRegistryNorFound',
                                 'ip': prod_registry_url})

    """返回信息"""
    return jsonify(ips_result)


if __name__ == '__main__':
    from waitress import serve
    serve(app, host='0.0.0.0', port=3002)

