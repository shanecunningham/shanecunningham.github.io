+++
author = "Shane Cunningham"
date = 2015-05-05T08:03:10Z
description = ""
draft = true
slug = "icehouse-to-juno-to-kilo-using-osad"
title = "Upgrading OpenStack: Icehouse to Juno to Kilo using OSAD"

+++


OpenStack Ansible Deployment (OSAD) is software that makes deploying large OpensStack installs a lot easier by using Ansible and LXC containers to automate the installation. Using this deployment method also allows an easier way to upgrade OpenStack. Upgrade OSAD with the release you want and run the playbooks -- OpenStack will be upgraded in place. This will be a barebones demo of upgrading from Icehouse to Juno to Kilo using OSAD in a 2-node configuration. 

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

openstack-ansible **9.0.11** - **Icehouse**
Template [rpc\_user\_config.yml](https://gist.github.com/shane-c/600d3c06215dfa348884)
Template [user_variables.yml](https://gist.github.com/shane-c/74bfc3ff1bcda3e8bca7)

<pre><code>cd /opt
git clone -b 9.0.11 https://github.com/openstack/openstack-ansible.git
curl -O https://bootstrap.pypa.io/get-pip.py
python get-pip.py \
  --find-links="http://mirror.rackspace.com/rackspaceprivatecloud/python_packages/9.0.11" \
  --no-index
pip install -r /opt/openstack-ansible/requirements.txt
cp -R /opt/openstack-ansible/etc/rpc\_deploy /etc
cd /opt/openstack-ansible/rpc\_deployment
</pre></code>
Edit your config files as needed. You can use a dedicated deployment host or just use infra01, I'll use infra01 as my deployment host in these examples. Note: if you are using a dedicated deployment host, it must have access to the br-mgmt network that your containers use.

Now we run the playbooks to setup the hosts and containers, install HAProxy, the infrastructure that OpenStack uses, and finally the OpenStack bits themselves.

<pre><code>ansible-playbook -e @/etc/rpc\_deploy/user\_variables.yml playbooks/setup/host-setup.yml
ansible-playbook -e @/etc/rpc\_deploy/user\_variables.yml playbooks/infrastructure/haproxy-install.yml
ansible-playbook -e @/etc/rpc\_deploy/user\_variables.yml playbooks/infrastructure/infrastructure-setup.yml
ansible-playbook -e @/etc/rpc\_deploy/user\_variables.yml playbooks/openstack/openstack-setup.yml
</pre></code>

Upgrade to openstack-ansible **10.1.14 - Juno**

First, let's make sure a few variables are set that openstack-ansible 10.X requires.

<pre><code>grep horizon\_secret\_key /etc/rpc\_deploy/user\_variables.yml
horizon\_secret\_key: 79199a49f8f1d98b6c6040e4
</pre></code>

That's already set, if not for you then add the variable. Also, remove `maas_repo_version` from user_variables.yml. 

Remove: the following MaaS checks. These should be removed before running the MaaS playbooks; when the playbooks are run, the checks and alarms will be recreated.

swift_account_replication_check
swift_async_check
swift_md5_check
swift_object_replication_check
swift_quarantine_check
swift_object_server_check
swift_container_server_check
swift_account_server_check
swift_proxy_server_check
rabbitmq\_status
galera\_check

Change: RabbitMQ and Galera alarm names
Using the Cloud Control Panel or API, delete all alarms (not checks) on each node associated with the RabbitMQ and Galera plugins. For example:

rabbitmq_disk_free_alarm_status--nodename
rabbitmq_mem_alarm_status--nodename
wsrep_local_state--nodename
wsrep_cluster_size--nodename

Get the openstack-ansible 10.1.14 code.

<pre><code>root@infra01:/opt/os-ansible-deployment/rpc_deployment# cd /opt/
root@infra01:/opt# mv os-ansible-deployment /root/os-ansible-deployment.9.0.11
root@infra01:/opt# git clone -b 10.1.14 https://github.com/openstack/openstack-ansible.git
Cloning into 'openstack-ansible'...
remote: Counting objects: 20517, done.
remote: Compressing objects: 100% (4/4), done.
remote: Total 20517 (delta 0), reused 0 (delta 0), pack-reused 20513
Receiving objects: 100% (20517/20517), 5.72 MiB | 1.98 MiB/s, done.
Resolving deltas: 100% (13515/13515), done.
Checking connectivity... done.
Note: checking out '195a9e9b586a05b626e7e682f387d887d2d360f5'.

You are in 'detached HEAD' state. You can look around, make experimental
changes and commit them, and you can discard any commits you make in this
state without impacting any branches by performing another checkout. If you want to create a new branch to retain commits you create, you may do so (now or later) by using -b with the checkout command again. Example: <br>
git checkout -b new\_branch\_name  <br>cd /opt/openstack-ansible/rpc\_deployment/
</pre></code>
Install Juno
<pre><code>ansible-playbook -e @/etc/rpc_deploy/user_variables.yml playbooks/setup-everything.yml
</pre></code>
<pre><code>PLAY RECAP ********************************************************************
compute01                  : ok=240  changed=50   unreachable=0    failed=0
compute01_cinder_volumes_container-c2ffd37d : ok=163  changed=28   unreachable=0    failed=0
compute01_rsyslog_container-06bb8656 : ok=124  changed=17   unreachable=0    failed=0
infra01                    : ok=85   changed=6    unreachable=0    failed=0
infra01_cinder_api_container-7473924c : ok=137  changed=22   unreachable=0    failed=0
infra01_elasticsearch_container-810f00fa : ok=123  changed=12   unreachable=0    failed=0
infra01_galera_container-09acbe7e : ok=167  changed=21   unreachable=0    failed=0
infra01_glance_container-ed84be54 : ok=138  changed=15   unreachable=0    failed=0
infra01_heat_apis_container-9536d6a6 : ok=163  changed=27   unreachable=0    failed=0
infra01_heat_engine_container-089b84c5 : ok=130  changed=19   unreachable=0    failed=0
infra01_horizon_container-9917dd61 : ok=135  changed=27   unreachable=0    failed=0
infra01_keystone_container-4a0ed286 : ok=187  changed=15   unreachable=0    failed=0
infra01_kibana_container-4d2d47d6 : ok=127  changed=18   unreachable=0    failed=0
infra01_logstash_container-7e585a9e : ok=120  changed=12   unreachable=0    failed=0
infra01_memcached_container-304b168e : ok=113  changed=11   unreachable=0    failed=0
infra01_neutron_agents_container-13265a4e : ok=206  changed=39   unreachable=0    failed=0
infra01_neutron_server_container-01daf82a : ok=140  changed=28   unreachable=0    failed=0
infra01_nova_api_ec2_container-add52306 : ok=138  changed=24   unreachable=0    failed=0
infra01_nova_api_metadata_container-11dad288 : ok=130  changed=24   unreachable=0    failed=0
infra01_nova_api_os_compute_container-77bb9898 : ok=141  changed=25   unreachable=0    failed=0
infra01_nova_cert_container-47db309c : ok=129  changed=23   unreachable=0    failed=0
infra01_nova_conductor_container-cd723303 : ok=130  changed=24   unreachable=0    failed=0
infra01_nova_scheduler_container-bc6c075c : ok=130  changed=24   unreachable=0    failed=0
infra01_nova_spice_console_container-fde1c0b9 : ok=153  changed=28   unreachable=0    failed=0
infra01_rabbit_mq_container-e98f5490 : ok=124  changed=15   unreachable=0    failed=0
infra01_rsyslog_container-cb49205a : ok=124  changed=17   unreachable=0    failed=0
infra01_utility_container-0d983989 : ok=118  changed=14   unreachable=0    failed=0


real	27m5.467s
user	1m33.890s
sys	0m53.390s
</pre></code>