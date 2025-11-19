from typing import ClassVar


class RequirementsConfig:

    CLASS: ClassVar[list[str]] = [
        "class_dream_team",
        "class_hyper_pro",
        "class_master_q",
        "class_pmaa",
        "class_saturday",
        "class_sparring",
        "class_weekday"
    ]

    OTHER: ClassVar[list[str]] = [
        "journals",
        "leadership",
        "leadership2",
        "meditation",
        "mentee",
        "mentor",
        "raok",
    ]

    PHYSICAL: ClassVar[list[str]] = [
        "burpees",
        "jumps",
        "kicks",
        "miles",
        "planks",
        "poomsae",
        "pull_ups",
        "push_ups",
        "rolls_falls",
        "self_defense",
        "sit_ups",
        "sparring"
    ]
