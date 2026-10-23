+++
author = "Shane Cunningham"
categories = ["openstack", "ceph"]
date = 2016-04-10T00:17:12Z
description = ""
draft = false
slug = "deploying-openstack-and-ceph"
tags = ["openstack", "ceph"]
title = "Deploying OpenStack Liberty with Ceph"

+++


In this example of deploying OpenStack I'll be adding a third server that will act as our [Ceph](http://ceph.com/) storage server. With a few config changes to openstack-ansible we will setup nova, cinder and glance to use Ceph as their backend storage systems.

**infra01**: 
Lenovo ThinkServer TS140 
Xeon E3-1225 v3 3.2 GHz 
16GB ECC RAM 
2 x 1Gb NICs
```
IP address for em1:        192.168.88.100  
IP address for br-mgmt:    172.29.236.51  
IP address for br-vxlan:   172.29.240.51  
IP address for br-storage: 172.29.244.51  
IP address for br-vlan:    none  
```

**compute01**: 
Dell Poweredge T110 II 
Xeon E3-1230 v2 3.3 GHz 
32GB ECC RAM 
2 x 1Gb NICs
```
IP address for em1:        192.168.88.101  
IP address for br-mgmt:    172.29.236.52  
IP address for br-vxlan:   172.29.240.52  
IP address for br-storage: 172.29.244.52  
IP address for br-vlan:    none
```

**object01**: 
Dell Poweredge T20
Intel Pentium G3220 3.0 GHz 
4GB ECC RAM 
2 x 1Gb NICs
3 x 2TB SATA drives for Ceph storage
```
IP address for em1:        192.168.88.102  
IP address for br-mgmt:    172.29.236.53  
IP address for br-vxlan:   172.29.240.53  
IP address for br-storage: 172.29.244.53  
IP address for br-vlan:    none
```

I'll jump right into the configuration for Ceph. This uses rpc-openstack (tag r12.0.0) which is openstack-ansible wrapped with some helpful additions like installing ceph for us. If you have questions on a more step by step openstack-ansible Kilo install, see my other posts. 

We need to add the Ceph environment file to /etc/openstack_deploy/env.d/ so openstack-ansible knows we want to deploy Ceph.

```
cp -a /opt/rpc-openstack/rpcd/etc/openstack_deploy/env.d/ceph.yml /etc/openstack_deploy/env.d
```

