# Transmute

Transmute是一款使用AI大模型驱动的智能翻译工具，可以同时对接多个大模型，比如OpenAI、DeepSeek、通义千问、豆包等。Transmute使用Python 3 + FastAPI技术开发。

## 主要特点

* 支持接入多种AI大模型，只要兼容OpenAI API接口均可。
* 支持多种AI模型切换
* AI智能翻译：智能纠错、智能识别、语意优化等。
* 支持流式传输
* 支持限制IP请求频率
* 支持限制输入字符串长度
* PWA支持

## 截图

![2f339be26c1f5bf9.png](https://img.rss.ink/imgs/2025/03/17/2f339be26c1f5bf9.png)

## 安装

> 目前仅支持Docker安装，请确保您已经安装Docker和Docker Compose

新建`docker-compose.yaml`文件，内容如下：

```yaml
version: '3.8'

services:
  transmute:
    container_name: transmute
    image: helloz/transmute
    ports:
      - "2082:2082"
    restart: always
    volumes:
      - /opt/transmute/app/data:/opt/transmute/app/data
```

然后输入`docker-compose up -d`启动。

## 使用

Transmute配置文件位于挂载目录下的`config/config.json`，使用标准的json格式：

```json
{
    "redis":{
        "host":"127.0.0.1",
        "port":6379,
        "password":"transmute2082",
        "db":0
    },
    "app":{
        "req_limit":100,
        "word_limit":3000
    },
    "site":{
        "title":"Transmute",
        "keywords":"Transmute,北冥翻译,智能翻译,AI翻译,翻译,翻译工具,翻译软件,翻译器,翻译网站",
        "description":"Transmute是一款基于人工智能的翻译工具，支持多种语言互译，提供多种翻译模型。",
        "sub_title":"AI大模型驱动的智能翻译工具"
    },
    "models":[
        {
            "base_url":"https://api.openai.com/v1",
            "model":"gpt-4o",
            "api_key":"sk-xxx",
            "name":"GPT-4o"
        }
    ]
}
```

需要修改`models`，添加您自己的AI大模型接口，大模型接口需要兼容OpenAI API格式，同时只需要路径的前缀部分，比如完整的API地址为：`https://api.openai.com/v1/chat/completions`，您只需要填写`https://api.openai.com/v1`，不需要末尾的`/chat/completions`，参数含义如下：

* `models.[0].base_url`：API前缀地址，不需要末尾的`/chat/completions`
* `models.[0].model`：模型参数值
* `models.[0].api_key`：密钥信息
* `models.[0].name`：前端显示的模型名称

可以在`models`节点下添加多个模型，比如：

```
"models":[
        {
            "base_url":"https://api.openai.com/v1",
            "model":"gpt-4o",
            "api_key":"sk-xxx",
            "name":"GPT-4o"
        },
        {
            "base_url":"https://api.deepseek.com/v1",
            "model":"deepseek-chat",
            "api_key":"sk-xxx",
            "name":"DeepSeek"
        }
    ]
```

**注意事项：**

1. 参数修改完毕后请务必校验json格式正确，否则可能导致程序异常
2. 修改参数后需要重启容器`docker restart transmute`才会生效
3. 然后访问`http://IP:2082`测试

**其他参数**

* `app.req_limit`：单个访客请求频率限制，单位为24H，超出请求频率后将被限制
* `app.word_limit`：最大可输入的字符串长度
* `site`：站点相关的信息

### 快捷键

* 支持`Ctrl + Enter` 或 `Command + Enter`提交翻译
* 支持 `ESC` 清空输入内容和结果

## 问题反馈

* 如果有任何问题可以在[Issues](https://github.com/helloxz/transmute/issues) 中提交。
* 或者添加我的微信：`xiaozme`，请务必备注Transmute

## 其他产品

如果您有兴趣，还可以了解我们的其他产品。

* [Zdir](https://www.zdir.pro/zh/) - 一款轻量级、多功能的文件分享程序。
* [OneNav](https://www.onenav.top/) - 高效的浏览器书签管理工具，将您的书签集中式管理。
* [ImgURL](https://www.imgurl.org/) - 2017年上线的免费图床。