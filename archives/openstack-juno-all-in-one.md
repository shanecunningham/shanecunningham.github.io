+++
author = "Shane Cunningham"
categories = ["openstack", "RDO"]
date = 2014-11-08T11:32:31Z
description = ""
draft = false
slug = "openstack-juno-all-in-one"
tags = ["openstack", "RDO"]
title = "OpenStack Juno All in One"

+++


Quick guide on setting up the [OpenStack Juno](http://www.openstack.org/software/juno/) release in an all in one server with one NIC using [RDO](https://openstack.redhat.com/Main_Page). This is configured for Neutron networking with floating IPs. 

My setup: CentOS 7 minimal, IP: 192.168.1.100

By default NetworkManager will be running and controlling our NICs. packstack will complain about this later so disable and stop the service. 

<pre><code>[root@juno-allinone ~]# systemctl disable NetworkManager
[root@juno-allinone ~]# systemctl stop NetworkManager
</pre></code>

Next we'll update some stuff, install the RDO Juno repo and install packstack.

<pre><code>[root@juno-allinone ~]# yum update -y
[root@juno-allinone ~]# yum install -y https://rdo.fedorapeople.org/rdo-release.rpm
[root@juno-allinone ~]# yum install -y openstack-packstack
</pre></code>

Now we install OpenStack. I didn't check what --allinone installs by default so I explicitly flag Nagios to no and yes to Heat. 

<pre><code>[root@juno-allinone ~]# packstack --allinone --provision-all-in-one-ovs-bridge=n --nagios-install=n --os-heat-install=y
</code></pre>

Next steps are the same in my previous guide. Change your physical NIC (ifcfg-p4p1) as needed. 

<pre><code>vim /etc/sysconfig/network-scripts/ifcfg-br-ex

DEVICE=br-ex
DEVICETYPE=ovs
TYPE=OVSBridge
BOOTPROTO=static
IPADDR=192.168.1.100 # Old physical NIC IP
NETMASK=255.255.255.0 
GATEWAY=192.168.1.1 
DNS1=192.168.1.1 
ONBOOT=yes

vim /etc/sysconfig/network-scripts/ifcfg-p4p1

DEVICE=p4p1
TYPE=OVSPort
DEVICETYPE=ovs
OVS_BRIDGE=br-ex
HWADDR="68:05:CA:16:8D:FB"
ONBOOT=yes
</pre></code>

Add the following to the /etc/neutron/plugin.ini file

<pre><code>network_vlan_ranges = physnet1
bridge_mappings = physnet1:br-ex
</code></pre>

<pre><code>[root@juno-allinone ~]# service network restart
</pre></code>

Networking should be setup from the host side. Now we can setup the OpenStack side of networking. I'd recommend creating a new tenant, but if you are using the 'admin' tenant, delete all routers/networks. Remember to set your floating IP range outside your DHCP range. 

<pre><code>[root@juno-allinone ~]# . keystonerc_admin

[root@juno-allinone ~(keystone_admin)]# neutron router-create router
[root@juno-allinone ~(keystone_admin)]# neutron net-create private
[root@juno-allinone ~(keystone_admin)]# neutron subnet-create private 10.0.0.0/24 --name private_subnet
[root@juno-allinone ~(keystone_admin)]# neutron router-interface-add router private_subnet
[root@juno-allinone ~(keystone_admin)]# neutron net-create public --router:external=True
[root@juno-allinone ~(keystone_admin)]# neutron subnet-create public 192.168.1.0/24 --name public_subnet --enable_dhcp=False --allocation-pool start=192.168.1.200,end=192.168.1.250 --gateway=192.168.1.1
[root@juno-allinone ~(keystone_admin)]# neutron router-gateway-set router public
</code></pre>

Allow ICMP and SSH.

<pre><code>[root@juno-allinone ~(keystone_admin)]# neutron security-group-rule-create --protocol icmp --direction ingress default
[root@juno-allinone ~(keystone_admin)]# neutron security-group-rule-create --protocol tcp --port-range-min 22 --port-range-max 22 --direction ingress default
</code></pre>

At this point you should be able to spin up a cirros instance to test and assign floating IPs to the instance. 