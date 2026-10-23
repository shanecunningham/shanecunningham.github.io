---
title: "My all in one OpenStack deployment at home"
date: 2014-01-19T22:33:09Z
description: "Deploying an all-in-one OpenStack Havana cloud on CentOS 6.4 with packstack, with floating IPs on the home network."
tags: ["openstack", "linux"]
archived: true
---

I use XenServer 6.2 as my hypervisor at home to run anywhere from 5-10 VMs. But I wanted to change up this setup and move to [OpenStack](http://www.openstack.org/) Private Cloud deployment. Yes, it's overkill for my use but oh well.

I've messed around a few times with using OpenStack as replacement for my XenServer 6.2 setup, but always ran into an issue, usually getting the networking correct given my home network. Luckily with the OpenStack Havana release networking has become much simpler to get my head around and deploy. Also, a number of OpenStack installer scripts and how to guides have improved since the early OpenStack releases. For my deployment I used [Red Hat's RDO](http://openstack.redhat.com/) and packstack to deploy OpenStack Havana. From Red Hat, "RDO is a community of people using and deploying OpenStack on Red Hat Enterprise Linux, Fedora and distributions derived from these (such as CentOS, Scientific Linux and others).".

My home network is pretty simple. 192.168.1.0/24 with pfSense as my firewall and router which connects to an HP ProCurve 8-port switch, I have a wireless AP and my two physical servers hooked into the switch. All clients go through my AP for access. There are a ton of different ways you can configure OpenStack, this is just one way that I found extremely easy to get working and understand.

## OpenStack host setup

CentOS 6.4 minimal, 192.168.1.75

Yes, I disabled SELinux, sorry [Major](http://stopdisablingselinux.com/). Edit your /etc/selinux/config file and set SELINUX=disabled so when we update and reboot, SELinux will be disabled.

```console
[root@openstack ~]# yum install -y http://rdo.fedorapeople.org/openstack-havana/rdo-release-havana.rpm
[root@openstack ~]# yum update -y
[root@openstack ~]# reboot now
```

We should now have the RDO repo and updated system with the kernel needed to run Neutron networks. Next we install packstack and one additional package needed.

```console
[root@openstack ~]# yum install -y openstack-packstack python-netaddr
```

This next command uses packstack to deploy an all in one OpenStack deployment. Since we're connecting this to an external network, we add the `--provision-all-in-one-ovs-bridge=n` flag.

```console
[root@openstack ~]# packstack --allinone --provision-all-in-one-ovs-bridge=n
```

This will take awhile, and once it finishes should give you some information on your configuration. You should be able to access the Horizon dashboard at http://192.168.1.75/dashboard. The login credentials will be in /root/keystone_admin. Before we work in Horizon let's first make some changes to our network interfaces on the OpenStack host. My physical NIC was p4p1, yours might be different so change as necessary.

Edit the /etc/sysconfig/network-scripts/ifcfg-br-ex interface config file. Make it look like the following.

```console
[root@openstack ~]# vim /etc/sysconfig/network-scripts/ifcfg-br-ex

DEVICE=br-ex
DEVICETYPE=ovs
TYPE=OVSBridge
BOOTPROTO=static
IPADDR=192.168.1.75 # Old physical NIC IP since we want the network restart to not kill the connection, otherwise pick something outside your dhcp range
NETMASK=255.255.255.0 # your netmask
GATEWAY=192.168.1.1 # your gateway
DNS1=192.168.1.1 # your nameserver
ONBOOT=yes
```

Now we edit the physical interface config file, mine was /etc/sysconfig/network-scripts/ifcfg-p4p1. Make the following changes and make sure you don't use BOOTPROTO in your config.

```console
[root@openstack ~]# vim /etc/sysconfig/network-scripts/ifcfg-p4p1

DEVICE=p4p1
HWADDR=52:54:00:92:05:AE # your MAC address
TYPE=OVSPort
DEVICETYPE=ovs
OVS_BRIDGE=br-ex
ONBOOT=yes
```

Next add the following to the /etc/neutron/plugin.ini file.

```ini {title="/etc/neutron/plugin.ini"}
network_vlan_ranges = physnet1
bridge_mappings = physnet1:br-ex
```

Now we restart networking, if you're connected with SSH your session should remain up.

```console
[root@openstack ~]# service network restart
```

## OpenStack setup

Okay, now we setup our OpenStack networking to connect to our external network. First, from Horizon or the command line, delete all networks, ports and routers it created by default. We will recreate our own private and public networks.

We'll be running OpenStack commands so we need credentials. The next commands create a new router named "router", a private and public network and a private subnet and a public subnet, then we set the default gateway for our router. For the public network I assign a range of IPs my home DHCP server does not assign to, so just make sure there is not an IP conflict with the IPs you're assigning here and your external network.

```console
[root@openstack ~]# . keystonerc_admin

[root@openstack ~(keystone_admin)]# neutron router-create router
[root@openstack ~(keystone_admin)]# neutron net-create private
[root@openstack ~(keystone_admin)]# neutron subnet-create private 10.0.0.0/24 --name private_subnet
[root@openstack ~(keystone_admin)]# neutron router-interface-add router private_subnet
[root@openstack ~(keystone_admin)]# neutron net-create public --router:external=True
[root@openstack ~(keystone_admin)]# neutron subnet-create public 192.168.1.0/24 --name public_subnet --enable_dhcp=False --allocation-pool start=192.168.1.200,end=192.168.1.250 --gateway=192.168.1.1
[root@openstack ~(keystone_admin)]# neutron router-gateway-set router public
```

That's it. Allow ICMP and SSH to your default security group in the Access & Security section in Horizon. You should now be able to spin up a new instance using the included cirros image to test this. On the Networking tab, only assign a private IP. We will be allocating a floating IP to our project, then assigning this floating IP to this instance for external access.

For the floating IP setup, select Access & Security then Allocate IP to Project. Pool should be your public network, then click on Allocate IP. To attach that floating IP to your new VM, select Associate. The IP should be the floating IP you just assigned to your project and for the Port to be associated select your instance you created.

If everything worked then from your laptop or computer on your 192.168.1.0 network you should be able to ping/SSH to this floating IP connected to your VM in the 192.168.1.200-250 range.

## Couple notes

When you add a floating IP to an instance, it won't show the interface inside the instances with "ip a" or "ifconfig". So it's best to view/manage these using the nova client.

```console
shane@ubuntu-devbox:~$ nova list

+--------------------------------------+---------+--------+------------+-------------+---------------------------------+
| ID | Name | Status | Task State | Power State | Networks |
+--------------------------------------+---------+--------+------------+-------------+---------------------------------+
| d17cf973-3920-4622-a64f-bfeb1bdd080e | devbox1 | ACTIVE | None | Running | private=10.0.0.2                          |
| 92170264-c474-4e21-9256-5f9e1672c858 | devbox2 | ACTIVE | None | Running | private=10.0.0.4, 192.168.1.202           |
+--------------------------------------+---------+--------+------------+-------------+---------------------------------+
```

Everything you can do in Horizon you should be able to do at the command line using OpenStack tools on the host. Each OpenStack service has its own set of tools to configure that service. Also, you can use the various [OpenStack clients](https://wiki.openstack.org/wiki/OpenStackClients) to manage your infrastructure and spin up/down resources. For example, from one of my other servers or laptop I can manage my own OpenStack deployment and I can also use these same clients (with different credentials of course) to manage my Rackspace infrastructure since they are also based on OpenStack.

This is my personal OpenStack credentials file I used to list my two servers above after [installing python-novaclient](http://docs.openstack.org/user-guide/content/install_clients.html).

```console
shane@ubuntu-devbox:~$ cat .myopenstack

export OS_USERNAME=admin
export OS_PASSWORD=keystoneadminpassword
export OS_TENANT_NAME=admin
export OS_AUTH_URL=http://192.168.1.75:35357/v2.0/
export NOVACLIENT_DEBUG=1
export NOVA_VERSION=2
```

Two OpenStack deployments, my own private cloud and one public [Rackspace Cloud](http://www.rackspace.com/cloud/), managed by the same tools. Pretty cool.
