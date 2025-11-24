import math
import sys
from pathlib import Path

from babel.dates import format_date
from babel.numbers import format_number, format_decimal
from fastapi.templating import Jinja2Templates

from config.i18n import _

BASE_DIR = Path(__file__).parent.parent


def pct_color(value: int | float, alpha: float = 1.0, basis: float = 0) -> str:
    pct = normalize(value + basis)
    r = 1 - (2 * (pct - 0.50)) if pct > 0.5  else 1.0
    g = 1.0 if pct > 0.5 else (2 * pct)
    b = 0.0
    a = normalize(alpha)

    return f"rgba({byte_value(r)},{byte_value(g)},{byte_value(b)},{a})"


def byte_value(value: int | float) -> int | float:
    return round(normalize(value) * 255)


def normalize(value: int | float) -> int | float:
    return max(min(value, 1.0), 0.0)


def percent(value: int | float) -> float:
    return normalize(value) * 100


def get_templates():
    templates = Jinja2Templates(directory=str(Path(BASE_DIR, 'templates')))
    templates.env.globals.update(_=_)
    #templates.env.add_extension("jinja2.ext.i18n")
    #templates.env.add_extension("jinja2.ext.with_")
    # templates.env.extensions=["jinja2.ext.i18n", "jinja2.ext.autoescape", "jinja2.ext.with_"]
    templates.env.filters["format_date"] = \
        lambda dt, format='medium', locale='en_US': format_date(dt, format=format, locale=locale)
    templates.env.filters["format_number"] = \
        lambda n, format='#,##0.##;-#', locale='en_US': format_decimal(n, format=format, locale=locale)
    templates.env.filters["normalize"] = lambda v: normalize(v)
    templates.env.filters["pct_color"] = lambda v: pct_color(v)
    templates.env.filters["percent"] = lambda v: percent(v)

    return templates
