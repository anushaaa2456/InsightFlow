"""Persona definitions and metadata for InsightFlow."""

PERSONAS = {
    "Executive": {
        "title": "CFO / C-Suite Executive",
        "description": "Focuses on top-line financials, root cause certainty, strategic capital allocation, and expected ROI.",
        "color": "#38BDF8",
        "kpi_focus": ["Revenue", "Profit Margin", "Customer Lifetime Value"],
        "badge": "Executive View"
    },
    "Regional Manager": {
        "title": "Regional Operations & Sales Director",
        "description": "Focuses on operational throughput, distribution stockouts, channel performance, and immediate tactical levers.",
        "color": "#34D399",
        "kpi_focus": ["AOV", "Inventory Availability", "Regional Sales"],
        "badge": "Operations View"
    },
    "Analyst": {
        "title": "Lead Business Intelligence Analyst",
        "description": "Focuses on MECE tree mathematical decomposition, evidence provenance, statistical significance, and uncertainty telemetry.",
        "color": "#818CF8",
        "kpi_focus": ["MECE Tree", "Decomposition Residuals", "Evidence Lineage"],
        "badge": "Analytics View"
    }
}

def get_persona_details(name: str):
    return PERSONAS.get(name, PERSONAS["Executive"])
