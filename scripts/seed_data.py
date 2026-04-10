#!/usr/bin/env python3
"""Seed initial competitor pricing data from manual research.

This script populates data/*.json with known pricing information
gathered from competitor pricing pages. Run once to bootstrap,
then use extractors for ongoing updates.

Usage:
    python scripts/seed_data.py
"""

import sys
from datetime import datetime, timezone
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.schemas.common import BillingUnit, ExtractionMethod, Feature, PricingInfo, TrialInfo, UserLimits
from src.schemas.smartsheet import (
    SmartsheetAddOn,
    SmartsheetPlan,
    SmartsheetPricing,
    SmartsheetSupport,
)
from src.schemas.wrike import WrikeAddOn, WrikePlan, WrikePricing
from src.schemas.asana import (
    AsanaAIStudio,
    AsanaAIStudioTier,
    AsanaPlan,
    AsanaPricing,
    SeatScalingRule,
)
from src.schemas.notion import NotionAddOn, NotionPlan, NotionPricing, NotionSpecialProgram
from src.schemas.monday import (
    MondayGlobalPolicies,
    MondayPlan,
    MondayPricing,
    MondayProduct,
)
from src.storage.json_store import save_competitor

NOW = datetime.now(timezone.utc)


def seed_smartsheet() -> SmartsheetPricing:
    return SmartsheetPricing(
        competitor="smartsheet",
        display_name="Smartsheet",
        url="https://www.smartsheet.com/pricing",
        extracted_at=NOW,
        extraction_method=ExtractionMethod.MANUAL,
        supported_currencies=["AUD", "CAD", "CHF", "DKK", "EUR", "GBP", "JPY", "NOK", "NZD", "SEK", "SGD", "USD", "ZAR"],
        plans=[
            SmartsheetPlan(
                name="Pro",
                slug="pro",
                label=None,
                is_custom_pricing=False,
                pricing=PricingInfo(
                    monthly_per_unit=129.0,
                    annual_per_unit=None,
                    unit=BillingUnit.MEMBER,
                ),
                trial=TrialInfo(days=30, credit_card_required=False),
                members=UserLimits(min=1, max=10),
                viewers="unlimited",
                guests=0,
                storage_gb=20,
                max_attachment_mb=30,
                automations_per_month=250,
                dashboard_widgets=10,
                sheets_per_report=1,
                features={
                    "views": [
                        Feature(name="Grid View", available=True),
                        Feature(name="Gantt View", available=True),
                        Feature(name="Calendar View", available=True),
                        Feature(name="Board View", available=True),
                        Feature(name="Timeline View", available=False),
                    ],
                    "collaboration": [
                        Feature(name="Conversations", available=True),
                        Feature(name="Comments", available=True),
                        Feature(name="Proofing", available=False),
                        Feature(name="Publish Sheets", available=False),
                    ],
                    "integrations": [
                        Feature(name="Microsoft Office 365", available=True),
                        Feature(name="Google Workspace", available=True),
                        Feature(name="Slack", available=True),
                        Feature(name="Adobe Creative Cloud", available=False),
                        Feature(name="Power BI", available=False),
                        Feature(name="Tableau", available=False),
                    ],
                    "security_admin": [
                        Feature(name="SSO (Google/Microsoft/Apple)", available=True),
                        Feature(name="Admin Center", available=True),
                        Feature(name="SAML SSO", available=False),
                        Feature(name="Directory Integrations", available=False),
                        Feature(name="CMEK", available=False),
                    ],
                },
            ),
            SmartsheetPlan(
                name="Business",
                slug="business",
                label="Most Popular",
                is_custom_pricing=False,
                pricing=PricingInfo(
                    monthly_per_unit=2419.0,
                    annual_per_unit=None,
                    unit=BillingUnit.MEMBER,
                ),
                trial=TrialInfo(days=30, credit_card_required=False),
                members=UserLimits(min=3, max=None),
                viewers="unlimited",
                guests="unlimited",
                storage_gb=1024,
                max_attachment_mb=250,
                automations_per_month="unlimited",
                dashboard_widgets="unlimited",
                sheets_per_report="unlimited",
                features={
                    "views": [
                        Feature(name="Grid View", available=True),
                        Feature(name="Gantt View", available=True),
                        Feature(name="Calendar View", available=True),
                        Feature(name="Board View", available=True),
                        Feature(name="Timeline View", available=True),
                        Feature(name="Workload Tracking", available=True),
                    ],
                    "collaboration": [
                        Feature(name="Conversations", available=True),
                        Feature(name="Comments", available=True),
                        Feature(name="Proofing", available=True),
                        Feature(name="Publish Sheets", available=True),
                        Feature(name="Collections", available=True),
                    ],
                    "integrations": [
                        Feature(name="Microsoft Office 365", available=True),
                        Feature(name="Google Workspace", available=True),
                        Feature(name="Slack", available=True),
                        Feature(name="Adobe Creative Cloud", available=True),
                        Feature(name="Power BI", available=True),
                        Feature(name="Tableau", available=True),
                    ],
                    "security_admin": [
                        Feature(name="SSO (Google/Microsoft/Apple)", available=True),
                        Feature(name="Admin Center", available=True),
                        Feature(name="Plan Insights", available=True),
                        Feature(name="Group Management", available=True),
                        Feature(name="Schedule Backups", available=True),
                        Feature(name="Domain Validation", available=True),
                        Feature(name="SAML SSO", available=False),
                        Feature(name="CMEK", available=False),
                    ],
                },
            ),
            SmartsheetPlan(
                name="Enterprise",
                slug="enterprise",
                label=None,
                is_custom_pricing=True,
                pricing=None,
                trial=None,
                members=UserLimits(min=10, max=None),
                viewers="unlimited",
                guests="unlimited",
                storage_gb=None,
                max_attachment_mb=None,
                automations_per_month="unlimited",
                dashboard_widgets="unlimited",
                sheets_per_report="unlimited",
                features={
                    "views": [
                        Feature(name="Grid View", available=True),
                        Feature(name="Gantt View", available=True),
                        Feature(name="Calendar View", available=True),
                        Feature(name="Board View", available=True),
                        Feature(name="Timeline View", available=True),
                        Feature(name="Workload Tracking", available=True),
                    ],
                    "security_admin": [
                        Feature(name="SSO (Google/Microsoft/Apple)", available=True),
                        Feature(name="Admin Center", available=True),
                        Feature(name="SAML SSO", available=True),
                        Feature(name="Directory Integrations", available=True),
                        Feature(name="User Provisioning", available=True),
                        Feature(name="Enterprise Plan Manager", available=True),
                        Feature(name="Safe Sharing", available=True),
                        Feature(name="Data Retention Policies", available=True),
                        Feature(name="Event Reporting", available=True),
                        Feature(name="CMEK", available=True),
                    ],
                    "ai": [
                        Feature(name="Generate Formulas", available=True),
                        Feature(name="Generate Text/Summaries", available=True),
                        Feature(name="Analyze Data", available=True),
                    ],
                },
            ),
            SmartsheetPlan(
                name="Advanced Work Management",
                slug="awm",
                label="Best Value",
                is_custom_pricing=True,
                pricing=None,
                trial=None,
                members=UserLimits(min=None, max=None),
                viewers="unlimited",
                guests="unlimited",
                storage_gb=None,
                max_attachment_mb=None,
                automations_per_month="unlimited",
                dashboard_widgets="unlimited",
                sheets_per_report="unlimited",
                features={
                    "views": [
                        Feature(name="Grid View", available=True),
                        Feature(name="Gantt View", available=True),
                        Feature(name="Calendar View", available=True),
                        Feature(name="Board View", available=True),
                        Feature(name="Timeline View", available=True),
                        Feature(name="Workload Tracking", available=True),
                    ],
                    "security_admin": [
                        Feature(name="All Enterprise features", available=True),
                    ],
                    "ai": [
                        Feature(name="Generate Formulas", available=True),
                        Feature(name="Generate Text/Summaries", available=True),
                        Feature(name="Analyze Data", available=True),
                    ],
                },
            ),
        ],
        add_ons=[
            SmartsheetAddOn(name="Brandfolder", description="Digital Asset Management", eligible_plans=["pro", "business", "enterprise", "awm"]),
            SmartsheetAddOn(name="Resource Management", eligible_plans=["business", "enterprise", "awm"]),
            SmartsheetAddOn(name="Dynamic View", eligible_plans=["business", "enterprise", "awm"], starting_price="$125/month"),
            SmartsheetAddOn(name="Data Shuttle", eligible_plans=["business", "enterprise", "awm"], starting_price="$100/month"),
            SmartsheetAddOn(name="Control Center", description="Portfolio Management", eligible_plans=["business", "enterprise", "awm"]),
            SmartsheetAddOn(name="Calendar App", eligible_plans=["business", "enterprise", "awm"]),
            SmartsheetAddOn(name="Pivot App", eligible_plans=["business", "enterprise", "awm"]),
            SmartsheetAddOn(name="Connectors", eligible_plans=["business", "enterprise", "awm"]),
            SmartsheetAddOn(name="DataMesh", eligible_plans=["business", "enterprise", "awm"]),
            SmartsheetAddOn(name="Bridge", description="Workflow Automation", eligible_plans=["enterprise", "awm"]),
            SmartsheetAddOn(name="WorkApps", description="No-Code Apps", eligible_plans=["enterprise", "awm"]),
        ],
        support_tiers=[
            SmartsheetSupport(
                level="Standard (Help, Community, Web Ticketing)",
                availability={"pro": "included", "business": "included", "enterprise": "included", "awm": "included"},
            ),
            SmartsheetSupport(
                level="Premium (24x7 chat, <2hr response)",
                availability={"pro": "add-on", "business": "add-on", "enterprise": "included", "awm": "included"},
            ),
            SmartsheetSupport(
                level="Technical Account Managers",
                availability={"pro": "not_available", "business": "not_available", "enterprise": "add-on", "awm": "add-on"},
            ),
            SmartsheetSupport(
                level="Professional Services",
                availability={"pro": "not_available", "business": "not_available", "enterprise": "add-on", "awm": "add-on"},
            ),
            SmartsheetSupport(
                level="Smartsheet University",
                availability={"pro": "not_available", "business": "not_available", "enterprise": "add-on", "awm": "included"},
            ),
        ],
    )


