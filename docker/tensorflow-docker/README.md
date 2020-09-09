# TensorFlow Docker Basics

목표: GCP 클라우드 환경에서 Docker와 GPU를 사용해서 TensorFlow CNN 모델 학습

    1. Official Image 이용
    2. Customized Image 이용

- [Practice](#Practice)
    * [SSH on GCP](#SSH-on-GCP)
    * [Install Docker on Virtual Machine](#Install-Docker-on-Virtual-Machine)
    * [Build Environment for Developing TensorFlow](#Build-Environment-for-Developing-TensorFlow)
        * [Official TensorFlow Docker Image](#Official-TensorFlow-Docker-Image)
        * [Customized Docker Image](#Customized-Docker-Image)
        * [Build Environment for Data Analysis](#Build-Environment-for-Data-Analysis)
        * [Save Docker Containers and Images](#Save-Docker-Containers-and-Images)
         
- [Cloud OJT](#Cloud-OJT)
    * [Docker Basic Commands](#Docker-Basic-Commands)
    * [Issues](#Issues)
    * [Reference Materials](#Reference-Materials)


# Practice

## SSH on GCP

[gcloud](https://cloud.google.com/sdk/gcloud/reference/beta/compute/ssh)

- `gcloud beta compute ssh --zone "my_zone" "instance_name" --project "project_id"`
- 성공 시 : [user_name@instance_name ~]$

## Install Docker on Virtual Machine

**Install & Set up Docker**
- Overview
    - Update Channel의 종류 [https://docs.docker.com/install/](https://docs.docker.com/install/)
        - **Stable** gives you latest releases for general availability.
        - **Test** gives pre-releases that are ready for testing before general availability.
        - **Nightly** gives you latest builds of work in progress for the next major release.
- Linux OS 버전 확인

    `$ grep . /etc/*-release`
    
    `$ cat /etc/issue`

- OS 별 Docker 설치 가이드

    (1) Ubuntu 19.10 / 18.04 (LTS) / 16.04 (LTS)

    [Install Docker Engine - Community](https://docs.docker.com/install/linux/docker-ce/ubuntu/)

    - 오래된 버전 Docker 지우기

        `$ sudo apt-get remove docker docker-engine [docker.io](http://docker.io/) containerd runc`

    - Repository 셋업

            $ sudo apt-get update
            # allow apt to use a repo over HTTPS
            $ sudo apt-get install \
                apt-transport-https \
                ca-certificates \
                curl \
                gnupg-agent \
                software-properties-common
            
            # add Docker's official GPG key
            $ curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
            
            # verify you have the key with fingerprint
            $ sudo apt-key fingerprint 0EBFCD88
                
            pub   rsa4096 2017-02-22 [SCEA]
                  9DC8 5822 9FC7 DD38 854A  E2D8 8D81 803C 0EBF CD88
            uid           [ unknown] Docker Release (CE deb) <docker@docker.com>
            sub   rsa4096 2017-02-22 [S]
        
    - Docker Engine - Community 설치
        1. Update the `apt` package index.

            `$ sudo apt-get update`
            
        2. 최신 버전 설치 또는
        
            `$ sudo apt-get install docker-ce docker-ce-cli containerd.io`

        3. 버전을 선택하여 설치

            - 사용가능한 버전 목록 보기

            `$ apt-cache madison docker-ce`

            - 두 번째 열에서 버전을 선택해 설치합니다 eg. 5:18.09.1~3-0~ubuntu-xenial.

            `$ sudo apt-get install docker-ce=<VERSION_STRING> docker-ce-cli=<VERSION_STRING> containerd.io`
          
        4. hello-world image를 실행하며 설치 완료를 확인

            `$ sudo docker run hello-world`

    - 사용자를 Docker 그룹에 추가하기

            $ cat /etc/group
            ...
            docker:x:997:

        - 설치 직후 Docker는 root만 사용할 수 있다.
        - 접속한 계정의 사용자가 사용하기 위해 다음을 실행

                $ sudo usermod -aG docker $USER
                $ cat /etc/group
                ...
                docker:x:997:newuser
                $ sudo service docker restart

    (2) CentOS 7.0+

    [https://docs.docker.com/install/linux/docker-ce/centos/](https://docs.docker.com/install/linux/docker-ce/centos/)

        # remove old version
        $ sudo yum remove docker \
                          docker-client \
                          docker-client-latest \
                          docker-common \
                          docker-latest \
                          docker-latest-logrotate \
                          docker-logrotate \
                          docker-engine
        $ sudo yum install -y yum-utils \
          device-mapper-persistent-data \
          lvm2
        # allow apt to use a repo over HTTPS
        $ sudo yum-config-manager \
            --add-repo \
            https://download.docker.com/linux/centos/docker-ce.repo
        repo saved to /etc/yum.repos.d/docker-ce.repo
        # install docker engine - community
        $ sudo yum install docker-ce docker-ce-cli containerd.io
        ...
        Complete!
        # (option) to install specific ver. of docker engine
        $ yum list docker-ce --showduplicates | sort -r
        $ sudo yum install docker-ce-<VERSION_STRING> docker-ce-cli-<VERSION_STRING> containerd.io
        # to start docker
        $ sudo systemctl start docker
        $ sudo docker run hello-world

    (3) MacOS

    [https://docs.docker.com/docker-for-mac/install/](https://docs.docker.com/docker-for-mac/install/)

    (4) Docker용 Cloud build 예제

    [https://cloud.google.com/cloud-build/docs/quickstart-docker?hl=ko](https://cloud.google.com/cloud-build/docs/quickstart-docker?hl=ko)


- 설치 완료 테스트를 위한 기본 명령어

    [도커docker-설치하고-기본적인-설정하기](https://www.44bits.io/ko/post/easy-deploy-with-docker#%EB%8F%84%EC%BB%A4docker-%EC%84%A4%EC%B9%98%ED%95%98%EA%B3%A0-%EA%B8%B0%EB%B3%B8%EC%A0%81%EC%9D%B8-%EC%84%A4%EC%A0%95%ED%95%98%EA%B8%B0)

        $ docker pull {IMAGE_NAME}
        # 예제
        $ docker pull centos
        Unable to find image 'centos:latest' locally
        latest: Pulling from library/centos
        8d30e94188e7: Pull complete
        Digest: sha256:2ae0d2c881c7123870114fb9cc7afabd1e31f9888dac8286884f6cf59373ed9b
        Status: Downloaded newer image for centos:latest
        # images 확인
        $ docker images
        REPOSITORY          TAG                 IMAGE ID            CREATED             SIZE
        centos              latest              980e0e4c79ec        5 weeks ago         196.8 MB

        # CentOS 환경에 접속 (완전히 격리된 환경에서 bash 프로그램을 실행)
        $ docker run -it centos:latest bash
        [root@d3fef9c0f9e9 /]#

    - Docker의 실행 중 Container 목록 출력

        $ docker ps
        CONTAINER ID        IMAGE               COMMAND             CREATED             STATUS              PORTS               NAMES
        d3fef9c0f9e9        centos:latest       "bash"              5 minutes ago       Up 5 minutes                            compassionate_turing

    - `docker restart` : 재실행
    - `docker attach` : 컨테이너에 실행된 프로세스와 터미널 상에서 입출력 주고 받기

- Uninstall
    1. Uninstall the Docker Engine - Community package:

        `$ sudo apt-get purge docker-ce`

    2. Images, containers, volumes, or customized configuration files on your host are not automatically removed. To delete all images, containers, and volumes:

        `$ sudo rm -rf /var/lib/docker`


## Build Environment for Developing TensorFlow

**목표** :  Official TensorFlow 이미지와 Cutomized TensorFlow 이미지를 활용해 분석 환경 구축

### Official TensorFlow Docker Image

[https://www.tensorflow.org/install/docker](https://www.tensorflow.org/install/docker)

- 이미지 다운로드

    - **CPU**만 포함하는 이미지

            # 이미지 다운로드
            docker pull tensorflow/tensorflow                     # latest stable release
            docker pull tensorflow/tensorflow:devel-gpu           # nightly dev release w/ GPU support
            docker pull tensorflow/tensorflow:latest-gpu-jupyter  # latest release w/ GPU support and Jupyter

            # TensorFlow에서 구성된 컨테이너를 시작하려면
            # docker run [-it] [--rm] [-p hostPort:containerPort] tensorflow/tensorflow[:tag] [command]
            docker run -it --rm tensorflow/tensorflow \       
            python -c "import tensorflow as tf; tf.enable_eager_execution(); print(tf.reduce_sum(tf.random_normal([1000, 1000])))"

            # TF에서 구성된 컨테이너 내에서 bash 쉘 시작
            docker run -it tensorflow/tensorflow bash
            # TF 프로그램을 컨테이너 내에서 실행하려면 호스트 dir를 마운트
            # 컨테이너의 작업 디렉터리를 변경: -v hostDir:containerDir -w workDir
            docker run -it --rm -v $PWD:/tmp -w /tmp tensorflow/tensorflow python ./script.py

        - Python3을 지원하는 TF 나이틀리 빌드 → Juptyter notebook 서버를 시작

            `docker run -it -p 8888:8888 tensorflow/tensorflow:nightly-py3-jupyter`

            `docker run -it --ip={my_ip} -p 8888:8888 tensorflow/tensorflow:nightly-py3-jupyter`

            → 호스트 웹 브라우저에서 URL 연다. (`http://127.0.0.1:8888/?token=...`)

            - Cloud shell에서 token을 복사하면 전체 주소가 복사될 수 있으니 주의!

            → 이후 python3 명령어로 python 실행 가능

    - **GPU** 지원 이미지
    
        - GPU 사용 가능한지 확인

            `lspci | grep -i nvidia`

        - ★`nvidia-docker` 설치를 확인합니다.

            docker run --runtime=nvidia --rm nvidia/cuda nvidia-smi

            (v2는 `docker --runtime=nvidia`)

        - GPU 사용 이미지

                docker run --runtime=nvidia -it --rm tensorflow/tensorflow:latest-gpu \ 
                python -c "import tensorflow as tf; tf.enable_eager_execution(); print(tf.reduce_sum(tf.random_normal([1000, 1000])))"

        - GPU 기반 스크립트를 반복해서 실행하는 경우 `docker exec`를 통해 컨테이너를 재사용

        - 최신 TensorFlow GPU 이미지를 사용하여 컨테이너에서 `bash` 셸 시작

            `docker run --runtime=nvidia -it tensorflow/tensorflow:latest-gpu bash`

- Q&A
    - CentOS 설치 후에 tensorflow를 install하는 것과 TF Docker를 설치하는 것의 차이점
        - 필요한 최소한의 OS 요소만 갖추는 것과 OS layer부터 customize하는 차이

### Customized Docker Image

[https://github.com/moduPlayGround/GPUServer/issues/8](https://github.com/moduPlayGround/GPUServer/issues/8)

- Dockerfile

    [Dockerfile (based on ubuntu:16.04)](https://github.com/soochem/docker-basics/blob/master/docker-image-build/Dockerfile)

    - Build image 구성

        ubuntu 16.04

        anaconda3 2018.12 (built on python 3.7.1)
        
        - Error : python 3.8이 설치됨 (원인 : conda update wrapt)
        
        jupyter notebook
        
        jupyter lab
        
    - 이슈

        - Working directory 또는 지정된 경로를 찾을 수 없음

                RUN mkdir /home/$USER_NAME/workspace
                RUN chown $USER_NAME:$USER_NAME /home/$USER_NAME/workspace

- 이미지 빌드

        docker build --build-arg UID=$(id -u) \
        	--build-arg USER_NAME={user_name} \
        	--build-arg JUPYTER_PASSWORD=skcc0001 \
        	--tag juptest:version .
        docker run -it -u {user_name} -d -p 8888:8888 \
        	-v /home/{user_name}/workspace:/home/{user_name}/workspace \
        	--name {user_name} juptest:version
        docker exec -it {user_name} jupyter lab \
        	--ip=0.0.0.0 --port 8888 \
        	--notebook-dir=~/workspace

    - Jupyter Lab 접속 성공 시

            ...
            [I 08:54:42.396 LabApp] The Jupyter Notebook is running at:             
            [I 08:54:42.396 LabApp] http://(fdeaf1238338 or 127.0.0.1):8888/                
            [I 08:54:42.396 LabApp] Use Control-C to stop this server and shut down all kernels (twice to skip confirmation).        
            [I 08:54:58.054 LabApp] 302 GET / (xxx.xx.xx.xx) 0.73ms 
            [I 08:54:58.373 LabApp] 302 GET /lab? (xxx.xx.xx.xx) 1.04ms
            [I 08:55:05.261 LabApp] 302 POST /login?next=%2Flab%3F (xxx.xx.xx.xx) 1.33ms
    
    - Error : 디스크 용량 문제
        - Error processing tar file(exit status 1): open /home/{user_name}/anaconda3/pkgs/qt-5.9.7-h5867ecd_1/qml/QtQuick/Extras/plugins.qmltypes: no space left on device
        - 문제 확인
            - 디스크 공간 사용의 문제점을 파악 : `df -h`
        - 문제 해결 : 디스크 크기를 100GB로 설정 (anaconda의 크기가 크다)
        
- Tensorflow 설치 v1.14.0

        pip install --upgrade pip
        pip install tensorflow
    
    - Tensorflow 버전 확인

            import tensorflow as tf
            print(tf.__version__)
            
    - Error: cannot uninstall 'wrapt'

            # 방법1 실패 (python 버전 업데이트)
            conda update wrapt
            # 방법2 성공
            pip install wrapt --upgrade --ignore-installed
            pip install tensorflow

### Build Environment for Data Analysis

- **Jupyter** 초기 접속

    jupyter_notebook_config.py를 생성하는 시기에 따라 두 가지 방법으로 분류

    (1) Docker image 빌드 시 반영

    -  Dockerfile 참고

    (2) Container 내 환경 구성
  
    - http://{외부ip}:{port} 접속에 문제가 생길 때 해결 방법 (임시적)

            # (수정 중) 먼저 bash shell로 container에 접속해야 함
            docker exec -it {container_name} bash
            # Dockerfile에서 config file을 만들지 않았다거나 다시 생성해야 할 때
            jupyter notebook --generate-config
            # vim이 없을 때
            apt-get install vim
            vim ~/.jupyter/jupyter_notebook_config.py

    - [jupyter_notebook_config.py](https://github.com/soochem/docker-kubernetes-basics/blob/master/docker/jupyter_notebook_config.py)

- **Conda** 환경 구성

    [https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html)
    
    - Anaconda에서 가상환경(env) 구축
        - 생성 : `conda create (--no-default-packages) -n myenv python=3.6`
        - 목록 : `conda env list`
        - 활성화 : `activate snowdeer_env`
        - 비활성화 : `deactivate`
        - 제거 : `conda env remove -n snowdeer_env`
        - 참고 : [파이선 가상환경 콘다 시작하기](https://graspthegist.com/post/learn-conda-1/)
        
    - `conda` 명령어 관련 이슈
        - Errors : No module named conda
                
                # 에러 발생
                File "/home/name/anaconda3/bin/conda", line 7, in <module>
                from conda.cli import main
                ImportError: No module named conda.cli
                
                # 해결방법 (시도 중...)
                echo $PATH
                sudo chown -R [username] [anaconda_dir]
                # anaconda 설정파일 참고 : ~/anaconda3/conda-meta/anaconda-<version>-<build>.json
                
        - Container 내에서는 conda 명령어가 실행 가능함
            - jupyter lab의 terminal에서는 conda 실행이 안됨

- **환경변수**와 **디렉토리** 구성
    
    - Working Directory 설정   
        - Launcher Error: Cannot read property 'path' of undefined

        - Container 내 working dir의 권한 설정 변경 (임시적)

### Save Docker Containers and Images

- Overview

    ![Flow](https://miro.medium.com/max/750/1*joAfS_1sBhCOJzJuaAzzeg.png)
    
- 컨테이너에서 이미지 생성
    
    `docker commit {container_name} {img_name}`
    
    - docker images로 저장된 이미지를 확인한다.
    
- 컨테이너 저장

    - 저장 (.tar) : `docker export {file_name} {img_name}`
    
    - 불러오기 : `docker import {file_name or url}`
    
- 이미지 저장

    - 저장 (.tar) : `docker save {file_name} {img_name}`
    
    - 불러오기 : `docker load {file_name}`

- 컨테이너 저장 vs. 이미지 저장
    
    docker export의 경우 컨테이너를 동작하는데 필요한 모든 파일이 압축된다. (프로세스 실행 상태 X)
    
    즉, tar파일에 컨테이너의 루트 파일시스템 전체가 들어있는 것이다.
    
    반면에 docker save는 레이어 구조까지 포함한 형태로 압축이 된다.

    즉, 기반이 되는 이미지가 같더라도 export와 save는 압축되는 파일 구조와 디렉토리가 다르다.
    
    - 참고 : [docker image를 tar 파일로 저장](https://www.leafcats.com/240)

- Docker 이미지 Docker Hub에 Push
    
        # Docker Hub에 로그인
        $ docker login
        
        # Docker user id 변수 지정해놓기
        $ export DOCKER_ID_USER={u_name}
        
        # Docker Image에 태그 달기
        $ docker tag {img_name} $DOCKER_ID_USER/{img_name}:{tag}
        
        # Tag가 적용된 Image를 Docker Cloud에 Push
        $ docker push $DOCKER_ID_USER/{img_name}

# Cloud OJT

## Docker Basic Commands

- 참고한 자료
    - [초보를 위한 도커 안내서 - 설치하고 컨테이너 실행하기](https://subicura.com/2017/01/19/docker-guide-for-beginners-2.html)
    
- Docker 구조
    ![Docker architecture](https://docs.docker.com/engine/images/architecture.svg)

- Docker 기본 명령어

    - 이미지 목록 : `docker images`
    
    - 이미지 다운로드 :  `docker pull [OPTIONS] NAME[:TAG|@DIGEST]`
    
    - 이미지 삭제 : `docker rmi [OPTIONS] IMAGE [IMAGE...]`
    
    - 컨테이너 실행

        `docker run [OPTIONS] IMAGE[:TAG|@DIGEST] [COMMAND] [ARG...]`

        - docker run 옵션: [http://pyrasis.com/book/DockerForTheReallyImpatient/Chapter20/28](http://pyrasis.com/book/DockerForTheReallyImpatient/Chapter20/28)

    - 컨테이너 중지

        `docker stop [OPTIONS] CONTAINER [CONTAINER...]`  # container name은 unique한 일부 id만 입력해도 된다.

    - 컨테이너 제거
    
        `docker rm [OPTIONS] CONTAINER [CONTAINER...]`
        - 중지된 컨테이너 모두 제거
            `docker rm -v $(docker ps -a -q -f status=exited)`

    - 컨테이너 로그 보기

        `docker logs [OPTIONS] CONTAINER`

        - 유용한 옵션 : -f(실시간), --tail
        
    - 컨테이너 명령어 실행

        `docker exec [OPTIONS] CONTAINER COMMAND [ARG...]`

        - (비교) run : 새로운 컨테이너 만들고 실행, exec : 실행 중 컨테이너에  명령어 내림
        - eg. `docker exec -it mysql /bin/bash`
        - 컨테이너에 SSH를 설치하는 것은 권장하지 않음
    
    - 도커와 버전 관리 시스템
        - **VCS** 용어 사용 : 저장소*Repository*, 풀*Pull*, 푸시*Push*, 커밋*Commit*, 차분*Diff* 등
    
    - 컨테이너 업데이트
        - 컨테이너 삭제 시 유지해야 하는 데이터는 반드시 컨테이너 내부가 아닌 외부 스토리지에 저장 eg. AWS S3, 데이터 볼륨 컨테이너를 추가
        - 데이터 볼륨 사용 방법
            - 호스트 디렉토리를 마운트 -v 호스트:컨테이너 옵션 사용

                    docker run -d -p 3306:3306 \
                      -e MYSQL_ALLOW_EMPTY_PASSWORD=true \
                      --name mysql \
                      *-v* **/my/own/datadir:/var/lib/mysql** \ # <- volume mount
                      mysql:5.7

    - 컨테이너 관리 : `Docker Compose`
        - 복잡한 설정을 쉽게 관리하기 위한 YAML 방식의 설정 파일 이용

                curl -L "https://github.com/docker/compose/releases/download/1.9.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
                chmod +x /usr/local/bin/docker-compose
                # test
                docker-compose version
                vi docker-compose.yml
                docker-compose up

    - 컨테이너 빌드 예제
    
        **Ubuntu:16.04**
        
            # /bin/bash 명령어로 ubuntu:16.04 컨테이너 실행
            docker run --rm -it ubuntu:16.04 /bin/bash
            # in container
            $ cat /etc/issue
            Ubuntu 16.04.6 LTS \n \l

            $ ls
            bin   dev  home  lib64  mnt  proc  run   srv  tmp  var
            boot  etc  lib   media  opt  root  sbin  sys  usr`


        **Redis**
        
            # background 모드로 실행 (-d)
            $ docker run -d -p 8881:6379 redis
            # container ID를 보여주고 바로 shell로 복귀

            $ telnet localhost 8881
            Trying 127.0.0.1...
            Connected to localhost.
            Escape character is '^]'.
            set mykey hello
            +OK
            get mykey
            $5
            hello
        
        
        **mySQL 서버**
        
        https://registry.hub.docker.com/_/mysql
        
            $ docker run -d -p 3306:3306 -e MYSQL_ROOT_PASSWORD=0000 --name mysql mysql
            $ docker exec -it mysql bash
            root@a070337b761a:/# mysql -u root -p
            Enter password:
            Welcome to the MySQL monitor.  Commands end with ; or \g.
            Your MySQL connection id is 9
            Server version: 8.0.19 MySQL Community Server - GPL
            ...
            mysql> show databases;
            +--------------------+
            | Database           |
            +--------------------+
            | information_schema |
            | mysql              |
            | performance_schema |
            | sys                |
            +--------------------+
            4 rows in set (0.01 sec)
            mysql> quit
            Bye
            Deleted
            Code - Shell
            docker run -d -p 3306:3306 \
              -e MYSQL_ALLOW_EMPTY_PASSWORD=true \
              --name mysql \
              -v /my/own/datadir:/var/lib/mysql \ # <- volume mount
              mysql:5.7

## Issues

- Cloud shell의 한계
    - 발견된 문제 : cloud shell에서 개발하면 vm instance에는 영향 X
    - Cloud Shell : [https://cloud.google.com/shell?hl=ko](https://cloud.google.com/shell?hl=ko)
    - Google Cloud Shell을 사용하면 브라우저에서 직접 명령줄을 통해 클라우드 리소스에 액세스
    - Google Cloud SDK를 시스템에 설치하지 않고도 프로젝트 및 리소스를 쉽게 관리
    - Cloud SDK gcloud 명령줄 도구 및 그 밖의 필요한 유틸리티를 필요할 때마다 항상 최신 및 인증된 상태로 사용

- Python 설치
    - pip 문제해결

        pip3 install --upgrade pip
        pip3 install --upgrade setuptools pip

## Reference Materials

- **CUDA** (Compute Unified Device Architecture) : GPU에서 수행하는 병렬 처리 알고리즘을 C언어를 비롯한 산업 표준 언어를 사용하여 작성할 수 있도록 하는 GPGPU(GPU 상의 범용 계산) 기술
    - 목적 : 많은 연산을 동시에 처리하기 위함
    - Hadoop/Spark가 CPU기반의 병렬 처리인 반면 CUDA는 GPU기반의 병렬처리 방식
    - NDIVIA Docker

- 용어
    - **컨테이너** : 도커 이미지에서 생성되는 리눅스 컨테이너. 특정 컨테이너는 하나만 존재할 수 있지만, 동일 이미지에서 컨테이너를 쉽게 여러번 생성할 수 있다.
    - **이미지** : 하나 이상의 파일 시스템 계층으로 이루어져 도커화된 app.을 실행하기 위한 모든 파일들의 메타데이터 정보를 가지고 있다. 하나의 도커 이미지가 여러 호스트에 카피될 수 있다. 이름과 태그(이미지의 특정 릴리즈 표시, eg. latest)를 가진다.
