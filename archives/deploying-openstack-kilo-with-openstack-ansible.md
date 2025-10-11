+++
author = "Shane Cunningham"
categories = ["openstack-ansible", "openstack"]
date = 2015-10-18T04:43:18Z
description = ""
draft = false
slug = "deploying-openstack-kilo-with-openstack-ansible"
tags = ["openstack-ansible", "openstack"]
title = "Deploying OpenStack Kilo with openstack-ansible"

+++


[openstack-ansible](https://github.com/openstack/openstack-ansible) is an open source project started by [Rackspace](http://www.rackspace.com/) to make deploying large OpenStack clouds easier. You describe your OpenStack environment in configuration files and openstack-ansible uses Ansible to lay down OpenStack from source and runs most OpenStack services inside LXC containers. 

The Kilo version of openstack-ansible was released last month. With that release came some significant changes from the Icehouse/Juno openstack-ansible code. This started as a Rackspace project, the Icehouse and Juno versions have  Rackspace specific bits inside. Like a playbook to make it easier for our RPC support team to interact with an environment or our monitoring as a service code that was bundled in with openstack-ansible. However, our awesome team saw an opportunity to turn this into a community driven official OpenStack project. They removed all Rackspace specific bits so that openstack-ansible can be used by anyone with no reference to Rackspace or RPC. 

So there are now two projects we can use. 

- [openstack-ansible](https://github.com/openstack/openstack-ansible) - only OpenStack

- [rpc-openstack](https://github.com/rcbops/rpc-openstack) - the above plus Rackspace added enhancenments like a full ELK stack for logging and monitoring as a service that can hook into the Rackspace Cloud Monitoring to monitor hosts/containers and OpenStack services

In this example I want ELK and monitoring as a serivce so I will deploy rpc-openstack. I've used this setup for a few examples. 

**infra01**:
Lenovo ThinkServer TS140 
Xeon E3-1225 v3 3.2 GHz 
8GB ECC RAM 
2 x 1Gb NICs

```
IP address for em1:        192.168.1.100
IP address for br-mgmt:    172.29.236.51
IP address for br-vxlan:   172.29.240.51
IP address for br-storage: 172.29.244.51
IP address for br-vlan:    none
```

**compute01**:
Dell Poweredge T110II 
Xeon E3-1230 v2 3.3 GHz 
32GB ECC RAM 
2 x 1Gb NICs

```
IP address for em1:        192.168.1.101
IP address for br-mgmt:    172.29.236.52
IP address for br-vxlan:   172.29.240.52
IP address for br-storage: 172.29.244.52
IP address for br-vlan:    none
```

**Packages required**
```
# deployment host
apt-get install -y aptitude build-essential git ntp ntpdate openssh-server python-dev sudo
   
# target hosts
apt-get install -y bridge-utils debootstrap ifenslave ifenslave-2.6 lsof lvm2 ntp ntpdate openssh-server sudo tcpdump vlan
```

**Networking**

For this example I'm not using VLANs so I'll setup the bridges with VXLAN interfaces.

[/etc/network/interfaces](https://gist.github.com/shane-c/28afa426358406d59fbb)

[/etc/network/interfaces/openstack-interfaces.cfg](https://gist.github.com/shane-c/1f3600c6f3099e6b4b60)

Just remember to increment your other nodes for the last octet. After a reboot, you should be able to ping back to infra01 on all three bridges. 

```
root@compute01:~# for i in 172.29.236.51 172.29.240.51 172.29.244.51; do fping $i; done
172.29.236.51 is alive
172.29.240.51 is alive
172.29.244.51 is alive
```

Now that we have our networking set we can download the openstack-ansible/rpc-openstack code and configure our deployment. The following happens on the deployment host, this can be a dedicated host but in this example I'll use infra01 as my deployment host. 

```
# git clone -b r11.1.6 --recursive https://github.com/rcbops/rpc-openstack /opt/rpc-openstack
```

Here we copy all the configs into /etc/openstack_deploy/.

```
# cp -r /opt/rpc-openstack/openstack-ansible/etc/openstack_deploy /etc/
```

These are Rackspace configs, mainly for MaaS.

```
# cp /opt/rpc-openstack/rpcd/etc/openstack_deploy/*extras* /etc/openstack_deploy/
```

Prepare deployment host for Ansible.

```
# ./openstack-ansible/scripts/bootstrap-ansible.sh
# pip install -r /opt/rpc-openstack/openstack-ansible/requirements.txt
```

The following commands generate random passwords and copy a template openstack\_user_config.yml file, which is the file where we describe our OpenStack environment. 

```
# /opt/rpc-openstack/scripts/update-yaml.py /etc/openstack_deploy/user_variables.yml /opt/rpc-openstack/rpcd/etc/openstack_deploy/user_variables.yml
# cp /etc/openstack_deploy/openstack_user_config.yml.example /etc/openstack_deploy/openstack_user_config.yml
# cd /opt/rpc-openstack/openstack-ansible/scripts
# python pw-token-gen.py --file /etc/openstack_deploy/user_secrets.yml
# python pw-token-gen.py --file /etc/openstack_deploy/user_extras_secrets.yml
```

**Template openstack\_user\_config.yml** - [/etc/openstack_deploy/openstack\_user\_config.yml](https://gist.github.com/shane-c/b9b151240f61e91427e2)

You can see in the config file how you could add nodes if you had a larger deployment. This method of deploying OpenStack is designed for large deployments with multiple compute, cinder and swift nodes. For example, you can add more compute hosts, just like you can for all services. 

```
compute_hosts:
  compute01:
    ip: 192.168.1.110
  compute02:
    ip: 192.168.1.111
  compute03:
    ip: 192.168.1.112
```

Notice even though we only have one infrastructure node, we can use the affinity feature to cluster these services on one host for testing. So we have a real three node Galera and RabbitMQ clusters. Our tenants will create networks with VXLAN and our external provider network we will create will be flat/flat. You could also set this up for VLANs if your networking infrastructure supports those. I'll be doing a guide soon for VLANs once I get my Mikrotik router up and running.

**Glance Config** - Uses Rackspace Cloud Files for Glance backend storage. Can also set to file to store in the glance container. Make sure the `glance_swift_store_container: rpc-images` container exists in the region you specify. 

```
root@infra01:/opt/rpc-openstack/openstack-ansible/playbooks# grep glance /etc/openstack_deploy/user_variables.yml

glance_ceilometer_enabled: false
glance_default_store: swift
glance_notification_driver: noop
glance_swift_store_endpoint_type: publicURL
glance_swift_store_region: DFW
glance_swift_store_container: rpc-images
glance_swift_store_auth_address: '{{ rackspace_cloud_auth_url }}'
glance_swift_store_key: '{{ rackspace_cloud_password }}'
glance_swift_store_user: '{{ rackspace_cloud_tenant_id }}:{{ rackspace_cloud_username }}'
```


**MaaS Config** - For MaaS, create an entity at https://intelligence.rackspace.com/cloud/entities for each of your hosts, the label has to match your servers hostnames. I created infra01 and compute01. The MaaS playbooks will install the monitoring agent to those hosts and setup the checks and alarms. For maas\_notification\_plan, grab the ID from https://intelligence.rackspace.com/cloud/notification-plans, either use the default or create a new one. My notification plan does both email and SMS alerts. 

<img src=https://6dbddbf8e5efac8bed3b-f96466f7bd752d7ade3ea7b63a5a8dcd.ssl.cf1.rackcdn.com/maas_email.png>

```
root@infra01:/opt/rpc-openstack/openstack-ansible/playbooks# grep -v '^#' /etc/openstack_deploy/user_extras_variables.yml| grep maas

maas_auth_method: password
maas_tenant_id: "{{ rackspace_cloud_tenant_id }}"
maas_auth_url: "{{ rackspace_cloud_auth_url }}"
maas_username: "{{ rackspace_cloud_username }}"
maas_api_key: "{{ rackspace_cloud_api_key }}"
maas_auth_token: some_token
maas_notification_plan: npQgbGTdDJ
maas_target_alias: public0_v4
maas_scheme: http
maas_alarm_local_consecutive_count: 5
maas_alarm_remote_consecutive_count: 2
maas_excluded_devices: ['/dev/sr0']
maas_filesystem_warning_threshold: 80.0
maas_filesystem_critical_threshold: 90.0
```

**Rackspace credentials** - As you can probably tell, if hooking Glance and MaaS into Rackspace you'll need to enter your cloud credentials. 

```
root@infra01:/opt/rpc-openstack/openstack-ansible/playbooks# grep '^rackspace' /etc/openstack_deploy/user_extras_variables.yml

rackspace_cloud_auth_url: https://identity.api.rackspacecloud.com/v2.0
rackspace_cloud_tenant_id: 
rackspace_cloud_username: 
rackspace_cloud_password:
rackspace_cloud_api_key:
```

**ELK Stack** - If you want the ELK stack created for logging then copy the following environment files. 

```
# cp /opt/rpc-openstack/rpcd/etc/openstack_deploy/env.d/elasticsearch.yml /etc/openstack_deploy/env.d
# cp /opt/rpc-openstack/rpcd/etc/openstack_deploy/env.d/kibana.yml /etc/openstack_deploy/env.d
# cp /opt/rpc-openstack/rpcd/etc/openstack_deploy/env.d/logstash.yml /etc/openstack_deploy/env.d
```

Now that we described our environment we can start running playbooks!

**setup-hosts.yml** - the bootstrap-ansible.sh script we ran earlier created a wrapper for ansible-playbook. We can use the openstack-ansible command to run playbooks, it will automatically include all config files from /etc/openstack_deploy/.

```
# cd /opt/rpc-openstack/openstack-ansible/playbooks
# openstack-ansible setup-hosts.yml

PLAY RECAP ********************************************************************
compute01                  : ok=52   changed=13   unreachable=0    failed=0
infra01                    : ok=52   changed=13   unreachable=0    failed=0
infra01_cinder_api_container-97bb86b8 : ok=14   changed=13   unreachable=0    failed=0
infra01_cinder_scheduler_container-45595f8a : ok=14   changed=13   unreachable=0    failed=0
infra01_galera_container-285a0792 : ok=14   changed=13   unreachable=0    failed=0
infra01_galera_container-2c14a508 : ok=14   changed=13   unreachable=0    failed=0
infra01_galera_container-dea4ed6c : ok=14   changed=13   unreachable=0    failed=0
infra01_glance_container-df8f6782 : ok=14   changed=13   unreachable=0    failed=0
infra01_heat_apis_container-429e480d : ok=14   changed=13   unreachable=0    failed=0
infra01_heat_engine_container-09eb5ad5 : ok=14   changed=13   unreachable=0    failed=0
infra01_horizon_container-422f2991 : ok=14   changed=13   unreachable=0    failed=0
infra01_horizon_container-f3df59bf : ok=14   changed=13   unreachable=0    failed=0
infra01_keystone_container-0d7a4d0c : ok=14   changed=13   unreachable=0    failed=0
infra01_keystone_container-2d73e396 : ok=14   changed=13   unreachable=0    failed=0
infra01_memcached_container-7df01f14 : ok=14   changed=13   unreachable=0    failed=0
infra01_neutron_agents_container-80cc6d88 : ok=14   changed=13   unreachable=0    failed=0
infra01_neutron_server_container-2336cf92 : ok=14   changed=13   unreachable=0    failed=0
infra01_nova_api_metadata_container-e444e98d : ok=14   changed=13   unreachable=0    failed=0
infra01_nova_api_os_compute_container-ca331872 : ok=14   changed=13   unreachable=0    failed=0
infra01_nova_cert_container-6f5a612d : ok=14   changed=13   unreachable=0    failed=0
infra01_nova_conductor_container-3891b9ad : ok=14   changed=13   unreachable=0    failed=0
infra01_nova_console_container-0a481d09 : ok=14   changed=13   unreachable=0    failed=0
infra01_nova_scheduler_container-638e2856 : ok=14   changed=13   unreachable=0    failed=0
infra01_rabbit_mq_container-19de8a9a : ok=14   changed=13   unreachable=0    failed=0
infra01_rabbit_mq_container-db8160a0 : ok=14   changed=13   unreachable=0    failed=0
infra01_rabbit_mq_container-ffa9d583 : ok=14   changed=13   unreachable=0    failed=0
infra01_repo_container-64a71607 : ok=14   changed=13   unreachable=0    failed=0
infra01_repo_container-cb57e740 : ok=14   changed=13   unreachable=0    failed=0
infra01_rsyslog_container-95b449dc : ok=14   changed=13   unreachable=0    failed=0
infra01_utility_container-0276d803 : ok=14   changed=13   unreachable=0    failed=0
```

**haproxy-install.yml** - If you're not using a physical load balancer we can use HAProxy. It will create HAProxy configs based on our containers/IPs and load balance services.

```
# openstack-ansible haproxy-install.yml
PLAY RECAP ********************************************************************
infra01                    : ok=14   changed=0    unreachable=0    failed=0
```

**setup-infrastructure.yml** - Galera, RabbitMQ, Memcached install

```
# openstack-ansible setup-infrastructure.yml

PLAY RECAP ********************************************************************
infra01_galera_container-285a0792 : ok=56   changed=35   unreachable=0    failed=0
infra01_galera_container-2c14a508 : ok=56   changed=35   unreachable=0    failed=0
infra01_galera_container-dea4ed6c : ok=56   changed=36   unreachable=0    failed=0
infra01_memcached_container-7df01f14 : ok=9    changed=6    unreachable=0    failed=0
infra01_rabbit_mq_container-19de8a9a : ok=52   changed=38   unreachable=0    failed=0
infra01_rabbit_mq_container-db8160a0 : ok=52   changed=38   unreachable=0    failed=0
infra01_rabbit_mq_container-ffa9d583 : ok=51   changed=37   unreachable=0    failed=0
infra01_repo_container-64a71607 : ok=47   changed=35   unreachable=0    failed=0
infra01_repo_container-cb57e740 : ok=45   changed=32   unreachable=0    failed=0
infra01_rsyslog_container-95b449dc : ok=15   changed=10   unreachable=0    failed=0
infra01_utility_container-0276d803 : ok=31   changed=18   unreachable=0    failed=0
```

**setup-openstack.yml** - OpenStack Kilo install

```
# openstack-ansible setup-openstack.yml

PLAY RECAP ********************************************************************
compute01                  : ok=203  changed=89   unreachable=0    failed=0
infra01_cinder_api_container-97bb86b8 : ok=74   changed=47   unreachable=0    failed=0
infra01_cinder_scheduler_container-45595f8a : ok=64   changed=40   unreachable=0    failed=0
infra01_glance_container-df8f6782 : ok=76   changed=49   unreachable=0    failed=0
infra01_heat_apis_container-429e480d : ok=76   changed=53   unreachable=0    failed=0
infra01_heat_engine_container-09eb5ad5 : ok=53   changed=37   unreachable=0    failed=0
infra01_horizon_container-422f2991 : ok=60   changed=42   unreachable=0    failed=0
infra01_horizon_container-f3df59bf : ok=64   changed=46   unreachable=0    failed=0
infra01_keystone_container-0d7a4d0c : ok=101  changed=55   unreachable=0    failed=0
infra01_keystone_container-2d73e396 : ok=86   changed=44   unreachable=0    failed=0
infra01_neutron_agents_container-80cc6d88 : ok=85   changed=58   unreachable=0    failed=0
infra01_neutron_server_container-2336cf92 : ok=64   changed=44   unreachable=0    failed=0
infra01_nova_api_metadata_container-e444e98d : ok=64   changed=39   unreachable=0    failed=0
infra01_nova_api_os_compute_container-ca331872 : ok=74   changed=47   unreachable=0    failed=0
infra01_nova_cert_container-6f5a612d : ok=64   changed=38   unreachable=0    failed=0
infra01_nova_conductor_container-3891b9ad : ok=64   changed=39   unreachable=0    failed=0
infra01_nova_console_container-0a481d09 : ok=69   changed=41   unreachable=0    failed=0
infra01_nova_scheduler_container-638e2856 : ok=64   changed=39   unreachable=0    failed=0
```

Whoo! OpenStack should be installed! If you ran into any errors I usually rerun the playbook a couple times and you can add -vvv for additional debugging. 

<a href=https://6dbddbf8e5efac8bed3b-f96466f7bd752d7ade3ea7b63a5a8dcd.ssl.cf1.rackcdn.com/kilo_dash_services.png><img width=200 height=200 src=https://6dbddbf8e5efac8bed3b-f96466f7bd752d7ade3ea7b63a5a8dcd.ssl.cf1.rackcdn.com/kilo_dash_services.png></a><a href=https://6dbddbf8e5efac8bed3b-f96466f7bd752d7ade3ea7b63a5a8dcd.ssl.cf1.rackcdn.com/kilo_dash_compute.png><img width=200 height=200 src=https://6dbddbf8e5efac8bed3b-f96466f7bd752d7ade3ea7b63a5a8dcd.ssl.cf1.rackcdn.com/kilo_dash_compute.png></a><a href=https://6dbddbf8e5efac8bed3b-f96466f7bd752d7ade3ea7b63a5a8dcd.ssl.cf1.rackcdn.com/kilo_dash_network.png><img width=200 height=200 src=https://6dbddbf8e5efac8bed3b-f96466f7bd752d7ade3ea7b63a5a8dcd.ssl.cf1.rackcdn.com/kilo_dash_network.png></a><a href=https://6dbddbf8e5efac8bed3b-f96466f7bd752d7ade3ea7b63a5a8dcd.ssl.cf1.rackcdn.com/kilo_dash_block.png><img width=200 height=200 src=https://6dbddbf8e5efac8bed3b-f96466f7bd752d7ade3ea7b63a5a8dcd.ssl.cf1.rackcdn.com/kilo_dash_block.png></a><a href=https://6dbddbf8e5efac8bed3b-f96466f7bd752d7ade3ea7b63a5a8dcd.ssl.cf1.rackcdn.com/kilo_dash_orch.png><img width=200 height=200 src=https://6dbddbf8e5efac8bed3b-f96466f7bd752d7ade3ea7b63a5a8dcd.ssl.cf1.rackcdn.com/kilo_dash_orch.png></a>

Here's some various commands ran on the environment after a successfull Kilo deployment.

```
root@infra01:~# free -m
             total       used       free     shared    buffers     cached
Mem:          7779       7272        507          5        147        949
-/+ buffers/cache:       6176       1603
Swap:         7983        165       7818

root@infra01:~# uptime
 23:07:54 up 23:47,  2 users,  load average: 0.60, 1.11, 0.98

root@compute01:~# nova-manage shell python
No handlers could be found for logger "oslo_config.cfg"
Python 2.7.6 (default, Jun 22 2015, 17:58:13)
[GCC 4.8.2] on linux2
Type "help", "copyright", "credits" or "license" for more information.
(InteractiveConsole)
>>> from nova import version
>>> version.version_string()
'2015.1.2'

root@infra01:/opt/rpc-openstack/openstack-ansible/playbooks# lxc-attach -n $(lxc-ls | grep utility)
root@infra01_utility_container-0276d803:/# . ~/openrc
root@infra01_utility_container-0276d803:/# openstack user list
+----------------------------------+--------------------+
| ID                               | Name               |
+----------------------------------+--------------------+
| 12273628c3964891b007756fdc99d447 | glance             |
| 2a973d9f2b6b4aa49f2c16ad39d24c32 | stack_domain_admin |
| 6ddb72da168843c89cac95cf799f1d10 | nova               |
| 721547e1e73a48ea9bd3f7ed860fb6fc | neutron            |
| 7cd45d1fbb7b42ca97d3d165629f28f0 | cinder             |
| ac5fb246db864bb3a46a1180d56b4989 | keystone           |
| dd697a8c3d72409f805a16833c1d1ceb | admin              |
| e034566361f54ab6844e5e252f428eaa | heat               |
+----------------------------------+--------------------+

root@infra01_utility_container-0276d803:/# openstack project list
+----------------------------------+---------+
| ID                               | Name    |
+----------------------------------+---------+
| 42915167075b4254aedb7a31b7a46736 | service |
| c5be3a44daf040eeb8bfd950ff5b39dd | admin   |
+----------------------------------+---------+

root@infra01_utility_container-0276d803:/# nova service-list
+----+------------------+-------------------------------------------+----------+---------+-------+----------------------------+-----------------+
| Id | Binary           | Host                                      | Zone     | Status  | State | Updated_at                 | Disabled Reason |
+----+------------------+-------------------------------------------+----------+---------+-------+----------------------------+-----------------+
| 1  | nova-conductor   | infra01_nova_conductor_container-3891b9ad | internal | enabled | up    | 2015-10-15T04:10:52.000000 | -               |
| 4  | nova-cert        | infra01_nova_cert_container-6f5a612d      | internal | enabled | up    | 2015-10-15T04:10:52.000000 | -               |
| 7  | nova-consoleauth | infra01_nova_console_container-0a481d09   | internal | enabled | up    | 2015-10-15T04:10:43.000000 | -               |
| 10 | nova-scheduler   | infra01_nova_scheduler_container-638e2856 | internal | enabled | up    | 2015-10-15T04:10:44.000000 | -               |
| 13 | nova-compute     | compute01                                 | nova     | enabled | up    | 2015-10-15T04:10:45.000000 | -               |
+----+------------------+-------------------------------------------+----------+---------+-------+----------------------------+-----------------+

root@infra01_utility_container-0276d803:/# neutron agent-list
+--------------------------------------+--------------------+-------------------------------------------+-------+----------------+---------------------------+
| id                                   | agent_type         | host                                      | alive | admin_state_up | binary                    |
+--------------------------------------+--------------------+-------------------------------------------+-------+----------------+---------------------------+
| 184f7611-a717-43a0-9c7f-6f4a73b35a62 | L3 agent           | infra01_neutron_agents_container-80cc6d88 | :-)   | True           | neutron-l3-agent          |
| a8a260cb-d006-4872-b220-6bc8ebf182c3 | Metering agent     | infra01_neutron_agents_container-80cc6d88 | :-)   | True           | neutron-metering-agent    |
| c1b986d8-f4fc-4444-88ba-049341ed686c | Linux bridge agent | infra01_neutron_agents_container-80cc6d88 | :-)   | True           | neutron-linuxbridge-agent |
| da86458d-bc93-400c-9f93-304748ed21bd | DHCP agent         | infra01_neutron_agents_container-80cc6d88 | :-)   | True           | neutron-dhcp-agent        |
| ef3fbd25-af2a-4fc4-a207-f6a919ba0bc3 | Metadata agent     | infra01_neutron_agents_container-80cc6d88 | :-)   | True           | neutron-metadata-agent    |
| efb81497-0ebd-45e4-ae19-9e5b64bf34e3 | Linux bridge agent | compute01                                 | :-)   | True           | neutron-linuxbridge-agent |
+--------------------------------------+--------------------+-------------------------------------------+-------+----------------+---------------------------+

root@infra01_utility_container-0276d803:/# cinder service-list
+------------------+---------------------------------------------+------+---------+-------+----------------------------+-----------------+
|      Binary      |                     Host                    | Zone |  Status | State |         Updated_at         | Disabled Reason |
+------------------+---------------------------------------------+------+---------+-------+----------------------------+-----------------+
| cinder-scheduler | infra01_cinder_scheduler_container-45595f8a | nova | enabled |   up  | 2015-10-15T04:11:18.000000 |       None      |
|  cinder-volume   |                compute01@lvm                | nova | enabled |   up  | 2015-10-15T04:11:09.000000 |       None      |
+------------------+---------------------------------------------+------+---------+-------+----------------------------+-----------------+

root@infra01_utility_container-0276d803:/# nova hypervisor-list
+----+------------------------+-------+---------+
| ID | Hypervisor hostname    | State | Status  |
+----+------------------------+-------+---------+
| 1  | compute01.attlocal.net | up    | enabled |
+----+------------------------+-------+---------+
```

**setup-logging.yml** - If you moved the ELK environment files in the previous step, setup-hosts.yml should have created the ELK containers on the logging node (infra01 in this example). So we just need to run the repo playbooks which will build the ELK/MaaS pip packages we need and then run the setup-logging.yml playbook.

```
# cd /opt/rpc-openstack/rpcd/playbooks
# openstack-ansible repo-pip-setup.yml
# openstack-ansible repo-build.yml
# openstack-ansible setup-logging.yml
```

<img src=https://6dbddbf8e5efac8bed3b-f96466f7bd752d7ade3ea7b63a5a8dcd.ssl.cf1.rackcdn.com/kilo_kabana2.png>
<img src=https://6dbddbf8e5efac8bed3b-f96466f7bd752d7ade3ea7b63a5a8dcd.ssl.cf1.rackcdn.com/kilo_kibana3.png>

**setup-maas.yml** - If our maas variables are set and the entities in Cloud Monitoring match our hostnames we can setup MaaS.

```
# cd /opt/rpc-openstack/rpcd/playbooks
# openstack-ansible setup-maas.yml
```

Here are some screenshots from my two node setup and MaaS.

<a href=https://6dbddbf8e5efac8bed3b-f96466f7bd752d7ade3ea7b63a5a8dcd.ssl.cf1.rackcdn.com/kilo_infra01_checks.png><img width=200 height=200 src=https://6dbddbf8e5efac8bed3b-f96466f7bd752d7ade3ea7b63a5a8dcd.ssl.cf1.rackcdn.com/kilo_infra01_checks.png></a><a href=https://6dbddbf8e5efac8bed3b-f96466f7bd752d7ade3ea7b63a5a8dcd.ssl.cf1.rackcdn.com/kilo_infra01_checks2.png><img width=200 height=200 src=https://6dbddbf8e5efac8bed3b-f96466f7bd752d7ade3ea7b63a5a8dcd.ssl.cf1.rackcdn.com/kilo_infra01_checks2.png></a><a href=https://6dbddbf8e5efac8bed3b-f96466f7bd752d7ade3ea7b63a5a8dcd.ssl.cf1.rackcdn.com/kilo_keystone_apiresponse.png><img width=200 height=200 src=https://6dbddbf8e5efac8bed3b-f96466f7bd752d7ade3ea7b63a5a8dcd.ssl.cf1.rackcdn.com/kilo_keystone_apiresponse.png></a><a href=https://6dbddbf8e5efac8bed3b-f96466f7bd752d7ade3ea7b63a5a8dcd.ssl.cf1.rackcdn.com/kilo_keystone_apiresponse2.png><img width=200 height=200 src=https://6dbddbf8e5efac8bed3b-f96466f7bd752d7ade3ea7b63a5a8dcd.ssl.cf1.rackcdn.com/kilo_keystone_apiresponse2.png></a><a href=https://6dbddbf8e5efac8bed3b-f96466f7bd752d7ade3ea7b63a5a8dcd.ssl.cf1.rackcdn.com/kilo_nova_apiresponse.png><img width=200 height=200 src=https://6dbddbf8e5efac8bed3b-f96466f7bd752d7ade3ea7b63a5a8dcd.ssl.cf1.rackcdn.com/kilo_nova_apiresponse.png></a><a href=https://6dbddbf8e5efac8bed3b-f96466f7bd752d7ade3ea7b63a5a8dcd.ssl.cf1.rackcdn.com/kilo_neutron_apiresponse.png><img width=200 height=200 src=https://6dbddbf8e5efac8bed3b-f96466f7bd752d7ade3ea7b63a5a8dcd.ssl.cf1.rackcdn.com/kilo_neutron_apiresponse.png></a><a href=https://6dbddbf8e5efac8bed3b-f96466f7bd752d7ade3ea7b63a5a8dcd.ssl.cf1.rackcdn.com/kilo_cinder_apiresponse.png><img width=200 height=200 src=https://6dbddbf8e5efac8bed3b-f96466f7bd752d7ade3ea7b63a5a8dcd.ssl.cf1.rackcdn.com/kilo_cinder_apiresponse.png></a><a href=https://6dbddbf8e5efac8bed3b-f96466f7bd752d7ade3ea7b63a5a8dcd.ssl.cf1.rackcdn.com/kilo_glance_apiresponse.png><img width=200 height=200 src=https://6dbddbf8e5efac8bed3b-f96466f7bd752d7ade3ea7b63a5a8dcd.ssl.cf1.rackcdn.com/kilo_glance_apiresponse.png></a><a href=https://6dbddbf8e5efac8bed3b-f96466f7bd752d7ade3ea7b63a5a8dcd.ssl.cf1.rackcdn.com/kilo_horizon.png><img width=200 height=200 src=https://6dbddbf8e5efac8bed3b-f96466f7bd752d7ade3ea7b63a5a8dcd.ssl.cf1.rackcdn.com/kilo_horizon.png></a>

Rackspace Cloud Monitoring is a free service and with the Intelligence dashboard is a really nice way to monitor the environment. 

**OpenStack configuration**

For this particular config (no VLANs, VXLAN bridges) I configured neutron as follows. Instances using the private-net can reach the Internet through the neutron router we create. 

```
root@infra01:/opt/rpc-openstack/rpcd/playbooks# lxc-attach -n $(lxc-ls | grep neutron_agents)
root@infra01_neutron_agents_container-80cc6d88:/# . ~/openrc

root@infra01_neutron_agents_container-80cc6d88:/# neutron router-create core-router
root@infra01_neutron_agents_container-80cc6d88:/# neutron net-create private-net --shared
root@infra01_neutron_agents_container-80cc6d88:/# neutron subnet-create private-net 10.0.0.0/24 --name private-subnet
root@infra01_neutron_agents_container-80cc6d88:/# neutron router-interface-add core-router private-subnet
root@infra01_neutron_agents_container-80cc6d88:/# neutron net-create external-net --router:external --provider:physical_network flat --provider:network_type flat
root@infra01_neutron_agents_container-80cc6d88:/# neutron subnet-create --name external-subnet --allocation-pool start=192.168.1.220,end=192.168.1.240 --disable-dhcp --gateway 192.168.1.254 external-net 192.168.1.0/24
root@infra01_neutron_agents_container-80cc6d88:/# neutron router-gateway-set core-router external-net

root@infra01_neutron_agents_container-80cc6d88:/# ip netns exec qdhcp-c3c1db92-1605-4bf5-a9af-56cc2552a765 ping -c3 8.8.8.8
PING 8.8.8.8 (8.8.8.8) 56(84) bytes of data.
64 bytes from 8.8.8.8: icmp_seq=1 ttl=51 time=28.1 ms
64 bytes from 8.8.8.8: icmp_seq=2 ttl=51 time=28.4 ms
64 bytes from 8.8.8.8: icmp_seq=3 ttl=51 time=28.3 ms

--- 8.8.8.8 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2002ms
rtt min/avg/max/mdev = 28.105/28.311/28.477/0.154 ms
```

Our network namespace for the private-net network can reach the Internet so our instances should have no problem doing the same. 

**Testing an instance and cinder**

```
root@infra01_utility_container-0276d803:/# cinder list
+--------------------------------------+--------+--------------+------+-------------+----------+--------------------------------------+
|                  ID                  | Status | Display Name | Size | Volume Type | Bootable |             Attached to              |
+--------------------------------------+--------+--------------+------+-------------+----------+--------------------------------------+
| 3672c351-d667-4a7e-8e5f-c306cf63fd00 | in-use |     None     |  10  |     None    |  false   | 04a73116-6769-4e68-9366-9351cd03b490 |
+--------------------------------------+--------+--------------+------+-------------+----------+--------------------------------------+

root@infra01:/opt/rpc-openstack/rpcd/playbooks# lxc-attach -n $(lxc-ls | grep neutron_agents)
root@infra01_neutron_agents_container-80cc6d88:/# . ~/openrc
root@infra01_neutron_agents_container-80cc6d88:/# glance image-create --disk-format qcow2 --container-format bare --name "Ubuntu 14.04.1 test" --copy-from http://cloud-images.ubuntu.com/trusty/current/trusty-server-cloudimg-amd64-disk1.img --is-public true

root@infra01_neutron_agents_container-80cc6d88:/# nova boot --flavor 2 --image 96238991-edea-4840-8dce-08ef388705ff --security-group rpc-support --key-name rpc_support --nic net-id=c3c1db92-1605-4bf5-a9af-56cc2552a765 vmtest
+--------------------------------------+-------------------------------------------------------+
| Property                             | Value                                                 |
+--------------------------------------+-------------------------------------------------------+
| OS-DCF:diskConfig                    | MANUAL                                                |
| OS-EXT-AZ:availability_zone          | nova                                                  |
| OS-EXT-SRV-ATTR:host                 | -                                                     |
| OS-EXT-SRV-ATTR:hypervisor_hostname  | -                                                     |
| OS-EXT-SRV-ATTR:instance_name        | instance-00000001                                     |
| OS-EXT-STS:power_state               | 0                                                     |
| OS-EXT-STS:task_state                | scheduling                                            |
| OS-EXT-STS:vm_state                  | building                                              |
| OS-SRV-USG:launched_at               | -                                                     |
| OS-SRV-USG:terminated_at             | -                                                     |
| accessIPv4                           |                                                       |
| accessIPv6                           |                                                       |
| adminPass                            | iQ5QS7iad5w4                                          |
| config_drive                         |                                                       |
| created                              | 2015-10-17T22:48:18Z                                  |
| flavor                               | m1.small (2)                                          |
| hostId                               |                                                       |
| id                                   | 351959b1-b9a0-4b97-9856-725c6985ad17                  |
| image                                | Ubuntu 14.04.1 (96238991-edea-4840-8dce-08ef388705ff) |
| key_name                             | rpc_support                                           |
| metadata                             | {}                                                    |
| name                                 | vmtest                                                |
| os-extended-volumes:volumes_attached | []                                                    |
| progress                             | 0                                                     |
| security_groups                      | rpc-support                                           |
| status                               | BUILD                                                 |
| tenant_id                            | c5be3a44daf040eeb8bfd950ff5b39dd                      |
| updated                              | 2015-10-17T22:48:18Z                                  |
| user_id                              | dd697a8c3d72409f805a16833c1d1ceb                      |
+--------------------------------------+-------------------------------------------------------+

root@infra01_neutron_agents_container-80cc6d88:/# nova list
+--------------------------------------+--------+--------+------------+-------------+----------------------+
| ID                                   | Name   | Status | Task State | Power State | Networks             |
+--------------------------------------+--------+--------+------------+-------------+----------------------+
| 351959b1-b9a0-4b97-9856-725c6985ad17 | vmtest | ACTIVE | -          | Running     | private-net=10.0.0.5 |
+--------------------------------------+--------+--------+------------+-------------+----------------------+

root@infra01_neutron_agents_container-80cc6d88:/# ip netns exec qdhcp-c3c1db92-1605-4bf5-a9af-56cc2552a765 ssh -i /root/.ssh/rpc_support ubuntu@10.0.0.5

The authenticity of host '10.0.0.5 (10.0.0.5)' can't be established.
ECDSA key fingerprint is 6c:6c:01:bf:48:0a:f7:7c:ec:1b:f2:5b:4a:33:30:26.
Are you sure you want to continue connecting (yes/no)? yes
Warning: Permanently added '10.0.0.5' (ECDSA) to the list of known hosts.
Welcome to Ubuntu 14.04.3 LTS (GNU/Linux 3.13.0-65-generic x86_64)

 * Documentation:  https://help.ubuntu.com/

  System information as of Sat Oct 17 22:58:29 UTC 2015

  System load:  0.54              Processes:           73
  Usage of /:   3.9% of 19.65GB   Users logged in:     0
  Memory usage: 3%                IP address for eth0: 10.0.0.5
  Swap usage:   0%

  Graph this data and manage this system at:
    https://landscape.canonical.com/

  Get cloud support with Ubuntu Advantage Cloud Guest:
    http://www.ubuntu.com/business/services/cloud

0 packages can be updated.
0 updates are security updates.
Last login: Sat Oct 17 22:58:29 2015

ubuntu@vmtest:~$
ubuntu@vmtest:~$ ping -c3 8.8.8.8
PING 8.8.8.8 (8.8.8.8) 56(84) bytes of data.
64 bytes from 8.8.8.8: icmp_seq=1 ttl=51 time=28.5 ms
64 bytes from 8.8.8.8: icmp_seq=2 ttl=51 time=27.7 ms
64 bytes from 8.8.8.8: icmp_seq=3 ttl=51 time=30.4 ms

--- 8.8.8.8 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2003ms
rtt min/avg/max/mdev = 27.738/28.941/30.496/1.169 ms
```

**Floating IP setup for remote access to instances**

```
root@infra01_neutron_agents_container-80cc6d88:/# neutron net-list
+--------------------------------------+--------------+-----------------------------------------------------+
| id                                   | name         | subnets                                             |
+--------------------------------------+--------------+-----------------------------------------------------+
| c3c1db92-1605-4bf5-a9af-56cc2552a765 | private-net  | 4cf88eef-5570-44f1-83bf-db3c7a5e42d3 10.0.0.0/24    |
| f415abd3-21fa-405f-8327-addb68e6e163 | external-net | a4816b8b-ddbd-4d35-97c0-6519efd3ebc3 192.168.1.0/24 |
+--------------------------------------+--------------+-----------------------------------------------------+

root@infra01_neutron_agents_container-80cc6d88:/# neutron floatingip-create external-net
Created a new floatingip:
+---------------------+--------------------------------------+
| Field               | Value                                |
+---------------------+--------------------------------------+
| fixed_ip_address    |                                      |
| floating_ip_address | 192.168.1.221                        |
| floating_network_id | f415abd3-21fa-405f-8327-addb68e6e163 |
| id                  | 068be72d-28bd-49c3-84df-c5c355499db3 |
| port_id             |                                      |
| router_id           |                                      |
| status              | DOWN                                 |
| tenant_id           | c5be3a44daf040eeb8bfd950ff5b39dd     |
+---------------------+--------------------------------------+

root@infra01_neutron_agents_container-80cc6d88:/# neutron floatingip-list
+--------------------------------------+------------------+---------------------+---------+
| id                                   | fixed_ip_address | floating_ip_address | port_id |
+--------------------------------------+------------------+---------------------+---------+
| 068be72d-28bd-49c3-84df-c5c355499db3 |                  | 192.168.1.221       |         |
+--------------------------------------+------------------+---------------------+---------+

root@infra01_neutron_agents_container-80cc6d88:/# neutron port-list
+--------------------------------------+------+-------------------+--------------------------------------------------------------------------------------+
| id                                   | name | mac_address       | fixed_ips                                                                            |
+--------------------------------------+------+-------------------+--------------------------------------------------------------------------------------+
| 12be3d9e-a0d1-40e8-9722-50f87dead191 |      | fa:16:3e:a6:c5:c1 | {"subnet_id": "4cf88eef-5570-44f1-83bf-db3c7a5e42d3", "ip_address": "10.0.0.5"}      |
| 2dbf3d49-7cc4-4d2a-b5a8-645f0d285fde |      | fa:16:3e:80:d5:41 | {"subnet_id": "4cf88eef-5570-44f1-83bf-db3c7a5e42d3", "ip_address": "10.0.0.1"}      |
| 956dfad1-2ce4-44b2-b6ae-792a65fefabd |      | fa:16:3e:12:61:db | {"subnet_id": "a4816b8b-ddbd-4d35-97c0-6519efd3ebc3", "ip_address": "192.168.1.221"} |
| d142bfe6-1195-4c68-8de9-f8a1841fcafc |      | fa:16:3e:b5:c5:10 | {"subnet_id": "a4816b8b-ddbd-4d35-97c0-6519efd3ebc3", "ip_address": "192.168.1.220"} |
| dcba07d7-a584-4241-8a30-2b99be359a39 |      | fa:16:3e:de:1e:a4 | {"subnet_id": "4cf88eef-5570-44f1-83bf-db3c7a5e42d3", "ip_address": "10.0.0.2"}      |
+--------------------------------------+------+-------------------+--------------------------------------------------------------------------------------+

root@infra01_neutron_agents_container-80cc6d88:/# neutron floatingip-associate 068be72d-28bd-49c3-84df-c5c355499db3 12be3d9e-a0d1-40e8-9722-50f87dead191
Associated floating IP 068be72d-28bd-49c3-84df-c5c355499db3
```

From my laptop, I can access the instance using the floating IP. I found you might have some MTU issues with SSH and this Ubuntu image because of the added overhead of using VXLAN for the bridges. Lowering the instance eth0 to 1400 MTU resolved that. 

```
[18:05]shane@work~$ ping -c3 192.168.1.221
PING 192.168.1.221 (192.168.1.221): 56 data bytes
64 bytes from 192.168.1.221: icmp_seq=0 ttl=63 time=4.811 ms
64 bytes from 192.168.1.221: icmp_seq=1 ttl=63 time=5.917 ms
64 bytes from 192.168.1.221: icmp_seq=2 ttl=63 time=2.224 ms

--- 192.168.1.221 ping statistics ---
3 packets transmitted, 3 packets received, 0.0% packet loss
round-trip min/avg/max/stddev = 2.224/4.317/5.917/1.548 ms

[18:07]shane@work~$ ssh ubuntu@192.168.1.221
The authenticity of host '192.168.1.221 (192.168.1.221)' can't be established.
RSA key fingerprint is 0b:f0:34:d4:47:92:d8:36:1a:93:7c:f3:d8:c8:32:35.
Are you sure you want to continue connecting (yes/no)? yes
Warning: Permanently added '192.168.1.221' (RSA) to the list of known hosts.
ubuntu@192.168.1.221's password:
Welcome to Ubuntu 14.04.3 LTS (GNU/Linux 3.13.0-65-generic x86_64)

 * Documentation:  https://help.ubuntu.com/

  System information as of Sat Oct 17 23:06:21 UTC 2015

  System load:  0.57              Processes:           74
  Usage of /:   3.9% of 19.65GB   Users logged in:     0
  Memory usage: 2%                IP address for eth0: 10.0.0.5
  Swap usage:   0%

  Graph this data and manage this system at:
    https://landscape.canonical.com/

  Get cloud support with Ubuntu Advantage Cloud Guest:
    http://www.ubuntu.com/business/services/cloud

0 packages can be updated.
0 updates are security updates.
Last login: Sat Oct 17 23:06:21 2015

ubuntu@vmtest:~$
```

And that's it! With openstack-ansible and a few config files we have a full OpenStack environment with Keystone, Nova, Cinder, Heat, Neutron, Horizon, ELK stack and monitored externally! I plan to have a few more posts showing the upgradability of using openstack-ansible and upgrading Icehouse -> Juno -> Kilo, all through in place upgrades. 

If you want more information or contribute/file bugs on openstack-ansible or rpc-openstack here are a few links. I'm super excited to see where the project is and where it will be going in Libery and Mitaka. 

Imagine being able to deploy Ironic, Trove, Magnum and other OpenStack projects this easily? 

Great docs for more detailed information - http://docs.rackspace.com/rpc/api/v11/bk-rpc-installation/content/rpc-common-front.html

https://github.com/openstack/openstack-ansible
https://launchpad.net/openstack-ansible
https://github.com/rcbops/rpc-openstack
http://www.rackspace.com/en-us/cloud/private
