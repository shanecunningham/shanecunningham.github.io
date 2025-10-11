+++
author = "Shane Cunningham"
categories = ["Nagios"]
date = 2014-02-19T06:00:21Z
description = ""
draft = false
slug = "simple-nagios-setup-with-open-monitoring-distribution"
tags = ["Nagios"]
title = "Simple Nagios setup with Open Monitoring Distribution"

+++


I've been a fan of <a href="http://www.nagios.org/">Nagios</a> for quite awhile. It has its issues, but with how easy it has become to setup with <a href="http://omdistro.org/">OMD</a> and check discovery using <a href="http://mathias-kettner.de/check_mk.html">Check_MK</a>, I don't know of anything else this powerful and simple to use. I'll go over this first part which is the OMD installation and setup.

I'm using CentOS 6.5 for my Nagios server. Download links and other distros can be found <a href="http://omdistro.org/download">here</a>.
<pre><code>
[root@nagios ~]# wget http://files.omdistro.org/releases/centos_rhel/omd-1.10-rh61-31.x86_64.rpm

[root@nagios ~]# yum localinstall omd-1.10-rh61-31.x86_64.rpm
</code></pre>
To setup your monitoring environment you will want to create a "site". It's possible to have multiple sites depending on what you will be monitoring. I just created a single site for my home monitoring.
<pre><code>
[root@nagios ~]# omd create home_nagios

[root@nagios ~]# omd start home_nagios
</code></pre>
You can check the current status of your OMD install with following command.
<pre><code>[root@nagios ~]# omd status
Doing 'status' on site home_nagios:
apache: running
rrdcached: running
npcd: running
nagios: running
crontab: running
-----------------------
Overall state: running
</code></pre>
After the omd start command you should be able to access your Nagios server from `http://IP/home_nagios`. This page will give you a few options for which control panel you want to view, including the default Nagios GUI, a Check_MK GUI and other data visualization GUIs available to monitor your Nagios data. Default login credentials are username - omdadmin password - omd. You'll want to change those. That's it.

OMD couldn't make it any easier to get a complete Nagios server installed with additional plugins that make setting up your nodes and checks very simple. In the next post I'll go over how I use Check_MK agent on my servers to automatically setup and discover checks for Nagios to monitor and some tips and notes I've found useful for this setup.