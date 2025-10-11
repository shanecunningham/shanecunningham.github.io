+++
author = "Shane Cunningham"
categories = ["Rackspace"]
date = 2013-11-20T02:12:12Z
description = ""
draft = false
slug = "manage-your-cloud-databases-with-trove-and-the-command-line"
tags = ["Rackspace"]
title = "Manage your Cloud Databases with trove and the command line"

+++


<a href="https://wiki.openstack.org/wiki/Trove">Trove</a> is an OpenStack project to supply databases as a service. <a href="http://www.rackspace.com/cloud/databases/">Rackspace's Cloud Databases</a> API are based on this and so the <a href="https://github.com/openstack/python-troveclient">trove Python client</a> is compatible with your Rackspace provided Cloud Databases or your own implementation of Trove.

This example we'll go over using this with Rackspaces's Cloud Databases. I'm using OS X so my example will be for that OS, but the client should be compatible with most Linux distros.
<pre><code>sudo</code> <code>pip </code><code>install</code> <code>python-troveclient</code></pre>
Now we'll setup some environment variables for the Trove client to use. Change &lt;username&gt; to your Cloud account username and &lt;tenant_id&gt; to your Cloud account number and &lt;password&gt; to your Cloud account users password. Also change the region (DFW, ORD, IAD, LON, SYD, HKG) to whichever data center you want to manage your Cloud Databases in.
<pre><code>vim .profile</code></pre>
<pre><code>export OS_AUTH_URL=https://identity.api.rackspacecloud.com/v2.0/
export OS_REGION_NAME=DFW
export OS_USERNAME=&lt;username&gt; 
export OS_TENANT_NAME=&lt;tenant_id&gt; 
export TROVE_SERVICE_TYPE=rax:database 
export OS_PASSWORD=&lt;password&gt; 
export OS_PROJECT_ID=&lt;tenant_id&gt;</code></pre>
<pre><code>source .profile</code></pre>
Now you can interact with your Cloud Databases. Some of the things trove makes extremely simple are creating, deleting, resizing and restarting database instances, enabling root access on your Cloud Database, which is disabled by default with Cloud Databases, backups and user management. Here's a few examples.
<pre><code>[19:53]shane@home~$ trove flavor-list
 +----+----------------+-------+
 | id | name | ram |
 +----+----------------+-------+
 | 1 | 512MB Instance | 512  |
 | 2 | 1GB Instance | 1024   |
 | 3 | 2GB Instance | 2048   |
 | 4 | 4GB Instance | 4096   |
 | 5 | 8GB Instance | 8192   |
 | 6 | 16GB Instance | 16384 |
 +----+----------------+-------+</code></pre>
Create a new Cloud Database instance with 512MB RAM and 2GB disk space.
<pre><code>[19:53]shane@home~$ trove create db1test 1 --size 2
 +----------+---------------------------------------------------------------+
 | Property | Value |
 +----------+---------------------------------------------------------------+
 | created | 2013-11-20T01:53:27 |
 | flavor | 1 |
 | hostname | 5430d126a923f214253d12875e9c9531ab29533c.rackspaceclouddb.com |
 | id | 95875e88-3b22-40e1-939d-86937f8651f0 |
 | name | db1test |
 | status | BUILD |
 | updated | 2013-11-20T01:53:28 |
 | volume | 2 |
 +----------+---------------------------------------------------------------+</code></pre>
Enable root on your Cloud Database instance.
<pre><code>[19:58]shane@home~$ trove root-show 95875e88-3b22-40e1-939d-86937f8651f0
 +-----------------+-------+
 | Property | Value |
 +-----------------+-------+
 | is_root_enabled | False |
 +-----------------+-------+</code></pre>
<pre><code>[19:59]shane@home~$ trove root-enable 95875e88-3b22-40e1-939d-86937f8651f0
 +----------+--------------------------------------+
 | Property | Value |
 +----------+--------------------------------------+
 | name | root |
 | password | 99a04946-13c7-452f-a794-bef91f1eb2b9 |
 +----------+--------------------------------------+</code></pre>
<pre><code>[19:59]shane@home~$ trove root-show 95875e88-3b22-40e1-939d-86937f8651f0
 +-----------------+-------+
 | Property | Value |
 +-----------------+-------+
 | is_root_enabled | True |
 +-----------------+-------+</code></pre>
The Trove clients makes backing up and restoring your Cloud Databases really simple too. Here's a list of the things the Trove client can do.

backup-create Creates a backup.
backup-delete Deletes a backup.
backup-list List available backups.
backup-list-instance
List available backups for an instance.
backup-show Show details of a backup.
create Creates a new instance.
database-create Creates a database on an instance.
database-delete Deletes a database.
database-list Lists available databases on an instance.
delete Deletes an instance.
flavor-list Lists available flavors.
flavor-show Show details of a flavor.
limit-list Lists the limits for a tenant.
list List all the instances.
resize-flavor Resizes the flavor of an instance.
resize-volume Resizes the volume size of an instance.
restart Restarts the instance.
root-enable Enables root for a instance.
root-show Gets root enabled status for a instance.
secgroup-add-rule Creates a security group rule.
secgroup-delete-rule
Deletes a security group rule.
secgroup-list Lists all security groups.
secgroup-show Shows details about a security group.
show Show details of an instance.
user-create Creates a user.
user-delete Deletes a user from the instance.
user-grant-access Grants access to a database(s) for a user.
user-list Lists the users for a instance.
user-revoke-access Revokes access to a database for a user.
user-show Gets a user from the instance.
user-show-access Gets a users access from the instance.
user-update-attributes
Updates a users attributes from the instance.