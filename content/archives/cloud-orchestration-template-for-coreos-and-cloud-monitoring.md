+++
author = "Shane Cunningham"
categories = ["Rackspace", "CoreOS"]
date = 2014-10-06T08:21:02Z
description = ""
draft = false
slug = "cloud-orchestration-template-for-coreos-and-cloud-monitoring"
tags = ["Rackspace", "CoreOS"]
title = "Cloud Orchestration template for CoreOS and Cloud Monitoring"

+++


[Cloud Orchestration](http://www.rackspace.com/blog/cloud-orchestration-automating-deployments-of-full-stack-configurations/) is an automated deployment service provided by Rackspace Cloud. The backend for this service is [OpenStack Heat](https://wiki.openstack.org/wiki/Heat). The following is a simple template for deploying CoreOS Stable and runs a small bash script after the server is built to set it up for Cloud Monitoring. The script just performs the steps in my previous post on monitoring CoreOS with Cloud Monitoring. The template is pretty self explanatory so you can edit it to your liking. 

<pre><code>heat_template_version: 2013-05-23

description: Deploy CoreOS that tracks the Stable Channel

parameters:
  count:
    description: Number of CoreOS machines to deploy
    type: number
    default: 1
    constraints:
    - range:
        min: 1
        max: 5
      description: Must be between 1 and 5 servers.
  key-name:
    type: string
    description: Name of key-pair to be used for compute instance
  flavor:
    type: string
    default: 1 GB Performance
    constraints:
    - allowed_values:
      - 1 GB Performance
      - 2 GB Performance
      - 4 GB Performance
      - 8 GB Performance
      description: |
        Must be a valid Rackspace Cloud Server flavor for the region you have
        selected to deploy into.
  priv-network:
    type: string
    description: Cloud Network UUID
  name:
    type: string
    description: Name of each CoreOS machine booted
    default: coreos.host

resources:
   machines:
    type: "OS::Heat::ResourceGroup"
    properties:
      count: { get_param: count }
      resource_def:
        type: OS::Nova::Server
        properties:
          key_name: { get_param: key-name }
          image: "66f325b7-1234-4f35-b86f-859dd09bd2f8"
          flavor: { get_param: flavor }
          name: { get_param: name }
          networks:
          - uuid: "00000000-0000-0000-0000-000000000000"
          - uuid: "11111111-1111-1111-1111-111111111111"
          - uuid: { get_param: priv-network }
          user_data_format: RAW
          config_drive: "true"
          user_data: |
            #!/bin/bash
            git clone https://github.com/jayofdoom/rackspace-monitoring-agent-coreos
            cd rackspace-monitoring-agent-coreos
            ./build_agent_container.bash
            mkdir -p /opt/rackspace-monitoring-agent
            tar -x -C /opt/rackspace-monitoring-agent -f rackspace-monitoring-agent-container.tar.xz
</code></pre>

The OpenStack Heat command line client works with Cloud Orchestration, so we will use that to spin our stacks up and down. You can setup your client from [here](http://docs.rackspace.com/orchestration/api/v1/orchestration-getting-started/content/Install_Heat_Client.html).

My example run:

<pre><code>~$ heat stack-create coreos-stable-maas --template-file ~/coreos-stable-mon.yaml -P key-name=shane-mbp -P priv-network="43937fdb-bf22-43da-9d19-e47d55de1a87" -P name="coreos4.host"

~$ heat stack-list
WARNING (httpclient) Failed to retrieve management_url from token
+--------------------------------------+---------------------------+-----------------+----------------------+
| id                                   | stack_name                | stack_status    | creation_time        |
+--------------------------------------+---------------------------+-----------------+----------------------+
| 887f9048-b881-4fff-8567-db95e1f96ea4 | ghost.cunninghamshane.com | ADOPT_COMPLETE  | 2014-08-25T18:59:05Z |
| 9e71c987-6c59-49e7-80ae-52c96a28f9b6 | coreos-stable             | CREATE_COMPLETE | 2014-09-27T03:37:36Z |
| aca607ea-3f85-4330-ae77-67864345b06d | coreos-stable-maas        | CREATE_COMPLETE | 2014-10-06T02:16:53Z |
+--------------------------------------+---------------------------+-----------------+----------------------+
</code></pre>