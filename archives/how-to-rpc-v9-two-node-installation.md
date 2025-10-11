+++
author = "Shane Cunningham"
categories = ["openstack-ansible", "openstack"]
date = 2015-01-11T05:16:25Z
description = ""
draft = false
slug = "how-to-rpc-v9-two-node-installation"
tags = ["openstack-ansible", "openstack"]
title = "Two node RPC v9 installation"

+++


[Rackspace Private Cloud](http://www.rackspace.com/cloud/private/openstack) powered by [OpenStack](http://www.openstack.org/) was recently re-architected to be much more flexible and reliable in RPC v9 (Icehouse) and the soon to be released RPC v10 (Juno). It actually deploys OpenStack in [LXC containers](https://linuxcontainers.org/lxc/introduction/) on your hosts. At first, you might think this adds a layer of complexity in an already complex process, but I've found it actually provides a tremendous amount of flexibility and an easier upgrade path for your OpenStack installation. Using this deployment method you should only have to edit two Ansible configuration files, so the process is not all that difficult and makes installing OpenStack simpler. 

The [reference architecture](http://docs.rackspace.com/rpc/api/v9/bk-rpc-installation/content/sec_overview_host-layout.html) for RPC v9 is designed to be more robust and scalable than previous versions with three infrastructure/controller nodes, physical redundant firewalls and load balancers. I don't have that kind of gear in my closet to test on, and don't want to use VLANs to segment this traffic, so this guide will be covering how to use Rackspace Private Cloud software on a two node (1 infrastructure node, 1 compute node) installation with 1 NIC.

**Keep in mind**:

- Official Rackspace Private Cloud install guide can be found [here](http://docs.rackspace.com/rpc/api/v9/bk-rpc-installation/content/rpc-common-front.html)
- My guide just goes over some that process with me using [openstack-ansible](https://launchpad.net/openstack-ansible) and only 2 physical nodes
- To perform this minimal configuration with no VLANs it uses VXLAN interfaces
- This is just for testing, learning how to deploy with [openstack-ansible](https://launchpad.net/openstack-ansible) and operating OpenStack with LXC containers

## My gear

**Infrastructure node**:

Lenovo ThinkServer TS140
Xeon E3-1225v3 3.2 GHz
8GB ECC RAM
2 NICs (only using 1 for OpenStack)

**Compute node**: 

Dell Poweredge T110II
Xeon E3-1230v2 3.3 GHz
32 GB ECC RAM
2 NICs (only using 1 for OpenStack)

**Network**: 192.168.1.0/24, we will be creating VXLAN interfaces/bridges for our nodes to talk. 


#### Deployment Hosts

You can have a dedicated server just for Ansible and the configuration files that are used to deploy OpenStack to your nodes, but I want to keep this as simple as possible so we will be combining our infrastructure and deployment node.

#### Target Hosts

Target hosts are your infrastructure, compute, cinder, swift, etc physical hosts. OpenStack and infrastructure services will be installed inside containers on these hosts. Let's prepare our infrastructure and compute nodes.

## Infrastructure/Deployment node

OS: Ubuntu Server 14.04 LTS
NIC: 192.168.1.50

<pre><code>root@infra1:~# apt-get update; apt-get upgrade -y
root@infra1:~# apt-get install -y aptitude build-essential git ntp ntpdate \
openssh-server python-dev sudo bridge-utils debootstrap ifenslave lsof lvm2 \
tcpdump vlan</pre></code>

Add the following to your /etc/network/interfaces file `source /etc/network/interfaces.d/*.cfg`. 

<pre><code>root@infra1:~# vim /etc/network/interfaces.d/openstack-interfaces.cfg</pre></code>

Copy the contents from [this gist](https://gist.github.com/shane-c/11aa8da9e54e5685038c), it contains the interfaces and bridges to setup. Feel free to change `dev em1` for the vxlan- interfaces depending on your physical NIC device name. I'd recommend leaving the IPs as is since the RPC config file is setup to use the 172.29 networks.

Give the server a reboot and confirm the bridges come up with their IPs. 

<pre><code>IP address for em1:        192.168.1.50
IP address for br-mgmt:    172.29.236.10
IP address for br-vxlan:   172.29.240.10
IP address for br-storage: 172.29.244.10</pre></code>

## Compute node

OS: Ubuntu Server 14.04 LTS
NIC: 192.168.1.55

Since this is just a target host, we install a few less packages. 
<pre><code>root@compute1:~# apt-get update; apt-get upgrade -y
root@compute1:~# apt-get install -y bridge-utils debootstrap ifenslave lsof \
lvm2 ntp ntpdate openssh-server sudo tcpdump vlan</pre></code>

Follow the same network setup as above, but change the br-mgmt address to 172.29.236.11, br-vxlan to 172.29.240.11, br-storage to 172.29.244.11. Compute node [gist](https://gist.github.com/shane-c/1ce2920639c315500771) if needed.

Reboot the compute node.

<pre><code>IP address for em1:        192.168.1.55
IP address for br-mgmt:    172.29.236.11
IP address for br-vxlan:   172.29.240.11
IP address for br-storage: 172.29.244.11</pre></code>

To confirm your nodes can talk over the VXLAN/br-mgmt 172.29 networks, login to your infrastructure node and ping 172.29.236.11 which should be the compute node. From the compute node ping 172.29.236.10.  

## Installation

From your infrastructure/deployment node create an SSH key and copy the public SSH key to all your target hosts /root/.ssh/authorized_keys file. Confirm you can login to the nodes with root from the infrastructure/deployment node. 

Now we need to grab the RPC installation playbooks and configs. I used the RPC v10 Juno branch in this setup, v10 is still in development so you can also use the better tested icehouse branch. 

<pre><code>root@infra1:~# cd /opt
root@infra1:/opt# git clone -b juno https://github.com/stackforge/os-ansible-deployment.git
root@infra1:/opt# curl -O https://bootstrap.pypa.io/get-pip.py
root@infra1:/opt# python get-pip.py
root@infra1:/opt# pip install -r /opt/os-ansible-deployment/requirements.txt
root@infra1:/opt# cp -R /opt/os-ansible-deployment/etc/rpc_deploy /etc</pre></code>

That last command copied the main configuration files directory, rpc\_deploy, to /etc. So going forward when you want to edit your rpc\_user\_variables.yml and user\_variables.yml files, edit them from /etc/rpc\_deploy/. 

**/etc/rpc\_deploy/user_variables.yml** is the file containing OpenStack and infrastructure service usernames, passwords and other variables you can set. There's a handy Python script you can run to auto generate these passwords. 

<pre><code>root@infra1:~# cd /opt/os-ansible-deployment/scripts
root@infra1:/opt/os-ansible-deployment/scripts# ./pw-token-gen.py --file /etc/rpc\_deploy/user\_variables.yml</pre></code>

If your compute node supports KVM, I would recommend adding `nova_virt_type: kvm` in user_variables.yml. 

**/etc/rpc\_deploy/rpc\_user\_variables.yml** is the config file where you define your OpenStack networks, IPs and which physical hosts will receive which OpenStack service. [Gist](https://gist.github.com/shane-c/a7026af3e7f6c9cebe34) of my rpc\_user_variables.yml for reference. Since we won't be using a physical load balancer we add an HAProxy host. You'll notice infra1 refers to my infrastructure hosts br-mgmt network, compute1 to my compute nodes br-mgmt, and I'm actually using my compute node for cinder too, again, flexibility. I'm also reusing the infra1 node for the log, network and haproxy hosts since we don't have dedicated servers for those tasks. Be sure to set `external_lb_vip_address` as the externally accessible IP, 192.168.1.50 in this setup.

Now we install. These can take awhile depending on your systems, the OpenStack playbooks take the longest. Forks is set to 15 in `/opt/os-ansible-deployment/rpc_deployment/ansible.cfg`, bump that up to 25 or higher if you prefer. Change directory to /opt/os-ansible-deployment/rpc\_deployment. First we run the host-setup.yml playbook, followed by the haproxy-install.yml, infrastructure-setup.yml and then the openstack-setup.yml playbook.

<pre><code>root@infra1:/opt/os-ansible-deployment/rpc\_deployment# ansible-playbook -e @/etc/rpc\_deploy/user\_variables.yml \
 playbooks/setup/host-setup.yml
</pre></code>

Hopefully each of these completes with zero items unreachable or failed. Now we run the HAProxy playbook and so on. 

<pre><code>root@infra1:/opt/os-ansible-deployment/rpc\_deployment# ansible-playbook -e @/etc/rpc\_deploy/user\_variables.yml \
 playbooks/infrastructure/haproxy-install.yml</pre></code>

<pre><code>root@infra1:/opt/os-ansible-deployment/rpc\_deployment# ansible-playbook -e @/etc/rpc\_deploy/user\_variables.yml \
 playbooks/infrastructure/infrastructure-setup.yml</pre></code>

[Verify](http://docs.rackspace.com/rpc/api/v9/bk-rpc-installation/content/sec-playbooks-infrastructure-verify.html) the infrastructure playbook ran successfully. At this point you should be able to hit your Kibana interface at https://192.168.1.50:8443. Isn't that an awesome Kibana dashboard? 

![kibana_small](https://6dbddbf8e5efac8bed3b-f96466f7bd752d7ade3ea7b63a5a8dcd.ssl.cf1.rackcdn.com/kibana_small.png)

Now we run the main OpenStack playbooks, this usually takes the longest. 

<pre><code>root@infra1:/opt/os-ansible-deployment/rpc\_deployment# ansible-playbook -e @/etc/rpc\_deploy/user\_variables.yml \
 playbooks/openstack/openstack-setup.yml</pre></code>

[Verify](http://docs.rackspace.com/rpc/api/v9/bk-rpc-installation/content/sec-playbooks-openstack-verify.html) OpenStack operation. That's it! You should have a two node RPC installation. The Horizon dashboard should be reachable at https://192.168.1.50/. You can also attach to the utility container and use the OpenStack clients to configure your Private Cloud.

<pre><code>root@infra1:~# lxc-ls | grep util
infra1\_utility\_container-9465f12e
root@infra1:~# lxc-attach -n infra1\_utility\_container-9465f12e
root@infra1\_utility\_container-9465f12e:~#
root@infra1\_utility\_container-9465f12e:~# . openrc
root@infra1\_utility\_container-9465f12e:~# nova list
+--------------------------------------+-------+--------+------------+-------------+---------------------------------+
| ID                                   | Name  | Status | Task State | Power State | Networks                        |
+--------------------------------------+-------+--------+------------+-------------+---------------------------------+
| ffa57e22-4335-449d-91bd-9397702fe1a8 | test1 | ACTIVE | -          | Running     | private=10.0.0.3, 192.168.1.221 |
+--------------------------------------+-------+--------+------------+-------------+---------------------------------+</pre></code>

## Notes, comments, additional links

I did run into a few random failures when running the playbooks, rerunning them usually fixed the issue. So before filing a [bug](https://launchpad.net/openstack-ansible), I'd recommend rerunning the playbook. I did come across times I just wanted to start over and blow away any containers already created. To clear out old containers and data I did the following on each node, I'm not 100% this is the proper way to do this. 

<pre><code>Remove container IPs from /etc/hosts
for i in \`lxc-ls\`; do lxc-stop -n $i; done
for i in \`lxc-ls\`; do lxc-destroy -n $i; done
rm -rf /openstack
rm /etc/rpc\_deploy/rpc\_inventory.json
rm /etc/rpc\_deploy/rpc\_hostnames\_ips.yml</pre></code>

The OpenStack APIs should be listening on your infra1 external IP, 192.168.1.50 in this example, so just point your [clients](https://wiki.openstack.org/wiki/OpenStackClients) to that IP and the required URL/port or just attach to the utility container. 

Swift should have been added to the playbooks recently, but I haven't tested it out yet. This two-node setup isn't going to be the best for performance (everything going through 1 NIC), I haven't tested networking on instances to see how well it performs with the VXLAN and bridge interfaces. There's probably a better way to setup the interfaces and if you find one let me know. I still need to see if I can get floating IPs working and how to setup the routers for the provider network. Things I tested quickly were spinning up a few cirros instances, making sure they can talk and creating a Cinder volume. I've started writing an Ansible playbook to automate the initial setup of the target hosts, I hope to post that soon. 

- Main repo for openstack-ansible: [https://github.com/stackforge/os-ansible-deployment](https://github.com/stackforge/os-ansible-deployment)
- Official docs for Rackspace Private Cloud: [http://docs.rackspace.com/rpc/api/v9/bk-rpc-installation/content/ch-overview.html](http://docs.rackspace.com/rpc/api/v9/bk-rpc-installation/content/ch-overview.html)
- Report bugs and follow project: [https://launchpad.net/openstack-ansible](https://launchpad.net/openstack-ansible)
- [https://developer.rackspace.com/blog/deploying-rackspace-private-cloud-v9-with-ansible/](https://developer.rackspace.com/blog/deploying-rackspace-private-cloud-v9-with-ansible/) - (Walter's post helped me figure out the networking when not using VLANs, my interfaces file is basically the one he has on [Github](https://github.com/wbentley15/rpcv9-deploy-pubcloud))

Moving OpenStack to LXC containers is a significant move for RPC, one that I believe opens up a great amount of flexibility. I look forward to learning and posting more about this method of installing OpenStack. 