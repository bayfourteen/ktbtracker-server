from babel.dates import format_date
from fastapi.templating import Jinja2Templates
from fastapi_babel import _


async def get_templates():
    templates = Jinja2Templates(directory="templates")
    templates.env.globals.update(_=_)
    templates.env.filters["format_date"] = \
        lambda dt, format='medium', locale='en_US': format_date(dt, format=format, locale=locale)
