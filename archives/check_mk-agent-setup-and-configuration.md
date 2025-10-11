+++
author = "Shane Cunningham"
categories = ["Nagios"]
date = 2014-02-20T07:40:25Z
description = ""
draft = false
slug = "check_mk-agent-setup-and-configuration"
tags = ["Nagios"]
title = "Check_MK agent setup and configuration"

+++


Setting up OMD to get a working Nagios server is really simple, but what makes this monitoring setup really awesome is how easy <a href="http://mathias-kettner.com/check_mk_introduction.html">Check___MK</a> makes finding, configuring and running these checks. Setup the agent on your nodes, or just monitor SNMP/ping data, then tell Nagios/Check_MK which hosts to monitor and it will inventory and monitor all available checks it can find.
<pre><code>
[root@node1 ~]# yum install -y xinetd check-mk-agent
</code></pre>
This should create a check-mk-agent config file for xinetd at /etc/xinetd.d/check-mk-agent. We can edit one option for security, I haven't tried running this as a regular user instead of root, but I should look into that. Uncomment the following line and specify your Nagios servers IP or hostname.
<pre><code>
[root@node1 ~]# vim /etc/xinetd.d/check-mk-agent

# configure the IP address(es) of your Nagios server here:
only_from = 10.208.162.213
</code></pre>
Restart xinetd and set to start on boot.
<pre><code>
[root@node1 ~]# service xinetd start; chkconfig xinetd on
</code></pre>
Last step for the agent is opening port 6556 on your nodes at the firewall with iptables. I would also recommend limiting this port to your Nagios servers IP as the only source IP to hit port 6556 with -s. That should complete the agent setup, xinetd should be listening on 6556 for our Nagios servers connections and iptables should be allowing traffic on port 6556 from our Nagios servers IP only.
<h2><strong>Nagios server setup</strong></h2>
I manage my /etc/hosts file on my Nagios server with SaltStack, some of my hosts are easier to manage this way so I can map them directly with IP and hostname, instead of DNS. Probably a number of ways you can set this part up but this is what works for me. All my servers/switch/router go in this hosts file and in the main.mk file I add the hostname to start Nagios checking those hosts.
<pre><code>
[root@nagios ~]# vim /etc/hosts

10.208.165.85 node1
162.242.244.184 db.server
10.0.0.1 pfSense
</code></pre>
su to your sites user to manage it.
<pre><code>
[root@nagios ~]# su - home_nagios
</code></pre>
Specify which hosts to check in the main.mk file.
<pre><code>
OMD[home_nagios]:~$ vim /opt/omd/sites/home_nagios/etc/check_mk/main.mk

# Put your host names here
# all_hosts = [ 'localhost' ]
all_hosts = [
'node1',
'db.server',
"pfSense|snmp"
]
</code></pre>
If everything is working correctly we should now inventory the checks and it will find all available checks Check___MK can monitor. Note with my pfSense check I specify SNMP, pfSense has SNMP checks available and Check_MK can find those automatically. Following output was from only adding node1 to my main.mk file.
<pre><code>
OMD[home_nagios]:~$ cmk -I
cpu.loads 1 new checks
cpu.threads 1 new checks
df 1 new checks
diskstat 1 new checks
kernel 3 new checks
kernel.util 1 new checks
lnx_if 2 new checks
logwatch 1 new checks
mem.used 1 new checks
mounts 1 new checks
postfix_mailq 1 new checks
tcp_conn_stats 1 new checks
uptime 1 new checks
</code></pre>
Now restart Nagios so we can see these checks/host in our GUIs.
<pre><code>
OMD[home_nagios]:~$ cmk -R
Generating Nagios configuration...OK
Validating Nagios configuration...OK
Precompiling host checks...OK
Restarting Nagios...OK
</code></pre>
<p style="text-align: center;"><img class="aligncenter" alt="" src="https://6dbddbf8e5efac8bed3b-f96466f7bd752d7ade3ea7b63a5a8dcd.ssl.cf1.rackcdn.com/node1_checks.png" width="501" height="185" /></p>
From the available GUIs available I prefer the Check_MK GUI. It has some awesome built in graphing for all checks. It has graphs for each check from 4 hours, 24 hours, 1 week, 1 month and 1 year. All done automagically.
<h2><strong>Notes</strong></h2>
Check_MK caches inventory checks, so if you find yourself in the situation where you made a change and -I and -R does not clear the old check, run cmk -II and it will re-inventory every check, hopefully removing the old and rechecking.

You can add plugins to Check___MK to monitor additional services such as MySQL. Here's a list of <a href="http://mathias-kettner.de/checkmk_check_catalogue.html">available plugins and check catalogue</a>. Notifications are easy to setup, more info <a href="http://mathias-kettner.de/checkmk_flexible_notifications.html">here</a>. Some <a href="http://mathias-kettner.de/checkmk_omd.html">notes</a> for integrating with OMD, and all other Check_MK documentation can he found <a href="http://mathias-kettner.de/checkmk.html">here</a>.

I still haven't looked into a HA type setup for Nagios/OMD, if your Nagios server goes down then monitoring is down. SaltStack makes setting up the agent on new servers very simlple. Also need to look into automating this even further with SaltStack and possibly having Check_MK find, inventory and reload the config as new servers are built.