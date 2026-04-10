"""Monday.com-specific pricing schema.

Monday.com has 4 distinct products, each with their own tiers:
- Work Management: Free, Basic, Standard, Pro, Enterprise
- CRM: Basic, Standard, Pro, Ultimate
- Dev: Basic, Standard, Pro, Enterprise
- Service: Standard, Pro, Enterprise

Key differences from others:
- Multiple distinct products with separate pricing
- Minimum 3 seats on all paid plans
- Custom quote required above 40 users
- 18% annual discount
- CRM has active contacts/deals limits, columns per board limits
- Service has no Basic tier
"""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator, model_validator

from .common import CompetitorBase, Feature, PricingInfo, TrialInfo


class MondayGlobalPolicies(BaseModel):
    """Global policies that apply across all Monday.com products."""

    minimum_seats: int = Field(default=3, description="Minimum seats for paid plans")
    annual_discount_pct: float = Field(default=18.0, description="Discount for annual billing")
    trial_days: int = Field(default=14, description="Free trial duration")
    custom_quote_above_seats: int = Field(default=40, description="Contact sales above this")
    refund_window_days: int = Field(default=30, description="Refund window for annual plans")


class MondayPlan(BaseModel):
    """A single plan within a Monday.com product."""

    name: str = Field(description="Display name: Free, Basic, Standard, Pro, Enterprise, Ultimate")
    slug: str = Field(description="Lowercase: free, basic, standard, pro, enterprise, ultimate")
    is_free: bool = Field(default=False)
    is_custom_pricing: bool = Field(default=False)
    pricing: PricingInfo | None = None
    free_seats_limit: int | None = Field(None, description="Max free seats (2 for Free plan)")

    # CRM-specific limits (only populated for CRM product)
    active_contacts_deals: int | str | None = Field(
        None, description="Active contacts/deals limit: int or 'unlimited'"
    )
    custom_dashboards: int | str | None = Field(
        None, description="Custom dashboard limit: int or 'unlimited'"
    )
    columns_per_board: int | str | None = Field(
        None, description="Column limit per board: int or 'unlimited'"
    )
    quotes_invoices_per_month: int | str | None = Field(
        None, description="Quotes/invoices per month: int or 'unlimited'"
    )

    # Features by category
    features: dict[str, list[Feature]] = Field(
        default_factory=dict,
        description="Feature categories vary by product"
    )

    @field_validator("features", mode="before")
    @classmethod
    def coerce_features(cls, v):
        return v if v is not None else {}

    @model_validator(mode="after")
    def pricing_consistency(self) -> "MondayPlan":
        if self.is_free and self.pricing is not None and self.pricing.monthly_per_unit and self.pricing.monthly_per_unit > 0:
            raise ValueError("Free plan should not have a price > 0")
        if self.is_custom_pricing and self.pricing is not None:
            raise ValueError("Custom pricing plans should not have pricing info")
        return self


class MondayProduct(BaseModel):
    """A single Monday.com product (Work Management, CRM, Dev, Service)."""

    name: str = Field(description="Product name: Work Management, CRM, Dev, Service")
    slug: str = Field(description="Lowercase: work-management, crm, dev, service")
    plans: list[MondayPlan]

    @model_validator(mode="after")
    def validate_plan_count(self) -> "MondayProduct":
        if len(self.plans) < 2:
            raise ValueError(f"Monday {self.name} should have at least 2 plans")
        return self


class MondayPricing(CompetitorBase):
    """Complete Monday.com pricing data."""

    global_policies: MondayGlobalPolicies = Field(default_factory=MondayGlobalPolicies)
    products: list[MondayProduct]

    @model_validator(mode="after")
    def validate_product_count(self) -> "MondayPricing":
        if len(self.products) < 1:
            raise ValueError("Monday.com should have at least 1 product")
        return self
