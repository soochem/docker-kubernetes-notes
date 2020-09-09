# Install KFServing

## 1. Prerequisite
* Kubernetes : v1.14.10-gke.27 --> v1.15.9 (for KNative)
  - HTTP Load Balancing : The HTTP Load Balancing add-on is required to use the Google Cloud Load Balancer with Kubernetes Ingress.
      - If enabled, a controller will be installed to coordinate applying load balancing configuration changes to your GCP project
  - Anthos Cloud Run : Anthos is a hybrid and multi-cloud application
      platform developed and supported by Google.
      Anthos is built on open source technologies, including Kubernetes, Istio, and Knative.
* Knative Serving & Istio
  - Knative depends on **Istio Ingress Gateway** to route requests to Knative services.
* ref.
    [Developer Guide](https://github.com/kubeflow/kfserving/blob/master/docs/DEVELOPER_GUIDE.md)

### 1.1. Istio v1.1.6+
- Version : 1.4.6 --> 1.3.1
    - If you want to get up running Knative quickly or you do not need service mesh,
        we recommend installing Istio without service mesh(sidecar injection)
    - **For Istio use versions 1.1.6 and 1.3.1 which have been tested, and for Kubernetes use 1.15+**
        (ref. [Developer Guide - Install KNative](https://github.com/kubeflow/kfserving/blob/master/docs/DEVELOPER_GUIDE.md#install-knative-on-a-kubernetes-cluster))
- Istio 다운로드 및 CRD 설치
   ```
   # Download and unpack Istio
   export ISTIO_VERSION=1.3.1
   curl -L https://git.io/getLatestIstio | sh -
   cd istio-${ISTIO_VERSION}
  
   for i in install/kubernetes/helm/istio-init/files/crd*yaml; do kubectl apply -f $i; done
  
   cat <<EOF | kubectl apply -f -
   apiVersion: v1
   kind: Namespace
   metadata:
     name: istio-system
     labels:
       istio-injection: disabled
   EOF
   ```

- Without Sidecar Injection
  ```
   # A lighter template, with just pilot/gateway.
   # Based on install/kubernetes/helm/istio/values-istio-minimal.yaml
   helm template --namespace=istio-system \
     --set prometheus.enabled=false \
     --set mixer.enabled=false \
     --set mixer.policy.enabled=false \
     --set mixer.telemetry.enabled=false \
     `# Pilot doesn't need a sidecar.` \
     --set pilot.sidecar=false \
     --set pilot.resources.requests.memory=128Mi \
     `# Disable galley (and things requiring galley).` \
     --set galley.enabled=false \
     --set global.useMCP=false \
     `# Disable security / policy.` \
     --set security.enabled=false \
     --set global.disablePolicyChecks=true \
     `# Disable sidecar injection.` \
     --set sidecarInjectorWebhook.enabled=false \
     --set global.proxy.autoInject=disabled \
     --set global.omitSidecarInjectorConfigMap=true \
     --set gateways.istio-ingressgateway.autoscaleMin=1 \
     --set gateways.istio-ingressgateway.autoscaleMax=2 \
     `# Set pilot trace sampling to 100%` \
     --set pilot.traceSampling=100 \
     --set global.mtls.auto=false \
     install/kubernetes/helm/istio \
     > ./istio-lean.yaml
   ```
  - `kubectl apply -f istio-lean.yaml`
  
### 1.2. Knative Serving v0.11.1+
- [설치 방법](https://knative.dev/docs/install/any-kubernetes-cluster/)
- Currently only Knative Serving is required, cluster-local-gateway is required
    to serve cluster-internal traffic for transformer and explainer use cases.
    Please follow instructions here to install cluster local gateway
1. Knative Serving
    - CRD 설치  
       `kubectl apply --filename https://github.com/knative/serving/releases/download/v0.14.0/serving-crds.yaml`
       `kubectl apply --filename https://github.com/knative/serving/releases/download/v0.14.0/serving-core.yaml`
    - Network layer 선택
       `kubectl apply --filename https://github.com/knative/net-istio/releases/download/v0.14.0/release.yaml`
       `kubectl --namespace istio-system get service istio-ingressgateway`
    - DNS 설정
       - Real DNS : curl 사용하고, Magic DNS 사용 불가할 때
       -- `kubectl get ksvc`
       --`curl -H "Host: helloworld-go.default.example.com" http://192.168.39.228:32198`
       --   - output : `Hello Go Sample v1!`
        ```
        # Here knative.example.com is the domain suffix for your cluster
        *.knative.example.com == A {external_ip}
        
        Once your DNS provider has been configured, direct Knative to use that domain:
        
        # Replace knative.example.com with your domain suffix
        kubectl patch configmap/config-domain \
          --namespace knative-serving \
          --type merge \
          --patch '{"data":{"knative.example.com":""}}'
        ```
    - Knative Serving Components 설치 확인
       `$ kubectl get pods --namespace knative-serving`
   
2. Eventing
    - Eventing Components 설치 확인
        `$ kubectl get pods --namespace knative-eventing`

3. Monitoring 
    - Monitoring Components 설치 확인
        `$ kubectl get pods --namespace knative-monitoring`
  
- Cluster Local Gateway 업데이트
  - [설치 방법](https://knative.dev/docs/install/installing-istio/#updating-your-install-to-use-cluster-local-gateway)
  1. helm 사용
      ```
       # Add the extra gateway.
       helm template --namespace=istio-system \
         --set gateways.custom-gateway.autoscaleMin=1 \
         --set gateways.custom-gateway.autoscaleMax=2 \
         --set gateways.custom-gateway.cpu.targetAverageUtilization=60 \
         --set gateways.custom-gateway.labels.app='cluster-local-gateway' \
         --set gateways.custom-gateway.labels.istio='cluster-local-gateway' \
         --set gateways.custom-gateway.type='ClusterIP' \
         --set gateways.istio-ingressgateway.enabled=false \
         --set gateways.istio-egressgateway.enabled=false \
         --set gateways.istio-ilbgateway.enabled=false \
         --set global.mtls.auto=false \
         install/kubernetes/helm/istio \
         -f install/kubernetes/helm/istio/example-values/values-istio-gateways.yaml \
         | sed -e "s/custom-gateway/cluster-local-gateway/g" -e "s/customgateway/clusterlocalgateway/g" \
         > ./istio-local-gateway.yaml
      
       kubectl apply -f istio-local-gateway.yaml
       ```
       ```
        output:
            poddisruptionbudget.policy/cluster-local-gateway created
            serviceaccount/cluster-local-gateway-service-account created
            serviceaccount/istio-multi unchanged
            clusterrole.rbac.authorization.k8s.io/istio-reader unchanged
            clusterrolebinding.rbac.authorization.k8s.io/istio-multi unchanged
            service/cluster-local-gateway created
            deployment.apps/cluster-local-gateway created
        ```
        
  2. 개발 목적  
      ```
       # Istio minor version should be 1.2 or 1.3
       export ISTIO_MINOR_VERSION=1.2 
       export VERSION=$(curl https://raw.githubusercontent.com/knative/serving/master/third_party/istio-${ISTIO_MINOR_VERSION}-latest)    
       kubectl apply -f https://raw.githubusercontent.com/knative/serving/master/third_party/${VERSION}/istio-knative-extras.yaml
       ```
  
### 1.3. Cert Manager v1.12.0+
- [설치 방법](https://cert-manager.io/docs/installation/kubernetes/)
- CRD 설치 (Kubernetes 1.15+)
   `$ kubectl apply --validate=false -f https://github.com/jetstack/cert-manager/releases/download/v0.15.0/cert-manager.yaml`
   ```
   kubectl create clusterrolebinding cluster-admin-binding \
   --clusterrole=cluster-admin \
   --user=$(gcloud config get-value core/account)
   ```
- 설치 확인
   `kubectl get pods --namespace cert-manager`
   
## KFServing
- KFServing 설치
    ```
    TAG=0.2.2
    CONFIG_URI=https://raw.githubusercontent.com/kubeflow/kfserving/master/install/$TAG/kfserving.yaml
    kubectl apply -f ${CONFIG_URI}
    
    # For kubernetes 1.14
    env:
    - name: ENABLE_WEBHOOK_NAMESPACE_SELECTOR
      value: enabled
    
    # For Kubernetes 1.15
    $ kubectl patch \
    mutatingwebhookconfiguration inferenceservice.serving.kubeflow.org \
    --patch '{"webhooks":[{"name": "inferenceservice.kfserving-webhook-server.pod-mutator","objectSelector":{"matchExpressions":[{"key":"serving.kubeflow.org/inferenceservice", "operator": "Exists"}]}}]}'
    mutatingwebhookconfiguration.admissionregistration.k8s.io/inferenceservice.serving.kubeflow.org patched
    ```
    - ref. [standalone-kfserving-installation](https://github.com/kubeflow/kfserving#standalone-kfserving-installation)   
    - 설치 확인
        `$ kubectl get po -n kfserving-system`
        ```
        output: 
            NAME                             READY   STATUS    RESTARTS   AGE
            kfserving-controller-manager-0   2/2     Running   1          4m54s
        ```
- SDK 설치
    - `$ pip install kfserving`
    - SDK 예제
        https://github.com/kubeflow/kfserving/blob/master/docs/samples/client/kfserving_sdk_sample.ipynb
 
 ### Inference
- InferenceService Quick Starts (Istio 1.4.6 -> 1.3.1)
    ```
    # Wait all pods to be ready then launch KFServing InferenceService.
    $ kubectl apply -f docs/samples/sklearn/sklearn.yaml
    $ Check KFServing InferenceService status.
    $ kubectl get inferenceservices sklearn-iris
    NAME           URL                                                              READY   DEFAULT TRAFFIC   CANARY TRAFFIC   AGE
    sklearn-iris   http://sklearn-iris.default.example.com/v1/models/sklearn-iris   True    100                                109s
    
    # Curl the InferenceService
    $ kubectl port-forward --namespace istio-system $(kubectl get pod \
            --namespace istio-system \
            --selector="app=istio-ingressgateway" \
            --output jsonpath='{.items[0].metadata.name}') 8080:80
    $ curl -v -H "Host: sklearn-iris.default.example.com" http://localhost:8080/v1/models/sklearn-iris:predict -d @./docs/samples/sklearn/iris-input.json
    
    # To use External IP (NodePort OR LoadBalancer)
    $ curl -v -H "Host: sklearn-iris.default.example.com" http://{external_ip}:8080/v1/models/sklearn-iris:predict -d @./docs/samples/sklearn/iris-input.json  
    ```

- Debug (LoadBalancer 사용)
    - Resource list
        ```
        $ kubectl get inferenceservices sklearn-iris -n sklearn
        NAME           URL                                                              READY   DEFAULT TRAFFIC   CANARY TRAFFIC   AGE
        sklearn-iris   http://sklearn-iris.sklearn.example.com/v1/models/sklearn-iris   True    100                                16s
        
        $ kubectl get svc -n istio-system
        NAME                    TYPE           CLUSTER-IP   EXTERNAL-IP    PORT(S)
        cluster-local-gateway   ClusterIP      10.0.27.9    <none>         80/TCP,443/TCP,31400/TCP
        ,15011/TCP,8060/TCP,15029/TCP,15030/TCP,15031/TCP,15032/TCP                         
        istio-ingressgateway    LoadBalancer   10.0.24.46   {external_ip}   15020:32216/TCP,80:31380
        /TCP,443:31390/TCP,31400:31400/TCP,15029:30115/TCP,15030:30524/TCP,15031:30321/TCP,15032:30
        193/TCP,15443:31130/TCP 
        istio-pilot             ClusterIP      10.0.31.8    <none>         15010/TCP,15011/TCP,8080
        /TCP,15014/TCP
        ```
    - Inference Request
        ```
        $ curl -v -H "Host: sklearn-iris.sklearn.example.com" http://{external_ip}:31380/v1/models/sklearn-iris:predict 
        ```
        ```
        output:
            $ curl -v -H "Host: sklearn-iris.sklearn.example.com" http://{external_ip}:31380/v1/models/sklearn-iris:predict -d @./iris-input.json
     
            * About to connect() to {external_ip} port 31380 (#0)
            *   Trying {external_ip}...
            * Connected to {external_ip} ({external_ip}) port 31380 (#0)
            > POST /v1/models/sklearn-iris:predict HTTP/1.1
            > User-Agent: curl/7.29.0
            > Accept: */*
            > Host: sklearn-iris.sklearn.example.com
            > Content-Length: 76
            > Content-Type: application/x-www-form-urlencoded
            > 
            * upload completely sent off: 76 out of 76 bytes
            < HTTP/1.1 200 OK
            < content-length: 23
            < content-type: text/html; charset=UTF-8
            < date: Tue, 12 May 2020 16:23:14 GMT
            < server: istio-envoy
            < x-envoy-upstream-service-time: 5228
            < 
            * Connection #0 to host {external_ip} left intact
            {"predictions": [1, 1]}(base)
        ```

### Additional Materials
1. custom knative ingressgateway (ref. [Setting up custom ingress gateway](https://knative.dev/docs/serving/setting-up-custom-ingress-gateway/))
    ```
      default : istio-ingressgateway
      custom knative-ingressgateway
        kubectl edit gateway knative-ingress-gateway -n knative-serving
            istio: ingressgateway --> custom: ingressgateway
    ```
