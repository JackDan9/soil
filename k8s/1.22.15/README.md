# Kubernetes 1.22.15版本安装

## 要求1-网络
- 能访问外网

## 要求2-机器资源
至少两台机器(一台master, 一台slave1)
- 16Core 32GB 1TB(master)
- 16Core 32GB 500GB(slave1)
- 16Core 32GB 500GB(slave2)
- 16Core 32GB 1TB(slave3)

## 配置Master
执行如下命令来配置master主机。该程序会自动做一下几步:

- 安装`docker`组件
- 安装`k8s`组件(kubeadm, kubelet等)
- 通过kubeadm启动集群
- 安装flannel组件

```shell
curl http://xxx.xxxx.xxx/1.22.15/master.sh | bash
```

## 配置Slave

执行如下命令来配置slave主机。该程序会自动做以下几步:

- 安装docker组件
- 安装k8s组件(kubeadm,kubelet等)

```shell
curl https://xxx.xxx.xxx/1.22.15/slave.sh | bash
```

## 将slave加入集群

执行以下命令可以将slave加入到集群中。具体参数在执行master.sh的终端获取

```shell
kubeadm join ${masterip}:6443 --token ${token} \
> --discovery-token-ca-cert-hash ${sha256}
```

例子:
```shell
kubeadm join 172.27.88.38:6443 --token ngqbmr.d6eyccpzec32g5sc --discovery-token-ca-cert-hash sha256:b2ec3cbfa4961f656625b8e9ddfd0e6628d437d03669dcdb4e4137ca0e23992e
```

> 参考: https://blog.csdn.net/qq_22917569/article/details/130445041