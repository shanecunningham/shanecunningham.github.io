+++
author = "Shane Cunningham"
categories = ["openstack-ansible", "openstack"]
date = 2015-03-21T11:01:33Z
description = ""
draft = false
slug = "openstack-in-containers-install-and-upgrade"
tags = ["openstack-ansible", "openstack"]
title = "Deploying OpenStack in containers: Install and Upgrade"

+++


My post on using [openstack-ansible](https://github.com/stackforge/os-ansible-deployment) to deploy OpenStack in [LXC containers](https://linuxcontainers.org/lxc/introduction/) in a two-node configuration with two NICs. One NIC is used for management, API and VM to VM traffic, the other NIC is for external network access. This is just for testing and messing around with deploying OpenStack in containers. An advantage to deploying with Ansible and containers is the easier upgrade path it provides. I'll show a simple example of that in place upgrade with going from Icehouse to Juno with just running a few playbooks.  

###2 Nodes


**infra1**:
Lenovo ThinkServer TS140 
Xeon E3-1225 v3 3.2 GHz 
8GB ECC RAM 
2 x 1Gb NICs

<pre><code>IP address for em1:        192.168.1.100
IP address for br-mgmt:    172.29.236.10
IP address for br-vxlan:   172.29.240.10
IP address for br-storage: 172.29.244.10
IP address for br-vlan:    none</pre></code>

**compute1**:
Dell Poweredge T110II 
Xeon E3-1230 v2 3.3 GHz 
32GB ECC RAM 
2 x 1Gb NICs

<pre><code>IP address for em1:        192.168.1.101
IP address for br-mgmt:    172.29.236.11
IP address for br-vxlan:   172.29.240.11
IP address for br-storage: 172.29.244.11
IP address for br-vlan:    none</pre></code>

Template [/etc/network/interfaces](https://gist.github.com/shane-c/28afa426358406d59fbb) and [/etc/network/interfaces.d/openstack-interfaces.cfg](https://gist.github.com/shane-c/1f3600c6f3099e6b4b60)

###Icehouse Install

We'll be deploying from the infra1 node, you could also have a dedicated 'deployment host', but for simplicity I deploy from infra1. Now we grab the version of openstack-ansible that will deploy Icehouse. 

<pre><code>root@infra1:~# cd /opt
root@infra1:/opt# git clone -b 9.0.9 https://github.com/stackforge/os-ansible-deployment.git
root@infra1:/opt# curl -O https://bootstrap.pypa.io/get-pip.py
root@infra1:/opt# python get-pip.py \
  --find-links="http://mirror.rackspace.com/rackspaceprivatecloud/python\_packages/icehouse" \
  --no-index
root@infra1:/opt# pip install -r /opt/os-ansible-deployment/requirements.txt
root@infra1:/opt# cp -R /opt/os-ansible-deployment/etc/rpc\_deploy /etc</pre></code>

Edit your /etc/rpc\_deploy/user\_variables.yml and /etc/rpc\_deploy/rpc\_user\_config.yml files which describe the environment. The following script can be used to generate user_variables.yml for service passwords. 

<pre><code>root@infra1:~# cd /opt/os-ansible-deployment/scripts
root@infra1:/opt/os-ansible-deployment/scripts# ./pw-token-gen.py --file /etc/rpc\_deploy/user\_variables.yml</pre></code>

You can see in the rpc\_user\_variables.yml file how you could add nodes if you had a larger deployment. This method of deploying OpenStack is designed for large deployments with multiple compute, cinder and swift nodes. For example, you can add more compute hosts like below.

<pre><code>compute_hosts:
  compute1:
    ip: 192.168.1.110
  compute2:
    ip: 192.168.1.111
  compute3:
    ip: 192.168.1.112</pre></code>

Template [/etc/rpc\_deploy/rpc\_user\_config.yml](https://gist.github.com/shane-c/f708f68fc597327d07a1) and [/etc/rpc\_deploy/user\_variables.yml](https://gist.github.com/shane-c/fa969ff78a110c4c23b4). In addition to the OpenStack service settings and passwords, the user\_variables.yml file can be used to integrate two services (Glance, Monitoring as a Service) with your public Rackspace cloud services. This is completely optional, you can still use the filesystem/NFS/NetApp for the glance backend and you don't have to install MaaS, but it gives you some additional options. For example, we can use [Cloud Files](http://www.rackspace.com/cloud/files) which is based on OpenStack Swift for the Glance backend in our private cloud. We can also use the included MaaS playbooks to hook into the (free) [Cloud Monitoring](http://www.rackspace.com/cloud/monitoring) service provided by Rackspace to monitor all of our hosts/containers/API services using the Cloud Monitoring API. The following values need to be setup in user\_variables.yml if you want to integrate the two services with your public cloud account. Change to your own public cloud account details and you can choose which data center and container to store your Glance images in Cloud Files.

<pre><code>glance\_container\_mysql\_password: 29e5e030146bbb9da53
glance\_default\_store: swift
glance\_notification\_driver: noop
glance\_service\_password: 311c46084d7e979175231787b39f90d93a
glance\_swift\_store\_auth\_address: '{{ rackspace\_cloud\_auth\_url }}'
glance\_swift\_store\_container: RPCGlance
glance\_swift\_store\_endpoint\_type: publicURL
glance\_swift\_store\_key: '{{ rackspace\_cloud\_password }}'
glance\_swift\_store\_region: DFW
glance\_swift\_store\_user: '{{ rackspace\_cloud\_tenant\_id }}:{{ rackspace\_cloud\_username }}'
maas\_alarm\_local\_consecutive\_count: 3
maas\_alarm\_remote\_consecutive\_count: 1
maas\_api\_key: '{{ rackspace\_cloud\_api\_key }}'
maas\_api\_url: https://monitoring.api.rackspacecloud.com/v1.0/{{ rackspace\_cloud\_tenant\_id }}
maas\_auth\_method: password
maas\_auth\_token: 820e62a9a0702154988f35d3a51baaf81df03883faae4c8f365f12a
maas\_auth\_url: '{{ rackspace\_cloud\_auth\_url }}'
maas\_check\_period: 60
maas\_check\_timeout: 30
maas\_keystone\_password: 0fa5ecea7459bfa25734b44cd5427
maas\_keystone\_user: maas
maas\_monitoring\_zones:
- mzdfw
- mziad
- mzord
- mzlon
maas\_notification\_plan: npQgbGTdDJ
maas\_repo\_version: 9.0.6
maas\_scheme: https
maas\_target\_alias: public0\_v4
maas\_username: '{{ rackspace\_cloud\_username }}'
rackspace\_cloud\_api\_key: Users API key
rackspace\_cloud\_auth\_url: https://identity.api.rackspacecloud.com/v2.0
rackspace\_cloud\_password: Control panel password
rackspace\_cloud\_tenant\_id: Account number
rackspace\_cloud\_username: Account username</pre></code>

Now comes running the playbooks and Ansible will deploy OpenStack. These are the playbooks and order to run. Since we're not using a physical load balancer like an f5, we add the HAProxy playbook which will use our infra1 node as the load balancer for the environment.

- playbooks/setup/host-setup.yml
- playbooks/infrastructure/haproxy-install.yml
- playbooks/infrastructure/infrastructure-setup.yml
- playbooks/openstack/openstack-setup.yml

Hopefully each of these completes with zero items unreachable or failed. If you do receive a failure I usually rerun the playbook at least once and use -vvv to get more verbose output. 

<pre><code>root@infra1:/opt/os-ansible-deployment/rpc\_deployment# ansible-playbook -e @/etc/rpc\_deploy/user\_variables.yml \
 playbooks/setup/host-setup.yml
</pre></code>

<pre><code>root@infra1:/opt/os-ansible-deployment/rpc\_deployment# ansible-playbook -e @/etc/rpc\_deploy/user\_variables.yml \
 playbooks/infrastructure/haproxy-install.yml</pre></code>

<pre><code>root@infra1:/opt/os-ansible-deployment/rpc\_deployment# ansible-playbook -e @/etc/rpc\_deploy/user\_variables.yml \
 playbooks/infrastructure/infrastructure-setup.yml</pre></code>

[Verify](http://docs.rackspace.com/rpc/api/v9/bk-rpc-installation/content/sec-playbooks-infrastructure-verify.html) the infrastructure playbook ran successfully. At this point you should be able to hit your Kibana interface at https://192.168.1.100:8443. The user is 'kibana' and the password can be found in 'kibana\_password' in user_variables.yml. 

[![kibana_icehouse](https://6dbddbf8e5efac8bed3b-f96466f7bd752d7ade3ea7b63a5a8dcd.ssl.cf1.rackcdn.com/kibana_icehouse.png)](https://6dbddbf8e5efac8bed3b-f96466f7bd752d7ade3ea7b63a5a8dcd.ssl.cf1.rackcdn.com/kibana_icehouse.png)

Now we run the main OpenStack playbooks, these can take some time to complete. 

<pre><code>root@infra1:/opt/os-ansible-deployment/rpc\_deployment# ansible-playbook -e @/etc/rpc\_deploy/user\_variables.yml \
 playbooks/openstack/openstack-setup.yml</pre></code>
 
[![horizon](https://6dbddbf8e5efac8bed3b-f96466f7bd752d7ade3ea7b63a5a8dcd.ssl.cf1.rackcdn.com/horizon1.png)](https://6dbddbf8e5efac8bed3b-f96466f7bd752d7ade3ea7b63a5a8dcd.ssl.cf1.rackcdn.com/horizon1.png)

OpenStack should be installed!

###Monitoring as a Service

This is optional as far as deploying OpenStack is concerned, but it's a really nice way to monitor your hosts, containers and services (for free). Just setup your public Rackspace cloud account details in user\_variables.yml and then run these playbooks. The playbooks will setup the monitoring agent and setup the checks for all hosts/containers/services, tying them to the notification plan you can create from [https://intelligence.rackspace.com](https://intelligence.rackspace.com). Click Notify and setup your notification plan. Then grab the notification ID, usually something like 'nphpgsP4DM' which you can see in the URL. Enter that in the maas\_notification\_plan section in user\_variables.yml. The only other thing you need to do is create an entity using the hostname for each server. From  https://intelligence.rackspace.com just click Create Entity. The MaaS playbook and the Cloud Monitoring API will automatically use the entities as long as they match your servers hostnames.

<pre><code>root@infra1:/opt/os-ansible-deployment/rpc\_deployment# ansible-playbook -e @/etc/rpc\_deploy/user\_variables.yml \
 playbooks/monitoring/raxmon-setup.yml
</pre></code>
<pre><code>root@infra1:/opt/os-ansible-deployment/rpc\_deployment# ansible-playbook -e @/etc/rpc\_deploy/user\_variables.yml \
 playbooks/monitoring/maas_local.yml
</pre></code>
<pre><code>root@infra1:/opt/os-ansible-deployment/rpc\_deployment# ansible-playbook -e @/etc/rpc\_deploy/user\_variables.yml \
 playbooks/monitoring/maas_remote.yml
</pre></code>
<pre><code>root@infra1:/opt/os-ansible-deployment/rpc\_deployment# ansible-playbook -e @/etc/rpc\_deploy/user\_variables.yml \
 playbooks/monitoring/maas_cdm.yml
</pre></code>

[![maas_1](https://6dbddbf8e5efac8bed3b-f96466f7bd752d7ade3ea7b63a5a8dcd.ssl.cf1.rackcdn.com/maas1.png)](https://6dbddbf8e5efac8bed3b-f96466f7bd752d7ade3ea7b63a5a8dcd.ssl.cf1.rackcdn.com/maas1.png)

[![maas_3](https://6dbddbf8e5efac8bed3b-f96466f7bd752d7ade3ea7b63a5a8dcd.ssl.cf1.rackcdn.com/maas3.png)](https://6dbddbf8e5efac8bed3b-f96466f7bd752d7ade3ea7b63a5a8dcd.ssl.cf1.rackcdn.com/maas3.png)

Did I mention Cloud Monitoring is free? :D

###OpenStack Networking

**Note**: Since we're not using VLANs I know the naming can be a bit confusing, I need to look into changing the naming since I believe the rpc\_user\_config.yml allows that. Traffic to a VMs floating IP enters the infra/network node on p4p1/br-vlan and the compute node accepts the traffic on em1/br-vxlan, so it's not truly segmented traffic. Fine for testing but I need to look into changing that up since there are two NICs on my servers.

The utility container is a helpful container with tools like the OpenStack clients installed. When interacting with the deployment you probably want to attach to the utility container and peform actions. I'd also recommend setting up an alias that quickly connects to the utility container.

<pre><code>root@infra1:~# lxc-ls | grep utility
infra1\_utility\_container-e2a359e9
root@infra1:~# lxc-attach -n infra1\_utility\_container-e2a359e9
root@infra1\_utility\_container-e2a359e9:~#</pre></code>

Here's what I did to setup two networks, one private for instance to instance traffic, and the other external for floating IPs. Our install should have put a file with our credentials at /root/openrc that we need to source to talk to our OpenStack installation.

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

###In place upgrade to Juno

One of the main advantages to deploying with Ansible and inside LXC containers is the ability it gives you to perform in place upgrades. This is an extremely simplified example, of course, with only 2 nodes, and doesn't neccessarily reflect the upgrade complications of larger deployments. It's just a little demo, but still pretty impressive given the past issues with upgrading OpenStack. 

First, let's verify what code base we're on.

<pre><code>root@compute1:~# nova-manage shell python
Python 2.7.6 (default, Mar 22 2014, 22:59:56)
[GCC 4.8.2] on linux2
Type "help", "copyright", "credits" or "license" for more information.
(InteractiveConsole)
\>>> from nova import version
\>>> version.version_string()
'2014.1.3'</pre></code>

We can verify the version from https://wiki.openstack.org/wiki/Releases, '2014.1.3' corresponds to the Icehouse release from Oct 2, 2014. 

Now all we have to do is download the openstack-ansible Juno bits and rerun the  same playbooks. To check instances reaction to the upgrade I'll ping to and from a running instance during the upgrade. We can also check the API response time from our Cloud Monitoring MaaS.

<pre><code>root@infra1:/opt# mv os-ansible-deployment/* /root/openstack-ansible-backup/
root@infra1:/opt# rm -rf os-ansible-deployment/
root@infra1:/opt# git clone -b 10.1.5 https://github.com/stackforge/os-ansible-deployment.git
root@infra1:/opt# cd os-ansible-deployment/rpc_deployment/</pre></code>

As for the config files, the only change I made was removing `maas_repo_version` from user\_variables.yml and deleting the alarms for the RabbitMQ checks from https://intelligence.rackspace.com. We also need to copy the new rpc_enviroment.yml file into /etc/rpc\_deploy/, for example, `# cp /opt/os-ansible-deployment/etc/rpc_deploy/rpc_environment.yml /etc/rpc_deploy/`. Additional options and documentation can be found [here](http://docs.rackspace.com/rpc/api/v10/bk-rpc-v10-releasenotes/content/rpc-upgrade-v9-v10.html). 

With the Juno openstack-ansible ready we run the following playbooks just like the Icehouse install.

<pre><code>root@infra1:/opt/os-ansible-deployment/rpc\_deployment# ansible-playbook -e @/etc/rpc\_deploy/user\_variables.yml \
 playbooks/setup/host-setup.yml
</pre></code>
<pre><code>root@infra1:/opt/os-ansible-deployment/rpc\_deployment# ansible-playbook -e @/etc/rpc\_deploy/user\_variables.yml \
 playbooks/infrastructure/infrastructure-setup.yml
</pre></code>
<pre><code>root@infra1:/opt/os-ansible-deployment/rpc\_deployment# ansible-playbook -e @/etc/rpc\_deploy/user\_variables.yml \
 playbooks/openstack/openstack-setup.yml
</pre></code>

Our monitoring system picked up some raises in API response time, but the only container that triggered an alarm was Horizon. It recovered on its own. 

infra1 node CPU and RAM visuals during the upgrade. 

[![maas_juno_infra1](https://6dbddbf8e5efac8bed3b-f96466f7bd752d7ade3ea7b63a5a8dcd.ssl.cf1.rackcdn.com/maas_juno_infra1.png)](https://6dbddbf8e5efac8bed3b-f96466f7bd752d7ade3ea7b63a5a8dcd.ssl.cf1.rackcdn.com/maas_juno_infra1.png)

Keystone API during upgrade.

[![maas_juno_keystone](https://6dbddbf8e5efac8bed3b-f96466f7bd752d7ade3ea7b63a5a8dcd.ssl.cf1.rackcdn.com/maas_juno_keystone.png)](https://6dbddbf8e5efac8bed3b-f96466f7bd752d7ade3ea7b63a5a8dcd.ssl.cf1.rackcdn.com/maas_juno_keystone.png)

Neutron API during upgrade.

[![maas_juno_neutron](https://6dbddbf8e5efac8bed3b-f96466f7bd752d7ade3ea7b63a5a8dcd.ssl.cf1.rackcdn.com/maas_juno_nuetron.png)](https://6dbddbf8e5efac8bed3b-f96466f7bd752d7ade3ea7b63a5a8dcd.ssl.cf1.rackcdn.com/maas_juno_nuetron.png)

Nova API during upgrade.

[![maas_juno_nova](https://6dbddbf8e5efac8bed3b-f96466f7bd752d7ade3ea7b63a5a8dcd.ssl.cf1.rackcdn.com/maas_juno_nova.png)](https://6dbddbf8e5efac8bed3b-f96466f7bd752d7ade3ea7b63a5a8dcd.ssl.cf1.rackcdn.com/maas_juno_nova.png)

Pinging to the running instance from my laptop during the upgrade. 

<pre><code>--- 192.168.1.221 ping statistics ---
3469 packets transmitted, 3462 packets received, 0.2% packet loss
round-trip min/avg/max/stddev = 1.236/3.223/92.280/2.421 ms</pre></code>

Ping out from the instance to google.com during the upgrade.

<pre><code>--- google.com ping statistics ---
3413 packets transmitted, 3404 packets received, 0% packet loss
round-trip min/avg/max = 26.933/29.034/136.694 ms</pre></code>

And as you can see we're now running '2014.2.1' which is Juno, Dec 5, 2014 code. 

<pre><code>root@compute1:~# nova-manage shell python
Python 2.7.6 (default, Mar 22 2014, 22:59:56)
[GCC 4.8.2] on linux2
Type "help", "copyright", "credits" or "license" for more information.
(InteractiveConsole)
\>>> from nova import version
\>>> version.version_string()
'2014.2.1'</pre></code>

That should be it. This was a very simple example of deploying and upgrading OpenStack into LXC containers using openstack-ansible, all done with editing a couple config files and runnning some playbooks, pretty awesome!

Icehouse docs: http://docs.rackspace.com/rpc/api/v9/bk-rpc-installation/content/rpc-common-front.html
Juno docs: http://docs.rackspace.com/rpc/api/v10/bk-rpc-installation/content/rpc-common-front.html
Upgrade docs: http://docs.rackspace.com/rpc/api/v10/bk-rpc-v10-releasenotes/content/rpc-common-front.html
openstack-ansible: https://launchpad.net/openstack-ansible -- https://github.com/stackforge/os-ansible-deployment
Rackspace Private Cloud powered by OpenStack: http://www.rackspace.com/cloud/private/openstack 