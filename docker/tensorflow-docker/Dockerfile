# Reference : https://github.com/moduPlayGround/GPUServer/issues/8

# On Ubuntu base image, install anaconda and modify jupyter config.py
FROM ubuntu:16.04

# Install packages
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        #python3.7 \
        #python-setuptools \
        #python3-pip \
        #python3-dev \
        cmake \
        git \
        curl \
        vim \
        ca-certificates
#RUN pip -q install --upgrade pip

# Make working dir (testing...)
RUN mkdir /home/$USER_NAME/workspace
RUN chown $USER_NAME:$USER_NAME /home/$USER_NAME/workspace

# Add $USER_NAME
ARG UID
ARG USER_NAME
RUN apt-get update && apt-get install -y sudo && \
    adduser $USER_NAME -u $UID --quiet --gecos "" --disabled-password && \
    echo "$USER_NAME ALL=(root) NOPASSWD:ALL" > /etc/sudoers.d/$USER_NAME && \
    chmod 0440 /etc/sudoers.d/$USER_NAME

# Below commands will be executed as $USER_NAME
USER $USER_NAME
RUN curl -o /home/$USER_NAME/anaconda.sh -O https://repo.anaconda.com/archive/Anaconda3-2018.12-Linux-x86_64.sh
RUN chmod +x /home/$USER_NAME/anaconda.sh && \
     /home/$USER_NAME/anaconda.sh -b -p /home/$USER_NAME/anaconda3 && \
     /home/$USER_NAME/anaconda3/bin/conda clean -ya
ENV PATH /home/$USER_NAME/anaconda3/bin:${PATH}

RUN echo "cd ~" >> ~/.bashrc

# Run jupyter
USER $USER_NAME
ARG JUPYTER_PASSWORD
RUN jupyter notebook --generate-config

# Enable jupyter lab
RUN jupyter serverextension enable --py jupyterlab --sys-prefix

# Install plotly for advanced visualization on jupyter lab
#RUN pip install plotly && \
#    conda install -c conda-forge nodejs && \
#    jupyter labextension install @jupyterlab/plotly-extension

# Modify config file
RUN jupyter_sha=$(python -c "from notebook.auth import passwd; print(passwd('${JUPYTER_PASSWORD}'))") && \
    echo "c.NotebookApp.password=u'$jupyter_sha'" >> ~/.jupyter/jupyter_notebook_config.py && \
    echo "c.NotebookApp.ip='0.0.0.0'" >> ~/.jupyter/jupyter_notebook_config.py && \
    echo "c.NotebookApp.open_browser=False" >> ~/.jupyter/jupyter_notebook_config.py && \
    echo "c.NotebookApp.terminado_settings = { 'shell_command': ['bash'] }" >> ~/.jupyter/jupyter_notebook_config.py

# Run command
CMD ["jupyter", "notebook", "--port=8888", "--no-browser", "--ip=0.0.0.0", "--allow-root"]
