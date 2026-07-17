"""Home page view-model builder."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

UNSPLASH_HERO = "https://images.unsplash.com/photo-1587300003388-59208cc962cb?w=800&q=80"
UNSPLASH_AVATAR = "https://images.unsplash.com/photo-1587300003388-59208cc962cb?w=200&q=80"


@dataclass
class DetailBlockVM:
    title: str
    text: str = ""
    bullets: list[str] = field(default_factory=list)


@dataclass
class HomePageVM:
    pet_name: str
    greeting: str
    greeting_sub: str
    hero_url: str
    avatar_url: str
    breed_label: str
    age_display: str
    weight_display: str
    sex: str
    tags: list[str]
    detail_blocks: list[DetailBlockVM]


class HomeRenderer:
    def build(self, report: dict[str, Any]) -> HomePageVM:
        profile = report.get("profile", {})
        pet_name = profile.get("pet_name", "Dolly")
        breeds = profile.get("breeds", ["Golden Retriever", "Labrador Retriever"])
        if len(breeds) > 1:
            breed_label = f"{breeds[0]} × {breeds[1]} Mix"
        else:
            breed_label = breeds[0] if breeds else "Mixed Breed"

        return HomePageVM(
            pet_name=pet_name,
            greeting=f"Hello, {pet_name}'s Parent 👋",
            greeting_sub=f"Here's {pet_name}'s latest wellness journey with Wagtopia.",
            hero_url=UNSPLASH_HERO,
            avatar_url=UNSPLASH_AVATAR,
            breed_label=breed_label,
            age_display=f"{profile.get('age_years', 3):.0f} yrs",
            weight_display=f"{profile.get('weight_kg', 28):.0f} kg",
            sex=profile.get("sex", "Female"),
            tags=["Energetic", "Friendly", "Sensitive Skin", "Loves Treats", "Social"],
            detail_blocks=[
                DetailBlockVM(
                    "Personality",
                    "Energetic, affectionate, highly social — loves attention from groomers and thrives in group play sessions.",
                ),
                DetailBlockVM(
                    "Behavior Notes",
                    bullets=[
                        "Slightly skittish during blow drying",
                        "Responds well to treats",
                        "Prefers slow introductions to new grooming tools",
                    ],
                ),
                DetailBlockVM(
                    "Sensitive Areas",
                    "Sensitive around paws and eye area. Extra care taken during ear cleaning and paw pad trimming.",
                ),
                DetailBlockVM(
                    "Favorite Treats",
                    bullets=[
                        "Frozen yogurt bites",
                        "Duck training treats",
                        "Wagtopia Bakery Salmon Crisps",
                    ],
                ),
            ],
        )
