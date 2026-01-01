import gettext
import logging
import re
from pathlib import Path

from fastapi import Request, status
from fastapi.templating import Jinja2Templates
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import RedirectResponse

from src.config.observability import debug
from src.config.settings import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()


class TranslationWrapper:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.init_translation()
        return cls._instance

    def init_translation(self):
        locale = "en"  # Default locale
        locales_dir = Path(__file__).parent.parent / "locales"
        self.translations = gettext.translation(
            "messages",
            localedir=locales_dir,
            languages=[locale],
            fallback=True
        )
        self.translations.install()
        logger.info(f"Translations INSTALLED locale={locale}, localedir={locales_dir}, fallback=True")

    def gettext(self, message: str) -> str:
        return self.translations.gettext(message)

    def info(self) -> dict[str, str]:
        return self.translations.info()


class I18nMiddleware(BaseHTTPMiddleware):
    def __init__(self, app,):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        request_locale = request.url.path.strip('/').split('/')[0]
        current_locale = await get_locale(request)

        #logger.info(f"I18NMiddleware {request_locale=} {current_locale=} {settings=}")
        #if request_locale not in settings.supported_locales or request_locale != current_locale.split('-')[0]:
        #    logger.warning(f"Redirecting request to {str(request.url)}")
        #    return RedirectResponse(url=f"/{current_locale.split('-')[0]}{request.url.path}", status_code=status.HTTP_303_SEE_OTHER)

        response = await call_next(request)
        return response


@debug
async def get_locale(request: Request):
    return await set_locale(request)


@debug
async def set_locale(request: Request, language: str | None = None):
    locales_dir = Path(__file__).parent.parent / "locales"
    translation_wrapper = TranslationWrapper()

    # Query parameter "lang" ALWAYS takes precedence!
    if language is None and request.query_params.get("lang"):
        query_language = request.query_params.get("lang")
        logger.info(f"Detected explicitly requested language (request query parameter): {query_language}")
        if query_language in settings.supported_languages:
            language = query_language

    # Otherwise, the client's preferred language (cookie) is next
    if language is None and request.cookies.get("preferred_locale"):
        preferred_language = request.cookies.get("preferred_locale")
        logger.debug(f"Detected preferred locale (request cookie): {preferred_language}")
        if preferred_language.split('-')[0] in settings.supported_languages:
            language = preferred_language.replace('-', '_')

    # See if the browser supports one of our supported locales
    if language is None and request.headers.get("Accept-Language"):
        accepted_languages = re.findall(r"([^,]+)", request.headers.get("Accept-Language"))
        accepted_languages.sort(key=lambda t: (t + ";q=1.0").split(';')[1].split('=')[1], reverse=True)
        logger.debug(f"Detected browser supported locale(s) (request header): {accepted_languages}")
        for accepted_language in accepted_languages:
            if accepted_language.split('-')[0] in settings.supported_locales:
                language = accepted_language.split(';')[0].replace('-', '_')

    # Fallback to "en"!
    if language is None:
        logger.debug("Falling back to default locale: en")
        language = "en"

    # If the language has NOT changed, simply return the current language
    if translation_wrapper.translations.info().get("language") == language.replace('_', '-'):
        logger.info(f"Translations ALREADY INSTALLED languages={language}, localedir={locales_dir}, fallback=True")
        return language.replace('_', '-')

    print(f"Setting language to: {language} {translation_wrapper.translations.info()}")
    translation_wrapper.translations = gettext.translation(
        "messages", localedir=locales_dir, languages=[language], fallback=True
    )
    translation_wrapper.translations.install()
    logger.info(f"Translations INSTALLED languages={language}, localedir={locales_dir}, fallback=True")

    return language.replace('_', '-')


def _(message: str) -> str:
    translation_wrapper = TranslationWrapper()
    # logger.debug(f"Translating message: {message} -> {translation_wrapper.gettext(message)}")
    return translation_wrapper.gettext(message)
