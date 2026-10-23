+++
author = "Shane Cunningham"
categories = ["Rackspace", "CoreOS"]
date = 2014-08-05T11:24:00Z
description = ""
draft = false
slug = "monitoring-coreos-with-rackspace-cloud-monitoring"
tags = ["Rackspace", "CoreOS"]
title = "Monitoring CoreOS with Rackspace Cloud Monitoring"

+++


**Updated 8/5 to use systemd unit file.**

Recently decided to move my blog to containers and [CoreOS](https://coreos.com) for learning and fun. While setting up an [HAProxy](http://www.haproxy.org) container on one of my CoreOS hosts I thought about how I would monitor the host. Luckily, smart people have already thought about this. :)

I use Rackpace's Cloud Monitoring and [agent](http://www.rackspace.com/knowledge_center/article/install-the-cloud-monitoring-agent) which can be setup on any server in any datacenter or cloud provider. Rackspace hosted servers get a nice GUI and [awesome dashboard](https://intelligence.rackspace.com/) for the checks and monitoring data, but you could still set it all up on a non Rackspace hosted server using the [Cloud Monitoring API](http://docs.rackspace.com/cm/api/v1.0/cm-devguide/content/overview.html) and [raxmon](https://developer.rackspace.com/blog/using-raxmon-to-configure-rackspace-cloud-monitoring/). 

The goods: https://github.com/jayofdoom/rackspace-monitoring-agent-coreos
<pre><code>git clone https://github.com/jayofdoom/rackspace-monitoring-agent-coreos
</code></pre>
<pre><code>cd rackspace-monitoring-agent-coreos
./build_agent_container.bash
mkdir -p /opt/rackspace-monitoring-agent
tar -x -C /opt/rackspace-monitoring-agent -f rackspace-monitoring-agent-container.tar.xz
</code></pre>

Next you'll register the agent so that it can interact with the control panel. 

<pre><code>cd /opt/rackspace-monitoring-agent
usr/bin/rackspace-monitoring-agent --setup
</code></pre>
Enter your username and [API key](http://www.rackspace.com/knowledge_center/article/rackspace-cloud-essentials-viewing-and-regenerating-your-api-key). If this is the first time setting up Cloud Monitoring on this server choose Create New Token. Next choose the entitiy, this is usually 1., but choose the option which matches your servers hostname and IP. If it's a non Rackspace hosted server you'll have to create a new entity and access the data from the API. 

<pre><code>Please select the Entity that corresponds to this server:
  1. core1.host - enhAOHzL6U
       private0_v4: xxxx
       public1_v6: xxxx
       access_ip1_v4: xxxx
       access_ip0_v6: xxxx
       public0_v4: xxxx
  2. Create a new Entity for this server (not supported by Rackspace Cloud Control Panel)
  3. Do not associate with an Entity
</code></pre>

We can use the systemd unit file included in the repo to start the monitoring agent. When you registered the agent it should have created /etc/rackspace-monitoring-agent.cfg with some data Cloud Monitoring needs. We'll move this file to a location in the directory structure systemd-nspawn creates. 

<pre><code>mv /etc/rackspace-monitoring-agent.cfg /opt/rackspace-monitoring-agent/etc/rackspace-monitoring-agent.conf.d/
</code></pre>

I had to edit the systemd unit file to start the agent with the config file we just moved. Open the rackspace-monitoring-agent.service to edit. Notice I added the **-c /etc/rackspace-monitoring-agent.conf.d/rackspace-monitoring-agent.cfg** to starting the agent. 

<pre><code>[Service]
ExecStart=/usr/bin/systemd-nspawn -D /opt/rackspace-monitoring-agent --share-system --capability=all --bind=/sys:/sys --bind=/dev:/dev --bind=/dev/pts:/dev/pts --bind=/usr/share/oem:/mnt --user=root --keep-unit /usr/bin/rackspace-monitoring-agent -c /etc/rackspace-monitoring-agent.conf.d/rackspace-monitoring-agent.cfg -l /var/log/rackspace-monitoring-agent.log --exit-on-upgrade
Restart=always
RestartSec=30s

[Install]
WantedBy=multi-user.target
</code></pre>

Now we'll copy the unit file and start it up. 

<pre><code>cp rackspace-monitoring-agent.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable rackspace-monitoring-agent.service
systemctl start rackspace-monitoring-agent.service
</code></pre>

From your control panel you should see your real time values, and monitoring data at the [dashboard](https://intelligence.rackspace.com/). A few examples. 

<pre><code>core1 ~ # free -m
             total       used       free     shared    buffers    cached
Mem:          7984        285       7699          0          4       144
-/+ buffers/cache:        136       7847
Swap:            0          0          0
</code></pre>

![coreos2](https://6dbddbf8e5efac8bed3b-f96466f7bd752d7ade3ea7b63a5a8dcd.ssl.cf1.rackcdn.com/coreos2.png)

![coreos1](https://6dbddbf8e5efac8bed3b-f96466f7bd752d7ade3ea7b63a5a8dcd.ssl.cf1.rackcdn.com/coreos1.png)

This is just an example, as you probably know CoreOS is changing frequently so this solution could change at any time.