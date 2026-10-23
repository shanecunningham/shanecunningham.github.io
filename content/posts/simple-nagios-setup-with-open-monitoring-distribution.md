---
title: "Simple Nagios setup with Open Monitoring Distribution"
date: 2014-02-19T06:00:21Z
description: "Installing Open Monitoring Distribution (OMD) 1.10 on CentOS 6.5 and creating a Nagios site with omd create and omd start."
tags: ["nagios", "monitoring"]
archived: true
---

I've been a fan of [Nagios](http://www.nagios.org/) for quite awhile. It has its issues, but with how easy it has become to setup with [OMD](http://omdistro.org/) and check discovery using [Check_MK](http://mathias-kettner.de/check_mk.html), I don't know of anything else this powerful and simple to use. I'll go over this first part which is the OMD installation and setup.

I'm using CentOS 6.5 for my Nagios server. Download links and other distros can be found [here](http://omdistro.org/download).

```console
[root@nagios ~]# wget http://files.omdistro.org/releases/centos_rhel/omd-1.10-rh61-31.x86_64.rpm

[root@nagios ~]# yum localinstall omd-1.10-rh61-31.x86_64.rpm
```

To setup your monitoring environment you will want to create a "site". It's possible to have multiple sites depending on what you will be monitoring. I just created a single site for my home monitoring.

```console
[root@nagios ~]# omd create home_nagios

[root@nagios ~]# omd start home_nagios
```

You can check the current status of your OMD install with following command.

```console
[root@nagios ~]# omd status
Doing 'status' on site home_nagios:
apache: running
rrdcached: running
npcd: running
nagios: running
crontab: running
-----------------------
Overall state: running
```

After the omd start command you should be able to access your Nagios server from `http://IP/home_nagios`. This page will give you a few options for which control panel you want to view, including the default Nagios GUI, a Check_MK GUI and other data visualization GUIs available to monitor your Nagios data. Default login credentials are username - omdadmin password - omd. You'll want to change those. That's it.

OMD couldn't make it any easier to get a complete Nagios server installed with additional plugins that make setting up your nodes and checks very simple. In the next post I'll go over how I use Check_MK agent on my servers to automatically setup and discover checks for Nagios to monitor and some tips and notes I've found useful for this setup.
