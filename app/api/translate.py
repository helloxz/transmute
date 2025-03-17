
from openai import OpenAI
from fastapi import Request,HTTPException
from fastapi.responses import StreamingResponse
from app.utils.helper import *
import json
import os
import langid
from datetime import datetime
from app.main import *
from pydantic import BaseModel
import httpx

# 支持的目标语言
support_languages = [
    {
        "name": "自动检测",
        "value": "auto"
    },
    {
        "name": "简体中文",
        "value": "zh-CN"
    },
    {
        "name": "繁体中文",
        "value": "zh-HK"
    },
    {
        "name": "英语",
        "value": "en-US"
    },
    {
        "name": "日语",
        "value": "ja-JP"
    },
    {
        "name": "韩语",
        "value": "ko-KR"
    },
    {
        "name": "西班牙语",
        "value": "es-ES"
    },
    {
        "name": "法语",
        "value": "fr-FR"
    },
    {
        "name": "德语",
        "value": "de-DE"
    }
]


# ZincSearch 配置，暂时没有使用
ZINCSEARCH_URL = "xxx"  # ZincSearch 的 URL
INDEX_NAME = "transmute"  # 索引名称
AUTH = ("xxx", "xxx")  # 认证信息（用户名和密码）

async def add_document_to_zincsearch(document: dict):
    """
    将文档异步非阻塞地写入 ZincSearch。
    
    :param document: 符合 mappings 结构的文档字典。
    :return: 写入结果。
    """
    # 构建 ZincSearch 的 API URL
    url = f"{ZINCSEARCH_URL}/api/{INDEX_NAME}/_doc"
    try:
        # 发送 POST 请求到 ZincSearch
        async with httpx.AsyncClient(auth=AUTH) as client:
            response = await client.post(url, json=document)
            response.raise_for_status()  # 如果请求失败，抛出异常
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    return {"status": "success", "response": response.json()}


# 声明需要的参数
class InputItem(BaseModel):
    target_language: str
    model: str
    input: str
    browser_lang:str = None


class Translate:
    modelList = []
    def __init__(self):
        # 获取当前工作路径
        current_path = os.getcwd()
        # 打印当前路径
        # print("当前路径:", current_path)
        # 从配置文件中获取模型列表
        with open('app/data/config/config.json', 'r') as file:
            data = json.load(file)

        self.modelList = data["models"]

    # 对话接口
    async def chat(self,item:InputItem,request: Request = None):
        # 解析json数据
        target_language = item.target_language
        model = item.model
        input = item.input
        browser_lang = item.browser_lang
        # 判断目标语言是否支持
        if not self._is_support_language(target_language):
            return show_json(400, "The target language is not supported", None)
        
        # 判断模型是否存在
        modelInfo = self._is_support_model(model)
        if not modelInfo:
            return show_json(400, "The model does not exist", None)
        
        # print("modelInfo:", modelInfo)
        word_limit = request.app.state.config["app"]["word_limit"]
        # 判断内容长度，必须2到1000个字符之间 
        if len(input) < 2 or len(input) > word_limit:
            return show_json(400, f'The content length must be between 2 and {word_limit} characters', None)
        
        # 检测输入语言，然后自动设置目标语言
        if target_language == "auto":
            # 使用langid库检测语言
            lang, _ = langid.classify(input)
            if lang == "zh":
                target_language = "en-US"
            elif lang == "en":
                target_language = "zh-CN"
            else:
                # 如果既不是中文也不是英文，则默认翻译为英文
                target_language = "en-US"
        
        # 设置提示词
        prompt = f"""
你是一个专业的翻译官，请将用户输入的内容翻译为 {target_language} 语言。仅翻译尖括号 <<<>>> 之间的内容，直接返回翻译结果，不要包含 <<<>>> 或其他解释。

在进行翻译时，请遵循以下指南:
1. 仔细识别输入文本中的错别字并进行修正。
2. 仅翻译尖括号 <<<>>> 之间的内容，直接返回翻译结果，不要包含 <<<>>> 或其他解释。
3. 确保翻译后的内容在语法和语义上符合目标语言的表达习惯。
4. 尽量使翻译结果优美、流畅，避免生硬的表达。
5. 不要改变原文的意思。
6. 保持原文的段落和格式。
"""


        # 初始化客户端
        client = OpenAI(
            api_key=modelInfo["api_key"],  # 替换为你的密钥
            base_url=modelInfo["base_url"]  # 替换为你的地址
        )

        def generate():
            stream = client.chat.completions.create(
                model=modelInfo["model"],
                temperature=0.5,
                messages=[
                    {"role": "assistant", "content": prompt},
                    {
                        "role": "user",
                        "content": f"<<<{input}>>>",
                    }
                ],
                stream=True  # 启用流式输出
            )
            
            for chunk in stream:
                if chunk.choices and len(chunk.choices) > 0:
                    content = chunk.choices[0].delta.content
                    
                    # print(content)
                    if content is not None:
                        value = {
                            "value": content
                        }
                        
                        
                        # 按照SSE格式发送数据
                        # yield f"data: {content}\n\n"
                        # 使用json.dumps将字典转换为JSON格式的字符串
                        yield f"data: {json.dumps(value)}\n\n"
        
            yield f"data: [DONE]\n\n"
        
        # 请求次数+1
        await self._add_req_count(request)

        # 写入日志
        """
        asyncio.create_task(add_document_to_zincsearch({
            "ip": get_client_ip(request),
            "user_agent": request.headers.get("user-agent"),
            "input": input,
            "output": self.output,
            "target_lang": target_language,
            "model": model,
            "browser_lang": browser_lang
        }))
        """
        # 返回流式响应
        return StreamingResponse(generate(), media_type="text/event-stream")
    
    # 判断目标语言是否支持
    def _is_support_language(self,target_language: str):
        # 遍历support_languages,然后判断self.target_language是否在support_languages中
        for lang in support_languages:
            if lang["value"] == target_language:
                return True
        return False

    # 检查模型是否存在
    def _is_support_model(self,model: str):
        for modelInfo in self.modelList:
            if modelInfo["model"] == model:
                return modelInfo
            
        # 如果不存在，返回False
        return False
    
    # 请求次数+1
    async def _add_req_count(self,request: Request):
        # 生成key
        # 获取当前日期并格式化为 YYYYMMDD
        current_date = datetime.now().strftime('%Y%m%d')
        # request = Request
        ip = get_client_ip(request)
        key = "transmute:" + current_date + ":" + ip
        await request.app.state.redis.incr(key)
        # 设置过期时间为24小时
        await request.app.state.redis.expire(key, 24 * 60 * 60)

    # 获取模型列表
    async def get_models(self,request:Request):
        newModelList = []
        # 遍历并去除敏感数据
        for model in self.modelList:
            newModelList.append({
                "model": model["model"],
                "name": model["name"]
            })
        return show_json(200, "success", newModelList)
    
    # 获取支持的目标语言
    async def get_languages(self):
        return show_json(200, "success", support_languages)