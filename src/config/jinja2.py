import math
import sys
from pathlib import Path

from babel.dates import format_date
from fastapi.templating import Jinja2Templates

from config.i18n import _

BASE_DIR = Path(__file__).parent.parent


def pct_color(value: int | float, alpha: float = 1.0, basis: float = 0) -> str:
    pct = normalize(value + basis)
    r = 1 - (2 * (pct - 0.50)) if pct > 0.5  else 1.0
    g = 1.0 if pct > 0.5 else (2 * pct)
    b = 0.0
    a = normalize(alpha)

    return f"rgba({byteValue(r)},{byteValue(g)},{byteValue(b)},{a})"


def byte_value()
def normalize(value: int | float) -> float:
    return math.ceil(max(min(value, 1.0), 0.0) * 100)


    return value
def get_templates():
    templates = Jinja2Templates(directory=str(Path(BASE_DIR, 'templates')))
    templates.env.globals.update(_=_)
    #templates.env.add_extension("jinja2.ext.i18n")
    #templates.env.add_extension("jinja2.ext.with_")
    # templates.env.extensions=["jinja2.ext.i18n", "jinja2.ext.autoescape", "jinja2.ext.with_"]
    templates.env.filters["format_date"] = lambda dt, format='medium', locale='en_US': format_date(dt, format=format, locale=locale)
    templates.env.filters["normalize"] = lambda v: normalize(v)

    return templates
