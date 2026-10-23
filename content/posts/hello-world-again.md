---
title: "Hello, world (again)"
date: 2026-10-23T00:00:00-05:00
description: "The blog has a new look and a fresh start, plus four kubectl one-liners for a quick read on any cluster."
tags: ["kubernetes", "meta"]
---

This blog has been offline and online a few times since 2010, through WordPress, Ghost and Hugo. It's back with a new look and a fresh start.

Everything I wrote before now is still here and marked as [archived](/archive/). Those posts are kept as they were written, so expect old versions of ESXi, OpenStack and friends. New posts start here.

Every hello world needs a hello world, so here's one from a Kubernetes cluster.

## Say hello

One line that greets you with every node and the kubelet version it runs:

```sh
kubectl get nodes -o json | jq -r '"hello, world from \(.items | length) nodes: " + ([.items[] | "\(.metadata.name) (\(.status.nodeInfo.kubeletVersion))"] | join(", "))'
```

```text
hello, world from 3 nodes: cp-1 (v1.34.1), worker-1 (v1.34.1), worker-2 (v1.33.5)
```

A greeting that doubles as an upgrade check: `worker-2` is a minor version behind.

## And a few that earn their keep

**Version skew at a glance.** Same data, grouped, for clusters with more than a handful of nodes:

```sh
kubectl get nodes -o json | jq -r '[.items[].status.nodeInfo.kubeletVersion] | group_by(.) | map("\(.[0]) x\(length)") | join("  ")'
```

```text
v1.33.5 x1  v1.34.1 x2
```

**Who keeps restarting.** Total restarts per pod across all its containers, worst first, zeros skipped:

```sh
kubectl get pods -A -o json | jq -r '.items[] | [([.status.containerStatuses[]?.restartCount] | add // 0), "\(.metadata.namespace)/\(.metadata.name)"] | select(.[0] > 0) | @tsv' | sort -rn | head
```

```text
15	shop/api-7d9f
2	shop/web-55c
```

**What's actually unhappy.** `--field-selector=status.phase!=Running` misses the classic case: a pod in `CrashLoopBackOff` still reports phase `Running`. This looks at container readiness instead, skips finished Job pods, and says why each pod is stuck:

```sh
kubectl get pods -A -o json | jq -r '.items[] | select(.status.phase != "Succeeded") | select((.status.containerStatuses // [{}]) | any(.ready != true)) | ["\(.metadata.namespace)/\(.metadata.name)", .status.phase, ([.status.containerStatuses[]? | select(.ready != true) | .state.waiting.reason // .state.terminated.reason // "NotReady"] | join(",") | if . == "" then "Unscheduled" else . end)] | @tsv' | column -t
```

```text
shop/api-7d9f  Running  CrashLoopBackOff
shop/cache-0   Pending  Unscheduled
shop/img-x     Pending  ImagePullBackOff
```

All four need only `kubectl` and `jq`, and they're read-only, so they're safe to run against any cluster you can reach.

More soon.
