---
title: "salt-cloud and Rackspace Cloud Servers: Part 2"
date: 2013-07-27T17:10:07Z
description: "An expanded salt-cloud rackspace.conf profile file covering Rackspace Cloud Linux distros and server sizes, and how to list them."
tags: ["saltstack", "rackspace"]
archived: true
---

In my previous post I showed how easy it is to get salt-cloud provisioning tool working with Rackspace Cloud to spin up and bootstrap your new Cloud Server with salt. The /etc/salt/cloud.profiles.d/rackspace.conf file in that example only included one 512MB Cloud Server running Ubuntu Server 12.04. I've updated this file with all of the Linux distros and server sizes included in Rackspace Cloud. You can see these from your salt-master with 'salt-cloud --list-sizes rackspace' and to view the images list you can run 'salt-cloud --list-images rackspace'.

You can rename these to whatever you like, I used the distro-version-size format, so 'salt-cloud -p CentOS-6.2-4G centos-test' would be used to spin up a 4GB CentOS 6.2 server. Look through the file for all the names and sizes for all 512MB to 30GB Cloud Servers.

```yaml {title="/etc/salt/cloud.profiles.d/rackspace.conf"}
CentOS-6.2-30G:
      provider: rackspace
      size: 30GB Standard Instance
      image: CentOS 6.2
```

[Download](http://cdn.cunninghamshane.com/rackspace.conf) - /etc/salt/cloud.profiles.d/rackspace.conf

There are Windows Server images available and I'm working on adding those to the file, but those versions are a bit of a mess with all the R2, SP1, SP2 , SQL and SharePoint images available. To add to the problem certain Windows Server version can only be built with certain server sizes. Hope this helps with using salt-cloud with Rackspace Cloud.
