# kubectl config 설정

- 기본 명령어
    ``` 
    # 나의 현재 config
    kubectl config view
    # 나의 config 목록
    kubectl config get-contexts
    # 나의 current context (현재 사용 중인 설정)
    kubectl config current-context
    # config 변경
    kubectl config use-context {my_context} 
    ```

- 환경
  - OS: MacOS / Linux
  - Kubernetes: v1.14
  - AWS CLI: v2

- Kubectl 설치
  - ref. [kubectl 설치](https://docs.aws.amazon.com/ko_kr/eks/latest/userguide/install-kubectl.html)
    ```
    # 파일 다운로드 
    curl -o kubectl https://amazon-eks.s3.us-west-2.amazonaws.com/1.14.6/2019-08-22/bin/darwin/amd64/kubectl
    # 바이너리에 실행 권한을 적용합니다. 
    chmod +x ./kubectl
    # 바이너리를 PATH의 폴더에 복사합니다. kubectl 버전이 이미 설치된 경우 $HOME/bin/kubectl을 생성하고 $HOME/bin이 $PATH로 시작하도록 해야 합니다.
    mkdir -p $HOME/bin && cp ./kubectl $HOME/bin/kubectl && export PATH=$PATH:$HOME/bin
    # (선택 사항) 셸 초기화 파일에 $HOME/bin 경로를 추가하면 셸을 열 때 구성됩니다.
    echo 'export PATH=$PATH:$HOME/bin' >> ~/.bash_profile
    # 버전 확인
    kubectl version --short --client
    ```

- Kubectl config 세팅 및 권한 획득
  - GKE
    - ref. [Cloud SDK 도구 승인](https://cloud.google.com/sdk/docs/authorizing?hl=ko)
        - gcloud 설정   
          `$ gcloud init`  
          `$ gcloud auth login`   
        - Config 설정
          - GKE 클러스터 메뉴에서 “연결” 버튼 선택 → 명령어 복사 후 실행
  - EKS
    - AWS 설정   
      `$ aws configure`   
        — “내 보안 자격 증명”에서 키 확인 후 입력 (CLI, SDK 및 API 액세스를 위한 액세스 키)
        — (관리자 권한 필요) cluster 관리자 계정에서 aws-auth에 추가   
            `kubectl edit -n kube-system configmap/aws-auth`

    - Config 설정   
      `aws eks --region {my_region} update-kubeconfig --name {cluster_name}`
    
    - 권한 확인   
      `kubectl get pods -n {name_space}`
        - 실행 중인 리소스가 없거나 실행 내역이 나오면 성공
        - 서버에 로그인 해야 한다(aws configure)거나 리소스에 접근 권한이 없다고 하면(클러스터 관리자에게 권한 부여 요청해야 함) 실패
      
    - cf. [AWS CLI 설치](https://docs.aws.amazon.com/ko_kr/cli/latest/userguide/install-cliv2.html)
        ```
        ## MacOS
        # 파일 다운로드 : https://awscli.amazonaws.com/AWSCLIV2.pkg
        $ sudo ln -s /folder/installed/aws-cli/aws /folder/in/path/aws
        $ sudo ln -s /folder/installed/aws-cli/aws_completer /folder/in/path/aws_completer
        
        # Linux
        $ curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
        $ unzip awscliv2.zip
        $ sudo ./aws/install
        
        # 설치 확인
        $ which aws
        # /usr/local/bin/aws 
        $ aws --version
        # aws-cli/2.0.0 Python/3.7.4 Darwin/18.7.0 botocore/2.0.0
        ```


