+++
author = "Shane Cunningham"
categories = ["Rackspace", "Docker"]
date = 2015-01-21T06:09:00Z
description = ""
draft = false
slug = "use-cloud-files-for-docker-registry-storage"
tags = ["Rackspace", "Docker"]
title = "Use Cloud Files for Docker registry storage"

+++


If you want to run your own private Docker registry here's a quick and easy way to do that using [Rackspace Cloud Files](http://www.rackspace.com/cloud/files/) as the backend storage. Cloud Files is based on [OpenStack Swift](https://wiki.openstack.org/wiki/Swift), so it comes with all the built in features and reliability that's designed into Swift. Since this is Docker we'll do it with the official Docker registry container, install docker-registry-driver-swift, and pass in our Cloud Files/Rackspace information when we run the container. 

####Dockerfile

<pre><code>\# Dockerfile to build docker registry with swift support
\#
FROM registry
RUN apt-get update && apt-get install -yq python-lxml git
RUN git clone https://github.com/bacongobbler/docker-registry-driver-swift.git /src
RUN pip install /src</pre></code>

####Build the image

<pre><code>docker build -rm -t swift-registry .</pre></code>

####Run the container with our Cloud Files/Rackspace info. 

<pre><code>docker run -d \
-e SETTINGS\_FLAVOR=swift \
-e STORAGE\_PATH=/ \
-e OS\_CONTAINER=Cloud Files container name \
-e OS\_AUTH\_URL=https://identity.api.rackspacecloud.com/v2.0/ \
-e OS\_USERNAME=Cloud Account Username \
-e OS\_PASSWORD=Cloud Account Password \
-e OS\_TENANT\_NAME=Cloud Account ID # \
-e OS\_REGION\_NAME=Region (IAD, ORD, DFW, SYD, HKG) \
-e SEARCH\_BACKEND=sqlalchemy \
-p 5000:5000 \
swift-registry</pre></code>

To test locally you can push/pull to localhost:5000, or test remotely to your servers public IP and port 5000. Note: this is wide open so I'll leave securing it up to you, there are a few htpasswd/HTTPS solutions documented out there.