+++
author = "Shane Cunningham"
categories = ["Rackspace"]
date = 2013-06-15T06:14:02Z
description = ""
draft = false
slug = "add-cloud-networks-to-existing-cloud-server"
tags = ["Rackspace"]
title = "Add Cloud Networks to existing Cloud Server"

+++


Cloud Networks is a really cool up and coming feature in the <a href="http://www.rackspace.com/cloud/">Rackspace Cloud</a>. It enables you to create private networks only accessible by your Cloud infrastructure. When first released, you could only attach a <a href="http://www.rackspace.com/cloud/servers/">Cloud Server</a> to <a href="http://www.rackspace.com/knowledge_center/article/getting-started-with-cloud-networks">Cloud Networks</a> when creating a new Cloud Server or by taking an image and then creating a new Cloud Server based off of that image and attaching Cloud Networks at that time. Not the best situation if you already have a stable Cloud infrastructure. Luckily we can now attach Cloud Networks to an already running Cloud Server. Make sure the server is a NextGen Cloud Server based on OpenStack. This tutorial was run on Debian 6 Squeeze, but should be pretty much the same on other Linux distros. If you have any issues with a particular distro please let me know.

First we need to install a few packages. The easiest way is to use pip.
<pre><code>apt-get install python-pip
pip install os_virtual_interfacesv2_python_novaclient_ext
pip install rackspace-novaclient</code></pre>
Now we will create a file for our Rackspace credentials and enter your information in the &lt; &gt; parts of the file.
<pre><code>vim ~/.bash_profile

export OS_AUTH_URL=https://identity.api.rackspacecloud.com/v2.0/
export OS_AUTH_SYSTEM=rackspace
export OS_REGION_NAME=DFW
export OS_USERNAME=&lt;username&gt;
export OS_TENANT_NAME=&lt;account_number&gt;
export NOVA_RAX_AUTH=1
export OS_PASSWORD=&lt;api_key&gt;
export OS_PROJECT_ID=&lt;account_number&gt;
export OS_NO_CACHE=1
</code></pre>
<pre><code>
chmod 600 ~/.bash_profile
source ~/.bash_profile</code></pre>
We should be able to run some nova commands and receive the information we need to attach Cloud Networks.
<pre><code>nova credentials #note the token ID
nova network-list #note the network ID for your Cloud Network
nova virtual-interface-list e74780b5-d110-4faa-bfc4-87802b90aaf1 #this is the instance ID of the Cloud Server you want to attach Cloud Networks to, you should see a public and private interface.</code></pre>
Now we use nova to attach the Cloud Network to your existing Cloud Server.
<pre><code>usage: nova virtual-interface-create &lt;network_id&gt; &lt;instance_id&gt;
nova virtual-interface-create 30712e92-40d3-4259-bd73-2ed8b09abcf5 e74780b5-d110-4faa-bfc4-87802b90aaf1</code></pre>
You should receive a response with the IP etc information for the new virtual interface.

When you run virtual-interface-command with your instance ID you should see the new interface. You should also see it in the control panel and with a command such as ip a on the actual server.
<pre><code>nova virtual-interface-list e74780b5-d110-4faa-bfc4-87802b90aaf1</code></pre>
You should now have your Cloud Network attached to your already running Cloud Server. There are a number of ways to do this, but I ran this on the actual Cloud Server. You could really run this wherever you can run rackspace-novaclient and install the Cloud Network plugin, `os__virtual_interfacesv2_python_novaclient_ext`. If you have any questions or need any help with this, please leave a comment or shoot me an email and I will get back to you.

Here are some links that might further help with this task.

<a href="http://docs.rackspace.com/servers/api/v2/cn-devguide/content/api_virt_interfaces.html">http://docs.rackspace.com/servers/api/v2/cn-devguide/content/api_virt_interfaces.html</a>

<a href="http://docs.rackspace.com/servers/api/v2/cs-gettingstarted/content/section_gs_install_nova.html">http://docs.rackspace.com/servers/api/v2/cs-gettingstarted/content/section_gs_install_nova.html</a>