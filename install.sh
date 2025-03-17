#!/bin/sh

# 安装依赖
install_deps(){
    akp update
    apk add python3
    apk add py3-pip
    mkdir -p  /opt/transmute && cd /opt/transmute
}

# 安装 Python 依赖
install_python_deps(){
    python3 -m venv venv
    source venv/bin/activate
    pip3 install -r requirements.txt
}


# 清理缓存，缩小镜像体积
clean(){
    rm -rf /var/cache/apk/*
    rm -rf /root/.cache
    #rm -rf /opt/transmute/venv
}

install_deps && install_python_deps && clean