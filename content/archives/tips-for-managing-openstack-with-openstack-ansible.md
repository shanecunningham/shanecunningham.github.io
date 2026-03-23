+++
author = "Shane Cunningham"
categories = ["openstack", "openstack-ansible"]
date = 2015-07-18T22:56:06Z
description = ""
draft = false
slug = "tips-for-managing-openstack-with-openstack-ansible"
tags = ["openstack", "openstack-ansible"]
title = "Tips for managing OpenStack with openstack-ansible"

+++


[openstack-ansible](https://github.com/stackforge/os-ansible-deployment) (OSAD), is a deployment method that uses Ansible to lay down OpenStack inside LXC containers. It makes deploying large OpenStack deployments easier. Deploying most components of OpenStack inside LXC containers also makes upgrading as easy as downloading the new playbooks and running.

Here are some tips on managing the cluster once you're up and runnning. Since the inventory includes all your hosts and containers, you can use Ansible to manage OpenStack and system administration tasks.

To use the inventory file automatically, cd to /opt/os-ansible-deployment/rpc_deployment.

**Physical host groups**

```
# ansible -m shell hosts -a "uptime"
infra1 | success | rc=0 >>
 12:22:37 up 15:21,  3 users,  load average: 0.14, 0.29, 0.35
compute1 | success | rc=0 >>
 12:22:37 up 15:20,  1 user,  load average: 0.00, 0.01, 0.05
# ansible -m shell infra_hosts -a "w"
# ansible -m shell compute_hosts -a "w"
# ansible -m shell storage_hosts -a "w"
# ansible -m shell network_hosts -a "w"
# ansible -m shell haproxy_hosts -a "w"
# ansible -m shell infra1 -a "w"
# ansible -m shell compute1 -a "w"
```

**Container host groups**

```
# ansible -m shell cinder_api_container -a "w"
# ansible -m shell cinder_volumes_container -a "w"
# ansible -m shell elasticsearch_container -a "w"
# ansible -m shell galera_container -a "w"
# ansible -m shell glance_container -a "w"
# ansible -m shell heat_apis_container -a "w"
# ansible -m shell heat_engine_container -a "w"
# ansible -m shell horizon_container -a "w"
# ansible -m shell keystone_container -a "w"
# ansible -m shell kibana_container -a "w"
# ansible -m shell logstash_container -a "w"
# ansible -m shell memcached_container -a "w"
# ansible -m shell neutron_agents_container -a "w"
# ansible -m shell neutron_server_container -a "w"
# ansible -m shell nova_api_ec2_container -a "w"
# ansible -m shell nova_api_metadata_container -a "w"
# ansible -m shell nova_api_os_compute_container -a "w"
# ansible -m shell nova_cert_container -a "w"
# ansible -m shell nova_conductor_container -a "w"
# ansible -m shell nova_scheduler_container -a "w"
# ansible -m shell nova_spice_console_container -a "w"
# ansible -m shell rabbit_mq_container -a "w"
# ansible -m shell rsyslog_container -a "w"
# ansible -m shell utility_container -a "w"
```

```
# ansible -m shell all -a "w"
```

Using Ansible [ad-hoc](http://docs.ansible.com/intro_adhoc.html) and [patterns](http://docs.ansible.com/intro_patterns.html) for hosts you can see how you can manage both OpenStack and various other tasks you might need to perform on a cluster of hosts/containers.

You can also combine host groups with ":", for example, pulling last 10 lines for the neutron containers log files.

```
# ansible -m shell neutron_agents_container:neutron_server_container -a "tail /var/log/neutron/*"
```

Looking for an instance UUID on all compute hosts.

```
# ansible -m shell compute_hosts -a "grep 'e73581eb-454a-4ee1-ab79-2d938b631d87' /var/log/nova/*"
```

**LCX tips**

Sometimes you will want to restart an LXC container.

```
# lxc-stop -n infra1_glance_container-dd666740 && lxc-start -d -n infra1_glance_container-dd666740
# lxc-stop -n $(lxc-ls | grep glance) && lxc-start -d -n $(lxc-ls | grep glance)
```

You might also want to blow away everything and start over without rekicking your OS. These are the steps I go through that should clear everything out.

```
# ansible -m shell hosts -a 'for i in `lxc-ls`; do lxc-stop -n $i && lxc-destroy -n $i; done'
# ansible -m shell hosts -a 'cp /etc/hosts /etc/hosts.bak; grep -v container- /etc/hosts > /etc/hosts.new && mv -f /etc/hosts.new /etc/hosts'
# ansible -m shell infra_hosts -a 'rm -rf /openstack/*'
```

If you want a new inventory file to be generated, remove these files and rerun the playbooks.

```
# rm /etc/rpc_deploy/rpc_inventory.json /etc/rpc_deploy/rpc_hostnames_ips.yml
```

**Rebuilding specific LXC container**

In openstack-ansible there are many tags you can use to run specific parts of the playbooks. You can also use --limit to limit playbooks to specific hosts or containers. For example, I needed to delete the glance container. Instead of running the full playbooks (you can, they are idempotent), we will limit it to the glance container.

```
# lxc-stop -n infra1_glance_container-dd666740 && lxc-destroy -n infra1_glance_container-dd666740
# glance image-list
(HTTP 503)
# ansible-playbook -e @/etc/rpc_deploy/user_variables.yml playbooks/setup/host-setup.yml --limit infra1_glance_container-dd666740
PLAY RECAP ********************************************************************
infra1_glance_container-dd666740 : ok=35   changed=23   unreachable=0    failed=0
# ansible-playbook -e @/etc/rpc_deploy/user_variables.yml playbooks/openstack/openstack-setup.yml --limit infra1_glance_container-dd666740
PLAY RECAP ********************************************************************
infra1_glance_container-dd666740 : ok=111  changed=33   unreachable=0    failed=0
# glance image-list
+--------------------------------------+---------------------+-------------+------------------+-----------+--------+
| ID                                   | Name                | Disk Format | Container Format | Size      | Status |
+--------------------------------------+---------------------+-------------+------------------+-----------+--------+
| c1fa5486-0837-46a2-8f10-7aff4047eca9 | cirros              | qcow2       | bare             | 13200896  | active |
| d32d4324-8425-48d1-a40f-2424d3dae156 | Ubuntu Server 14.04 | qcow2       | bare             | 257229312 | active |
+--------------------------------------+---------------------+-------------+------------------+-----------+--------+
```

It's recommended to run 3 x infrastructure hosts for a proper Galera and RabbitMQ clusters. So normally you would have 3 x glance containers too. In the above scenario you could do this in production and it should load balance between your 3 x glance containers. That 503 I received above was from HAProxy because I only have one infrastructure node.

Hope this helps!
