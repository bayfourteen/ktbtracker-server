from typing import ClassVar

def _(message: str) -> str: return message


class RequirementsConfig:

    CLASS: ClassVar[list[str]] = [
        _("class_dream_team"),
        _("class_hyper_pro"),
        _("class_master_q"),
        _("class_pmaa"),
        _("class_saturday"),
        _("class_sparring"),
        _("class_weekday"),
    ]

    OTHER: ClassVar[list[str]] = [
        _("journals"),
        _("leadership"),
        _("leadership2"),
        _("meditation"),
        _("mentee"),
        _("mentor"),
        _("raok"),
    ]

    PHYSICAL: ClassVar[list[str]] = [
        _("burpees"),
        _("jumps"),
        _("kicks"),
        _("miles"),
        _("planks"),
        _("poomsae"),
        _("pull_ups"),
        _("push_ups"),
        _("rolls_falls"),
        _("self_defense"),
        _("sit_ups"),
        _("sparring"),
    ]
