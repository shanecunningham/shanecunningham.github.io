+++
author = "Shane Cunningham"
date = 2017-10-22T11:32:17Z
description = ""
draft = false
slug = "self-hosted-kubernetes-with-terraform-tectonic-installer"
title = "Self-hosted Kubernetes with Tectonic-Installer"

+++


This is more of an update to my [previous post on deploying a self-hosted Kubernetes](https://cunninghamshane.com/bare-metal-self-hosted-kubernetes/) cluster using Bootkube/Matchbox. Since then there's been some updates and CoreOS has open sourced their tectonic-installer project. This adds Terraform, so the full stack for the bare-metal provider is Terraform -> Matchbox -> Bootkube -> Tectonic assets/manifests. 

This time I created a Container Linux VM to act as the PXE and deployment host. All of this is from readily available documentation, compiled down to what you need to get up and running quickly. I have two physical servers, one will act as the controller [node1] and the other as the worker [node2]. 

#### Setup Matchbox

```
# wget https://github.com/coreos/matchbox/releases/download/v0.6.1/matchbox-v0.6.1-linux-amd64.tar.gz
# wget https://github.com/coreos/matchbox/releases/download/v0.6.1/matchbox-v0.6.1-linux-amd64.tar.gz.asc
# gpg --keyserver pgp.mit.edu --recv-key 18AD5014C99EF7E3BA5F6CE950BDD3E0FC8A365E
# gpg --verify matchbox-v0.6.1-linux-amd64.tar.gz.asc matchbox-v0.6.1-linux-amd64.tar.gz
# tar xzvf matchbox-v0.6.1-linux-amd64.tar.gz
# cd matchbox-v0.6.1-linux-amd64
# cp contrib/systemd/matchbox-for-tectonic.service /etc/systemd/system/matchbox.service
# sed -i 's/0.6.0/0.6.1/g' /etc/systemd/system/matchbox.service
# cd scripts/tls
# export SAN=DNS.1:tectonic-installer,IP.1:192.168.88.12
# ./cert-gen
# mkdir /etc/matchbox
# cp ca.crt server.crt server.key /etc/matchbox
# systemctl daemon-reload
# systemctl start matchbox
```

##### Verify Matchbox

```
# tectonic-installer matchbox-v0.6.1-linux-amd64 # rkt list
UUID		APP		IMAGE NAME			STATE		CREATED		STARTED		NETWORKS
de9762ff	matchbox	quay.io/coreos/matchbox:v0.6.1	running		2 days ago	2 days ago

# tectonic-installer matchbox-v0.6.1-linux-amd64 # dig +short tectonic-installer
192.168.88.12

# tectonic-installer matchbox-v0.6.1-linux-amd64 # curl http://tectonic-installer:8080
matchbox
```

##### Setup dnsmasq

This is optional of course, but if you don't have any other PXE server available this little container can get it done easily. 

```
# rkt trust --prefix "quay.io/coreos/dnsmasq"
```

```
# cat << 'EOF' > /etc/systemd/system/dnsmasq.service
[Unit]
Description=dnsmasq server

[Service]
Environment="IMAGE=quay.io/coreos/dnsmasq"
Environment="TECHOSTNAME=tectonic-installer"
Environment="TECIP=192.168.88.12"
ExecStart=/usr/bin/rkt run \
  --net=host \
  ${IMAGE} \
  --caps-retain=CAP_NET_ADMIN,CAP_NET_BIND_SERVICE,CAP_SETGID,CAP_SETUID,CAP_NET_RAW \
  -- -d -q \
  --dhcp-range=192.168.88.105,192.168.88.110 \
  --enable-tftp \
  --tftp-root=/var/lib/tftpboot \
  --dhcp-userclass=set:ipxe,iPXE \
  --dhcp-boot=tag:#ipxe,undionly.kpxe \
  --dhcp-boot=tag:ipxe,http://${TECIP}:8080/boot.ipxe \
  --address=/${TECHOSTNAME}/${TECIP} \
  --log-queries \

[Install]
WantedBy=multi-user.target
EOF
```
```
# systemctl daemon-reload
# systemctl start dnsmasq
```

You should have two rkt containers running.

```
tectonic-installer tls # rkt list
UUID		APP		IMAGE NAME			STATE		CREATED		STARTED		NETWORKS
296289c5	dnsmasq		quay.io/coreos/dnsmasq:latest	running		52 seconds ago	52 seconds ago
4863a784	matchbox	quay.io/coreos/matchbox:v0.6.1	running		13 minutes ago	13 minutes ago
```

##### Get Container Linux image

Download Container Linux image for PXE boot. 

```
# cd ~/matchbox-v0.6.1-linux-amd64
# mkdir -p /var/lib/matchbox/assets
# ./scripts/get-coreos stable 1520.6.0 /var/lib/matchbox/assets
```

##### Setup tectonic-installer

```
# cd ~
# wget https://releases.tectonic.com/releases/tectonic_1.7.5-tectonic.1.tar.gz
# tar xzvf tectonic_1.7.5-tectonic.1.tar.gz
# cd tectonic
# export INSTALLER_PATH=$(pwd)/tectonic-installer/linux/installer
# export PATH=$PATH:$(pwd)/tectonic-installer/linux
# terraform version
Terraform v0.10.4
```

##### Setup Terraform

```
# terraform init ./platforms/metal
# export CLUSTER=home-cluster
# mkdir -p build/${CLUSTER}
# cp examples/terraform.tfvars.metal build/${CLUSTER}/terraform.tfvars
```

I found it a bit frustrating finding the correct variables that worked. I'd rather not say how many times I ran `terraform plan` with 0 errors only to run into constant errors on `terraform apply`. Also, I found golang/terraform debug messages to be lacking to say the least. Coming from mostly debugging OpenStack and Python, I found the error messages difficult to even figure out where to look for a problem. I'm not exactly sure if it's more on the terraform or golang side (and me being a go newbie), but I'm sure this will improve. 

Some of these you might not need, but tectonic-installer requires them. Others stated they were required, but it worked fine without them. This is probably an issue with the documentation and the fact I didn't know exactly which variables I needed only for the opensource tectonic-installer and which went to the Tectonic Installer GUI. To further confuse this, some of these variables explicitly state they are for cloud providers, but this is the bare-metal example file. These variables worked for my install, you'll have to edit as needed.

```
// The e-mail address used to:
// 1. login as the admin user to the Tectonic Console.
// 2. generate DNS zones for some providers.
//
// Note: This field MUST be set manually prior to creating the cluster.
tectonic_admin_email = "shane.c82@gmail.com"

// The bcrypt hash of admin user password to login to the Tectonic Console.
// Use the bcrypt-hash tool (https://github.com/coreos/bcrypt-tool/releases/tag/v1.0.0) to generate it.
//
// Note: This field MUST be set manually prior to creating the cluster.
tectonic_admin_password_hash = "yourpwhash"

// The Container Linux update channel.
//
// Examples: `stable`, `beta`, `alpha`
tectonic_cl_channel = "stable"

// This declares the IP range to assign Kubernetes pod IPs in CIDR notation.
tectonic_cluster_cidr = "10.2.0.0/16"

// The name of the cluster.
// If used in a cloud-environment, this will be prepended to `tectonic_base_domain` resulting in the URL to the Tectonic console.
//
// Note: This field MUST be set manually prior to creating the cluster.
// Warning: Special characters in the name like '.' may cause errors on OpenStack platforms due to resource name constraints.
tectonic_cluster_name = "home-cluster"

// If set to true, experimental Tectonic assets are being deployed.
tectonic_experimental = true

// CoreOS kernel/initrd version to PXE boot.
// Must be present in Matchbox assets and correspond to `tectonic_cl_channel`.
//
// Example: `1298.7.0`
tectonic_metal_cl_version = "1520.6.0"

// The domain name which resolves to controller node(s)
//
// Example: `cluster.example.com`
tectonic_metal_controller_domain = "node1"

// Ordered list of controller domain names.
//
// Example: `["node2.example.com", "node3.example.com"]`
tectonic_metal_controller_domains = ["node1"]

// Ordered list of controller MAC addresses for matching machines.
//
// Example: `["52:54:00:a1:9c:ae"]`
tectonic_metal_controller_macs = ["44:39:c4:53:4c:39"]

// Ordered list of controller names.
//
// Example: `["node1"]`
tectonic_metal_controller_names = ["node1"]

// The content of the Matchbox CA certificate to trust.
// /etc/matchbox/ca.crt

tectonic_metal_matchbox_ca = <<EOF
-----BEGIN CERTIFICATE-----

...

-----END CERTIFICATE-----
EOF

// The content of the Matchbox client TLS certificate.
// ~/matchbox-v0.6.1-linux-amd64/scripts/tls/client.crt

tectonic_metal_matchbox_client_cert = <<EOF
-----BEGIN CERTIFICATE-----

...

-----END CERTIFICATE-----
EOF

// The content of the Matchbox client TLS key.
// ~/matchbox-v0.6.1-linux-amd64/scripts/tls/client.key

tectonic_metal_matchbox_client_key = <<EOF
-----BEGIN RSA PRIVATE KEY-----

...

-----END RSA PRIVATE KEY-----
EOF

// Matchbox HTTP read-only URL.
//
// Example: `e.g. http://matchbox.example.com:8080`
tectonic_metal_matchbox_http_url = "http://tectonic-installer:8080"

// The Matchbox gRPC API endpoint.
//
// Example: `matchbox.example.com:8081`
tectonic_metal_matchbox_rpc_endpoint = "tectonic-installer:8081"

// Ordered list of worker domain names.
//
// Example: `["node2.example.com", "node3.example.com"]`
tectonic_metal_worker_domains = ["node2"]

// Ordered list of worker MAC addresses for matching machines.
//
// Example: `["52:54:00:b2:2f:86", "52:54:00:c3:61:77"]`
tectonic_metal_worker_macs = ["D4:AE:52:C8:A1:8D"]

// Ordered list of worker names.
//
// Example: `["node2", "node3"]`
tectonic_metal_worker_names = ["node2"]

// This declares the IP range to assign Kubernetes service cluster IPs in CIDR notation. The maximum size of this IP range is /12
tectonic_service_cidr = "10.3.0.0/16"

// SSH public key to use as an authorized key.
//
// Example: `ssh-rsa AAAB3N...`
tectonic_ssh_authorized_key = "ssh-rsa AAAAB3NzaC1y...root@tectonic-installer"

// The Tectonic statistics collection URL to which to report.
tectonic_stats_url = "https://stats-collector.tectonic.com"

// If set to true, a vanilla Kubernetes cluster will be deployed, omitting any Tectonic assets.
tectonic_vanilla_k8s = true
```

##### Terraform apply/plan

```
# eval $(ssh-agent)
# ssh-add
# terraform plan -var-file=build/${CLUSTER}/terraform.tfvars platforms/metal
# terraform apply -var-file=build/${CLUSTER}/terraform.tfvars platforms/metal
```

At this point you should be able to reboot your servers and they, hopefully, will PXE boot, install Container Linux, reboot and then start laying down the files and setting up self-hosted Kubernetes. Both servers need to have Container Linux running post reboot, and your deployment host needs to be able to SSH to the nodes to drop the manifests/tls and other assets onto them. Once that's done, bootkube takes over and creates a temporary control plane, bootstraps the permanent control plane and then stops the bootkube container. The worker node should automatically join the cluster with the asset files that were put onto it.

The kubeconfig you can use to access the cluster can be found here:

```
tectonic-installer tectonic # ls -la generated/auth/kubeconfig
-rwxr-xr-x. 1 root root 6001 Oct 22 03:58 generated/auth/kubeconfig
```

```
# kubectl cluster-info
Kubernetes master is running at https://node1:443
KubeDNS is running at https://node1:443/api/v1/namespaces/kube-system/services/kube-dns/proxy

To further debug and diagnose cluster problems, use 'kubectl cluster-info dump'.

# kubectl get nodes
NAME      STATUS    ROLES     AGE       VERSION
node1     Ready     master    10m       v1.7.5+coreos.1
node2     Ready     node      10m       v1.7.5+coreos.1
```

This is a little older version of Kubernetes, so I'm going to play around with this and see if I can do an in-place upgrade to 1.8.1, and see if updating the manifests file to 1.8.1 before running apply will allow a new install of that version. The process is a little more streamlined and I'm sure you can find other ways to automate portions of this process, but hopefully it gave you a quick view into how simple CoreOS has made PXE booting bare-metal servers and getting a self-hosted Kubernetes cluster running. 