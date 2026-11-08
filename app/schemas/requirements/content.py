from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class CopyText(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    text: str = Field(
        min_length=1,
        max_length=2000,
    )

    source: Literal["user", "ai"] = "user"

    must_preserve: bool = True

    confirmed: bool = False


class AdvertisementContent(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    headline: CopyText | None = None

    subheadline: CopyText | None = None

    description: CopyText | None = None

    slogan: CopyText | None = None

    tagline: CopyText | None = None

    call_to_action: CopyText | None = None

    price: CopyText | None = None

    offer: CopyText | None = None

    promo_code: CopyText | None = None

    disclaimer: CopyText | None = None

    contact_information: CopyText | None = None

    website: CopyText | None = None

    additional_text_instructions: str | None = None