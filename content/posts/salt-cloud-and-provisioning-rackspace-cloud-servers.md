---
title: "salt-cloud and provisioning Rackspace Cloud Servers"
date: 2013-07-19T07:47:35Z
description: "Using salt-cloud on a SaltStack master to provision Rackspace Cloud Servers as salt minions with an Ubuntu profile."
tags: ["saltstack", "rackspace"]
archived: true
---

This weekend I setup [SaltStack](http://saltstack.com/) in a VM in my home lab, with all my home VMs and [Rackspace Cloud Servers](http://www.rackspace.com/cloud/servers/) as salt-minions. Everything worked pretty well. I even used my salt-master and some salt states to install check_mk_agent on all my VMs. They all hooked into a [OMD/Nagios](http://omdistro.org/) VM running in my home lab and 163 checks later I have my monitoring system working. About 3 hours of work and a few cups of coffee. I still have a lot to learn with SaltStack, especially the proper way to use and configure salt states, grains and pillars.

[salt-cloud](https://github.com/saltstack/salt-cloud) is a public cloud provisioning tool that can quickly spin up and bootstrap your new Cloud Servers with salt-minion for easy configuration management. salt-cloud can be used with a number of Cloud providers but I'm going to use [Rackspace Cloud](http://www.rackspace.com/cloud/). Here's how I setup salt-cloud on my already running salt-master in my home lab. My salt-master server is CentOS 6.4.

```sh
yum install salt-cloud python-pip sshpass
python-pip install apache_libcloud
```

```sh
mkdir /etc/salt/cloud.providers.d
vim /etc/salt/cloud.providers.d/rackspace.conf
```

```yaml {title="/etc/salt/cloud.providers.d/rackspace.conf"}
rackspace-config:
  # Set the location of the salt-master
  # IP or hostname of your salt-master
  # hostname points to my home IP and port forward to my salt-master
  minion:
    master: home.yourdomain.com

  # Configure Rackspace using the OpenStack plugin
  #
  identity_url: 'https://identity.api.rackspacecloud.com/v2.0/tokens'
  compute_name: cloudServersOpenStack
  protocol: ipv4

  # Set the compute region:
  # can be DFW, ORD, SYD
  compute_region: DFW

  # Configure Rackspace authentication credentials
  #
  user: rackspaceusername
  tenant: rackspaceuserid
  apikey: rackspaceapikey

  provider: openstack
```

```sh
mkdir /etc/salt/cloud.profiles.d
vim /etc/salt/cloud.profiles.d/rackspace.conf
```

```yaml {title="/etc/salt/cloud.profiles.d/rackspace.conf"}
rackspace_512:
    provider: rackspace-config
    size: 512MB Standard Instance
    image: Ubuntu 12.04 LTS (Precise Pangolin)
```

Now let's create the Cloud Server. Running this first one in debug mode so you can see what it does and more detail in case there are any errors.

```sh
salt-cloud -l debug -p rackspace_512 newserver
```

That will take some time but should give you some details on your new Cloud Server when finished. Now we run this simple ping test with salt to make sure it's working.

```text
salt 'newserver' test.ping

newserver:
    True
```

This was a really simple example to show how fast you can get a provisioning tool up and running with SaltStack and Rackspace Cloud. I only included one image and server size, but you can add all OS images and sizes available in the Rackspace Cloud from 512MB to 30GB servers. There's probably a lot cooler things you can do with this and I look forward to learning more on salt-cloud. If you have any tips on provisioning let me know!
