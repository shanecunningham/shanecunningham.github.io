---
title: "Hyper-V and CentOS"
date: 2011-07-19T06:51:00Z
tags: ["hyper-v"]
---

CentOS is not listed as a supported OS for Microsoft’s Hyper-V but I’ve found it works pretty well. Whenever I install CentOS on Hyper-V I forget the configuration file you have to create to get eth0 working. So here it is.

Install CentOS. Add legacy NIC in Hyper-V settings.

Create file `/etc/sysconfig/network-scripts/ifcfg-eth0` and input the following with your values of course.

```text
DEVICE=eth0
BOOTPROTO=static
BROADCAST=192.168.0.255
IPADDR=192.168.0.100
NETMASK=255.255.255.0
NETWORK=192.168.0.0
ONBOOT=yes
TYPE=Ethernet
GATEWAY=192.168.0.1
```

Some other commands or config files that might need to be edited.

```text
service network restart - restart networking
/etc/hosts - server IP and hostname
/etc/resolv.conf - nameserver and IP
route add -net 0.0.0.0 gw 192.168.0.1 eth0 - add default route
```
