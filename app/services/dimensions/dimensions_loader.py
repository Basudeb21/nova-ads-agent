
import json
import re
from pathlib import Path
from typing import Any

from app.core.config import ROOT_DIR


DIMENSIONS_FILE = ROOT_DIR / "config" / "dimensions.json"


class DimensionsLoader:

    PLACEMENT_ALIASES = {
        "instagram": {
            "feed": "feed_square",
            "instagram_feed": "feed_square",
            "post": "feed_square",
            "instagram_post": "feed_square",
            "feed_post": "feed_square",
            "square_post": "feed_square",
            "square_feed": "feed_square",
            "portrait_feed": "feed_portrait",
            "instagram_portrait_feed": "feed_portrait",
            "portrait_post": "feed_portrait",
            "feed_portrait_post": "feed_portrait",
            "instagram_story": "story",
            "reel": "reels_cover",
            "instagram_reel": "reels_cover",
            "reels": "reels_cover",
            "reels_cover": "reels_cover",
        },
        "facebook": {
            "feed": "feed_square",
            "facebook_feed": "feed_square",
            "post": "feed_square",
            "facebook_post": "feed_square",
            "feed_post": "feed_square",
            "square_post": "feed_square",
            "portrait_feed": "feed_portrait",
            "portrait_post": "feed_portrait",
            "facebook_story": "story",
            "cover_image": "cover",
        },
        "youtube": {
            "video_thumbnail": "thumbnail",
            "youtube_thumbnail": "thumbnail",
            "post": "community_post",
            "community": "community_post",
        },
        "tiktok": {
            "post": "feed",
            "video": "feed",
            "tiktok_feed": "feed",
        },
        "linkedin": {
            "feed": "feed_square",
            "linkedin_feed": "feed_square",
            "post": "feed_square",
            "linkedin_post": "feed_square",
            "square_post": "feed_square",
            "landscape_post": "feed_landscape",
            "landscape_feed": "feed_landscape",
        },
        "website": {
            "banner": "banner_landscape",
            "landscape_banner": "banner_landscape",
            "square_banner": "banner_square",
        },
    }

    def __init__(self):
        self.dimensions: dict[str, Any] = {}
        self.load()

    def load(self) -> None:
        if not DIMENSIONS_FILE.exists():
            raise FileNotFoundError(
                f"Dimensions configuration not found: {DIMENSIONS_FILE}"
            )

        try:
            with DIMENSIONS_FILE.open("r", encoding="utf-8") as file:
                data = json.load(file)

        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Invalid dimensions JSON: {exc}"
            ) from exc

        if not isinstance(data.get("platforms"), dict):
            raise ValueError(
                "Dimensions configuration must contain a platforms object."
            )

        self.dimensions = data

    @staticmethod
    def _normalize_name(value: str) -> str:
        value = value.strip().lower()
        value = re.sub(r"[\s-]+", "_", value)
        return re.sub(r"_+", "_", value).strip("_")

    def get_all_platforms(self) -> dict[str, Any]:
        return self.dimensions["platforms"]

    def get_platform(self, platform: str) -> dict[str, Any]:
        platform = self._normalize_name(platform)
        platforms = self.get_all_platforms()

        if platform not in platforms:
            raise ValueError(
                f"Unsupported platform: {platform}"
            )

        return platforms[platform]

    def get_placements(self, platform: str) -> dict[str, Any]:
        return self.get_platform(platform)["placements"]

    def get_placement(
        self,
        platform: str,
        placement: str,
    ) -> dict[str, Any]:

        platform = self._normalize_name(platform)
        placement = self._normalize_name(placement)

        placements = self.get_placements(platform)

        canonical_placement = self.PLACEMENT_ALIASES.get(
            platform,
            {},
        ).get(placement, placement)

        if canonical_placement not in placements:
            raise ValueError(
                f"Unknown placement '{placement}' for platform '{platform}'. "
                f"Supported placements: {', '.join(placements.keys())}"
            )

        result = placements[canonical_placement].copy()

        result["platform"] = platform
        result["placement"] = canonical_placement
        result["dimension_id"] = (
            f"{platform}.{canonical_placement}"
        )

        return result

    def get_all_placements(self) -> list[dict[str, Any]]:
        result = []

        for platform, platform_data in self.get_all_platforms().items():
            for placement, details in platform_data["placements"].items():
                result.append({
                    **details,
                    "platform": platform,
                    "placement": placement,
                    "dimension_id": f"{platform}.{placement}",
                })

        return result


dimensions_loader = DimensionsLoader()
