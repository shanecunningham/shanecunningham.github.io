---
title: "Monitor OpenIndiana/Solaris 11 with check_mk_agent and Nagios"
date: 2012-12-07T07:12:09Z
description: "Monitoring an OpenIndiana/Solaris 11 ZFS host from Nagios using the check_mk agent run through inetd."
tags: ["nagios", "monitoring", "zfs"]
archived: true
---

Here's a short how-to on monitoring OpenIndiana (Solaris 11) that is running ZFS using Nagios, [check___mk](http://mathias-kettner.com/check_mk.html) and `check_mk_agent`. This awesome open source tool makes setting up your servers to be checked by Nagios super easy. In the past I would manually create or edit the Nagios .cfg files for my environment and install various agents depending on OS architecture on the servers I wanted to monitor. Even though I am not monitoring a ton of servers it still took quite a bit of time. Now I use `check_mk` and [Open Monitoring Distribution](http://omdistro.org/). I plan to write-up a more detailed post on OMD soon, but I found it's a very impressive bundled Nagios package with many important addons and can easily be installed on every major Linux distribution. On to monitoring Solaris 11.

Download the Solaris agent `(check_mk_agent.solaris)` from [GitHub](https://github.com/sileht/check_mk/tree/master/agents)

Copy and rename this file to `/usr/bin/check_mk_agent`

Edit `/etc/services` and add

```text
check_mk        6556/tcp
```

Now for Solaris we need to edit `/etc/inet/inetd.conf` and add

```text
check_mk stream tcp nowait root /usr/sbin/tcpd /usr/bin/check_mk_agent
```

Enter these commands at the shell, should not receive any errors.

```sh
inetconv
inetconv -e
```

On your OMD/Nagios box put your Solaris box into the all_hosts and run these commands.

Inventory new checks

```sh
cmk -I
```

Reload Nagios

```sh
cmk -O
```

Check_MK is so awesome it even automagically monitors your ZFS pools!