def seed_wrike() -> WrikePricing:
    return WrikePricing(
        competitor="wrike",
        display_name="Wrike",
        url="https://www.wrike.com/price/",
        extracted_at=NOW,
        extraction_method=ExtractionMethod.MANUAL,
        plans=[
            WrikePlan(
                name="Free",
                slug="free",
                is_free=True,
                is_custom_pricing=False,
                pricing=None,
                users=UserLimits(min=1, max=None),
                storage_gb_per_user=None,
                automations_per_seat_month=None,
                guest_users=None,
                active_tasks=200,
                features={
                    "views": [
                        Feature(name="Board/Kanban View", available=True),
                        Feature(name="Table View", available=True),
                        Feature(name="Gantt Chart", available=False),
                        Feature(name="Calendar View", available=False),
                    ],
                    "task_mgmt": [
                        Feature(name="Task Management with Subtasks", available=True),
                        Feature(name="Custom Fields", available=False),
                        Feature(name="Custom Workflows", available=False),
                        Feature(name="Request Forms", available=False),
                    ],
                    "collaboration": [
                        Feature(name="Comments and @mentions", available=True),
                        Feature(name="Guest Invites", available=True),
                        Feature(name="File Sharing", available=True),
                    ],
                    "integrations": [
                        Feature(name="Google Drive", available=True),
                        Feature(name="Dropbox", available=True),
                        Feature(name="Box", available=True),
                        Feature(name="Office 365", available=True),
                        Feature(name="OneDrive", available=True),
                    ],
                },
            ),
            WrikePlan(
                name="Team",
                slug="team",
                is_free=False,
                is_custom_pricing=False,
                pricing=PricingInfo(
                    monthly_per_unit=12.0,
                    annual_per_unit=9.80,
                    unit=BillingUnit.USER,
                    annual_discount_pct=18.3,
                ),
                trial=TrialInfo(days=14, credit_card_required=False),
                users=UserLimits(min=2, max=25),
                storage_gb_per_user=2.0,
                automations_per_seat_month=50,
                guest_users=20,
                active_tasks="unlimited",
                ai_tier="Essentials",
                features={
                    "views": [
                        Feature(name="Board/Kanban View", available=True),
                        Feature(name="Table View", available=True),
                        Feature(name="Gantt Chart", available=True),
                        Feature(name="Calendar View", available=True),
                    ],
                    "task_mgmt": [
                        Feature(name="Unlimited Tasks", available=True),
                        Feature(name="Custom Workflows", available=True),
                        Feature(name="Custom Fields", available=True),
                        Feature(name="Request Forms", available=True),
                        Feature(name="Dependencies", available=True),
                    ],
                    "collaboration": [
                        Feature(name="Shareable Dashboards", available=True),
                    ],
                    "integrations": [
                        Feature(name="G Suite", available=True),
                        Feature(name="Office 365", available=True),
                        Feature(name="Slack", available=True),
                        Feature(name="Salesforce", available=False),
                    ],
                    "ai": [
                        Feature(name="Generative AI (Essentials)", available=True),
                    ],
                },
            ),
            WrikePlan(
                name="Business",
                slug="business",
                is_free=False,
                is_custom_pricing=False,
                pricing=PricingInfo(
                    monthly_per_unit=None,
                    annual_per_unit=24.80,
                    unit=BillingUnit.USER,
                ),
                trial=TrialInfo(days=14, credit_card_required=False),
                billing_note="Annual billing only",
                users=UserLimits(min=5, max=200),
                storage_gb_per_user=5.0,
                automations_per_seat_month=200,
                guest_users="unlimited",
                active_tasks="unlimited",
                ai_tier="Elite",
                features={
                    "resource_mgmt": [
                        Feature(name="Portfolio Management", available=True),
                        Feature(name="Resource Management", available=True),
                        Feature(name="Capacity Planning", available=True),
                        Feature(name="Workload Charts", available=True),
                        Feature(name="Time Tracking", available=True),
                    ],
                    "task_mgmt": [
                        Feature(name="Project Blueprints", available=True),
                        Feature(name="Custom Item Types", available=True),
                        Feature(name="Cross-tagging", available=True),
                    ],
                    "collaboration": [
                        Feature(name="File Proofing", available=True),
                    ],
                    "integrations": [
                        Feature(name="Salesforce", available=True),
                        Feature(name="NetSuite", available=True),
                        Feature(name="Adobe Creative Cloud", available=True),
                    ],
                    "ai": [
                        Feature(name="AI Risk Predictions", available=True),
                        Feature(name="AI Elite Features", available=True),
                    ],
                },
            ),
            WrikePlan(
                name="Enterprise",
                slug="enterprise",
                is_free=False,
                is_custom_pricing=True,
                pricing=None,
                trial=TrialInfo(days=14, credit_card_required=False),
                billing_note="Annual billing only",
                users=UserLimits(min=5, max=None),
                storage_gb_per_user=10.0,
                automations_per_seat_month=1000,
                guest_users="unlimited",
                active_tasks="unlimited",
                features={
                    "security": [
                        Feature(name="SAML-based SSO", available=True),
                        Feature(name="Two-Factor Authentication", available=True),
                        Feature(name="Custom Access Roles", available=True),
                        Feature(name="Audit Reports", available=True),
                    ],
                    "integrations": [
                        Feature(name="Tableau", available=True),
                        Feature(name="Business Intelligence API", available=True),
                    ],
                },
            ),
            WrikePlan(
                name="Pinnacle",
                slug="pinnacle",
                is_free=False,
                is_custom_pricing=True,
                pricing=None,
                billing_note="Annual billing only",
                users=UserLimits(min=5, max=None),
                storage_gb_per_user=15.0,
                automations_per_seat_month="unlimited",
                guest_users="unlimited",
                active_tasks="unlimited",
                features={
                    "resource_mgmt": [
                        Feature(name="Team Utilization Dashboard", available=True),
                        Feature(name="Budgeting", available=True),
                        Feature(name="Dynamic Budgeting", available=True),
                        Feature(name="Bookings", available=True),
                        Feature(name="Forecasting", available=True),
                    ],
                    "security": [
                        Feature(name="Locked Spaces", available=True),
                        Feature(name="Custom Job Roles", available=True),
                    ],
                    "collaboration": [
                        Feature(name="Advanced Proofing (HTML5, SharePoint)", available=True),
                    ],
                    "integrations": [
                        Feature(name="Native Power BI", available=True),
                    ],
                },
            ),
            WrikePlan(
                name="Apex",
                slug="apex",
                is_free=False,
                is_custom_pricing=True,
                pricing=None,
                billing_note="Annual billing only",
                users=UserLimits(min=5, max=None),
                storage_gb_per_user=15.0,
                automations_per_seat_month="unlimited",
                guest_users="unlimited",
                active_tasks="unlimited",
                ai_tier="Full Suite",
                features={
                    "ai": [
                        Feature(name="Full AI-powered Intelligence Suite", available=True),
                        Feature(name="Visual Collaboration Tools", available=True),
                        Feature(name="Automated Data Flows", available=True),
                    ],
                },
            ),
        ],
        add_ons=[
            WrikeAddOn(name="Wrike Integrate", description="Advanced integrations platform", eligible_plans=["enterprise", "pinnacle", "apex"]),
            WrikeAddOn(name="Wrike Lock", description="Enhanced data security / encryption key ownership", eligible_plans=["enterprise", "pinnacle", "apex"]),
            WrikeAddOn(name="Wrike Sync", description="Cross-platform project synchronization", eligible_plans=["enterprise", "pinnacle", "apex"]),
            WrikeAddOn(name="Additional Storage", description="500 GB or 1 TB increments", eligible_plans=["team", "business", "enterprise", "pinnacle", "apex"]),
        ],
    )


