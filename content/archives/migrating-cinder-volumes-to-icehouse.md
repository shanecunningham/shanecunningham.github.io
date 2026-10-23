+++
author = "Shane Cunningham"
categories = ["openstack"]
date = 2014-05-09T07:20:18Z
description = ""
draft = false
slug = "migrating-cinder-volumes-to-icehouse"
tags = ["openstack"]
title = "Migrating Cinder volumes to Icehouse"

+++


I upgraded my all in one OpenStack Havana box to the new [Icehouse](http://www.openstack.org/software/icehouse/) release. All the same steps apply as in [my all in one OpenStack deployment](https://www.cunninghamshane.com/my-all-in-one-openstack-deployment-at-home/) post except use http://rdo.fedorapeople.org/rdo-release.rpm which now redirects to the Icehouse RPM. I wanted to blow everything away and not perform an upgrade. The only issue I ran into was I boot my VMs with Cinder volumes for persistant storage (just use LVM to create a volume group named "cinder-volumes") and I wanted to move those to Icehouse with the data untouched. 

Maybe there's an easier way to do this? This is what worked for me. 

Before reinstalling CentOS 6.5 minimal I backed up all MySQL OpenStack Havana databases. I used [this](https://github.com/rcbops/support-tools/blob/master/havana-tools/database_backup.sh) script but you can easily do this by hand using mysqldump if you wanted. I left my LVM config on my other disks as is. I went through the full setup using RDO and setup Neutron for external floating IPs. After that I dropped the cinder database on the new install, created a new cinder database then imported my backup from Havana to this new cinder database. 

Copy your cinder.sql dump to the the new server and cd to the directory that contains it. 

<pre><code>[root@openstack ~]# CINDER_SERVICE=$(ls /etc/init.d/ | grep -E "cinder")
[root@openstack ~]# for i in $CINDER_SERVICE; do service $i stop; done
[root@openstack ~]# mysql -e "drop database cinder"
[root@openstack ~]# mysql -e "create database cinder"
[root@openstack ~]# mysql -o cinder < cinder.sql
</code></pre>
Now we need to edit some Cinder database values to remove any old references. Some of these values need to change for your database. I'm no DBA. :\
<pre><code>[root@openstack ~]# mysql

mysql> use cinder
mysql> update volumes set project_id="newadmintenantUUID" where project_id="oldadmintenantUUID”;
mysql> update volumes set attach_status="detached" where attach_status="attached”;
mysql> update volumes set instance_uuid=NULL where instance_uuid="anyoldinstanceUUID”;
mysql> update volumes set status="available" where status="in-use”;

[root@openstack ~]# cinder-manage db sync
</code></pre>
For my setup those are the values I needed to change to get my Cinder volumes back to available and not attached to any non-existant instances. Now start up the Cinder services.
<pre><code>for i in $CINDER_SERVICE; do service $i start; done
</code></pre>
After those changes my Cinder volumes from my Havana install were now available in Icehouse to be attached or bootable from a new VM with my existing data on the volumes.