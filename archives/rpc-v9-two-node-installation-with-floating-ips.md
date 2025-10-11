+++
author = "Shane Cunningham"
categories = ["openstack", "openstack-ansible"]
date = 2015-02-07T05:29:57Z
description = ""
draft = false
slug = "rpc-v9-two-node-installation-with-floating-ips"
tags = ["openstack", "openstack-ansible"]
title = "RPC v9 - Two node with floating IPs"

+++


Building on my [previous post](https://www.cunninghamshane.com/how-to-rpc-v9-two-node-installation/) on installing Rackspace Private Cloud in a two node configuration, this update changes that slightly to allow for external network access and floating IPs to work with this deployment. My previous post used all VXLAN interfaces from a single physical NIC. That would not allow external/floating IPs to work, or at least I couldn't get it to work. Since I have two physical NICs on these servers this guide will use both - **em1** for br-mgmt, br-vxlan, br-storage via VXLAN interfaces since I don't want to use VLANs, and **p4p1** for br-vlan, which has direct access to my external network, 192.168.1.0/24. 

**Keep in mind**:

- Official Rackspace Private Cloud install guide can be found [here](http://docs.rackspace.com/rpc/api/v9/bk-rpc-installation/content/rpc-common-front.html)
- My guide just goes over some that process with me using [openstack-ansible](https://launchpad.net/openstack-ansible) and only 2 physical nodes
- To perform this minimal configuration with no VLANs it uses VXLAN interfaces
- This is just for testing, learning how to deploy with [openstack-ansible](https://launchpad.net/openstack-ansible) and operating OpenStack with [LXC containers](https://help.ubuntu.com/lts/serverguide/lxc.html)

##Networking

/etc/network/interfaces - [gist](https://gist.github.com/shane-c/28afa426358406d59fbb)

/etc/network/interfaces.d/openstack-interfaces.cfg - [gist](https://gist.github.com/shane-c/1f3600c6f3099e6b4b60)

Just to document everything that actually worked for me I'm including both files, interfaces and openstack-interfaces.cgf, but obviously edit as needed. I setup both of these on my infrastructure and compute physical nodes. The VXLAN interfaces use em1. br-vlan uses p4p1. Change the br-mgmt, br-vxlan, br-storage IPs for your different nodes. Notice p4p1 and br-vlan don't have IPs. 

**infra1**:
<pre><code>IP address for em1:        192.168.1.100
IP address for br-mgmt:    172.29.236.10
IP address for br-vxlan:   172.29.240.10
IP address for br-storage: 172.29.244.10
IP address for br-vlan:    none</pre></code>

**compute1**:
<pre><code>IP address for em1:        192.168.1.101
IP address for br-mgmt:    172.29.236.11
IP address for br-vxlan:   172.29.240.11
IP address for br-storage: 172.29.244.11
IP address for br-vlan:    none</pre></code>

##Installing

See [previous post](https://www.cunninghamshane.com/how-to-rpc-v9-two-node-installation/) on setting up target hosts for the packages and dependencies required. Now we need to grab the RPC installation playbooks and configs. I used the RPC v10 Juno branch in this setup, v10 is still in development so you can also use the better tested icehouse branch. 

<pre><code>root@infra1:~# cd /opt
root@infra1:/opt# git clone -b juno https://github.com/stackforge/os-ansible-deployment.git
root@infra1:/opt# curl -O https://bootstrap.pypa.io/get-pip.py
root@infra1:/opt# python get-pip.py
root@infra1:/opt# pip install -r /opt/os-ansible-deployment/requirements.txt
root@infra1:/opt# cp -R /opt/os-ansible-deployment/etc/rpc_deploy /etc</pre></code>

**/etc/rpc\_deploy/user_variables.yml** is the file containing OpenStack and infrastructure service usernames, passwords and other variables you can set. There's a handy Python script you can run to auto generate these passwords. 

<pre><code>root@infra1:~# cd /opt/os-ansible-deployment/scripts
root@infra1:/opt/os-ansible-deployment/scripts# ./pw-token-gen.py --file /etc/rpc\_deploy/user\_variables.yml</pre></code>

If your compute node supports KVM, I would recommend adding `nova_virt_type: kvm` in user_variables.yml. 

**/etc/rpc\_deploy/rpc\_user\_variables.yml** is the config file where you define your OpenStack networks, IPs and which physical hosts will receive which OpenStack service. [Gist](https://gist.github.com/shane-c/a7026af3e7f6c9cebe34) of my rpc\_user_variables.yml for reference. Since we won't be using a physical load balancer we add an HAProxy host. You'll notice infra1 refers to my infrastructure hosts br-mgmt network, compute1 to my compute nodes br-mgmt, and I'm actually using my compute node for cinder too, again, flexibility. I'm also reusing the infra1 node for the log, network and haproxy hosts since we don't have dedicated servers for those tasks. Be sure to set `external_lb_vip_address` as the externally accessible IP.

Now we install. These can take awhile depending on your systems, the OpenStack playbooks take the longest. Forks is set to 15 in `/opt/os-ansible-deployment/rpc_deployment/ansible.cfg`, bump that up to 25 or higher if you prefer. Change directory to `/opt/os-ansible-deployment/rpc_deployment`. First we run the host-setup.yml playbook, followed by the haproxy-install.yml, infrastructure-setup.yml and then the openstack-setup.yml playbook.

<pre><code>root@infra1:/opt/os-ansible-deployment/rpc\_deployment# ansible-playbook -e @/etc/rpc\_deploy/user\_variables.yml \
 playbooks/setup/host-setup.yml
</pre></code>

Hopefully each of these completes with zero items unreachable or failed. Now we run the HAProxy playbook and so on. 

<pre><code>root@infra1:/opt/os-ansible-deployment/rpc\_deployment# ansible-playbook -e @/etc/rpc\_deploy/user\_variables.yml \
 playbooks/infrastructure/haproxy-install.yml</pre></code>

<pre><code>root@infra1:/opt/os-ansible-deployment/rpc\_deployment# ansible-playbook -e @/etc/rpc\_deploy/user\_variables.yml \
 playbooks/infrastructure/infrastructure-setup.yml</pre></code>

[Verify](http://docs.rackspace.com/rpc/api/v9/bk-rpc-installation/content/sec-playbooks-infrastructure-verify.html) the infrastructure playbook ran successfully. At this point you should be able to hit your Kibana interface at https://IP:8443. Isn't that an awesome Kibana dashboard?

![kibana_small](https://6dbddbf8e5efac8bed3b-f96466f7bd752d7ade3ea7b63a5a8dcd.ssl.cf1.rackcdn.com/kibana_small.png)

Now we run the main OpenStack playbooks, these can take some time to complete. 

<pre><code>root@infra1:/opt/os-ansible-deployment/rpc\_deployment# ansible-playbook -e @/etc/rpc\_deploy/user\_variables.yml \
 playbooks/openstack/openstack-setup.yml</pre></code>

[Verify](http://docs.rackspace.com/rpc/api/v9/bk-rpc-installation/content/sec-playbooks-openstack-verify.html) OpenStack operation. That's it! You should have a two node RPC installation. The Horizon dashboard should be reachable at your servers external IP over HTTPS.

##Neutron setup and floating IPs

The utility container is a helpful container with tools like the OpenStack clients installed. When interacting with the deployment you probably want to attach to the utility container and peform actions.

<pre><code>root@infra1:~# lxc-ls | grep utility
infra1\_utility\_container-e2a359e9
root@infra1:~# lxc-attach -n infra1\_utility\_container-e2a359e9
root@infra1\_utility\_container-e2a359e9:~#</pre></code>

Here's what I did to setup two networks, one private for instance to instance traffic, and the other external for floating IPs. Our install should have put a openrc file with our 'admin' credentials in the utility container at /root. With this simple 2-node setup, don't get caught up with the bridge names. The br-vlan is what we use for our external network even though we are not using VLANs. I think you can edit these names in the config but I will need to test.

<pre><code>root@infra1\_utility\_container-e2a359e9:~# source openrc
root@infra1\_utility\_container-e2a359e9:~# neutron router-create router
root@infra1\_utility\_container-e2a359e9:~# neutron net-create private
root@infra1\_utility\_container-e2a359e9:~# neutron subnet-create private 10.0.0.0/24 --name private\_subnet
root@infra1\_utility\_container-e2a359e9:~# neutron router-interface-add router private\_subnet
root@infra1\_utility\_container-e2a359e9:~# neutron net-create ext-net --router:external True --provider:physical\_network vlan --provider:network\_type flat
root@infra1\_utility\_container-e2a359e9:~# neutron subnet-create ext-net --name ext-subnet --allocation-pool start=192.168.1.220,end=192.168.1.240 --disable-dhcp --gateway 192.168.1.254 192.168.1.0/24
root@infra1\_utility\_container-e2a359e9:~# neutron router-gateway-set router ext-net</pre></code>

Now you can add a floating IP to your tenant and assign it to an instance. You can do that from Horizon or the command line from the utility container. Use neutron floatingip-list, floatingip-create, port-list (or just use Horizon) to get the info you need. neutron floatingip-associate uses FLOATINGIP\_ID PORT. 

<pre><code>root@infra1\_utility\_container-e2a359e9:~# neutron floatingip-create 5c9919d4-592b-4cf7-ab8c-58a1a9f6c35e
Created a new floatingip:
+---------------------+--------------------------------------+
| Field               | Value                                |
+---------------------+--------------------------------------+
| fixed\_ip\_address    |                                      |
| floating\_ip\_address | 192.168.1.226                        |
| floating\_network\_id | 5c9919d4-592b-4cf7-ab8c-58a1a9f6c35e |
| id                  | 1d3a3c8c-361a-4227-a92d-1338ab224de5 |
| port\_id             |                                      |
| router\_id           |                                      |
| status              | DOWN                                 |
| tenant\_id           | eb02f61d35f0433799b180b74c9b85fc     |
+---------------------+--------------------------------------+ <br>
root@infra1\_utility\_container-e2a359e9:~# neutron floatingip-associate 1d3a3c8c-361a-4227-a92d-1338ab224de5 c9a51a71-a815-4cbf-92db-c51891acd325
Associated floating IP 1d3a3c8c-361a-4227-a92d-1338ab224de5 <br>
root@infra1\_utility\_container-e2a359e9:~# ping -c3 192.168.1.226
PING 192.168.1.226 (192.168.1.226) 56(84) bytes of data.
64 bytes from 192.168.1.226: icmp\_seq=1 ttl=62 time=1.50 ms
64 bytes from 192.168.1.226: icmp\_seq=2 ttl=62 time=0.690 ms
64 bytes from 192.168.1.226: icmp\_seq=3 ttl=62 time=0.683 ms
--- 192.168.1.226 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2000ms
rtt min/avg/max/mdev = 0.683/0.957/1.500/0.385 ms</pre></code>

Woot! Next up, adding a Swift node! If you're having any issues reaching the floating IP take a look at your security group settings and open ICMP, SSH as needed. 