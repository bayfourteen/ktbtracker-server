from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum
from itertools import chain
from typing import Iterator

from django.utils.translation import gettext as _


class classproperty:
    def __init__(self, f):
        self.f = f

    def __get__(self, instance, owner):
        return self.f(owner)


@dataclass
class RequirementsConfig:
    title: str
    description: str


class Requirements(Enum):
    # --- Physical Requirements ---
    BURPEES = RequirementsConfig(_("Burpees"), _("dream_team"))
    JUMPS = RequirementsConfig(_("Jumps"), _("dream_team"))
    KICKS = RequirementsConfig(_("Kicks"), _("dream_team"))
    MILES = RequirementsConfig(_("Miles"), _("dream_team"))
    PLANKS = RequirementsConfig(_("Planks"), _("dream_team"))
    POOMSAE = RequirementsConfig(_("Poomsae"), _("dream_team"))
    PULL_UPS = RequirementsConfig(_("Pull-ups"), _("dream_team"))
    PUSH_UPS = RequirementsConfig(_("Push-ups"), _("dream_team"))
    ROLLS_FALLS = RequirementsConfig(_("Rolls & Falls"), _("dream_team"))
    SELF_DEFENSE = RequirementsConfig(_("Self-Defense"), _("dream_team"))
    SIT_UPS = RequirementsConfig(_("Sit-Ups"), _("dream_team"))
    SPARRING = RequirementsConfig(_("Sparring"), _("dream_team"))
    # --- Class Requirements ---
    CLASS_DREAM_TEAM = RequirementsConfig(_("DreamTeam Class"), _("dream_team"))
    CLASS_HYPER_PRO = RequirementsConfig(_("HyperQuest Class"), _("dream_team"))
    CLASS_MASTER_Q = RequirementsConfig(_("MasterQuest Class"), _("dream_team"))
    CLASS_PMAA = RequirementsConfig(_("PMAA Class"), _("dream_team"))
    CLASS_SATURDAY = RequirementsConfig(_("Weekday Class"), _("dream_team"))
    CLASS_SPARRING = RequirementsConfig(_("Sparring Class"), _("dream_team"))
    CLASS_WEEKDAY = RequirementsConfig(_("Saturday Class (Black Belt)"), _("dream_team"))
    # --- Other Requirements ---
    JOURNALS = RequirementsConfig(_("Journals"), _("dream_team"))
    LEADERSHIP = RequirementsConfig(_("Lead Class/Activity"), _("dream_team"))
    LEADERSHIP2 = RequirementsConfig(_("Assist Class/Activity"), _("dream_team"))
    MEDITATION = RequirementsConfig(_("Meditation"), _("dream_team"))
    MENTEE = RequirementsConfig(_("Be Mentored"), _("dream_team"))
    MENTOR = RequirementsConfig(_("Mentor Someone"), _("dream_team"))
    RAOK = RequirementsConfig(_("Random Acts of Kindness"), _("dream_team"))

    @classmethod
    def get_description(cls, key: str, default: str | None = None, case_sensitive: bool = False):
        if key is None:
            return default
        if case_sensitive:
            for m in cls:
                if m.name == key:
                    return m.value.description
            return default
        target = str(key).lower()
        for m in cls:
            if m.name.lower() == target:
                return m.value.description
        return default

    @property
    def description(self) -> str:
        return self.value.description

    @property
    def key(self) -> str:
        return self.name.lower()

    @property
    def title(self) -> str:
        return self.value.title

    @classmethod
    def get_title(cls, key: str, default: str | None = None, case_sensitive: bool = False):
        if key is None:
            return default
        if case_sensitive:
            for m in cls:
                if m.name == key:
                    return m.value.title
            return default
        target = str(key).lower()
        for m in cls:
            if m.name.lower() == target:
                return m.value.title
        return default

    @classmethod
    def TRACKING_NAMES(cls) -> dict[str, str]:
        return {e.key: e.title for e in cls}

    @classmethod
    def CLASS(cls) -> Iterable[str]:
        return [
            cls.CLASS_DREAM_TEAM.key,
            cls.CLASS_HYPER_PRO.key,
            cls.CLASS_MASTER_Q.key,
            cls.CLASS_SATURDAY.key,
            cls.CLASS_SPARRING.key,
            cls.CLASS_WEEKDAY.key,
        ]

    @classmethod
    def OTHER(cls) -> Iterable[Requirements]:
        return [
            cls.JOURNALS,
            cls.LEADERSHIP,
            cls.LEADERSHIP2,
            cls.MEDITATION,
            cls.MENTEE,
            cls.MENTOR,
            cls.RAOK,
        ]

    @classmethod
    def PHYSICAL(cls) -> Iterable[str]:
        return [
            cls.BURPEES.key,
            cls.JUMPS.key,
            cls.KICKS.key,
            cls.MILES.key,
            cls.PLANKS.key,
            cls.POOMSAE.key,
            cls.PULL_UPS.key,
            cls.PUSH_UPS.key,
            cls.ROLLS_FALLS.key,
            cls.SELF_DEFENSE.key,
            cls.SIT_UPS.key,
            cls.SPARRING.key,
        ]
