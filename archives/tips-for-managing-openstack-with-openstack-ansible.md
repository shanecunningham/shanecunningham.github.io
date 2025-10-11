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

<pre><code class="nohighlight "># ansible -m shell hosts -a "uptime"
infra1 | success | rc=0 >>
 12:22:37 up 15:21,  3 users,  load average: 0.14, 0.29, 0.35
compute1 | success | rc=0 >>
 12:22:37 up 15:20,  1 user,  load average: 0.00, 0.01, 0.05 <br>
\# ansible -m shell infra\_hosts -a "w"
\# ansible -m shell compute\_hosts -a "w"
\# ansible -m shell storage\_hosts -a "w"
\# ansible -m shell network\_hosts -a "w"
\# ansible -m shell haproxy_hosts -a "w"
\# ansible -m shell infra1 -a "w"
\# ansible -m shell compute1 -a "w"
</pre></code>

**Container host groups**

<pre><code class="nohighlight">\# ansible -m shell cinder\_api\_container -a "w"
\# ansible -m shell cinder\_volumes\_container -a "w"
\# ansible -m shell elasticsearch\_container -a "w"
\# ansible -m shell galera\_container -a "w"
\# ansible -m shell glance\_container -a "w"
\# ansible -m shell heat\_apis\_container -a "w"
\# ansible -m shell heat\_engine\_container -a "w"
\# ansible -m shell horizon\_container -a "w"
\# ansible -m shell keystone\_container -a "w"
\# ansible -m shell kibana\_container -a "w"
\# ansible -m shell logstash\_container -a "w"
\# ansible -m shell memcached\_container -a "w"
\# ansible -m shell neutron\_agents\_container -a "w"
\# ansible -m shell neutron\_server\_container -a "w"
\# ansible -m shell nova\_api\_ec2\_container -a "w"
\# ansible -m shell nova\_api\_metadata\_container -a "w"
\# ansible -m shell nova\_api\_os\_compute\_container -a "w"
\# ansible -m shell nova\_cert\_container -a "w"
\# ansible -m shell nova\_conductor\_container -a "w"
\# ansible -m shell nova\_scheduler\_container -a "w"
\# ansible -m shell nova\_spice\_console\_container -a "w"
\# ansible -m shell rabbit\_mq\_container -a "w"
\# ansible -m shell rsyslog\_container -a "w"
\# ansible -m shell utility\_container -a "w"
</pre></code>

<pre><code class="nohighlight">\# ansible -m shell all -a "w"
</pre></code>

Using Ansible [ad-hoc](http://docs.ansible.com/intro_adhoc.html) and [patterns](http://docs.ansible.com/intro_patterns.html) for hosts you can see how you can manage both OpenStack and various other tasks you might need to perform on a cluster of hosts/containers.

You can also combine host groups with ":", for example, pulling last 10 lines for the neutron containers log files.

<pre><code class="nohighlight">\# ansible -m shell neutron\_agents\_container:neutron\_server\_container -a "tail /var/log/neutron/*"
</pre></code>

Looking for an instance UUID on all compute hosts.

<pre><code class="nohighlight">\# ansible -m shell compute_hosts -a "grep 'e73581eb-454a-4ee1-ab79-2d938b631d87' /var/log/nova/*"
</pre></code>

**LCX tips**

Sometimes you will want to restart an LXC container.

<pre><code class="nohighlight">\# lxc-stop -n infra1\_glance\_container-dd666740 && lxc-start -d -n infra1\_glance\_container-dd666740 <br>
\# lxc-stop -n $(lxc-ls | grep glance) && lxc-start -d -n $(lxc-ls | grep glance)
</pre></code>

You might also want to blow away everything and start over without rekicking your OS. These are the steps I go through that should clear everything out. 

<pre><code class="nohighlight">\# ansible -m shell hosts -a 'for i in \`lxc-ls\`; do lxc-stop -n $i && lxc-destroy -n $i; done' <br>
\# ansible -m shell hosts -a 'cp /etc/hosts /etc/hosts.bak; grep -v container- /etc/hosts > /etc/hosts.new && mv -f /etc/hosts.new /etc/hosts' <br>
\# ansible -m shell infra_hosts -a 'rm -rf /openstack/*'
</pre></code>

If you want a new inventory file to be generated, remove these files and rerun the playbooks. 
<pre><code class="nohighlight">
\# rm /etc/rpc\_deploy/rpc\_inventory.json /etc/rpc\_deploy/rpc\_hostnames_ips.yml
</pre></code>

**Rebuilding specific LXC container**

In openstack-ansible there are many tags you can use to run specific parts of the playbooks. You can also use --limit to limit playbooks to specific hosts or containers. For example, I needed to delete the glance container. Instead of running the full playbooks (you can, they are idempotent), we will limit it to the glance container. 

<pre><code class="nohighlight">\# lxc-stop -n infra1\_glance\_container-dd666740 && lxc-destroy -n infra1\_glance\_container-dd666740 <br>
\# glance image-list
(HTTP 503) <br>
\# ansible-playbook -e @/etc/rpc\_deploy/user\_variables.yml playbooks/setup/host-setup.yml --limit infra1\_glance\_container-dd666740 <br>
PLAY RECAP \******************************************************************** <br>infra1\_glance\_container-dd666740 : ok=35   changed=23   unreachable=0    failed=0 <br>
\# ansible-playbook -e @/etc/rpc\_deploy/user\_variables.yml playbooks/openstack/openstack-setup.yml --limit infra1\_glance\_container-dd666740 <br>
PLAY RECAP ******************************************************************** <br>infra1\_glance\_container-dd666740 : ok=111  changed=33   unreachable=0    failed=0 <br>
\# glance image-list
+--------------------------------------+---------------------+-------------+------------------+-----------+--------+
| ID                                   | Name                | Disk Format | Container Format | Size      | Status |
+--------------------------------------+---------------------+-------------+------------------+-----------+--------+
| c1fa5486-0837-46a2-8f10-7aff4047eca9 | cirros              | qcow2       | bare             | 13200896  | active |
| d32d4324-8425-48d1-a40f-2424d3dae156 | Ubuntu Server 14.04 | qcow2       | bare             | 257229312 | active |
+--------------------------------------+---------------------+-------------+------------------+-----------+--------+
</pre></code>

It's recommended to run 3 x infrastructure hosts for a proper Galera and RabbitMQ clusters. So normally you would have 3 x glance containers too. In the above scenario you could do this in production and it should load balance between your 3 x glance containers. That 503 I received above was from HAProxy because I only have one infrastructure node.

Hope this helps!