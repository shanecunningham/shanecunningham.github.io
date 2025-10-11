+++
author = "Shane Cunningham"
categories = ["Nagios"]
date = 2012-12-07T07:12:09Z
description = ""
draft = false
slug = "monitor-openindianasolaris-11-with-check_mk_agent-and-nagios"
tags = ["Nagios"]
title = "Monitor OpenIndiana/Solaris 11 with check_mk_agent and Nagios"

+++


Here's a short how-to on monitoring OpenIndiana (Solaris 11) that is running ZFS using Nagios, <a href="http://mathias-kettner.com/check_mk.html">check___mk</a> and `check_mk_agent`. This awesome open source tool makes setting up your servers to be checked by Nagios super easy. In the past I would manually create or edit the Nagios .cfg files for my environment and install various agents depending on OS architecture on the servers I wanted to monitor. Even though I am not monitoring a ton of servers it still took quite a bit of time. Now I use `check_mk` and <a href="http://omdistro.org/">Open Monitoring Distribution</a>. I plan to write-up a more detailed post on OMD soon, but I found it's a very impressive bundled Nagios package with many important addons and can easily be installed on every major Linux distribution. On to monitoring Solaris 11.

Download the Solaris agent `(check_mk_agent.solaris)` from <a href="https://github.com/sileht/check_mk/tree/master/agents">GitHub</a>

Copy and rename this file to `/usr/bin/check_mk_agent`

Edit <code>/etc/services</code> and add

<pre><code>check_mk        6556/tcp</code></pre>

Now for Solaris we need to edit <code>/etc/inet/inetd.conf</code> and add

<pre><code>check_mk stream tcp nowait root /usr/sbin/tcpd /usr/bin/check_mk_agent</code></pre>

Enter these commands at the shell, should not receive any errors.

<pre><code>inetconv
inetconv -e</pre></code>

On your OMD/Nagios box put your Solaris box into the all_hosts and run these commands.

Inventory new checks

<pre><code>cmk -I</pre></code>

Reload Nagios

<pre><code>cmk -O</pre></code>

Check_MK is so awesome it even automagically monitors your ZFS pools!