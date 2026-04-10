"""Monday.com Work Management comparison table definition.

This mapping is derived from the actual comparison table visible on
monday.com/pricing. It maps each feature to its section and per-tier
availability/value.

Legend for tier values:
  True = available (checkmark)
  False = not available (dash)
  str = specific value shown (e.g., "3", "250/month", "5 GB")

Last verified: 2026-04-10 from monday.com/pricing screenshot.
"""

# Sections in display order matching the pricing page
COMPARISON_SECTIONS = [
    "Essentials",
    "Collaboration",
    "Productivity",
    "Views and reporting",
    "Resource management",
    "Security & privacy",
    "Administration & control",
    "Advanced reporting & analytics",
    "Support",
]

# Feature definitions: (feature_key, display_name, {tier: value})
# feature_key maps to pricingPage.features.titles.{key} in i18n
COMPARISON_FEATURES: dict[str, list[tuple[str, str, dict]]] = {
    "Essentials": [
        ("boards", "Boards", {"free": "3", "basic": "Unlimited", "standard": "Unlimited", "pro": "Unlimited", "enterprise": "Unlimited"}),
        ("items", "Items", {"free": "Up to 1,000", "basic": "Unlimited", "standard": "Unlimited", "pro": "Unlimited", "enterprise": "Unlimited"}),
        ("columnTypes", "Column types", {"free": "8", "basic": "20+", "standard": "20+", "pro": "20+", "enterprise": "20+"}),
        ("storage", "File storage", {"free": "500 MB", "basic": "5 GB", "standard": "20 GB", "pro": "100 GB", "enterprise": "1000 GB"}),
        ("activityLog", "Activity log", {"free": "1 week", "basic": "1 week", "standard": "6 months", "pro": "1 year", "enterprise": "5 years"}),
        ("templates", "Templates", {"free": "200+", "basic": "200+", "standard": "200+", "pro": "200+", "enterprise": "200+"}),
        ("workdocs", "Docs", {"free": "3", "basic": "Unlimited", "standard": "Unlimited", "pro": "Unlimited", "enterprise": "Unlimited"}),
        ("import_export_excel", "Import/Export Excel", {"free": True, "basic": True, "standard": True, "pro": True, "enterprise": True}),
        ("importFromOtherTools", "Import from other tools", {"free": False, "basic": True, "standard": True, "pro": True, "enterprise": True}),
        ("mobile", "iOS and Android apps", {"free": True, "basic": True, "standard": True, "pro": True, "enterprise": True}),
    ],
    "Collaboration": [
        ("updatesSection", "Updates section", {"free": True, "basic": True, "standard": True, "pro": True, "enterprise": True}),
        ("viewers", "Free viewers", {"free": False, "basic": "Unlimited", "standard": "Unlimited", "pro": "Unlimited", "enterprise": "Unlimited"}),
        ("embed_docs", "Embedded documents", {"free": False, "basic": True, "standard": True, "pro": True, "enterprise": True}),
        ("whiteboard", "Whiteboard collaboration", {"free": False, "basic": True, "standard": True, "pro": True, "enterprise": True}),
        ("zoom_integration", "Zoom integration", {"free": False, "basic": True, "standard": True, "pro": True, "enterprise": True}),
        ("guests", "Guest access", {"free": False, "basic": False, "standard": True, "pro": True, "enterprise": True}),
    ],
    "Productivity": [
        ("customizableNotifications", "Customizable notifications", {"free": True, "basic": True, "standard": True, "pro": True, "enterprise": True}),
        ("forms", "Shareable forms", {"free": False, "basic": False, "standard": True, "pro": True, "enterprise": True}),
        ("formsCustomization", "Forms customization", {"free": False, "basic": False, "standard": True, "pro": True, "enterprise": True}),
        ("integrations", "Integrations", {"free": False, "basic": False, "standard": "250 actions/month", "pro": "25,000 actions/month", "enterprise": "250,000 actions/month"}),
        ("automations", "Automations", {"free": False, "basic": False, "standard": "250 actions/month", "pro": "25,000 actions/month", "enterprise": "250,000 actions/month"}),
        ("premiumIntegrations", "Premium integrations", {"free": False, "basic": False, "standard": False, "pro": True, "enterprise": True}),
        ("timeTracking", "Time tracking", {"free": False, "basic": False, "standard": False, "pro": True, "enterprise": True}),
        ("formula", "Formula column", {"free": False, "basic": False, "standard": False, "pro": True, "enterprise": True}),
        ("dependencyColumn", "Dependency column", {"free": False, "basic": False, "standard": False, "pro": True, "enterprise": True}),
        ("tags", "Custom tags", {"free": False, "basic": False, "standard": False, "pro": True, "enterprise": True}),
    ],
    "Views and reporting": [
        ("kanbanView", "Kanban view", {"free": True, "basic": True, "standard": True, "pro": True, "enterprise": True}),
        ("timeline", "Timeline view", {"free": False, "basic": False, "standard": True, "pro": True, "enterprise": True}),
        ("calendar", "Calendar view", {"free": False, "basic": False, "standard": True, "pro": True, "enterprise": True}),
        ("ganttCharts", "Gantt charts", {"free": False, "basic": False, "standard": True, "pro": True, "enterprise": True}),
        ("chartView", "Chart view", {"free": False, "basic": False, "standard": False, "pro": True, "enterprise": True}),
        ("map", "Map view", {"free": False, "basic": False, "standard": False, "pro": True, "enterprise": True}),
        ("workload", "Workload", {"free": False, "basic": False, "standard": False, "pro": True, "enterprise": True}),
        ("dashboards", "Dashboards", {"free": False, "basic": "1 board", "standard": "5 boards", "pro": "20 boards", "enterprise": "50 boards"}),
    ],
    "Resource management": [
        ("calendarSync", "Calendar sync (Google & Outlook)", {"free": False, "basic": False, "standard": False, "pro": True, "enterprise": True}),
        ("projectPortfolioManagement", "Simple project portfolio management", {"free": False, "basic": False, "standard": False, "pro": True, "enterprise": True}),
        ("advancedProjectPortfolioManagement", "Advanced project portfolio management", {"free": False, "basic": False, "standard": False, "pro": False, "enterprise": True}),
        ("resourceAllocation", "Resource allocation & management", {"free": False, "basic": False, "standard": False, "pro": False, "enterprise": True}),
        ("milestonesManagement", "Milestones management", {"free": False, "basic": False, "standard": False, "pro": True, "enterprise": True}),
    ],
    "Security & privacy": [
        ("google", "Google authentication", {"free": True, "basic": True, "standard": True, "pro": True, "enterprise": True}),
        ("twoFa", "Two-factor authentication", {"free": False, "basic": False, "standard": False, "pro": True, "enterprise": True}),
        ("saml", "Single Sign On (SAML)", {"free": False, "basic": False, "standard": False, "pro": False, "enterprise": True}),
        ("hipaa", "HIPAA Compliance", {"free": False, "basic": False, "standard": False, "pro": False, "enterprise": True}),
        ("soc", "SOC 2 Type II Compliance", {"free": False, "basic": False, "standard": False, "pro": False, "enterprise": True}),
        ("privateBoards", "Private boards and docs", {"free": False, "basic": False, "standard": False, "pro": True, "enterprise": True}),
        ("privateWorkspaces", "Private workspaces", {"free": False, "basic": False, "standard": False, "pro": False, "enterprise": True}),
        ("content_directory", "Content directory", {"free": False, "basic": False, "standard": False, "pro": False, "enterprise": True}),
    ],
    "Administration & control": [
        ("maximumSeats", "Maximum number of seats", {"free": "2", "basic": "Unlimited", "standard": "Unlimited", "pro": "Unlimited", "enterprise": "Unlimited"}),
        ("boardAdministrators", "Board administrators", {"free": False, "basic": False, "standard": False, "pro": False, "enterprise": True}),
        ("scimProvisioning", "SCIM provisioning", {"free": False, "basic": False, "standard": False, "pro": False, "enterprise": True}),
        ("auditLog", "Audit log", {"free": False, "basic": False, "standard": False, "pro": False, "enterprise": True}),
        ("sessions", "Session management", {"free": False, "basic": False, "standard": False, "pro": False, "enterprise": True}),
        ("panicMode", "Panic mode", {"free": False, "basic": False, "standard": False, "pro": False, "enterprise": True}),
        ("accountPermissions", "Advanced account permissions", {"free": False, "basic": False, "standard": False, "pro": False, "enterprise": True}),
        ("ip_restrictions", "IP restrictions", {"free": False, "basic": False, "standard": False, "pro": False, "enterprise": True}),
        ("integrationPermissions", "Integration permissions", {"free": False, "basic": False, "standard": False, "pro": False, "enterprise": True}),
    ],
    "Advanced reporting & analytics": [
        ("workPerformanceInsights", "Work performance insights", {"free": False, "basic": False, "standard": False, "pro": False, "enterprise": True}),
        ("pivotAnalysis", "Pivot analysis & reports", {"free": False, "basic": False, "standard": False, "pro": False, "enterprise": True}),
        ("dashboardEmailNotifications", "Dashboard email notifications", {"free": False, "basic": False, "standard": False, "pro": True, "enterprise": True}),
    ],
    "Support": [
        ("emailSupport", "24/7 customer support", {"free": True, "basic": True, "standard": True, "pro": True, "enterprise": True}),
        ("knowledgeBase", "Self-serve knowledge base", {"free": True, "basic": True, "standard": True, "pro": True, "enterprise": True}),
        ("webinars", "Daily live webinars", {"free": True, "basic": True, "standard": True, "pro": True, "enterprise": True}),
        ("prioritisedCustomerSupport", "Prioritised customer support", {"free": False, "basic": True, "standard": True, "pro": True, "enterprise": True}),
        ("premiumSupport", "Enterprise support", {"free": False, "basic": False, "standard": False, "pro": False, "enterprise": True}),
        ("csManager", "Dedicated customer success manager", {"free": False, "basic": False, "standard": False, "pro": False, "enterprise": True}),
    ],
}

# AI features shown on the tier cards (not in comparison table)
AI_FEATURES = {
    "free": [],
    "basic": [("ai_credits", "AI credits"), ("sidekick_ai_assistant", "Sidekick AI Assistant (Limited)")],
    "standard": [("ai_credits", "AI credits"), ("sidekick_ai_assistant", "AI Sidekick (lite)")],
    "pro": [("ai_credits", "AI credits"), ("sidekick_ai_assistant", "AI Sidekick (lite)")],
    "enterprise": [("ai_credits", "AI credits"), ("sidekick_ai_assistant", "AI Sidekick (plus)")],
}
