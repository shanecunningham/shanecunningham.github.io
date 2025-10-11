+++
author = "Shane Cunningham"
date = 2012-03-29T03:17:26Z
description = ""
draft = false
slug = "two-linux-notes"
title = "Two Linux notes"

+++


<strong>SSH Tunnel for web traffic</strong>

<pre><code>ssh -D 9998 -C shane@myserver.com</code></pre>

Where "myserver.com" is a server you operate with SSH setup. Now you need to configure your browser to use the tunnel. In OS X you can go to Network -&gt; Advanced -&gt; Proxies -&gt; Check SOCKS and input <code>localhost:9998</code> or whatever port you used. Directly from Chrome you can also select Preferences -&gt; Under The Hood -&gt; Change Proxy Settings... -&gt; and it will go directly to your OS X Network/Proxies tab.

Compare your IP address at any of the check IP sites, I like <a title="canihazip.com" href="http://canihazip.com/">canihazip.com</a>. It should be the IP of your SSH server and not your coffee shop/hotel/wherever you are connected.

<strong>Visualize your running processes</strong>

<pre><code>pstree -p</code></pre>

I just learned this command today, it gives you a visual tree like look at your processes running. I don't have very many processes running on my VPS so this is a quick way I can check which SSHD process I just ran this command from so I can kill a different SSHD process. Probably not the most efficient way to do that but it works!  :)