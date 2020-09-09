# Kubeflow

## Prerequsites
- 배경지식
    - Kubernetes
    - kustomize

- [요구사항](https://www.kubeflow.org/docs/started/k8s/overview/#minimum-system-requirements)
    - 클러스터 최소 스펙 (worker node 1+)
        - 4 CPU
        - 50 GB storage
        - 12 GB memory
        - [추천사항] Kubernetes version: 1.14
        - Version Compatibility 
           
                Kubernetes	Kubeflow 0.4	Kubeflow 0.5	Kubeflow 0.6	Kubeflow 0.7	Kubeflow 1.0
                1.11	    compatible  	compatible  	incompatible	incompatible	incompatible
                1.12	    compatible	    compatible	    incompatible	incompatible	incompatible
                1.13	    compatible  	compatible  	incompatible	incompatible	incompatible
                1.14	    compatible  	compatible  	compatible	    compatible	    compatible
                1.15	    incompatible	compatible  	compatible	    compatible	    compatible
                1.16	    incompatible	incompatible	incompatible	incompatible	incompatible

## Install (supporting multi-tenancy)
- [다양한 설치 옵션](https://www.kubeflow.org/docs/started/getting-started/#overview-of-installation-options)
- [설치 방법](https://www.kubeflow.org/docs/started/k8s/kfctl-istio-dex/)
- [Kfserving with Dex](https://github.com/kubeflow/kfserving/tree/master/docs/samples/istio-dex)

- cf. Dex Certificates
    - Certificate 생성
      ```
       apiVersion: cert-manager.io/v1alpha2
       kind: Certificate
       metadata:
         name: istio-ingressgateway-certs
         namespace: istio-system
       spec:
         commonName: istio-ingressgateway.istio-system.svc
         ipAddresses:
         - <LB_IP>    
         isCA: true
         issuerRef:
           kind: ClusterIssuer
           name: kubeflow-self-signing-issuer
         secretName: istio-ingressgateway-certs
       ```