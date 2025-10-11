+++
author = "Shane Cunningham"
date = 2012-03-23T02:55:21Z
description = ""
draft = false
slug = "add-linux-integration-services-v3-2-to-centos-6-2-vm"
title = "Add Linux Integration Services v3.2 to CentOS 6.2 VM"

+++


Here are the steps to install <a title="Linux Integration Services v3.2" href="http://www.microsoft.com/download/en/details.aspx?id=28188" target="_blank">Linux Integration Services v3.2</a> to a CentOS 6.2 VM in Hyper-V.

Add the Linux IC v3.2.iso to a CD-Rom attached to your CentOS 6.2 VM.

<pre><code>mount /dev/cdrom /media</code></pre>

Create a directory, for example, <code>mkdir /home/LinuxServices</code>

<pre><code>cp /media/* /home/LinuxServices
cd /home/LinuxServices
./install.sh</code></pre>