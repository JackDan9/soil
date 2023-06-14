#!/bin/bash
set -ex
echo "install k8s 1.22.15 slave"
TMP=/tmp/`whoami`/`date +'%Y%m%d-%H%M%S'`
mkdir -p $TMP
cd $TMP
yum install -y yum-utils device-mapper-persistent-data lvm2
yum-config-manager --add-repo http://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
yum install docker-ce -y

systemctl start docker
systemctl enable docker
docker version
docker ps
systemctl stop firewalld
systemctl disable firewalld

setenforce 0 || true

swapoff -a
cat > /etc/sysctl.d/k8s.conf << EOF
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
EOF
sysctl --system

cat > /etc/yum.repos.d/kubernetes.repo << EOF
[kubernetes]
name=Kubernetes
baseurl=https://mirrors.aliyun.com/kubernetes/yum/repos/kubernetes-el7-x86_64
enabled=1
gpgcheck=0
repo_gpgcheck=0
gpgkey=https://mirrors.aliyun.com/kubernetes/yum/doc/yum-key.gpg
https://mirrors.aliyun.com/kubernetes/yum/doc/rpm-package-key.gpg
EOF

yum install -y kubectl-1.22.15 kubeadm-1.22.15 kubelet-1.22.15


cat > /etc/docker/daemon.json << EOF
{
  "registry-mirrors": [
    "https://registry.docker-cn.com"
  ],
  "dns": ["8.8.8.8", "8.8.4.4"],
  "exec-opts": ["native.cgroupdriver=systemd"]
}
EOF

systemctl start kubelet
systemctl enable kubelet
systemctl restart docker
systemctl restart kubelet
