---
title: "Two Linux notes"
date: 2012-03-29T03:17:26Z
description: "Routing browser traffic through an SSH SOCKS tunnel with ssh -D, and viewing the process tree with pstree -p."
tags: ["linux", "networking"]
---

**SSH Tunnel for web traffic**

```sh
ssh -D 9998 -C shane@myserver.com
```

Where "myserver.com" is a server you operate with SSH setup. Now you need to configure your browser to use the tunnel. In OS X you can go to Network -> Advanced -> Proxies -> Check SOCKS and input `localhost:9998` or whatever port you used. Directly from Chrome you can also select Preferences -> Under The Hood -> Change Proxy Settings... -> and it will go directly to your OS X Network/Proxies tab.

Compare your IP address at any of the check IP sites, I like [canihazip.com](http://canihazip.com/). It should be the IP of your SSH server and not your coffee shop/hotel/wherever you are connected.

**Visualize your running processes**

```sh
pstree -p
```

I just learned this command today, it gives you a visual tree like look at your processes running. I don't have very many processes running on my VPS so this is a quick way I can check which SSHD process I just ran this command from so I can kill a different SSHD process. Probably not the most efficient way to do that but it works!  :)