def seed_asana() -> AsanaPricing:
    return AsanaPricing(
        competitor="asana",
        display_name="Asana",
        url="https://asana.com/pricing",
        extracted_at=NOW,
        extraction_method=ExtractionMethod.MANUAL,
        plans=[
            AsanaPlan(
                name="Personal",
                slug="personal",
                tagline="For one or two people managing personal projects",
                is_free=True,
                is_custom_pricing=False,
                pricing=None,
                users=UserLimits(min=1, max=2),
                automations_per_month_org=None,
                ai_actions_per_month=None,
                storage_per_file_mb=100,
                portfolios=None,
                projects_per_portfolio=None,
                features={
                    "views": [
                        Feature(name="List View", available=True),
                        Feature(name="Board View", available=True),
                        Feature(name="Calendar View", available=True),
                        Feature(name="Timeline/Gantt", available=False),
                    ],
                    "task_mgmt": [
                        Feature(name="Unlimited Tasks", available=True),
                        Feature(name="Unlimited Projects", available=True),
                        Feature(name="Assignees", available=True),
                        Feature(name="Due Dates", available=True),
                        Feature(name="Recurring Tasks", available=True),
                        Feature(name="Dependencies", available=False),
                        Feature(name="Custom Fields", available=False),
                        Feature(name="Milestones", available=False),
                    ],
                    "reporting": [
                        Feature(name="Dashboards", available=False),
                        Feature(name="Advanced Reporting", available=False),
                        Feature(name="Portfolios", available=False),
                        Feature(name="Goals", available=False),
                    ],
                    "integrations": [
                        Feature(name="100+ Free Integrations", available=True),
                    ],
                    "admin_security": [
                        Feature(name="Multi-Factor Authentication", available=True),
                        Feature(name="Google SSO", available=False),
                        Feature(name="Admin Console", available=False),
                    ],
                },
            ),
            AsanaPlan(
                name="Starter",
                slug="starter",
                tagline="For growing teams that need to track their projects' progress and hit deadlines",
                is_free=False,
                is_custom_pricing=False,
                pricing=PricingInfo(
                    monthly_per_unit=13.49,
                    annual_per_unit=10.99,
                    unit=BillingUnit.USER,
                    annual_discount_pct=18.5,
                ),
                users=UserLimits(min=2, max=500),
                automations_per_month_org=250,
                ai_actions_per_month=150,
                storage_per_file_mb=100,
                portfolios=None,
                projects_per_portfolio=5,
                features={
                    "views": [
                        Feature(name="List View", available=True),
                        Feature(name="Board View", available=True),
                        Feature(name="Calendar View", available=True),
                        Feature(name="Timeline/Gantt", available=True),
                    ],
                    "task_mgmt": [
                        Feature(name="Dependencies", available=True),
                        Feature(name="Custom Fields", available=True),
                        Feature(name="Custom Templates", available=True),
                        Feature(name="Milestones", available=True),
                        Feature(name="Forms (Basic)", available=True),
                    ],
                    "automation": [
                        Feature(name="Workflow Builder", available=True),
                        Feature(name="Automations", value="250/month org-wide", available=True),
                    ],
                    "reporting": [
                        Feature(name="Dashboards", available=True),
                        Feature(name="Advanced Search", available=True),
                        Feature(name="Portfolios", available=True, value="5 projects per portfolio"),
                        Feature(name="Goals", available=False),
                        Feature(name="Advanced Reporting", available=False),
                    ],
                    "collaboration": [
                        Feature(name="Unlimited Guest Users", available=True),
                    ],
                    "admin_security": [
                        Feature(name="Google SSO", available=True),
                        Feature(name="Private Teams/Projects", available=True),
                        Feature(name="Admin Console", available=True),
                        Feature(name="SAML SSO", available=False),
                    ],
                    "ai": [
                        Feature(name="Asana Intelligence", available=True, value="150 actions/month"),
                    ],
                },
            ),
            AsanaPlan(
                name="Advanced",
                slug="advanced",
                tagline="For companies that need to manage a portfolio of work and goals across departments",
                is_free=False,
                is_custom_pricing=False,
                pricing=PricingInfo(
                    monthly_per_unit=30.49,
                    annual_per_unit=24.99,
                    unit=BillingUnit.USER,
                    annual_discount_pct=18.0,
                ),
                users=UserLimits(min=2, max=500),
                automations_per_month_org=25000,
                ai_actions_per_month="unlimited",
                storage_per_file_mb=100,
                portfolios="unlimited",
                projects_per_portfolio="unlimited",
                features={
                    "reporting": [
                        Feature(name="Goals", available=True),
                        Feature(name="Unlimited Portfolios", available=True),
                        Feature(name="Portfolio Workload Management", available=True),
                        Feature(name="Advanced Reporting Dashboards", available=True),
                    ],
                    "automation": [
                        Feature(name="Automations", value="25,000/month org-wide", available=True),
                    ],
                    "collaboration": [
                        Feature(name="Proofing & Approvals", available=True),
                        Feature(name="Branching Logic Forms", available=True),
                    ],
                    "time_tracking": [
                        Feature(name="Native Time Tracking", available=True),
                    ],
                    "admin_security": [
                        Feature(name="Locked Custom Fields", available=True),
                        Feature(name="Scaled Security", available=True),
                        Feature(name="SAML SSO", available=False),
                    ],
                    "integrations": [
                        Feature(name="Salesforce", available=False, note="Enterprise only"),
                        Feature(name="Tableau", available=False, note="Enterprise only"),
                        Feature(name="Power BI", available=False, note="Enterprise only"),
                    ],
                },
            ),
            AsanaPlan(
                name="Enterprise",
                slug="enterprise",
                tagline="For companies that need to coordinate and automate complex work across departments, without limits",
                is_free=False,
                is_custom_pricing=True,
                pricing=None,
                estimated_price_per_user_month=35.0,
                users=UserLimits(min=1, max=None),
                automations_per_month_org="unlimited",
                ai_actions_per_month="unlimited",
                storage_per_file_mb=100,
                portfolios="unlimited",
                projects_per_portfolio="unlimited",
                features={
                    "automation": [
                        Feature(name="Workflow Bundles", available=True),
                        Feature(name="Universal Workload Management", available=True),
                    ],
                    "admin_security": [
                        Feature(name="SAML SSO", available=True),
                        Feature(name="SCIM Provisioning", available=True),
                        Feature(name="Guest & Mobile Data Controls", available=True),
                        Feature(name="Custom Branding", available=True),
                        Feature(name="Admin Announcements", available=True),
                        Feature(name="Sandboxes", available=True),
                    ],
                    "integrations": [
                        Feature(name="Salesforce", available=True),
                        Feature(name="Tableau", available=True),
                        Feature(name="Power BI", available=True),
                    ],
                    "support": [
                        Feature(name="24/7 Priority Support", available=True),
                    ],
                },
            ),
            AsanaPlan(
                name="Enterprise+",
                slug="enterprise-plus",
                tagline="For companies that need to meet strict compliance requirements with flexible, precise controls",
                is_free=False,
                is_custom_pricing=True,
                pricing=None,
                estimated_price_per_user_month=45.0,
                users=UserLimits(min=1, max=None),
                automations_per_month_org="unlimited",
                ai_actions_per_month="unlimited",
                storage_per_file_mb=100,
                portfolios="unlimited",
                projects_per_portfolio="unlimited",
                features={
                    "compliance": [
                        Feature(name="HIPAA Compliance", available=True),
                        Feature(name="Data Residency", available=True),
                        Feature(name="EKM (Encrypted Key Management)", available=True),
                        Feature(name="Audit Log API", available=True),
                        Feature(name="Admin Console Data Export", available=True),
                    ],
                    "integrations": [
                        Feature(name="SIEM Integration (Splunk)", available=True),
                        Feature(name="eDiscovery (Exterro, Hanzo, Everlaw)", available=True),
                        Feature(name="DLP (Nightfall/Netskope)", available=True),
                        Feature(name="Archiving (Theta Lake)", available=True),
                    ],
                    "admin_security": [
                        Feature(name="Managed Workspaces", available=True),
                        Feature(name="App Management", available=True),
                        Feature(name="Trusted Guest Domains", available=True),
                    ],
                },
            ),
        ],
        ai_studio=AsanaAIStudio(
            eligible_plans=["starter", "advanced", "enterprise", "enterprise-plus"],
            tiers=[
                AsanaAIStudioTier(name="Basic", description="Included with rate limits", pricing="included"),
                AsanaAIStudioTier(name="Plus", description="For individuals/small teams", pricing="paid", billing="monthly/annual"),
                AsanaAIStudioTier(name="Pro", description="For scaling complex workflows", pricing="paid", billing="annual only"),
            ],
            credit_packs=[{"credits": 1000, "price": "$100"}],
        ),
        seat_scaling=[
            SeatScalingRule(range_start=2, range_end=5, increment=1),
            SeatScalingRule(range_start=6, range_end=30, increment=5),
            SeatScalingRule(range_start=31, range_end=100, increment=10),
            SeatScalingRule(range_start=101, range_end=500, increment=25),
            SeatScalingRule(range_start=501, range_end=None, increment=50),
        ],
    )


