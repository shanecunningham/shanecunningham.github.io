+++
author = "Shane Cunningham"
categories = ["openstack"]
date = 2015-03-13T09:43:35Z
description = ""
draft = false
slug = "openstack-swift-and-cyberduck"
tags = ["openstack"]
title = "OpenStack Swift and Cyberduck"

+++


Just a couple notes. I recently added a [Swift](https://wiki.openstack.org/wiki/Swift) node to my OpenStack deployment in my closet. For some reason I kept wanting to point Cyberduck to the infra1\_swift\_proxy\_container at port 8080. Instead, you want to point it to port 5000 for Keystone auth, duh. By default SSL is not enabled in Swift so you can download the HTTP OpenStack profile [OpenstackSwift(HTTP).cyberduckprofile](https://svn.cyberduck.ch/trunk/profiles/Openstack%20Swift%20(HTTP).cyberduckprofile). "Username:" in Cyberduck wants tenant:user, so out of the box you could use admin:admin, and the "Secret Key" would be the admin users password.

![httpcyberduck.png](https://6dbddbf8e5efac8bed3b-f96466f7bd752d7ade3ea7b63a5a8dcd.ssl.cf1.rackcdn.com/httpcyberduck.png)

My Swift node has 3 x 2TB for the disks with only 1 NIC for the transfers. Over WiFi it averaged about 9.3 MB/s and from another server on my network about 35 MB/s. Still need to fiddle with the Swift node. 

Adding a Swift node with [openstack-ansible](https://github.com/stackforge/os-ansible-deployment) - [http://docs.rackspace.com/rpc/api/v10/bk-rpc-swift/content/ch-object-storage-overview.html](http://docs.rackspace.com/rpc/api/v10/bk-rpc-swift/content/ch-object-storage-overview.html)