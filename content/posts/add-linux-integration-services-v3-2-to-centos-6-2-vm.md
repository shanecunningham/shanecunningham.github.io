---
title: "Add Linux Integration Services v3.2 to CentOS 6.2 VM"
date: 2012-03-23T02:55:21Z
tags: []
---

Here are the steps to install [Linux Integration Services v3.2](http://www.microsoft.com/download/en/details.aspx?id=28188) to a CentOS 6.2 VM in Hyper-V.

Add the Linux IC v3.2.iso to a CD-Rom attached to your CentOS 6.2 VM.

```sh
mount /dev/cdrom /media
```

Create a directory, for example, `mkdir /home/LinuxServices`

```sh
cp /media/* /home/LinuxServices
cd /home/LinuxServices
./install.sh
```
