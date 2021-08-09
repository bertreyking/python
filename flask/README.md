# 使用手手册

1. 功能说明
```
- post 请求入参，并判断 values 格式(数据类型 form 表单)
- 默认同步镜像到生产所有镜像仓库(docker run 时需要指定 REG_IP)，传参有生产镜像仓库 IP 时，仅同步到该仓库
```

2. api接口启动(REG_IP 对应镜像仓库IP地址，api接口最大支持30个镜像仓库)
```
docker run -itd -p 3002:3002 \
-v /var/run/docker.sock:/var/run/docker.sock \
-e REG_IP=192.168.1.10 \
-e REG_IP=192.168.1.10 \
--name post_api_name \
192.167.1.10/registry/pushimages:latest
```