def seed_notion() -> NotionPricing:
    return NotionPricing(
        competitor="notion",
        display_name="Notion",
        url="https://www.notion.com/pricing",
        extracted_at=NOW,
        extraction_method=ExtractionMethod.MANUAL,
        plans=[
            NotionPlan(
                name="Free",
                slug="free",
                is_free=True,
                is_custom_pricing=False,
                pricing=None,
                file_upload_limit="5 MB",
                page_history_days=7,
                external_guests=10,
                charts=1,
                notion_site_domains=1,
                ai_data_retention_days=30,
                teamspaces_open_closed=False,
                teamspaces_private=False,
                features={
                    "content_collab": [
                        Feature(name="Pages & Blocks", available=True, value="limited for 2+ members"),
                        Feature(name="Export (HTML/Markdown/CSV)", available=False),
                        Feature(name="Export as PDF", available=False),
                    ],
                    "ai": [
                        Feature(name="AI Core (chat, generate, autofill)", available=True, value="limited trial"),
                        Feature(name="AI Meeting Notes", available=True, value="limited trial"),
                        Feature(name="Enterprise Search", available=True, value="limited trial"),
                        Feature(name="Notion Agents", available=True, value="limited trial"),
                    ],
                    "integrations": [
                        Feature(name="Notion Calendar", available=True),
                        Feature(name="Notion Mail", available=True),
                        Feature(name="Basic Integrations", available=False),
                        Feature(name="Premium Integrations", available=False),
                    ],
                    "databases_automation": [
                        Feature(name="Subtasks/Dependencies", available=False),
                        Feature(name="Custom Properties", available=False),
                        Feature(name="Forms", available=True, value="basic"),
                        Feature(name="Dashboards", available=False),
                        Feature(name="Public API", available=False),
                        Feature(name="Automations", available=False),
                    ],
                    "security_admin": [
                        Feature(name="2-Step Verification", available=False),
                        Feature(name="SAML SSO", available=False),
                        Feature(name="SCIM", available=False),
                        Feature(name="Audit Log", available=False),
                    ],
                    "support": [
                        Feature(name="Standard Support", available=True),
                        Feature(name="Premium Support", available=False),
                    ],
                },
            ),
            NotionPlan(
                name="Plus",
                slug="plus",
                is_free=False,
                is_custom_pricing=False,
                pricing=PricingInfo(
                    monthly_per_unit=10.0,
                    annual_per_unit=8.0,
                    unit=BillingUnit.MEMBER,
                    annual_discount_pct=20.0,
                ),
                file_upload_limit="unlimited",
                page_history_days=30,
                external_guests="unlimited",
                charts="unlimited",
                notion_site_domains=5,
                ai_data_retention_days=30,
                teamspaces_open_closed=True,
                teamspaces_private=False,
                features={
                    "content_collab": [
                        Feature(name="Unlimited Pages & Blocks", available=True),
                        Feature(name="Export (HTML/Markdown/CSV)", available=True),
                        Feature(name="Export as PDF", available=False),
                    ],
                    "ai": [
                        Feature(name="AI Core (chat, generate, autofill)", available=True, value="limited trial"),
                        Feature(name="AI Meeting Notes", available=True, value="limited trial"),
                    ],
                    "integrations": [
                        Feature(name="Basic Integrations", available=True),
                        Feature(name="Premium Integrations", available=False),
                    ],
                    "databases_automation": [
                        Feature(name="Subtasks/Dependencies", available=True),
                        Feature(name="Custom Properties & Filtering", available=True),
                        Feature(name="Unlimited Charts", available=True),
                        Feature(name="Custom Forms", available=True),
                        Feature(name="Dashboards", available=True),
                        Feature(name="Public API", available=True),
                        Feature(name="Webhooks", available=True),
                        Feature(name="Automations", available=True, value="buttons only"),
                    ],
                    "web_publishing": [
                        Feature(name="Unlimited Published Pages", available=True),
                        Feature(name="Advanced SEO", available=True),
                    ],
                    "security_admin": [
                        Feature(name="2-Step Verification", available=True),
                        Feature(name="SAML SSO", available=False),
                    ],
                },
            ),
            NotionPlan(
                name="Business",
                slug="business",
                label="Recommended",
                is_free=False,
                is_custom_pricing=False,
                pricing=PricingInfo(
                    monthly_per_unit=20.0,
                    annual_per_unit=16.0,
                    unit=BillingUnit.MEMBER,
                    annual_discount_pct=20.0,
                ),
                file_upload_limit="unlimited",
                page_history_days=90,
                external_guests="unlimited",
                charts="unlimited",
                notion_site_domains=5,
                ai_data_retention_days=30,
                teamspaces_open_closed=True,
                teamspaces_private=True,
                features={
                    "ai": [
                        Feature(name="AI Core (chat, generate, autofill)", available=True, value="full access"),
                        Feature(name="AI Meeting Notes", available=True, value="full access"),
                        Feature(name="Enterprise Search", available=True, value="full access"),
                        Feature(name="Notion Agents", available=True, value="full access"),
                    ],
                    "integrations": [
                        Feature(name="Premium Integrations", available=True),
                        Feature(name="Advanced Integrations", available=False),
                    ],
                    "databases_automation": [
                        Feature(name="Database Automations", available=True),
                        Feature(name="1-way Database Syncs", available=True),
                        Feature(name="Conditional Logic Forms", available=True),
                    ],
                    "content_collab": [
                        Feature(name="Permission Groups", available=True),
                        Feature(name="Granular Database Permissions", available=True),
                        Feature(name="Export as PDF", available=True),
                    ],
                    "security_admin": [
                        Feature(name="SAML SSO", available=True),
                        Feature(name="Advanced Security Controls", available=True),
                        Feature(name="Workspace Analytics", available=True),
                        Feature(name="SCIM", available=False),
                        Feature(name="Audit Log", available=False),
                    ],
                },
            ),
            NotionPlan(
                name="Enterprise",
                slug="enterprise",
                is_free=False,
                is_custom_pricing=True,
                pricing=None,
                file_upload_limit="unlimited",
                page_history_days="unlimited",
                external_guests="unlimited",
                charts="unlimited",
                notion_site_domains=5,
                ai_data_retention_days=0,
                teamspaces_open_closed=True,
                teamspaces_private=True,
                features={
                    "integrations": [
                        Feature(name="Advanced Integrations", available=True),
                    ],
                    "security_admin": [
                        Feature(name="SCIM Provisioning", available=True),
                        Feature(name="Granular Admin Roles", available=True),
                        Feature(name="Audit Log", available=True),
                        Feature(name="Admin Content Search", available=True),
                        Feature(name="Domain Management", available=True),
                        Feature(name="Workspace Consolidation", available=True),
                        Feature(name="Security & Compliance Integrations", available=True),
                    ],
                    "support": [
                        Feature(name="Premium Support", available=True),
                        Feature(name="Customer Success Manager", available=True),
                    ],
                },
            ),
        ],
        add_ons=[
            NotionAddOn(name="AI Add-on", description="For Free/Plus plans", monthly_price="$10/member/month", annual_price="$8/member/month"),
            NotionAddOn(name="Custom Agents", description="Free trial, then credit-based", monthly_price="$10 per 1,000 credits", annual_price="$10 per 1,000 credits"),
            NotionAddOn(name="AI Credit Pack", description="1,000 credits", monthly_price="$100"),
            NotionAddOn(name="Custom Domains & Branding", monthly_price="$10/month/domain", annual_price="$8/month/domain"),
        ],
        special_programs=[
            NotionSpecialProgram(
                name="Student/Educator Discount",
                description="Plus plan free for single-member workspaces with qualifying school email",
            ),
        ],
    )


