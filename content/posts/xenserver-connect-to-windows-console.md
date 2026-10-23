+++
author = "Shane Cunningham"
categories = ["XenServer", "Windows Server"]
date = 2013-09-07T05:47:53Z
description = ""
draft = false
slug = "xenserver-connect-to-windows-console"
tags = ["XenServer", "Windows Server"]
title = "XenServer connect to Windows console"

+++


Connecting to a Linux console in XenServer is is easy as xl console, but slightly more difficult with a Windows VM since the terminal can't display the Windows GUI. SSH tunneling and VNC to the rescue. First, grab the VNC port the Windows VM uses with the following command. You'll need the dom-id of the Windows VM. <code>xl list</code> or <code>xe vm-list name-label=YourWindowsNameLabel params=dom-id</code> to find it.
<pre><code>xenstore-read /local/domain/dom-id/console/vnc-port
[root@xenserver ~]# xenstore-read /local/domain/31/console/vnc-port
5902</code></pre>
So the Windows VM has the console running on 127.0.0.1:5902. From your local machine we will need to setup an SSH tunnel to this port.
<pre><code>ssh -L &lt;local port&gt;:localhost:&lt;VM console port&gt; &lt;username&gt;@&lt;xenserver host&gt;
ssh -L 5902:localhost:5902 root@192.168.2.100</code></pre>
That should log you into the XenServer host and setup a tunnel on your local machines port 5902 to the XenServers port 5902. I tried to use VNC Viewer for this but after trying to connect it would close VNC Viewer immediately. Not sure what the issue is, but I was able to get this working perfectly with <a href="http://sourceforge.net/projects/chicken/">Chicken of the VNC</a>.
<pre><code>Host: localhost
Display or port: 5902</code></pre>
Hit Connect and your should see your Windows VM console. I was able to install Windows and now have an easy way to access all Windows VMs from the XenServer console.