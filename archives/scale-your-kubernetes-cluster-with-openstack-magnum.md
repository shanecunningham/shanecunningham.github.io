+++
author = "Shane Cunningham"
categories = ["Kubernetes"]
date = 2017-02-08T11:12:34Z
description = ""
draft = false
slug = "scale-your-kubernetes-cluster-with-openstack-magnum"
tags = ["Kubernetes"]
title = "Scale your Kubernetes cluster with OpenStack Magnum"

+++


Quick post on how easy OpenStack Magnum makes scaling your Kubernetes clusters up or down. I spun up a one controller, one worker node Kubernetes cluster. Scaling this cluster up and down, where Magnum takes care of adding and removing the worker node to the cluster, is only one command each way.

```
$ kubectl cluster-info
Kubernetes master is running at https://192.168.88.233:6443
KubeUI is running at https://192.168.88.233:6443/api/v1/proxy/namespaces/kube-system/services/kube-ui

$ kubectl get nodes
NAME                                                    STATUS                     AGE
10.0.0.3                                                Ready,SchedulingDisabled   6m
ku-ptzjkk2wew-0-b2tsvzrd63o4-kube-minion-uol3nin7zndb   Ready                      4m

root@infra01-utility-container-e6fba879:~# nova list
+--------------------------------------+-------------------------------------------------------+--------+------------+-------------+----------------------------------+
| ID                                   | Name                                                  | Status | Task State | Power State | Networks                         |
+--------------------------------------+-------------------------------------------------------+--------+------------+-------------+----------------------------------+
| 643e4ad8-a9db-44c8-b236-8536efc5fc44 | ku-4b3scjlreg-0-jvxjrtd2b7lg-kube-master-wri52qlujljn | ACTIVE | -          | Running     | private=10.0.0.3, 192.168.88.233 |
| 0aa58f68-b05c-4c3d-b54b-93848132d2f4 | ku-ptzjkk2wew-0-b2tsvzrd63o4-kube-minion-uol3nin7zndb | ACTIVE | -          | Running     | private=10.0.0.4, 192.168.88.227 |
+--------------------------------------+-------------------------------------------------------+--------+------------+-------------+----------------------------------+
``` 

We use the cluster-update command to add another worker node.

```
root@infra01-utility-container-e6fba879:~# magnum cluster-update kubernetes replace node_count=2

root@infra01-utility-container-e6fba879:~# magnum cluster-list
+--------------------------------------+------------+------------+--------------+--------------------+
| uuid                                 | name       | node_count | master_count | status             |
+--------------------------------------+------------+------------+--------------+--------------------+
| 1f9b9f78-d707-482e-b7e7-021e5250f3e4 | kubernetes | 2          | 1            | UPDATE_IN_PROGRESS |
+--------------------------------------+------------+------------+--------------+--------------------+
```

Once complete we have another worker node instance and Kubernetes now has two worker nodes it can use to deploy your applications.

