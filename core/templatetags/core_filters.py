from datetime import date

from django.template import library
from django.template.defaultfilters import stringfilter

register = library.Library()


@register.filter
def pct_color(value: int | float, alpha: float = 1.0, basis: float = 0) -> str:
    pct = normalize(value + basis)
    r = 1 - (2 * (pct - 0.50)) if pct > 0.5  else 1.0
    g = 1.0 if pct > 0.5 else (2 * pct)
    b = 0.0
    a = normalize(alpha)

    return f"rgba({byte_value(r)},{byte_value(g)},{byte_value(b)},{a})"


@register.filter
def byte_value(value: int | float) -> int | float:
    return round(normalize(value) * 255)


@register.filter
def normalize(value: int | float) -> int | float:
    return max(min(value, 1.0), 0.0)


@register.filter
def percent(value: int | float) -> float:
    return normalize(value) * 100


@register.filter
def factional(value: int | float) -> bool:
    #logger.info(f"factional({value}) type={type(value)}")
    return type(value) == float


@register.filter
def format_number(value: int | float) -> int | float:
    return str(value)


@register.simple_tag(name="format")
@stringfilter
def tag_format_string(value: str, *args, **kwargs) -> str:
    return value.format(*args, **kwargs)


@register.filter
def available(value: date, field: str) -> bool:
    #logger.info(f"available({value}, {field}) type={type(value)}, weekday={value.weekday()}")
    if value.weekday() < 6:
        if value.weekday() < 5:
            return field.startswith("class_") and field != "class_saturday"
        return field == "class_saturday"
    return False


@register.filter
def index(value, arg):
    try:
        return value[arg]
    except IndexError:
        return ''


@register.filter
def add(value, arg):
    """Adds the argument from the value."""
    try:
        return float(value) + float(arg)
    except (ValueError, TypeError):
        return ''


@register.filter
def sub(value, arg):
    """Subtracts the argument from the value."""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return ''

@register.filter
def mul(value, arg):
    """Multiplies the value by the argument."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ''

@register.filter
def div(value, arg):
    """Divides the value by the argument."""
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError):
        return ''


register.filter("cycle_day", lambda v: v if v < 0 else v + 1)
register.filter("cycle_week", lambda v: v if v < 0 else v + 1)

