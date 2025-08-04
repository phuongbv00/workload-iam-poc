### Considerations When Using Minikube
```shell
minikube start \
    --extra-config=apiserver.service-account-signing-key-file=/var/lib/minikube/certs/sa.key \
    --extra-config=apiserver.service-account-key-file=/var/lib/minikube/certs/sa.pub \
    --extra-config=apiserver.service-account-issuer=api \
    --extra-config=apiserver.api-audiences=api,spire-server \
    --extra-config=apiserver.authorization-mode=Node,RBAC
```

### SPIRE Setup

```shell
kubectl apply -f spire/spire-namespace.yaml
kubectl get namespaces
```

#### SPIRE Server

```shell
kubectl apply \
    -f spire/server-account.yaml \
    -f spire/spire-bundle-configmap.yaml \
    -f spire/server-cluster-role.yaml
```

```shell
kubectl apply \
    -f spire/server-configmap.yaml \
    -f spire/server-statefulset.yaml \
    -f spire/server-service.yaml
```

#### SPIRE Agent

```shell
kubectl apply \
    -f spire/agent-account.yaml \
    -f spire/agent-cluster-role.yaml
```

```shell
kubectl apply \
    -f spire/agent-configmap.yaml \
    -f spire/agent-daemonset.yaml
```

#### Verify SPIRE Components

```shell
kubectl get statefulset --namespace spire
kubectl get daemonset --namespace spire
kubectl get pods --namespace spire
kubectl get services --namespace spire
```

#### SPIRE Registration Entries

For the node:

```shell
kubectl exec -n spire spire-server-0 -- \
    /opt/spire/bin/spire-server entry create \
    -spiffeID spiffe://example.org/ns/spire/sa/spire-agent \
    -selector k8s_psat:cluster:demo-cluster \
    -selector k8s_psat:agent_ns:spire \
    -selector k8s_psat:agent_sa:spire-agent \
    -node
```

For the workload:

```shell
kubectl exec -n spire spire-server-0 -- \
    /opt/spire/bin/spire-server entry create \
    -spiffeID spiffe://example.org/ns/default/sa/default \
    -parentID spiffe://example.org/ns/spire/sa/spire-agent \
    -selector k8s:ns:default \
    -selector k8s:sa:default
```

### MetalLB Installation

```shell
kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.13.7/config/manifests/metallb-native.yaml
```

```shell
kubectl wait --namespace metallb-system \
                --for=condition=ready pod \
                --selector=app=metallb \
                --timeout=90s
```

```shell
kubectl apply -f metallb/metallb-config.yaml
```