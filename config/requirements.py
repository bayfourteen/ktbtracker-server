from typing import ClassVar

def N_(message: str) -> str: return message


class RequirementsConfig:

    CLASS: ClassVar[list[str]] = [
        N_("class_dream_team"),
        N_("class_hyper_pro"),
        N_("class_master_q"),
        N_("class_pmaa"),
        N_("class_saturday"),
        N_("class_sparring"),
        N_("class_weekday"),
    ]

    OTHER: ClassVar[list[str]] = [
        N_("journals"),
        N_("leadership"),
        N_("leadership2"),
        N_("meditation"),
        N_("mentee"),
        N_("mentor"),
        N_("raok"),
    ]

    PHYSICAL: ClassVar[list[str]] = [
        N_("burpees"),
        N_("jumps"),
        N_("kicks"),
        N_("miles"),
        N_("planks"),
        N_("poomsae"),
        N_("pull_ups"),
        N_("push_ups"),
        N_("rolls_falls"),
        N_("self_defense"),
        N_("sit_ups"),
        N_("sparring"),
    ]