```
$ kubectl get nodes
NAME                                                    STATUS                     AGE
10.0.0.3                                                Ready,SchedulingDisabled   26m
ku-ptzjkk2wew-0-b2tsvzrd63o4-kube-minion-uol3nin7zndb   Ready                      24m
ku-ptzjkk2wew-1-xftlqmufmfbw-kube-minion-5dzkg7qmxeoo   Ready                      43s

root@infra01-utility-container-e6fba879:~# nova list
+--------------------------------------+-------------------------------------------------------+--------+------------+-------------+----------------------------------+
| ID                                   | Name                                                  | Status | Task State | Power State | Networks                         |
+--------------------------------------+-------------------------------------------------------+--------+------------+-------------+----------------------------------+
| 643e4ad8-a9db-44c8-b236-8536efc5fc44 | ku-4b3scjlreg-0-jvxjrtd2b7lg-kube-master-wri52qlujljn | ACTIVE | -          | Running     | private=10.0.0.3, 192.168.88.233 |
| 0aa58f68-b05c-4c3d-b54b-93848132d2f4 | ku-ptzjkk2wew-0-b2tsvzrd63o4-kube-minion-uol3nin7zndb | ACTIVE | -          | Running     | private=10.0.0.4, 192.168.88.227 |
| 9775879c-1371-4668-bbb8-3d2cd4185da3 | ku-ptzjkk2wew-1-xftlqmufmfbw-kube-minion-5dzkg7qmxeoo | ACTIVE | -          | Running     | private=10.0.0.5, 192.168.88.228 |
+--------------------------------------+-------------------------------------------------------+--------+------------+-------------+----------------------------------+

root@infra01-utility-container-e6fba879:~# magnum cluster-list
+--------------------------------------+------------+------------+--------------+-----------------+
| uuid                                 | name       | node_count | master_count | status          |
+--------------------------------------+------------+------------+--------------+-----------------+
| 1f9b9f78-d707-482e-b7e7-021e5250f3e4 | kubernetes | 2          | 1            | UPDATE_COMPLETE |
+--------------------------------------+------------+------------+--------------+-----------------+

root@infra01-utility-container-e6fba879:~# magnum cluster-show 1f9b9f78-d707-482e-b7e7-021e5250f3e4
+---------------------+------------------------------------------------------------+
| Property            | Value                                                      |
+---------------------+------------------------------------------------------------+
| status              | UPDATE_COMPLETE                                            |
| cluster_template_id | b27777df-9583-4885-a8e5-d864d4dfd519                       |
| node_addresses      | ['192.168.88.227', '192.168.88.228']                       |
| uuid                | 1f9b9f78-d707-482e-b7e7-021e5250f3e4                       |
| stack_id            | c2eaa062-37af-4d70-b67c-7e25aa9159ae                       |
| status_reason       | Stack UPDATE completed successfully                        |
| created_at          | 2017-02-07T03:31:26+00:00                                  |
| updated_at          | 2017-02-07T03:59:42+00:00                                  |
| coe_version         | v1.2.0                                                     |
| keypair             | magnum-kubernetes-key                                      |
| api_address         | https://192.168.88.233:6443                                |
| master_addresses    | ['192.168.88.233']                                         |
| create_timeout      | 60                                                         |
| node_count          | 2                                                          |
| discovery_url       | https://discovery.etcd.io/e228b24e33b90fb36a04f16bb2fbdf76 |
| master_count        | 1                                                          |
| container_version   | 1.9.1                                                      |
| name                | kubernetes                                                 |
+---------------------+------------------------------------------------------------+
```

Decreasing the cluster is just as simple.

```
root@infra01-utility-container-e6fba879:~# magnum cluster-update kubernetes replace node_count=1

root@infra01-utility-container-e6fba879:~# magnum cluster-list
+--------------------------------------+------------+------------+--------------+-----------------+
| uuid                                 | name       | node_count | master_count | status          |
+--------------------------------------+------------+------------+--------------+-----------------+
| 62710f47-3482-48b7-8a30-fb13fee021fe | kubernetes | 1          | 1            | UPDATE_COMPLETE |
+--------------------------------------+------------+------------+--------------+-----------------+

root@infra01-utility-container-e6fba879:~# nova list
+--------------------------------------+-------------------------------------------------------+--------+------------+-------------+----------------------------------+
| ID                                   | Name                                                  | Status | Task State | Power State | Networks                         |
+--------------------------------------+-------------------------------------------------------+--------+------------+-------------+----------------------------------+
| 643e4ad8-a9db-44c8-b236-8536efc5fc44 | ku-4b3scjlreg-0-jvxjrtd2b7lg-kube-master-wri52qlujljn | ACTIVE | -          | Running     | private=10.0.0.3, 192.168.88.225 |
| 0aa58f68-b05c-4c3d-b54b-93848132d2f4 | ku-ptzjkk2wew-0-b2tsvzrd63o4-kube-minion-uol3nin7zndb | ACTIVE | -          | Running     | private=10.0.0.4, 192.168.88.227 |
+--------------------------------------+-------------------------------------------------------+--------+------------+-------------+----------------------------------+
```

In this example I was working with a single Kubernetes cluster named 'kubernetes'. OpenStack Magnum makes managing multiple clusters very simple. You can use the tool to manage Docker Swarm, Mesos and Kubernetes clusters, and as long as you have the compute resources, scale when you need to.