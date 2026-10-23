---
title: "Use PuTTY to connect to Amazon EC2"
date: 2011-06-12T10:15:00Z
description: "Connecting PuTTY to an Amazon EC2 CentOS instance by converting the .pem key to a .ppk with PuTTYgen."
tags: ["linux", "windows"]
archived: true
---

Another I’m going to post because I’ll forget…I was messing around with Amazon EC2 and had some minor issues connecting using SSH and PuTTY. Here are the simple steps I used to connect to a CentOS EC2 instance.

Open SSH in the Security Groups section of AWS Management Console.

Download [PuTTY and PuTTYgen](http://www.chiark.greenend.org.uk/~sgtatham/putty/download.html). Open PuTTYgen and load the .pem key you downloaded from Amazon when you created the instance.

Save private key as “id_rsa-gsg-keypair.ppk”, ignore pass phrase prompt.

Open a command prompt and cd to the directory where your putty.exe is located.

```sh
putty.exe -i id_rsa-gsg-keypair.ppk root@your-amazon-public-dns.amazonaws.com
```

“your-amazon-public-dns.amazonaws.com” is your own public DNS address that you can get from AWS Management Console under Instance Actions -> Connect.

You could of course use the PuTTY GUI and select the .ppk file.

I could login is a root with CentOS, but I’ve read this might be ec2-user or something else depending on the EMI you are using.
