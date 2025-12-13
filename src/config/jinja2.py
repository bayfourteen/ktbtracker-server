import logging
import math
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

from babel.dates import format_date
from babel.numbers import format_number, format_decimal
from fastapi.templating import Jinja2Templates
from fastapi_csrf_jinja.jinja_processor import csrf_token_processor
from pydantic.alias_generators import to_camel
from sqlmodel import case

from config.i18n import _
from config.observability import debug

logger = logging.getLogger(__name__)

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


def factional(value: int | float) -> bool:
    logger.info(f"factional({value}) type={type(value)}")
    return type(value) == float


def available(value: date, field: str) -> bool:
    logger.info(f"available({value}, {field}) type={type(value)}, weekday={value.weekday()}")
    if value.weekday() < 6:
        if value.weekday() < 5:
            return field.startswith("class_") and field != "class_saturday"
        return field == "class_saturday"
    return False


@debug
def get_templates():
    templates = Jinja2Templates(directory=str(Path(BASE_DIR, 'templates')), context_processors=[csrf_token_processor()])
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
    templates.env.filters["to_camel"] = lambda v: to_camel(v)
    templates.env.filters["cycle_day"] = lambda v: v if v < 0 else v + 1
    templates.env.filters["cycle_week"] = lambda v: v if v < 0 else v + 1
    templates.env.tests["available"] = lambda v, f: available(v, f)
    templates.env.tests["fractional"] = lambda v: factional(v)

    return templates
