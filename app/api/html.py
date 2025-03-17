from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


class Html:
    def __init__(self):
        pass

    async def index(self,request: Request):
        templates = Jinja2Templates(directory="app/templates")
        # 获取站点信息
        siteInfo = request.app.state.config["site"]
        return templates.TemplateResponse(
            request=request, name="index.html",context={"siteInfo": siteInfo}
        )