# Kubernetes Basics
1. [Introduction](#1-Introduction)
    - 1.1. [Install Kubernetes](#11-Install-Kubernetes)
    - 1.2. [Introduction to Kubernetes](#12-Introduction-to-Kubernetes)
    - 1.3. [Pod](#13-Pod)
    - 1.4. [ReplicaSet](#14-ReplicaSet)
    - 1.5. [Deployment](#15-Deployment)
    - 1.6. [Service](#16-Service)
2. [Manage & Set Kubernetes Resources](#2-Manage-&-Set-Kubernetes-Resources)   
3. [Ingress](#3-Ingress)
4. [Persistent Volume & Persistent Volume Claim](#4-Persistent-Volume-&-Persistent-Volume-Claim)
5. [Service Account & RBAC](#5-Service-Account-&-RBAC)

- Reference : "시작하세요! 도커/쿠버네티스 (용찬호 지음, 위키북스)"
- Test Environments
    - Cloud Platform : GKE
    - Node type : n1-standard-2 (vCPUs: 2, 메모리: 7.50GB)
    - Kubernetes version : 1.14.10
    - kubectl version : 1.18.0


## 1. Introduction
### 1.1. Install Kubernetes
- Kubernetes 설치 환경의 종류
    1. Managed Kubernetes 사용 : GKE, EKS, ...
        1. Google - Google Kubernetes Engine, GKE
        2. AWS - Elastic Kubernetes Service, EKS
        3. Azure - Azure Kubernetes Service, AKS
    2. 클라우드 서버 인프라에서 설치 : kubespray, kubeadm, **kops**
    3. 자체 서버 환경에서 설치 : kubespray, kubeadm
        * 1 -> 3으로 갈수록 클라우드에 대한 의존성은 낮아지며, 관리의 복잡도는 증가한다.
    - cf. GKE Cluster 구조
        ![GKE](https://cloud.google.com/kubernetes-engine/images/cluster-architecture.svg?hl=ko)
    
- [**Checklist**] 여러 서버로 구성된 Kubernetes 클러스터 설치 
    1. 모든 서버의 시간이 ntp로 동기화돼 있는가?
    2. 모든 서버의 MAC 주소가 다른가? (특히 VM 사용 시)
    3. 모든 서버가 2GB 메모리, 2 CPU 이상의 자원을 가지고 있는가?
    4. 모든 서버에서 메모리 스왑을 비활성화했는가?
        * swapoff -a
        * cf. swap : 메모리 공간이 부족할 때 DRAM에서 디스크로 페이지를 내림

- GKE 빠른 시작
    - ref. https://cloud.google.com/kubernetes-engine/docs/quickstart?hl=ko
    1. gcloud 설정
        - `gcloud init`
        - `gcloud config set project project-id`
        - `gcloud config set compute/zone compute-zone`
    2. GKE 클러스터 생성
        - `gcloud container clusters create cluster-name --num-nodes=1`
        - `gcloud container clusters get-credentials cluster-name`
    2. 노드 풀 추가
        - 생성 `gcloud container node-pools create pool-name --cluster cluster-name`
            - GPU 사용 
                ```  
                gcloud container node-pools create [POOL_NAME] \   
                --accelerator type=[GPU_TYPE],count=[AMOUNT] --zone [COMPUTE_ZONE] \   
                --cluster [CLUSTER_NAME] [--num-nodes 3 --min-nodes 0 --max-nodes 5 \   
                --enable-autoscaling]
                ```
        - 리스트 `gcloud container node-pools list --cluster cluster-name`
        - 크기 조정 `gcloud container clusters resize cluster-name --node-pool pool-name \   
            --num-nodes num-nodes`
        - 삭제 `gcloud container node-pools delete pool-name --cluster cluster-name`
    3. 배포 만들기
        - `kubectl create deployment hello-server --image=gcr.io/google-samples/hello-app:1.0`    
    4. 배포 노출
        - `kubectl expose deployment hello-server --type LoadBalancer \   
           --port 80 --target-port 8080`
    5. 삭제
        - 애플리케이션 서비스 삭제 `kubectl delete service hello-server`
        - 클러스터 삭제 `gcloud container clusters delete cluster-name`

### 1.2. Introduction to Kubernetes
- 모든 리소스는 오브젝트 형태로 관리
    * eg. 컨테이너 집합 (Pods), Pods를 관리하는 컨트롤러 (Replica Set), 사용자 (Service Account), 노드 (Node), ...
    * 사용 가능한 오브젝트 `$ kubectl api-resources`
    * 오브젝트에 대한 설명 `$ kubectl explain {resource_name}`

- YAML 파일과 kubectl로 사용
    * eg. 컨테이너, 컨테이너 설정값 (ConfigMap), 비밀값 (Secrets) 등

- 여러 개의 컴포넌트로 구성
    * Kubernetes 노드의 역할은 마스터, 워커로 나뉨
        * 마스터 : 클러스터 관리
            * 실행되는 컴포넌트 : API 서버 (kube-apiserver), 컨트롤러 매니저 (kube-contoller-manager), 스케줄러 (kube-scheduler), DNS 서버 (coreDNS)
        * 워커 : 워커에서 애플리케이션 컨테이너 생성
        * 모든 노드에서 실행되는 컴포넌트 : 프락시 (kube-proxy, 오버레이 네트워크 구성), 네트워크 플러그인 (calico, flannel)
            * **kubelet** : 컨테이너의 생성, 삭제, 마스터-워커 간 통신을 담당하는 중요한 에이전트

### 1.3. Pod

### 1.4. ReplicaSet

### 1.5. Deployment

### 1.6. Service
- 서비스의 종류
    - ClusterIP : Kubernetes **내부**에서만 포드에 접근할 때 사용. 외부로 포드를 노출하기 않는다.
    - NodePort : 포드에 접근할 수 있는 포트를 클러스터의 모든 노드에 동일하게 개방. 외부에서 포드에 접근 가능.
        - 접근할 수 있는 포트는 랜덤으로 정해진다. 특정 포트로 접근하도록 설정 가능
    - **LoadBalancer** : **클라우드 플랫폼**에서 제공하는 로드 밸러서를 동적으로 프로비저닝해 포드에 연결. 외부에서 포드에 접근 가능.
        - 일반적으로, AWS, GCP 등 클라우드 플랫폼 환경에서만 사용 가능

- [LoadBalancer] 클라우드 플랫폼의 로드 밸런서와 연동하기
    - 참고
        - [GKE - Ingress로 HTTP Load Balancer 설정](https://cloud.google.com/kubernetes-engine/docs/tutorials/http-balancer?hl=ko)
        - [GKE - HTTP(S) Load Balancer와 Cloud Run for Anthos on Google Cloud 통합](https://cloud.google.com/solutions/integrating-https-load-balancing-with-istio-and-cloud-run-for-anthos-deployed-on-gke)

## 2. Manage & Set Kubernetes Resources

## 3. Ingress
- Ingress의 의미
    - 일반적 의미 : 외부에서 내부로 향하는 것
        - eg. Ingress Traffic : 외부에서 서버로 유입되는 트래픽, Ingress Network : 인그레스 트래픽을 처리하기 위한 네트워크
    - Ingress : 외부 요청을 어떻게 **처리**할 것인지 네트워크 7계층 레벨에서 정의하는 Kubernetes 오브젝트
        - Ingress 오브젝트의 기능
            - 외부 요청 라우팅 : 특정 경로로 들어온 요청을 어떤 서비스로 전달할지 정의하는 라우팅 규칙 설정
            - 가상 호스트 기반의 요청 처리 : 같은 IP에 대해 다른 도메인 이름으로 요청이 도착했을 때, 어떻게 처리할지 정의
            - SSL/TLS 보안 연결 처리 : 여러 개의 서비스로 요청을 라우팅할 때, 보안 연결을 위한 인증서 적용
        - Ingress의 요청을 처리할 서버로 무엇을 선택하는지에 따라 기능이 조금씩 달라진다. -> up to you
- Ingress의 필요성
    - 각 Deployment를 외부에 노출 할 때
        - NodePort 또는 LoadBalancer 사용 시
            - 각 Deployment에 대응하는 Service 연결 -> 각 Service의 URL로 접근
            - 각 Service와 Deployment에 대해 일일이 설정 - eg. 보안 연결, 접근 도메인 및 클라이언트 상태에 기반한 라우팅 구현
        - Ingress 사용 시
            - URL 엔드포인트를 단 하나만 생성
            - Ingress가 라우팅 정의, 보안 연결 등 세부 설정 수행
    - ★**핵심** : 외부 요청에 대한 처리 규칙을 Kubernetes 자체 기능으로 편리하게 관리
        
- Ingress의 구조
    - Ingress 목록 : `$ kubectl get ingress(ing)`
    - Ingress 생성
       - YAML 예시
            ```
            apiVersion: networking.k8s.io/v1beta1
            kind: Ingress
            metadata:
              name: my-ingress
            spec:
              rules:
              - host: your-store.example
              - http:
                  paths:
                  - path: /*
                    backend:
                      serviceName: my-products
                      servicePort: 60000
                  - path: /discounted
                    backend:
                      serviceName: my-discounted-products
                      servicePort: 80
            ```
       - host : 해당 도메인 이름으로 접근하는 요청에 대해서 처리 규칙을 적용 (여러 host 정의 가능)
       - path : 해당 경로에 들어온 요청을 어느 서비스로 전달할지 정의 (여러 path 정의 가능)
       - serviceName, servicePort : path로 들어온 요청이 전달될 서비스 & 포트
       - 예시 설명
           - LoadBalancer IP 주소를 도메인 이름 your-store.example에 연결했다고 가정해 보세요.
           - 클라이언트가 요청을 your-store.example에 전송하면 요청은 포트 60000에서 my-products라는 Kubernetes 서비스로 라우팅됩니다.
           - 클라이언트가 요청을 your-store.example/discounted에 전송하면 요청은 포트 80에서 my-discounted-products라는 Kubernetes 서비스로 라우팅됩니다.
           - 인그레스의 path 필드에서 지원되는 유일한 와일드 카드 문자는 * 문자입니다. * 문자는 슬래시(/) 다음에 와야 하며 패턴의 마지막 문자여야 합니다. eg. /* , /foo/* , /foo/bar/* 
    - 구조 예시
    ![Ingress](https://cloud.google.com/kubernetes-engine/images/ingress-http2.svg?hl=ko)
        - ref. https://cloud.google.com/kubernetes-engine/images/ingress-http2.svg?hl=ko
        - ref. https://tech.kakao.com/2018/12/24/kubernetes-deploy/   
- Annotation
    - Ingress의 추가적 기능. YAML 파일의 주석 항목을 정의함으로써 다양한 옵션을 사용할 수 있다.
    - eg.   
        ```
        kind: Service
        ...
          annotations:
            cloud.google.com/neg: '{"ingress": true}'       # [1]
        ```
        - 예시 설명
            - [1] : 네트워크 엔드포인트 그룹(NEG)를 사용하여 GKE의 Pod 엔드포인트로 직접 Load Balance를 수행하는 방법
                - 서비스 기본이 아니며, 인그레스 규칙의 백엔드인 서비스에 cloud.google.com/neg 주석과 함께 명시적으로 적용되어야 합니다.
                - 출처 : https://cloud.google.com/kubernetes-engine/docs/concepts/ingress?hl=ko   

        ```
        ...   
        annotations:
            nginx.ingress.kubernetes.io/rewrite-target: /   # [2]
            kubernetes.io/ingress.class: "nginx"            # [3]
        ```
        - 예시 설명
            - [2] : 정의된 경로(path)로 들어온 요청을 rewrite-target에 설정된 경로로 전달
            - [3] : 해당 Ingress 규칙을 어떤 Ingress Controller에 적용할지 의미
- ref
  - [Kubernetes - Ingress](https://kubernetes.io/ko/docs/concepts/services-networking/ingress/)
  - [Naver Cloud - NKS](https://docs.ncloud.com/ko/nks/nks-1-4.html)

### 따라하기 예제   
- [예제1] Ingress와 HTTP Load Balancing
  - ref.
      - [인그레스를 사용한 HTTP(S) 부하 분산 설정](https://cloud.google.com/kubernetes-engine/docs/tutorials/http-balancer?hl=ko)
      - [외부 HTTP(S) 부하 분산용 인그레스](https://cloud.google.com/kubernetes-engine/docs/concepts/ingress-xlb?hl=ko)
  
  - 클러스터 만들기
      1. CloudRun으로 만들기
          ```
           CLUSTER=cloudrun-gke-gclb-tutorial
           ZONE=us-central1-f
          
           gcloud beta container clusters create $CLUSTER \
               --addons HorizontalPodAutoscaling,HttpLoadBalancing,CloudRun \
               --enable-ip-alias \
               --enable-stackdriver-kubernetes \
               --machine-type n1-standard-2 \
               --zone $ZONE
           ```  
      2. UI로 만들기
      3. CLI (gcloud)로 만들기
  
- 외부 Load Balancing Ingress 구성
  - 1st App Deploy : `kubectl apply -f hello-world-deployment.yaml`
       ```
       apiVersion: apps/v1
       kind: Deployment
       metadata:
         name: hello-world-deployment
       spec:
         selector:
           matchLabels:
             greeting: hello
             department: world
         replicas: 3
         template:
           metadata:
             labels:
               greeting: hello
               department: world
           spec:
             containers:
             - name: hello
               image: "gcr.io/google-samples/hello-app:2.0"
               env:
               - name: "PORT"
                 value: "50000"
       ```
  - 1st Deployment 노출하는 Service : `kubectl apply -f hello-world-service.yaml`
       ```
       apiVersion: v1
       kind: Service
       metadata:
         name: hello-world
       spec:
         type: NodePort
         selector:
           greeting: hello
           department: world
         ports:
         - protocol: TCP
           port: 60000
           targetPort: 50000
       ```
  - 2nd App Deploy : 같은 방식으로 8080번 포트를 사용하는 서비스를 통해 요청을 받으면, 80번 포트 구성원 포드 중 하나로 전달되도록 설계
  - Ingress 생성 : `kubectl apply -f my-ingress.yaml`
       ```
       apiVersion: networking.k8s.io/v1beta1
       kind: Ingress
       metadata:
         name: my-ingress
       spec:
         rules:
         - http:
             paths:
             - path: /*
               backend:
                 serviceName: hello-world
                 servicePort: 60000
             - path: /kube
               backend:
                 serviceName: hello-kubernetes
                 servicePort: 80
       ```
      - Load Balancer 구성할 때까지 기다리면,
           `kubectl get ingress my-ingress --output yaml`
           ```
           output:
               status:
                 loadBalancer:
                   ingress:
                   - ip: xxx.x.xx.xx
           ```
          
      -  curl [LOAD_BALANCER_IP]/
          ```
           output:
               Hello, world!
               Version: 2.0.0
               Hostname: ...
           ```
      - curl [LOAD_BALANCER_IP]/
          ```
           output:
              Hello Kubernetes!
           ```
- [예제2] Load Balancing과 Cloud Run
  - ref. [HTTP(S) 부하 분산과 Cloud Run for Anthos on Google Cloud 통합](https://cloud.google.com/solutions/integrating-https-load-balancing-with-istio-and-cloud-run-for-anthos-deployed-on-gke)


## 4. Persistent Volume & Persistent Volume Claim

## 5. Service Account & RBAC

