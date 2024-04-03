# 获取 k8s 中 yaml 文件
- deployment \ sts
```
kubectl get deplotment,sts --all-namespaces | grep -vE 'NAMESPACE|dce-system|default|kube-system|monitoring|logclean' | awk '{print $1,$2}' \
| while read line; \
do \
kubectl get -n $line -o yaml > `echo $line | awk '{print $2}' | sed 's#/#_#g'`.yaml; \
done
```

# 数据格式化处理
- deploy_exportcsv.py  # 导出 csv 支持筛选
```
依赖库
openpyxl
yaml
os
```
- dcedeploy_yaml.py # 导出表格格式
```
依赖库
prettytable
yaml
os
```
# generateyaml 是对 k8s 的 yaml 文件中字段进行清洗
1. [参考连接](https://github.com/bertreyking/bertreyking.github.io/releases/tag/generateyaml-v4)