def seed_monday() -> MondayPricing:
    return MondayPricing(
        competitor="monday",
        display_name="Monday.com",
        url="https://monday.com/pricing",
        extracted_at=NOW,
        extraction_method=ExtractionMethod.MANUAL,
        global_policies=MondayGlobalPolicies(
            minimum_seats=3,
            annual_discount_pct=18.0,
            trial_days=14,
            custom_quote_above_seats=40,
            refund_window_days=30,
        ),
        products=[
            MondayProduct(
                name="Work Management",
                slug="work-management",
                plans=[
                    MondayPlan(
                        name="Free",
                        slug="free",
                        is_free=True,
                        is_custom_pricing=False,
                        pricing=None,
                        free_seats_limit=2,
                        features={
                            "core": [
                                Feature(name="Up to 3 boards", available=True),
                                Feature(name="Unlimited docs", available=True),
                                Feature(name="200+ templates", available=True),
                                Feature(name="iOS/Android apps", available=True),
                            ],
                        },
                    ),
                    MondayPlan(
                        name="Basic",
                        slug="basic",
                        is_free=False,
                        is_custom_pricing=False,
                        pricing=PricingInfo(
                            monthly_per_unit=12.0,
                            annual_per_unit=9.0,
                            unit=BillingUnit.SEAT,
                            annual_discount_pct=25.0,
                        ),
                        features={
                            "core": [
                                Feature(name="Unlimited free viewers", available=True),
                                Feature(name="Unlimited items", available=True),
                                Feature(name="5 GB storage", available=True),
                                Feature(name="Prioritized customer support", available=True),
                            ],
                        },
                    ),
                    MondayPlan(
                        name="Standard",
                        slug="standard",
                        is_free=False,
                        is_custom_pricing=False,
                        pricing=PricingInfo(
                            monthly_per_unit=14.0,
                            annual_per_unit=12.0,
                            unit=BillingUnit.SEAT,
                            annual_discount_pct=14.3,
                        ),
                        features={
                            "core": [
                                Feature(name="Timeline & Gantt views", available=True),
                                Feature(name="Calendar view", available=True),
                                Feature(name="Guest access", available=True),
                                Feature(name="Automations", available=True, value="250 actions/month"),
                                Feature(name="Integrations", available=True, value="250 actions/month"),
                                Feature(name="20 GB storage", available=True),
                            ],
                        },
                    ),
                    MondayPlan(
                        name="Pro",
                        slug="pro",
                        is_free=False,
                        is_custom_pricing=False,
                        pricing=PricingInfo(
                            monthly_per_unit=24.0,
                            annual_per_unit=19.0,
                            unit=BillingUnit.SEAT,
                            annual_discount_pct=20.8,
                        ),
                        features={
                            "core": [
                                Feature(name="Private boards", available=True),
                                Feature(name="Chart view", available=True),
                                Feature(name="Time tracking", available=True),
                                Feature(name="Formula column", available=True),
                                Feature(name="Automations", available=True, value="25,000 actions/month"),
                                Feature(name="Integrations", available=True, value="25,000 actions/month"),
                                Feature(name="100 GB storage", available=True),
                            ],
                        },
                    ),
                    MondayPlan(
                        name="Enterprise",
                        slug="enterprise",
                        is_free=False,
                        is_custom_pricing=True,
                        pricing=None,
                        features={
                            "core": [
                                Feature(name="Enterprise-scale automations & integrations", available=True),
                                Feature(name="Multi-level permissions", available=True),
                                Feature(name="Enterprise-grade security", available=True),
                                Feature(name="Advanced reporting & analytics", available=True),
                                Feature(name="1000 GB storage", available=True),
                            ],
                            "security": [
                                Feature(name="SAML SSO", available=True),
                                Feature(name="SCIM Provisioning", available=True),
                                Feature(name="Audit Log", available=True),
                                Feature(name="HIPAA Compliance", available=True),
                            ],
                        },
                    ),
                ],
            ),
            MondayProduct(
                name="CRM",
                slug="crm",
                plans=[
                    MondayPlan(
                        name="Basic",
                        slug="basic",
                        is_free=False,
                        is_custom_pricing=False,
                        pricing=PricingInfo(
                            monthly_per_unit=18.0,
                            annual_per_unit=12.0,
                            unit=BillingUnit.SEAT,
                            annual_discount_pct=33.3,
                        ),
                        active_contacts_deals=1000,
                        custom_dashboards=1,
                        columns_per_board=5,
                        quotes_invoices_per_month=20,
                        features={
                            "crm": [
                                Feature(name="Centralized Communications Hub", available=True),
                                Feature(name="Mass Email", available=True),
                                Feature(name="Email Sequences", available=True),
                                Feature(name="Custom Automations", available=True),
                                Feature(name="iOS/Android Apps", available=True),
                            ],
                        },
                    ),
                    MondayPlan(
                        name="Standard",
                        slug="standard",
                        is_free=False,
                        is_custom_pricing=False,
                        pricing=PricingInfo(
                            monthly_per_unit=25.0,
                            annual_per_unit=17.0,
                            unit=BillingUnit.SEAT,
                            annual_discount_pct=32.0,
                        ),
                        active_contacts_deals=10000,
                        features={
                            "crm": [
                                Feature(name="AI Credits", available=True),
                                Feature(name="AI Sidekick (lite)", available=True),
                                Feature(name="Notetaker Hours", available=True),
                                Feature(name="Data-driven Dashboards", available=True),
                            ],
                        },
                    ),
                    MondayPlan(
                        name="Pro",
                        slug="pro",
                        is_free=False,
                        is_custom_pricing=False,
                        pricing=PricingInfo(
                            monthly_per_unit=33.0,
                            annual_per_unit=28.0,
                            unit=BillingUnit.SEAT,
                            annual_discount_pct=15.2,
                        ),
                        active_contacts_deals="unlimited",
                        features={
                            "crm": [
                                Feature(name="Advanced CRM Features", available=True),
                            ],
                        },
                    ),
                    MondayPlan(
                        name="Ultimate",
                        slug="ultimate",
                        is_free=False,
                        is_custom_pricing=True,
                        pricing=None,
                        active_contacts_deals="unlimited",
                        features={
                            "crm": [
                                Feature(name="All CRM Features", available=True),
                                Feature(name="Enterprise Security", available=True),
                            ],
                        },
                    ),
                ],
            ),
            MondayProduct(
                name="Dev",
                slug="dev",
                plans=[
                    MondayPlan(
                        name="Basic",
                        slug="basic",
                        is_free=False,
                        is_custom_pricing=False,
                        pricing=PricingInfo(
                            monthly_per_unit=12.0,
                            annual_per_unit=9.0,
                            unit=BillingUnit.SEAT,
                            annual_discount_pct=25.0,
                        ),
                    ),
                    MondayPlan(
                        name="Standard",
                        slug="standard",
                        is_free=False,
                        is_custom_pricing=False,
                        pricing=PricingInfo(
                            monthly_per_unit=14.50,
                            annual_per_unit=12.0,
                            unit=BillingUnit.SEAT,
                            annual_discount_pct=17.2,
                        ),
                    ),
                    MondayPlan(
                        name="Pro",
                        slug="pro",
                        is_free=False,
                        is_custom_pricing=False,
                        pricing=PricingInfo(
                            monthly_per_unit=25.0,
                            annual_per_unit=20.0,
                            unit=BillingUnit.SEAT,
                            annual_discount_pct=20.0,
                        ),
                    ),
                    MondayPlan(
                        name="Enterprise",
                        slug="enterprise",
                        is_free=False,
                        is_custom_pricing=True,
                        pricing=None,
                    ),
                ],
            ),
            MondayProduct(
                name="Service",
                slug="service",
                plans=[
                    MondayPlan(
                        name="Standard",
                        slug="standard",
                        is_free=False,
                        is_custom_pricing=False,
                        pricing=PricingInfo(
                            monthly_per_unit=34.0,
                            annual_per_unit=31.0,
                            unit=BillingUnit.SEAT,
                            annual_discount_pct=8.8,
                        ),
                    ),
                    MondayPlan(
                        name="Pro",
                        slug="pro",
                        is_free=False,
                        is_custom_pricing=False,
                        pricing=PricingInfo(
                            monthly_per_unit=52.0,
                            annual_per_unit=45.0,
                            unit=BillingUnit.SEAT,
                            annual_discount_pct=13.5,
                        ),
                    ),
                    MondayPlan(
                        name="Enterprise",
                        slug="enterprise",
                        is_free=False,
                        is_custom_pricing=True,
                        pricing=None,
                    ),
                ],
            ),
        ],
    )


def main():
    """Seed all competitor data files."""
    seeders = {
        "smartsheet": seed_smartsheet,
        "wrike": seed_wrike,
        "asana": seed_asana,
        "notion": seed_notion,
        "monday": seed_monday,
    }

    print("Seeding competitor pricing data...")
    for name, seeder in seeders.items():
        try:
            data = seeder()
            path = save_competitor(name, data)
            print(f"  [OK] {name}: {path}")
        except Exception as e:
            print(f"  [FAIL] {name}: {e}")
            raise

    print("\nAll competitor data seeded successfully!")


if __name__ == "__main__":
    main()
