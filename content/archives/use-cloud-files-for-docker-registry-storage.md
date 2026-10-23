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

```
# Dockerfile to build docker registry with swift support
#
FROM registry
RUN apt-get update && apt-get install -yq python-lxml git
RUN git clone https://github.com/bacongobbler/docker-registry-driver-swift.git /src
RUN pip install /src
```

####Build the image

```
docker build -rm -t swift-registry .
```

####Run the container with our Cloud Files/Rackspace info.

```
docker run -d \
-e SETTINGS_FLAVOR=swift \
-e STORAGE_PATH=/ \
-e OS_CONTAINER=Cloud Files container name \
-e OS_AUTH_URL=https://identity.api.rackspacecloud.com/v2.0/ \
-e OS_USERNAME=Cloud Account Username \
-e OS_PASSWORD=Cloud Account Password \
-e OS_TENANT_NAME=Cloud Account ID # \
-e OS_REGION_NAME=Region (IAD, ORD, DFW, SYD, HKG) \
-e SEARCH_BACKEND=sqlalchemy \
-p 5000:5000 \
swift-registry
```

To test locally you can push/pull to localhost:5000, or test remotely to your servers public IP and port 5000. Note: this is wide open so I'll leave securing it up to you, there are a few htpasswd/HTTPS solutions documented out there.
