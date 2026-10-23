+++
author = "Shane Cunningham"
categories = ["Rackspace"]
date = 2013-05-25T20:34:33Z
description = ""
draft = false
slug = "cloud-block-storage-and-nfs"
tags = ["Rackspace"]
title = "Cloud Block Storage and NFS"

+++


With <a href="http://www.rackspace.com/cloud/">Rackspace Cloud</a> you can use <a href="http://www.rackspace.com/cloud/block-storage/">Cloud Block Storage</a> and NFS to create shared directories amongst your <a href="http://www.rackspace.com/cloud/servers/">Cloud Servers</a>. This setup was done on CentOS 6.3 and used the internal Cloud Server interfaces. First, attach your Cloud Block Storage to your Cloud Server. When I attached mine, it was designated /dev/xvdb. We will need to create a partition and format.
<pre><code>[root@nfsserver ~]# fdisk /dev/xvdb 
n #create partition 
defaults #can use defaults to use entire disk 
w #write changes
[root@nfsserver ~]# mkfs.ext4 /dev/xvdb1 #create ext4 filesystem on the partition</code></pre>
Here we create a directory to mount our Cloud Block Storage and mount it.
<pre><code>[root@nfsserver ~]# mkdir /mnt/nfs
[root@nfsserver ~]# mount /dev/xvdb1 /mnt/nfs</code></pre>
Now we can start the NSF installation on the Cloud Server that will be the NFS server.
<pre><code>[root@nfsserver ~]# yum install -y nfs-utils
[root@nfsserver ~]# chkconfig rpcbind on #rpcbind replaces portmap and needs to be running on server and client
[root@nfsserver ~]# service rpcbind start</code></pre>
/etc/exports is where we list the local directories the NFS server will share. The IP below is the IP of the <em>client</em>.
<pre><code>[root@nfsserver ~]# vim /etc/exports
/mnt/nfs        10.182.29.115(rw,sync,no_root_squash)</code></pre>
We need to open our firewall to the private IP of the client that will be accessing these shares.
<pre><code>[root@nfsserver ~]# iptables -I RH-Firewall-1-INPUT -s 10.182.29.115 -j ACCEPT
[root@nfsserver ~]# service iptables save</code></pre>
We can now start NFS
<pre><code>[root@nfsserver ~]# chkconfig nfslock on
[root@nfsserver ~]# service nfslock start
[root@nfsserver ~]# service nfs start</code></pre>
<h3>Setup on the clients.</h3>

We install nfs-utils and start rpcbind.
<pre><code>[root@nfsclient ~]# yum install -y nfs-utils
[root@nfsclient ~]# chkconfig nfslock on
[root@nfsclient ~]# chkconfig rpcbind on
[root@nfsclient ~]# chkconfig netfs on
[root@nfsclient ~]# service rpcbind start</code></pre>
Make our local directory to mount the NFS share and mount the share. The below IP is the NFS servers IP.
<pre><code>[root@nfsclient ~]# mkdir /mnt/nfs
[root@nfsclient ~]# mount -t nfs -o noatime,actimeo=3 10.180.22.69:/mnt/nfs /mnt/nfs</code></pre>
If the mount connected properly we can add an entry to our fstab so that it will mount the NFS share at bootup. The entry needs the IP of the NFS server.
<pre><code>
[root@nfsclient ~]# vim /etc/fstab
10.180.22.69:/mnt/nfs   /mnt/nfs                nfs     rw              0 0
</code></pre>
You can check your client to see if it is mounting the NFS properly. You can also run showmount -e on the NFS server to show your export list and clients.
<pre><code><strong>Client</strong>

[root@nfsclient ~]# mount
/dev/xvda1 on / type ext3 (rw,noatime,barrier=0)
proc on /proc type proc (rw)
sysfs on /sys type sysfs (rw)
devpts on /dev/pts type devpts (rw,gid=5,mode=620)
tmpfs on /dev/shm type tmpfs (rw)
none on /proc/sys/fs/binfmt_misc type binfmt_misc (rw)
none on /proc/xen type xenfs (rw)
sunrpc on /var/lib/nfs/rpc_pipefs type rpc_pipefs (rw)
<strong>10.180.22.69:/mnt/nfs on /mnt/nfs type nfs (rw,noatime,actimeo=3,vers=4,addr=10.180.22.69,clientaddr=10.182.29.115)</strong>

<strong>Server</strong>

[root@nfsserver ~]# showmount -e
Export list for shane-centos-dfw:
<strong>/mnt/nfs 10.182.29.115</strong></code></pre>
Test your NFS setup by creating a file in the NFS share directory on your client. When you run ls on the NFS server you should see the file that you just created on the client.
<pre><code><strong>Client</strong>

[root@nfsclient ~]# touch clientfile
[root@nfsclient ~]# ls -la
total 24
drwxrwxrwx 3 nfsnobody nfsnobody  4096 May 25 16:57 .
drwxr-xr-x 3 root      root       4096 May 25 16:45 ..
-rw-r--r-- 1 root      root          0 May 25 16:57 clientfile
drwxrwxrwx 2 nfsnobody nfsnobody 16384 May 16 23:59 lost+found

<strong>NFS Server</strong>

[root@fsserver ~]# ls -la /mnt/nfs/
total 24
drwxrwxrwx 3 nfsnobody nfsnobody  4096 May 25 16:57 .
drwxr-xr-x 3 root      root       4096 May 25 16:03 ..
-rw-r--r-- 1 root      root          0 May 25 16:57 clientfile
drwxrwxrwx 2 nfsnobody nfsnobody 16384 May 16 23:59 lost+found</code></pre>