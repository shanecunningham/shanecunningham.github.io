+++
author = "Shane Cunningham"
categories = ["openstack-ansible", "openstack"]
date = 2016-08-19T09:37:00Z
description = ""
draft = false
slug = "deploying-and-customizing-openstack-mitaka-with-openstack-ansible"
tags = ["openstack-ansible", "openstack"]
title = "Deploying and customizing OpenStack Mitaka with openstack-ansible"

+++


This guide will be similar to my other guides on how to install OpenStack using openstack-ansible, LXC containers and some simple YAML configs, but I plan to go a little more in depth with some of the configuration options and customizations that are available. This version will deploy OpenStack Mitaka.

### Overview 

- [Hardware](#hardware)
- [Setting up physical hosts](#setting-up-physical-hosts)
- [Downloading openstack-ansible](#downloading-openstack-ansible)
- [Customizing our OpenStack cloud](#customizing-our-openstack-cloud)
- [Installing OpenStack](#installing-openstack)
- [Configuring Neutron](#configuring-neutron)
- [Testing our cloud](#testing-our-cloud)
- [Next](#next)

### Hardware

**infra01**: 
Lenovo ThinkServer TS140 
Xeon E3-1225 v3 3.2 GHz 
16GB ECC RAM 
2 x 1Gb NICs (em1 and p4p1)
```
IP address for em1:        192.168.88.100  
IP address for br-mgmt:    172.29.236.51  
IP address for br-vxlan:   172.29.240.51  
IP address for br-storage: 172.29.244.51  
IP address for br-vlan:    none  
```

**compute01**: 
Dell PowerEdge T110 II 
Xeon E3-1230 v2 3.3 GHz 
32GB ECC RAM 
2 x 1Gb NICs (em1 and p4p1)
```
IP address for em1:        192.168.88.101  
IP address for br-mgmt:    172.29.236.52  
IP address for br-vxlan:   172.29.240.52  
IP address for br-storage: 172.29.244.52  
IP address for br-vlan:    none
```

<a name="setting-up-physical-hosts"></a>
### Setting up physical hosts

Create an SSH keypair on infra01 since we're going to use that as a deployment host for the environment. Make sure infra01's public SSH key is in /root/.ssh/authorized_keys on all servers, including infra01 itself.

##### Packages

Deployment host

```
# apt-get install aptitude build-essential git ntp ntpdate \
  openssh-server python-dev sudo
```

All other hosts (since we're using infra01 as our deployment host, this is also run on infra01)

```
# apt-get install bridge-utils debootstrap ifenslave ifenslave-2.6 \
  lsof lvm2 ntp ntpdate openssh-server sudo tcpdump vlan
```

##### Setup bridges

I have an 8-port HP ProCurve switch that supports VLANs. In my environment I've tagged the br-mgmt, br-vxlan and br-storage networks.

**br-mgmt** - LXC container management network - VLAN 10  
**br-vxlan** - VXLAN tunnel/overlay network - VLAN 20  
**br-storage** - storage network - VLAN 30  
**br-vlan** - In my home network I don't want my tenant networks to be VLAN tagged (I'll be doing flat, the br-vlan name might be a little confusing), although you could tag these for whatever you want. Later this will hopefully make more sense from an openstack-ansible configuration stand point.

infra01 - [/etc/network/interfaces](https://gist.github.com/shane-c/ca8d0943ff4adf3b8eba32c548681d28)
compute01 - [/etc/network/interfaces](https://gist.github.com/shane-c/2e5695665931cc2bb184fd85c287962a)

Those are single interface bonds. Easier for consistency when I'm using true HA bonds with four interfaces. You can configure these however you need, but the bridges are required except br-storage. 

<a name="downloading-openstack-ansible"></a>
### Downloading openstack-ansible

13.3.10 is the latest tagged release of openstack-ansible at the time of this writing. This will deploy OpenStack Mitaka. 

```
# git clone -b 13.3.10 https://github.com/openstack/openstack-ansible.git /opt/openstack-ansible
# cd /opt/openstack-ansible/
# scripts/bootstrap-ansible.sh
# cp -R /opt/openstack-ansible/etc/openstack_deploy /etc/openstack_deploy
# cp /etc/openstack_deploy/openstack_user_config.yml.example /etc/openstack_deploy/openstack_user_config.yml
```

openstack\_user\_config.yml is our main configuration file that describes our OpenStack cloud. I've included my example two node [openstack\_user\_config.yml](https://gist.github.com/shane-c/066a0cdeaf7927ea70be01d2219be461) for this guide.

<a name="customizing-our-openstack-cloud"></a>
### Customizing our OpenStack cloud

**Security** - Set [security hardening](http://docs.openstack.org/developer/openstack-ansible/install-guide/configure-initial.html#security-hardening) to true.

```
# echo "apply_security_hardening: true" >> /etc/openstack_deploy/user_variables.yml
``` 

**Affinity** - In this two node example, we use something called affinity in openstack\_user\_config.yml to create more than one container for a specific service, mainly used in all-in-one examples to test clustering. This gives us the ability to run a three node Galera cluster on a single host. In a production environment, you probably want to put your three containers on different physical hosts, maybe even in combination with affinity for added scalability. 

**Scaling** - One area openstack-ansible excels is its ability to easily scale to hundreds of nodes, all described in simple to understand YAML in openstack\_user\_config.yml. Here's a more real world example: 

I have 3 physical servers I want to manage my clustering services such as Galera and RabbitMQ. I have 3 different physical servers I want dedicated to running my OpenStack API services. I have 25 compute nodes and 5 cinder nodes with a volume group 'cinder-volumes' configured as my LVM backend. 1 physical server for my logging node and my 6 infrastructure nodes as my network nodes. My internal/external VIPs are VIPs managed on a physical F5 (outside this guide). My external VIP is a FQDN. My tenant VLANs will be 110 through 120 and I'll be creating neutron VLAN networks. 
 
My openstack\_user\_config.yml file might look something like [this](https://gist.github.com/shane-c/6784cc608557f157bd8a6ad695a8ee1f). 

**openstack\_user\_config.yml** - More details

```
cidr_networks:
  container: 172.29.236.0/22
  tunnel: 172.29.240.0/22
  storage: 172.29.244.0/22
```

cidr_networks - /22 networks where our containers, tunnel/overlay and storage network will build from. These can be whatever you need as long as they are large enough and correspond to the IPs you configure on your br-mgmt (container), br-vxlan (tunnel/overlay) and br-storage (storage) interfaces on each host.

```
used_ips:
  - "172.29.236.1,172.29.236.255"
  - "172.29.240.1,172.29.240.255"
  - "172.29.244.1,172.29.244.255"
```

used_ips - Here we define some IPs that we do not want openstack-ansible to use. These IPs are already being used on our hosts, other devices or we just want to reserve these for future expansion. When openstack-ansible creates our containers it automatically assigns them an IP out of the container network. Our internal VIP and physical hosts already have IPs out of these ranges so we put these in used\_ips to avoid duplicate IP problems. Out of a /22 network we reserve the first 255 addresses. Based on your network you might need to add more ranges or even single IPs for network gear etc. 

```
global_overrides:
  internal_lb_vip_address: 172.29.236.51
  external_lb_vip_address: openstack.cunninghamshane.com
  tunnel_bridge: "br-vxlan"
  management_bridge: "br-mgmt"
```

global_overrides - Most important are the internal and external VIPs. These will be our OpenStack internal/public/admin endpoints all services and clients will be using. We want our internal VIP to be an IP out of the br-mgmt network so all hosts/containers can access it. Our external VIP can be a true public IP or a private IP that you have access to in your larger network. 

```
  provider_networks:
    - network:
        container_bridge: "br-mgmt"
        container_type: "veth"
        container_interface: "eth1"
        ip_from_q: "container"
        type: "raw"
        group_binds:
          - all_containers
          - hosts
        is_container_address: true
        is_ssh_address: true
    - network:
        container_bridge: "br-vxlan"
        container_type: "veth"
        container_interface: "eth10"
        ip_from_q: "tunnel"
        type: "vxlan"
        range: "1:1000"
        net_name: "vxlan"
        group_binds:
          - neutron_linuxbridge_agent
    - network:
        container_bridge: "br-vlan"
        container_type: "veth"
        container_interface: "eth11"
        type: "flat"
        net_name: "flat"
        group_binds:
          - neutron_linuxbridge_agent
    - network:
        container_bridge: "br-storage"
        container_type: "veth"
        container_interface: "eth2"
        ip_from_q: "storage"
        type: "raw"
        group_binds:
          - glance_api
          - cinder_api
          - cinder_volume
          - nova_compute
```

provider\_networks - This is where you can modify how you want your OpenStack networking to be implemented. The group_binds correspond to Ansible groups so it knows which containers need which networks. 

The first network in this section tells openstack-ansible to give an eth1 interface to all our LXC containers out of the "container" network we defined in the cidr_networks section above. This will be attached to our br-mgmt interface on our hosts. 

The second network is for our tenants to use VXLAN networks. It will give our neutron agents container an eth10 interface. 

The third network is pretty important and there are a few ways you can set this up. For my use, even though this network is connecting to our br-vlan, I want it to be a flat:flat network. Another way you can do this in a production environment is to use VLANs. Say I wanted 20 tenant VLAN networks, the VLANs my network engineers have given me are 110 through 120 and 440 through 450.  

```
    - network:
        container_bridge: "br-vlan"
        container_type: "veth"
        container_interface: "eth11"
        type: "vlan"
        range: "110:120,440:450"
        net_name: "vlan"
        group_binds:
          - neutron_linuxbridge_agent
```

When I create my tenant VLAN networks in neutron I can create them like this:

```
# neutron net-create --provider:physical_network=vlan \
--provider:network_type=vlan --provider:segmentation_id=110 --shared DEV_110_NETWORK
```

The last network is our storage network which will be eth2 for the containers that require this interface. When doing swift or ceph, you want to add "- swift\_proxy" or "- mons" to the list of containers that receive this interface in the group_binds section.

**Environment passwords** - Generating passwords can be done with a password generator Python script.

```
# cd /opt/openstack-ansible/scripts/
# python pw-token-gen.py --file /etc/openstack_deploy/user_secrets.yml
```

**Overriding OpenStack .conf files** - You can literally customize OpenStack however you want with the override functionality built into openstack-ansible. There are many built in defaults in the playbooks that we can override in our user\_variables.yml file. For example, I want to increase the Nova CPU allocation ratio from the default of 2.0 to 4.0. 

```
# echo "nova_cpu_allocation_ratio: 4.0" >> /etc/openstack_deploy/user_variables.yml
```

However, there's no way every .conf variable available in every OpenStack service can be added to the Ansible roles/playbooks as one line overrides. So, an alternative was created to allow the deployer to modify any part of OpenStack's .conf files. Now let's say I want Nova to use LVM backends for my instances instead of the default file system /var/lib/nova location it normally puts instances.

```
cat <<EOF >> /etc/openstack_deploy/user_variables.yml
nova_nova_conf_overrides:
  libvirt:
    images_type: lvm
    images_volume_group: nova
EOF
``` 

This will edit the libvirt section of the nova.conf file with the following.

```
...
[libvirt]
images_type = lvm
images_volume_group = nova
...
```

And produce instances inside the nova volume group on the compute nodes.

```
root@compute01:~# lvs nova
  LV                                        VG   Attr      LSize  Pool Origin Data%  Move Log Copy%  Convert
  328f4f62-a3b6-4af9-af5c-58eaafce2cd1_disk nova -wi-ao--- 20.00g
  d73c82b1-c77f-4060-8f48-82d6383e4264_disk nova -wi-ao--- 20.00g
```

[Here's](http://docs.openstack.org/developer/openstack-ansible/install-guide/configure-openstack.html#overriding-conf-files) a list of all .conf files currently available with this method. 

I also want to enable Neutron LBaaS v2, so we can easily do that with the following configuration additions.

```
cat <<EOF >> /etc/openstack_deploy/user_variables.yml
neutron_plugin_base:
  - router
  - metering
  - neutron_lbaas.services.loadbalancer.plugin.LoadBalancerPluginv2
EOF
```

Now we enable the LBaaS Horizon panel.

```
# echo "horizon_enable_neutron_lbaas: true" >> /etc/openstack_deploy/user_variables.yml
```

Something else worth noting on customizations, you can also put these in openstack\_user\_config.yml on a per host level.

```
...
  compute01:
    ip: 10.240.0.1
    host_vars:
      nova_nova_conf_overrides:
        DEFAULT:
          force_config_drive: false
  compute02:
    ip: 10.240.0.2
    host_vars:
      nova_nova_conf_overrides:
        DEFAULT:
          use_cow_images: false
          config_drive_format: vfat
          force_config_drive: false
        libvirt:
          iscsi_use_multipath: true
    container_vars:
      nova_libvirt_images_rbd_pool: vms
...
```

<a name="installing-openstack"></a>
### Installing OpenStack

```
# cd /opt/openstack-ansible/playbooks/
# openstack-ansible setup-hosts.yml
# openstack-ansible haproxy-install.yml
# openstack-ansible setup-infrastructure.yml
# openstack-ansible setup-openstack.yml
```

When I ran through this on my home lab each playbook finished with 0 errors and I had a working Mitaka install. 

<a name="configuring-neutron"></a>
### Configuring Neutron

This is my go to neutron setup for my home lab. There are so many ways you can configure OpenStack and Neutron, but seeing this simplicity might help in getting familiar with it. My instances build from the 'private-net' network which is attached to the inside of my neutron router 'core-router'. My 'external-net' network is attached to the outside of my neutron router and where I create floating IPs used for SSH access from my homes 192.168.88.0/24 network. The neutron router has SNAT enabled for Internet access for my instances on the 'private-net'. 

```
# neutron router-create core-router  
# neutron net-create private-net --shared  
# neutron subnet-create private-net 10.0.0.0/24 --name private-subnet  
# neutron router-interface-add core-router private-subnet  
# neutron net-create external-net --router:external --provider:physical_network flat --provider:network_type flat  
# neutron subnet-create --name external-subnet --allocation-pool start=192.168.88.220,end=192.168.88.240 --disable-dhcp --gateway 192.168.88.1 external-net 192.168.88.0/24  
# neutron router-gateway-set core-router external-net
```

<a name="testing-our-cloud"></a>
### Testing our cloud

First make sure our namespace can reach the Internet.

```
root@infra01:/opt/openstack-ansible/playbooks# lxc-attach -n $(lxc-ls | grep neutron_agents)

root@infra01-neutron-agents-container-a5367dfb:/# ip netns
qdhcp-56e2c10b-b003-40fa-bbd5-b4d39cfb7cdd
qrouter-d912cb40-dd6b-4861-90de-816c125e562a

root@infra01-neutron-agents-container-a5367dfb:/# ip netns e qdhcp-56e2c10b-b003-40fa-bbd5-b4d39cfb7cdd ping -c3 8.8.8.8
PING 8.8.8.8 (8.8.8.8) 56(84) bytes of data.
64 bytes from 8.8.8.8: icmp_seq=1 ttl=54 time=23.4 ms
64 bytes from 8.8.8.8: icmp_seq=2 ttl=54 time=22.8 ms
64 bytes from 8.8.8.8: icmp_seq=3 ttl=54 time=21.4 ms

--- 8.8.8.8 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2003ms
rtt min/avg/max/mdev = 21.431/22.561/23.414/0.850 ms
```

That looks good. Let's spin up two instances.

```
root@infra01:/opt/openstack-ansible/playbooks# lxc-attach -n $(lxc-ls | grep utility)

root@infra01-utility-container-0887f189:/# . ~/openrc

root@infra01-utility-container-0887f189:/# for i in web1 web2; do nova boot --flavor m1.tiny --image 1b2b1e2b-1d8e-4174-b850-a22e2f092806 --security-group default --nic net-id=56e2c10b-b003-40fa-bbd5-b4d39cfb7cdd --key-name shane $i; done

root@infra01-utility-container-0887f189:/# nova list
+--------------------------------------+------+--------+------------+-------------+----------------------+
| ID                                   | Name | Status | Task State | Power State | Networks             |
+--------------------------------------+------+--------+------------+-------------+----------------------+
| 328f4f62-a3b6-4af9-af5c-58eaafce2cd1 | web1 | ACTIVE | -          | Running     | private-net=10.0.0.4 |
| d73c82b1-c77f-4060-8f48-82d6383e4264 | web2 | ACTIVE | -          | Running     | private-net=10.0.0.5 |
+--------------------------------------+------+--------+------------+-------------+----------------------+
```

I installed a web server on those to test out our LBaaS V2 functionality. This is pretty much straight from the LBaaS V2 examples. Our OpenStack binaries are in Python venvs, so to access them we source the activate file.

```
root@infra01-neutron-agents-container-a5367dfb:/# . /openstack/venvs/neutron-13.3.0/bin/activate

(neutron-13.3.0) root@infra01-neutron-agents-container-a5367dfb:/# . ~/openrc

(neutron-13.3.0) root@infra01-neutron-agents-container-a5367dfb:/# neutron lbaas-loadbalancer-create --name test-lb ff71eb35-c5bf-4718-84b0-2a5053f28912

Created a new loadbalancer:
+---------------------+--------------------------------------+
| Field               | Value                                |
+---------------------+--------------------------------------+
| admin_state_up      | True                                 |
| description         |                                      |
| id                  | 27108f90-2cdd-49b8-be27-96a6b8dc7211 |
| listeners           |                                      |
| name                | test-lb                              |
| operating_status    | OFFLINE                              |
| pools               |                                      |
| provider            | haproxy                              |
| provisioning_status | PENDING_CREATE                       |
| tenant_id           | 64f3aa02de1c4a4eb099c552fe5fc1d3     |
| vip_address         | 10.0.0.6                             |
| vip_port_id         | 69f42a59-573f-4032-888e-2d06e6ba1255 |
| vip_subnet_id       | ff71eb35-c5bf-4718-84b0-2a5053f28912 |
+---------------------+--------------------------------------+

(neutron-13.3.0) root@infra01-neutron-agents-container-a5367dfb:/# neutron lbaas-loadbalancer-show test-lb
+---------------------+--------------------------------------+
| Field               | Value                                |
+---------------------+--------------------------------------+
| admin_state_up      | True                                 |
| description         |                                      |
| id                  | 27108f90-2cdd-49b8-be27-96a6b8dc7211 |
| listeners           |                                      |
| name                | test-lb                              |
| operating_status    | ONLINE                               |
| pools               |                                      |
| provider            | haproxy                              |
| provisioning_status | ACTIVE                               |
| tenant_id           | 64f3aa02de1c4a4eb099c552fe5fc1d3     |
| vip_address         | 10.0.0.6                             |
| vip_port_id         | 69f42a59-573f-4032-888e-2d06e6ba1255 |
| vip_subnet_id       | ff71eb35-c5bf-4718-84b0-2a5053f28912 |
+---------------------+--------------------------------------+
```

Create an 'lbaas' security group.

```
# neutron security-group-create lbaas

# neutron security-group-rule-create \
  --direction ingress \
  --protocol tcp \
  --port-range-min 80 \
  --port-range-max 80 \
  --remote-ip-prefix 0.0.0.0/0 \
  lbaas

# neutron security-group-rule-create \
  --direction ingress \
  --protocol tcp \
  --port-range-min 443 \
  --port-range-max 443 \
  --remote-ip-prefix 0.0.0.0/0 \
  lbaas

# neutron security-group-rule-create \
  --direction ingress \
  --protocol icmp \
  lbaas

# neutron port-update \
  --security-group lbaas \
  69f42a59-573f-4032-888e-2d06e6ba1255
```

Create listener and test ping.

```
# neutron lbaas-listener-create \
  --name test-lb-http \
  --loadbalancer test-lb \
  --protocol HTTP \
  --protocol-port 80

Created a new listener:
+---------------------------+------------------------------------------------+
| Field                     | Value                                          |
+---------------------------+------------------------------------------------+
| admin_state_up            | True                                           |
| connection_limit          | -1                                             |
| default_pool_id           |                                                |
| default_tls_container_ref |                                                |
| description               |                                                |
| id                        | 4a237736-436e-42a5-ba93-d3a5be61768f           |
| loadbalancers             | {"id": "27108f90-2cdd-49b8-be27-96a6b8dc7211"} |
| name                      | test-lb-http                                   |
| protocol                  | HTTP                                           |
| protocol_port             | 80                                             |
| sni_container_refs        |                                                |
| tenant_id                 | 64f3aa02de1c4a4eb099c552fe5fc1d3               |
+---------------------------+------------------------------------------------+

(neutron-13.3.0) root@infra01-neutron-agents-container-a5367dfb:/# ip netns e qrouter-d912cb40-dd6b-4861-90de-816c125e562a ping -c3 10.0.0.6

PING 10.0.0.6 (10.0.0.6) 56(84) bytes of data.
64 bytes from 10.0.0.6: icmp_seq=1 ttl=64 time=0.094 ms
64 bytes from 10.0.0.6: icmp_seq=2 ttl=64 time=0.058 ms
64 bytes from 10.0.0.6: icmp_seq=3 ttl=64 time=0.063 ms

--- 10.0.0.6 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 1999ms
rtt min/avg/max/mdev = 0.058/0.071/0.094/0.018 ms

(neutron-13.3.0) root@infra01-neutron-agents-container-a5367dfb:/# ip netns e qrouter-d912cb40-dd6b-4861-90de-816c125e562a curl 10.0.0.6

<html><body><h1>503 Service Unavailable</h1>
No server is available to handle this request.
</body></html>
```

As expected, curling the IP doesn't yet work because we haven't put any backends in place. My web servers are 10.0.0.4 and 10.0.0.5.

```
# neutron lbaas-pool-create \
  --name test-lb-pool-http \
  --lb-algorithm ROUND_ROBIN \
  --listener test-lb-http \
  --protocol HTTP

# neutron lbaas-member-create \
  --subnet private-subnet \
  --address 10.0.0.4 \
  --protocol-port 80 \
  test-lb-pool-http
  
# neutron lbaas-member-create \
  --subnet private-subnet \
  --address 10.0.0.5 \
  --protocol-port 80 \
  test-lb-pool-http
```

Now curl works. Woot.

```
(neutron-13.3.0) root@infra01-neutron-agents-container-a5367dfb:/# for i in {1..10}; do ip netns e qrouter-d912cb40-dd6b-4861-90de-816c125e562a curl 10.0.0.6; done
WEB 2
WEB 1
WEB 2
WEB 1
WEB 2
WEB 1
WEB 2
WEB 1
WEB 2
WEB 1
```

Assign a floating IP from our external-net, and we can curl from outside the namespace.

```
[09:05]shane@work~$ for i in {1..10}; do curl 192.168.88.221; done
WEB 2
WEB 1
WEB 2
WEB 1
WEB 2
WEB 1
WEB 2
WEB 1
WEB 2
WEB 1
```

### Next

openstack-ansible (and other project names it's been called previously) has seen tremendous growth since it's early start with Icehouse to where it is now with OpenStack Mitaka. The Liberty and Mitaka releases are some of the most mature methods for deploying OpenStack with ease, customization options and at scale. I've been trying (and failing) to install OpenStack with different methods since Grizzly, and it's hard to express how simple and scalable openstack-ansible has made deploying OpenStack. 

With success comes interests and I'm extremely happy to see a vibrant community pop up around this project. New features and new OpenStack projects are beginning to be added more quickly. Some of my favorites are a focus on security (openstack-ansible-security) role and in the Newton release, being able to deploy the nova-lxd driver, multiple CPU architecture support and installing OpenStack Ironic and Magnum projects. I can't wait for these and more projects to be integrated into openstack-ansible so I can show how easy it's become to install OpenStack.

**More info**

IRC: #openstack-ansible on freenode
Launchpad: [https://launchpad.net/openstack-ansible](https://launchpad.net/openstack-ansible)
GitHub: [https://github.com/openstack/openstack-ansible/](https://github.com/openstack/openstack-ansible/)
Documentation: [http://docs.openstack.org/developer/openstack-ansible/install-guide/index.html](http://docs.openstack.org/developer/openstack-ansible/install-guide/index.html)