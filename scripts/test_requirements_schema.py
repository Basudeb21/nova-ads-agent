import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.schemas.requirements import (
    ProjectRequirements,
)


def main():

    print("\n========================================")
    print("  PROJECT REQUIREMENTS SCHEMA TEST")
    print("========================================")

    requirements = ProjectRequirements(
        project={
            "project_name": "Summer Product Campaign",
            "purpose": "Product advertisement",
            "category": "Beauty",
            "description": "Summer promotional campaign",
            "creative_variations": 3,
        },
        placements=[
            {"platform": "instagram", "placement": "story"},
            {"platform": "facebook", "placement": "feed_square"},
            {"platform": "youtube", "placement": "thumbnail"},
        ],
        audience={
            "age_group": ["18-24", "25-34"],
            "locations": ["India"],
            "interests": ["Beauty", "Skincare"],
        },
        creative_direction={
            "visual_style": "Premium and modern",
            "preferred_colors": ["Black", "Gold"],
            "avoid_colors": ["Neon Green"],
            "mood": "Luxury",
        },
        advertisement_content={
            "headline": {
                "text": "Discover Your Beauty",
                "source": "ai",
                "must_preserve": True,
                "confirmed": False,
            },
            "slogan": {
                "text": "Feel the difference.",
                "source": "user",
                "must_preserve": True,
                "confirmed": True,
            },
            "call_to_action": {
                "text": "Shop Now",
                "source": "user",
                "must_preserve": True,
                "confirmed": True,
            },
        },
        brand={
            "logo_required": True,
            "brand_name": "Example Brand",
        },
        additional_instructions=[
            "Keep the original product appearance.",
            "Use premium advertising aesthetics.",
        ],
    )

    print("\nProject:", requirements.project.project_name)

    print("\nResolved Placements:")

    for placement in requirements.placements:
        print(
            f"{placement.platform} / "
            f"{placement.placement}: "
            f"{placement.width}x{placement.height}"
        )

    print("\nCopy Preservation Test:")

    slogan = requirements.advertisement_content.slogan

    print("Slogan:", slogan.text)
    print("Source:", slogan.source)
    print("Must Preserve:", slogan.must_preserve)
    print("Confirmed:", slogan.confirmed)

    print("\nJSON Serialization Test:")

    print(requirements.model_dump_json(indent=4))

    print("\nREQUIREMENTS SCHEMA TEST SUCCESSFUL")


if __name__ == "__main__":
    main()