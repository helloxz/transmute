from app.api.translate import Translate
from app.api.html import Html

from fastapi import APIRouter

# 创建 APIRouter 实例
router = APIRouter()


translate = Translate()
html =Html()

router.post("/api/translate")(translate.chat)
router.get("/api/get/models")(translate.get_models)
router.get("/api/get/languages")(translate.get_languages)
router.get("/")(html.index)
