import logging
from datetime import date
from typing import Any

from django.template import library, Context
from django.template.defaultfilters import stringfilter

from core.models import Tracking
from tracking.forms import TrackingForm

logger = logging.getLogger(__name__)

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
def normalize(value: int | float) -> float:
    try:
        return min(max(float(value), 0.0), 1.0)
    except (ValueError, TypeError):
        return 0.0

@register.filter
def pct(value: int | float) -> float:
    try:
        return normalize(value) * 100.0
    except (ValueError, TypeError):
        return 0.0


@register.filter
def percent(value: int | float) -> float:
    try:
        return float(value) * 100.0
    except (ValueError, TypeError):
        return 0.0


@register.filter
def fractional(value: int | float) -> bool:
    return type(value) == float


@register.filter
def format_number(value: int | float) -> str:
    return str(value)


@register.simple_tag(name="format")
@stringfilter
def tag_format_string(value: str, *args, **kwargs) -> str:
    return value.format(*args, **kwargs)


@register.filter
def available(value: date, field: str) -> bool:
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
def keyof(value, arg):
    if isinstance(value, TrackingForm):
        logger.info(f"keyof {value=} {arg=}")
    if value:
        try:
            if isinstance(value, dict):
                return value[arg]
            if isinstance(value, object):
                return getattr(value, arg)
            return ''
        except IndexError | AttributeError | TypeError:
            return ''
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


@register.filter
def cycle_day(value):
    try:
        return int(value) if int(value) < 0 else int(value) + 1
    except (ValueError, TypeError):
        return ''


@register.filter
def cycle_week(value):
    try:
        return int(value) if int(value) < 0 else int(value) + 1
    except (ValueError, TypeError):
        return ''


@register.simple_tag(takes_context=True)
def nav_disabled(context: Context) -> str | None:
    return " disabled" if context.get("request") and context.get("request").path.startswith("/log") else ""


@register.simple_tag(takes_context=True)
def path_active(context: Context, *args: str | None, emit: str = " active") -> str:
    if args and len(args) == 1:
        return emit if context.get("request") and context.get("request").path.startswith(str(args[0])) else ""
    if args and len(args) > 1:
        return emit if context.get("request") and context.get("request").path in [str(arg) for arg in args] else ""
    return ""


@register.simple_tag(takes_context=True)
def tracking_for_date(context: Context, *args: Any | None) -> Tracking:
    object_list = context.get("object_list") or Tracking.objects.none()
    candidate = context.get("candidate")
    tracking_date = args[0] if args and isinstance(args[0], date) else date.today()

    if object_list.filter(tracking_date=tracking_date).exists():
        return object_list.get(tracking_date=tracking_date)

    return Tracking(candidate=candidate, tracking_date=tracking_date)