Create our [/etc/openstack\_deploy/conf.d/ceph.yml](https://gist.github.com/shane-c/bf629d203fccd25bd12dd678720ecbca) file which describes our specific Ceph deployment. We create 3 mons containers that live on the infrastructure host along with our other containers. We also tell Ansible where our OSD hosts are and the disks we'll be using for ceph storage. And the last storage_hosts section is where we tell cinder to use ceph for its backend storage for volumes.

```
---
mons_hosts:
  infra01:
    ip: 192.168.88.100
    affinity:
      ceph_mon_container: 3

osds_hosts:
  object01:
    ip: 192.168.88.102
    affinity:
      ceph_osd_container: 3
    container_vars:
    # The devices must be specified in conjunction with raw_journal_devices below.
    # If you want one journal device per five drives, specify the same journal_device five times.
      devices:
         - /dev/sda
         - /dev/sdb
         - /dev/sdc
    # Note: If a device does not have a matching "raw_journal_device",
    #       it will co-locate the journal on the device.
      raw_journal_devices:
        - /dev/sda
        - /dev/sdb
        - /dev/sdc

storage_hosts:
  infra01:
    ip: 192.168.88.100
    container_vars:
      cinder_backends:
        limit_container_types: cinder_volume
        ceph:
          volume_driver: cinder.volume.drivers.rbd.RBDDriver
          rbd_pool: volumes
          rbd_ceph_conf: /etc/ceph/ceph.conf
          rbd_flatten_volume_from_snapshot: 'false'
          rbd_max_clone_depth: 5
          rbd_store_chunk_size: 4
          rados_connect_timeout: -1
          glance_api_version: 2
          volume_backend_name: ceph
          rbd_user: "{{ cinder_ceph_client }}"
          rbd_secret_uuid: "{{ cinder_ceph_client_uuid }}"
```

If we are only using Ceph as the backend for Cinder (not using another host with LVM or any other backend) then we can containerize the cinder-volumes process. 

```
sed -i 's/is_metal: true/is_metal: false/g' /etc/openstack_deploy/env.d/cinder.yml
```

We need our mons containers to have an interface in the br-storage network so we need to add it to the group\_binds in our br-storage provider\_network section in openstack\_user\_config.yml file.

```
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
          - mons
```

Add these variables to the end of /etc/openstack\_deploy/user\_extra\_variables.yml. **Note**: common\_single\_host_mode is only required in this demo because I'm basically doing an all in one OSD host with only 3 disks. 

```
monitor_interface: 'eth1'
public_network: '172.29.236.0/22' # This is the network from external -> storage (and mons).
cluster_network: '172.29.244.0/22' # This is OSD to OSD replication.
common_single_host_mode: true
```

Add the following in /etc/openstack\_deploy/user\_variables.yml.

```
glance_default_store: rbd
nova_libvirt_images_rbd_pool: vms
nova_force_config_drive: False
nova_nova_conf_overrides:
  libvirt:
    live_migration_uri: qemu+ssh://nova@%s/system?keyfile=/var/lib/nova/.ssh/id_rsa&no_verify=1
```

We can now start running playbooks.

```
# openstack-ansible setup-hosts.yml
# openstack-ansible haproxy-install.yml
# cd ../../rpcd/playbooks
# openstack-ansible ceph-all.yml
```

At this point we should have a working Ceph installation. lxc-attach to one of the ceph_mon container on the infrastructure host and you should be able to run ceph -s and ceph df to check the status of ceph. Continue running setup-infrastructure.yml and setup-openstack.yml to complete the install.

```
root@infra01_ceph_mon_container-5e4cfc8d:/# ceph -s
    cluster db518fe7-6dc1-4a52-a2fc-86a4f0890f4d
     health HEALTH_OK
     monmap e1: 3 mons at {infra01_ceph_mon_container-5e4cfc8d=172.29.236.251:6789/0,infra01_ceph_mon_container-a5c1bfe6=172.29.236.191:6789/0,infra01_ceph_mon_container-c5e7ea12=172.29.238.198:6789/0}
            election epoch 8, quorum 0,1,2 infra01_ceph_mon_container-a5c1bfe6,infra01_ceph_mon_container-5e4cfc8d,infra01_ceph_mon_container-c5e7ea12
     osdmap e35: 3 osds: 3 up, 3 in
      pgmap v74: 512 pgs, 4 pools, 0 bytes data, 0 objects
            117 MB used, 5351 GB / 5352 GB avail
                 512 active+clean

root@infra01_ceph_mon_container-5e4cfc8d:/# ceph df
GLOBAL:
    SIZE      AVAIL     RAW USED     %RAW USED
    5352G     5351G         117M             0
POOLS:
    NAME        ID     USED     %USED     MAX AVAIL     OBJECTS
    images      1         0         0         1783G           0
    volumes     2         0         0         1783G           0
    vms         3         0         0         1783G           0
    backups     4         0         0         1783G           0
```

This is after adding a glance image, spinning up two instances and creating one cinder volume.

```
root@infra01_ceph_mon_container-5e4cfc8d:/# ceph -s
    cluster db518fe7-6dc1-4a52-a2fc-86a4f0890f4d
     health HEALTH_OK
     monmap e1: 3 mons at {infra01_ceph_mon_container-5e4cfc8d=172.29.236.251:6789/0,infra01_ceph_mon_container-a5c1bfe6=172.29.236.191:6789/0,infra01_ceph_mon_container-c5e7ea12=172.29.238.198:6789/0}
            election epoch 8, quorum 0,1,2 infra01_ceph_mon_container-a5c1bfe6,infra01_ceph_mon_container-5e4cfc8d,infra01_ceph_mon_container-c5e7ea12
     osdmap e42: 3 osds: 3 up, 3 in
      pgmap v257: 512 pgs, 4 pools, 2572 MB data, 384 objects
            7673 MB used, 5344 GB / 5352 GB avail
                 512 active+clean
  client io 61688 kB/s rd, 0 B/s wr, 422 op/s

root@infra01_ceph_mon_container-5e4cfc8d:/# ceph df
GLOBAL:
    SIZE      AVAIL     RAW USED     %RAW USED
    5352G     5344G        7673M          0.14
POOLS:
    NAME        ID     USED      %USED     MAX AVAIL     OBJECTS
    images      1      2252M      0.04         1781G         285
    volumes     2         16         0         1781G           3
    vms         3       320M         0         1781G          96
    backups     4          0         0         1781G           0
```

With [openstack-ansible](https://github.com/openstack/openstack-ansible) and [rpc-openstack](https://github.com/rcbops/rpc-openstack), getting an OpenStack cluster up and running with Ceph as the backend storage couldn't be easier. 