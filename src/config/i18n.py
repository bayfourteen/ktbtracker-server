import gettext
import logging
from pathlib import Path

from fastapi import Request
from fastapi.templating import Jinja2Templates
from starlette.middleware.base import BaseHTTPMiddleware

from src.config.observability import debug
from src.config.settings import get_settings

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
        locales_dir = Path(__file__).parent.parent / "locales"
        self.translations = gettext.translation(
            "messages",
            localedir=locales_dir,
            languages=[lang],
            fallback=True
        )
        self.translations.install()
        logger.info(f"Translations INSTALLED locale={lang}, localedir={locales_dir}, fallback=True")

    def gettext(self, message: str) -> str:
        return self.translations.gettext(message)

    def info(self) -> dict[str, str]:
        return self.translations.info()


class I18nMiddleware(BaseHTTPMiddleware):
    def __init__(self, app,):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        await set_locale(request)

        response = await call_next(request)
        return response


@debug
async def set_locale(request: Request, lang: str | None = None):
    locales_dir = Path(__file__).parent.parent / "locales"
    translation_wrapper = TranslationWrapper()
    settings = await get_settings()

    logger.info(f"{request.query_params=}")
    # Query parameter "lang" ALWAYS takes precedence!
    if lang is None and request.query_params.get("lang"):
        query_language = request.query_params.get("lang")
        logger.info(f"Detected explicitly requested locale (request query parameter): {query_language}")
        if query_language in settings.supported_locales:
            lang = query_language

    # Otherwise, the client's preferred locale (cookie) is next
    if lang is None and request.cookies.get("preferred_language"):
        preferred_language = request.cookies.get("preferred_language")
        logger.debug(f"Detected preferred locale (request cookie): {preferred_language}")
        if preferred_language in settings.supported_locales:
            lang = preferred_language

    # See if the browser supports one of our supported locales
    if lang is None and request.headers.get("Accept-Language"):
        logger.debug(f"Detected browser supported locale(s) (request header): {[tag.split("-")[0] for tag in request.headers.get("Accept-Language").split(",")]}")
        for accepted_language in [tag.split("-")[0] for tag in request.headers.get("Accept-Language").split(",")]:
            if accepted_language in settings.supported_locales:
                lang = accepted_language

    # Fallback to "en"!
    if lang is None:
        logger.debug("Falling back to default locale: en")
        lang = "en"

    # If the language has changed update our translations wrapper
    if translation_wrapper.translations.info().get("language") == lang:
        logger.info(f"Translations ALREADY INSTALLED language={lang}, localedir={locales_dir}, fallback=True")
        return lang

    print(f"Setting language to: {lang} {translation_wrapper.translations.info()}")
    translation_wrapper.translations = gettext.translation(
        "messages", localedir=locales_dir, languages=[lang], fallback=True
    )
    translation_wrapper.translations.install()
    logger.info(f"Translations INSTALLED language={lang}, localedir={locales_dir}, fallback=True")

    return lang


def _(message: str) -> str:
    translation_wrapper = TranslationWrapper()
    logger.info(f"Translating message: {message} -> {translation_wrapper.gettext(message)}")
    return translation_wrapper.gettext(message)
