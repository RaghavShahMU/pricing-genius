"""Wrike-specific pricing schema.

Wrike has 6 tiers: Free, Team, Business, Enterprise, Pinnacle, Apex.
Key differences from others:
- Per-user storage (GB per user)
- Automation actions per seat per month
- Guest user limits
- AI tier levels (Essentials, Elite, full suite)
- Business+ is annual billing only
"""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator, model_validator

from .common import CompetitorBase, Feature, PricingInfo, TrialInfo, UserLimits


class WrikePlan(BaseModel):
    """A single Wrike pricing tier."""

    name: str = Field(description="Display name: Free, Team, Business, Enterprise, Pinnacle, Apex")
    slug: str = Field(description="Lowercase: free, team, business, enterprise, pinnacle, apex")
    is_free: bool = Field(default=False)
    is_custom_pricing: bool = Field(default=False)
    pricing: PricingInfo | None = None
    trial: TrialInfo | None = None
    billing_note: str | None = Field(None, description="e.g., 'Annual billing only'")

    # User limits
    users: UserLimits | None = None

    # Resource limits
    storage_gb_per_user: float | None = Field(None, description="Storage in GB per user")
    automations_per_seat_month: int | str | None = Field(
        None, description="Automation actions per seat per month: int or 'unlimited'"
    )
    guest_users: int | str | None = Field(None, description="Free guest users: int or 'unlimited'")
    active_tasks: int | str | None = Field(
        None, description="Active task limit: int or 'unlimited'"
    )

    # AI features
    ai_tier: str | None = Field(None, description="AI tier name: 'Essentials', 'Elite', 'Full Suite'")

    # Features by category
    features: dict[str, list[Feature]] = Field(
        default_factory=dict,
        description="Categories: task_mgmt, views, collaboration, automation, resource_mgmt, security, reporting, integrations, ai"
    )

    @field_validator("features", mode="before")
    @classmethod
    def coerce_features(cls, v):
        return v if v is not None else {}

    @model_validator(mode="after")
    def pricing_consistency(self) -> "WrikePlan":
        if self.is_free and self.pricing is not None and self.pricing.monthly_per_unit and self.pricing.monthly_per_unit > 0:
            raise ValueError("Free plan should not have a price > 0")
        if self.is_custom_pricing and self.pricing is not None:
            raise ValueError("Custom pricing plans should not have pricing info")
        return self


class WrikeAddOn(BaseModel):
    """Wrike premium add-on."""

    name: str
    description: str | None = None
    eligible_plans: list[str] = Field(default_factory=list)


class WrikePricing(CompetitorBase):
    """Complete Wrike pricing data."""

    plans: list[WrikePlan]
    add_ons: list[WrikeAddOn] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_plan_count(self) -> "WrikePricing":
        if len(self.plans) < 3:
            raise ValueError("Wrike should have at least 3 plans")
        return self
