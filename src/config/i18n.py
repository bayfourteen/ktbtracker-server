import gettext
import logging
from pathlib import Path

from fastapi import Request
from fastapi.templating import Jinja2Templates
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class TranslationWrapper:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.init_translation()
        return cls._instance

    def init_translation(self):
        lang = "en"  # Default language
        locales_dir = Path(__file__).parent.parent / "locale"
        self.translations = gettext.translation(
            "messages",
            localedir=locales_dir,
            languages=[lang],
            fallback=True
        )
        self.translations.install()
        logger.info(f"Translations installed locale={lang}, localedir={locales_dir}, fallback=True")

    def gettext(self, message: str) -> str:
        return self.translations.gettext(message)

    def info(self) -> dict[str, str]:
        return self.translations.info()

class I18nMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, templates: Jinja2Templates):
        super().__init__(app)
        self.templates = templates

    async def dispatch(self, request: Request, call_next):
        lang = request.session.get('language') or request.headers.get("Accept-Language", "en")
        await set_locale(request, lang)

        self.templates.env.globals['_'] = _
        self.templates.env.globals['lang'] = lang

        response = await call_next(request)
        return response


async def set_locale(request: Request, lang: str = "en"):
    translation_wrapper = TranslationWrapper()

    locales_dir = Path(__file__).parent.parent / "locale"
    print(f"Setting language to: {lang}")
    translation_wrapper.translations = gettext.translation(
        "messages", localedir=locales_dir, languages=[lang], fallback=True
    )
    translation_wrapper.translations.install()
    logger.info(f"Translations installed language={lang}, localedir={locales_dir}, fallback=True")


def _(message: str) -> str:
    translation_wrapper = TranslationWrapper()
    logger.info(f"Translating message: {message} -> {translation_wrapper.gettext(message)}")
    return translation_wrapper.gettext(message)
