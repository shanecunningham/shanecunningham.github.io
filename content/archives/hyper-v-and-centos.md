+++
author = "Shane Cunningham"
categories = ["Hyper-V"]
date = 2011-07-19T06:51:00Z
description = ""
draft = false
slug = "hyper-v-and-centos"
tags = ["Hyper-V"]
title = "Hyper-V and CentOS"

+++


CentOS is not listed as a supported OS for Microsoft’s Hyper-V but I’ve found it works pretty well. Whenever I install CentOS on Hyper-V I forget the configuration file you have to create to get eth0 working. So here it is.

Install CentOS. Add legacy NIC in Hyper-V settings.

Create file <code>/etc/sysconfig/network-scripts/ifcfg-eth0</code> and input the following with your values of course.

<pre><code>DEVICE=eth0
BOOTPROTO=static
BROADCAST=192.168.0.255
IPADDR=192.168.0.100
NETMASK=255.255.255.0
NETWORK=192.168.0.0
ONBOOT=yes
TYPE=Ethernet
GATEWAY=192.168.0.1</code></pre>

Some other commands or config files that might need to be edited.

<pre><code>service network restart</code> - restart networking
<code>/etc/hosts</code> - server IP and hostname
<code>/etc/resolv.conf</code> - nameserver and IP
<code>route add -net 0.0.0.0 gw 192.168.0.1 eth0</code> - add default route</pre>

