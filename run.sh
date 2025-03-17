#!/bin/sh

# 复制配置文件
copyConfig(){
    # 检查app/config/config.json文件是否存在
    if [ ! -f "app/data/config/config.json" ]; then
        # 递归创建目录
        mkdir -p app/data/config
        # 复制配置文件
        cp app/config/config.default.json app/config/config.json
    fi
}

# 启动主进程
runMain(){
    # 获取环境变量WORKERS
    WORKERS=${WORKERS}
    # 判断变量是否存在
    if [ -z "$WORKERS" ]; then
        WORKERS=1
    fi
    # 启动主进程
    uvicorn app.main:app --workers $WORKERS --host
}

copyConfig
uvicorn app.main:app --workers 2 --host 0.0.0.0 --port 2082