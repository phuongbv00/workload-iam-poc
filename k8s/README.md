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
kubectl get statefulset -n spire
kubectl get daemonset -n spire
kubectl get pods -n spire
kubectl get services -n spire
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

### Workloads Setup

#### User Service

```shell
eval $(minikube docker-env)
docker build -f ../app/user-service/Dockerfile -t wip/user-service:latest ../
```

```shell
kubectl create configmap user-service-envoy --from-file=./workload/user-service/envoy.yaml
kubectl create configmap user-service-opa-policy-config \
    --from-file=./workload/user-service/opa-config.yaml \
    --from-file=./workload/user-service/opa-policy.rego
```

```shell
kubectl apply -f workload/user-service/deployment.yaml
kubectl apply -f workload/user-service/service.yaml
```

```shell
kubectl exec -n spire spire-server-0 -- \
    /opt/spire/bin/spire-server entry create \
    -parentID spiffe://example.org/ns/spire/sa/spire-agent \
    -spiffeID spiffe://example.org/ns/default/sa/default/user-service \
    -selector k8s:ns:default \
    -selector k8s:sa:default \
    -selector k8s:pod-label:app:user-service \
    -selector k8s:container-name:envoy
```

#### LLM Agent

```shell
eval $(minikube docker-env)
docker build -f ../app/llm-agent/Dockerfile -t wip/llm-agent:latest ../
```

```shell
kubectl create configmap llm-agent-envoy --from-file=./workload/llm-agent/envoy.yaml
```

```shell
kubectl exec -n spire spire-server-0 -- \
    /opt/spire/bin/spire-server entry create \
    -parentID spiffe://example.org/ns/spire/sa/spire-agent \
    -spiffeID spiffe://example.org/ns/default/sa/default/llm-agent \
    -selector k8s:ns:default \
    -selector k8s:sa:default \
    -selector k8s:pod-label:app:llm-agent \
    -selector k8s:container-name:envoy
```

```shell
kubectl apply -f workload/llm-agent/deployment.yaml
kubectl apply -f workload/llm-agent/service.yaml
```

### Pre-test

Run dashboard for easier debugging (optional):

```shell
minikube dashboard
```

Logs user-service pod main app (if not using dashboard):

```shell
kubectl get pods --no-headers | awk '/^user-service-/{print $1}' | while read pod; do
  kubectl logs -f "$pod" -c user-service
done
```

Logs user-service pod opa (if not using dashboard):

```shell
kubectl get pods --no-headers | awk '/^user-service-/{print $1}' | while read pod; do
  kubectl logs -f "$pod" -c opa
done
```

Create a tunnel from host to llm-agent for testing:

```shell
minikube tunnel
```

### Test

1. Invoke llm-agent to test happy-case

    ```shell
    curl http://localhost:8000/demo
    ```

2. Test invalid request

   Open file `./workload/user-service/opa-policy.rego` and comment-out `DELETE` policy statement:
    ```rego
    package envoy.authz
    #...
    #allow if {
    #    startswith(http_request.path, "/users/")
    #    http_request.method == "DELETE"
    #    spiffe_id == "spiffe://example.org/ns/default/sa/default/llm-agent"
    #}
    ```

   Reset configmap:
    ```shell
    kubectl delete configmap user-service-opa-policy-config
    kubectl create configmap user-service-opa-policy-config \
        --from-file=./workload/user-service/opa-config.yaml \
        --from-file=./workload/user-service/opa-policy.rego
    ```

   Restart user-service:
    ```shell
    kubectl scale deployment user-service --replicas=0
    kubectl scale deployment user-service --replicas=1
    ```

   Invoke llm-agent:
    ```shell
    curl http://localhost:8000/demo
    ```