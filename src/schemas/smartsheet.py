"""Smartsheet-specific pricing schema.

Smartsheet has 4 plan tiers: Pro, Business, Enterprise, AWM.
Key differences from others:
- Multi-currency support (13 currencies)
- Member min/max caps per plan
- Viewers and Guests as separate concepts
- Premium add-ons with separate pricing
- Tiered support levels (included/add-on/not available)
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator

from .common import CompetitorBase, Feature, PricingInfo, TrialInfo, UserLimits


class SmartsheetPlan(BaseModel):
    """A single Smartsheet pricing tier."""

    name: str = Field(description="Display name: Pro, Business, Enterprise, Advanced Work Management")
    slug: str = Field(description="Lowercase identifier: pro, business, enterprise, awm")
    label: str | None = Field(None, description="Marketing label: 'Most Popular', 'Best Value'")
    is_custom_pricing: bool = Field(default=False, description="True if contact-sales only")
    pricing: PricingInfo | None = Field(None, description="None if custom pricing")
    trial: TrialInfo | None = None

    # User limits
    members: UserLimits | None = None
    viewers: str = Field(default="unlimited", description="Viewer access: 'unlimited' or a number")
    guests: str | int = Field(default=0, description="Guest access: 'unlimited', int, or 0")

    # Resource limits
    storage_gb: int | None = Field(None, description="Total storage in GB")
    max_attachment_mb: int | None = Field(None, description="Max single attachment size in MB")
    automations_per_month: int | str = Field(
        description="Automations per month: integer or 'unlimited'"
    )
    dashboard_widgets: int | str = Field(
        default="unlimited", description="Dashboard widgets: integer or 'unlimited'"
    )
    sheets_per_report: int | str = Field(
        default="unlimited", description="Sheets per report: integer or 'unlimited'"
    )

    # Features organized by category
    features: dict[str, list[Feature]] = Field(
        default_factory=dict,
        description="Features grouped by category: views, formulas_data, automations, integrations, collaboration, security_admin"
    )

    @field_validator("features", mode="before")
    @classmethod
    def coerce_features(cls, v):
        return v if v is not None else {}

    @model_validator(mode="after")
    def pricing_consistency(self) -> "SmartsheetPlan":
        if self.is_custom_pricing and self.pricing is not None:
            raise ValueError("Custom pricing plans should not have pricing info")
        if not self.is_custom_pricing and self.pricing is None:
            raise ValueError("Non-custom plans must have pricing info")
        return self


class SmartsheetAddOn(BaseModel):
    """A premium add-on available for purchase."""

    name: str
    description: str | None = None
    eligible_plans: list[str] = Field(description="Plan slugs that can use this add-on")
    starting_price: str | None = Field(None, description="e.g., '$125/month' or None if contact-sales")


class SmartsheetSupport(BaseModel):
    """Support tier availability across plans."""

    level: str = Field(description="e.g., 'Standard', 'Premium', 'TAM'")
    availability: dict[str, str] = Field(
        description="Plan slug -> 'included' | 'add-on' | 'not_available'"
    )


class SmartsheetPricing(CompetitorBase):
    """Complete Smartsheet pricing data."""

    plans: list[SmartsheetPlan]
    add_ons: list[SmartsheetAddOn] = Field(default_factory=list)
    support_tiers: list[SmartsheetSupport] = Field(default_factory=list)
    supported_currencies: list[str] = Field(
        default_factory=lambda: ["USD"],
        description="ISO currency codes supported"
    )

    @model_validator(mode="after")
    def validate_plan_count(self) -> "SmartsheetPricing":
        if len(self.plans) < 2:
            raise ValueError("Smartsheet should have at least 2 plans")
        return self
