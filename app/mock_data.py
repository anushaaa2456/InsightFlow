"""Comprehensive mock scenarios matching Person 1 & 2 contracts and Round 2 demo requirements."""

DEMO_SCENARIOS = {
    "Scenario A: Strong Evidence (Revenue Drop)": {
        "name": "Scenario A — Strong Evidence",
        "description": "Revenue drops -8% due to high-margin SKU stockouts and product mix decline. Evidence is highly consistent across sales and operations.",
        "kpi": "Revenue",
        "entity": "North America",
        "period": "2026-W08",
        "actual_change": -0.082,
        "expected_change": -0.010,
        "materiality": "HIGH",
        "historical_trend": [
            {"date": "2026-01-05", "actual": 1200000, "expected": 1190000},
            {"date": "2026-01-12", "actual": 1220000, "expected": 1200000},
            {"date": "2026-01-19", "actual": 1210000, "expected": 1215000},
            {"date": "2026-01-26", "actual": 1250000, "expected": 1220000},
            {"date": "2026-02-02", "actual": 1230000, "expected": 1225000},
            {"date": "2026-02-09", "actual": 1240000, "expected": 1230000},
            {"date": "2026-02-16", "actual": 1225000, "expected": 1235000},
            {"date": "2026-02-23", "actual": 1124550, "expected": 1240000}
        ],
        "drivers": [
            {"driver": "AOV (Average Order Value)", "contribution": -0.051, "sub_drivers": ["Premium Mix Decline (-3.8%)", "Discount Expansion (-1.3%)"]},
            {"driver": "Active Customers", "contribution": -0.021, "sub_drivers": ["Repeat Customer Churn (-1.5%)", "New Acquisition Flat (-0.6%)"]},
            {"driver": "Purchase Frequency", "contribution": -0.010, "sub_drivers": ["Cart Abandonment (+0.4%)", "Session Depth Drop (-1.4%)"]}
        ],
        "hypothesis": "premium_product_mix_decline_due_to_stockouts",
        "competing_hypotheses": [
            {"hypothesis": "Competitor Aggressive Discounting", "score": 0.32, "status": "REJECTED", "reason": "Competitor price scraping showed stable pricing index (1.01x)"},
            {"hypothesis": "Checkout Gateway Failure", "score": 0.15, "status": "REJECTED", "reason": "Payment API latency normal (180ms), 99.98% success rate"},
            {"hypothesis": "Premium SKU Stockouts in Central Distribution Hub", "score": 0.89, "status": "VALIDATED", "reason": "Warehouse inventory for flagship SKU dropped to 0 across 4 distribution hubs"}
        ],
        "evidence": [
            {"source": "operations.csv", "finding": "Top 3 premium SKUs out of stock for 5 consecutive days in Eastern fulfillment center.", "freshness": "6 hours ago", "reliability": "Deterministic ERP log"},
            {"source": "transactions.csv", "finding": "Share of transactions with AOV > $250 decreased from 34% to 21%.", "freshness": "1 hour ago", "reliability": "Direct Transaction DB"},
            {"source": "business_context.json (Support)", "finding": "142 customer tickets reporting 'Out of Stock' on flagship Ultra series.", "freshness": "3 hours ago", "reliability": "Zendesk Ingestion"}
        ],
        "confidence": {
            "score": 0.89,
            "label": "HIGH",
            "breakdown": {
                "evidence_strength": 0.92,
                "consistency": 0.95,
                "coverage": 0.85,
                "statistical_support": 0.88
            }
        },
        "recommendation": {
            "action": "Expedite emergency stock transfer of Premium Ultra SKUs from Western backup facility & adjust digital storefront featured mix.",
            "expected_impact": "+1.2% to +1.8% Revenue Recovery within 5 business days",
            "owner": "VP Supply Chain & Head of Digital Merchandising",
            "feasibility": "HIGH",
            "risk": "Low inventory carrying cost on expedited freight ($4,200)",
            "monitoring_kpi": "Daily Premium SKU In-Stock % (Target > 98%)"
        }
    },
    "Scenario B: Ambiguous Evidence (Multiple Competing Drivers)": {
        "name": "Scenario B — Ambiguous Evidence",
        "description": "Revenue declines -4.5% with multiple competing causes of similar weight. System explicitly refuses to claim single root cause.",
        "kpi": "Revenue",
        "entity": "EMEA",
        "period": "2026-W08",
        "actual_change": -0.045,
        "expected_change": +0.005,
        "materiality": "MEDIUM",
        "historical_trend": [
            {"date": "2026-02-02", "actual": 850000, "expected": 845000},
            {"date": "2026-02-09", "actual": 860000, "expected": 850000},
            {"date": "2026-02-16", "actual": 840000, "expected": 855000},
            {"date": "2026-02-23", "actual": 811500, "expected": 860000}
        ],
        "drivers": [
            {"driver": "Conversion Rate", "contribution": -0.022, "sub_drivers": ["Mobile checkout drop (-1.2%)", "Ad click quality (-1.0%)"]},
            {"driver": "Average Order Value", "contribution": -0.023, "sub_drivers": ["Category discount shift (-1.5%)", "Bundle uptake drop (-0.8%)"]}
        ],
        "hypothesis": "unresolved_multi_factor_friction",
        "competing_hypotheses": [
            {"hypothesis": "Mobile App UI Checkout Latency", "score": 0.54, "status": "AMBIGUOUS", "reason": "App store crash rate rose 0.4%, but server logs show normal response times"},
            {"hypothesis": "Competitor Mid-Tier Campaign", "score": 0.52, "status": "AMBIGUOUS", "reason": "Competitor launched flash sale, but web search traffic remains flat"}
        ],
        "evidence": [
            {"source": "support_tickets", "finding": "Mixed customer feedback regarding new checkout flow and pricing promotions.", "freshness": "12 hours ago", "reliability": "Unstructured Tickets"},
            {"source": "operations.csv", "finding": "Inventory availability remained within normal parameters (96.4%).", "freshness": "1 day ago", "reliability": "ERP Log"}
        ],
        "confidence": {
            "score": 0.51,
            "label": "MEDIUM",
            "breakdown": {
                "evidence_strength": 0.50,
                "consistency": 0.45,
                "coverage": 0.60,
                "statistical_support": 0.49
            }
        },
        "recommendation": {
            "action": "Deploy telemetry A/B testing on mobile checkout while monitoring regional price sensitivity.",
            "expected_impact": "Clarification of root cause within 48 hours without risky policy changes",
            "owner": "Growth Product Lead & Analytics Team",
            "feasibility": "HIGH",
            "risk": "None",
            "monitoring_kpi": "Mobile Checkout Error Rate & Competitor Price Index"
        }
    },
    "Scenario C: Sparse History (New KPI Launch)": {
        "name": "Scenario C — Sparse History",
        "description": "Newly launched 'Next-Day Delivery Adoption' KPI has only 12 days of history. System triggers abstention rather than fabricating trends.",
        "kpi": "Next-Day Delivery Adoption Rate",
        "entity": "APAC Pilot",
        "period": "2026-W08",
        "actual_change": -0.150,
        "expected_change": 0.000,
        "materiality": "LOW (Insufficient Baseline)",
        "historical_trend": [
            {"date": "2026-02-18", "actual": 0.18, "expected": 0.18},
            {"date": "2026-02-20", "actual": 0.17, "expected": 0.18},
            {"date": "2026-02-23", "actual": 0.15, "expected": 0.18}
        ],
        "drivers": [],
        "hypothesis": "insufficient_sample_history",
        "competing_hypotheses": [
            {"hypothesis": "Service Disruption", "score": 0.20, "status": "UNVERIFIED", "reason": "Only 3 data points available; baseline variance undefined"}
        ],
        "evidence": [
            {"source": "kpi_registry.yaml", "finding": "Metric registered 12 days ago. Minimum observation window: 30 days.", "freshness": "Real-time", "reliability": "Registry Metadata"}
        ],
        "confidence": {
            "score": 0.18,
            "label": "INSUFFICIENT",
            "breakdown": {
                "evidence_strength": 0.15,
                "consistency": 0.20,
                "coverage": 0.10,
                "statistical_support": 0.12
            }
        },
        "recommendation": {
            "action": "Maintain passive telemetry collection; abstain from trigger-based operational adjustments until minimum 30-day cohort maturity.",
            "expected_impact": "Avoid false-positive operational overhead",
            "owner": "BI Platform & Data Engineering",
            "feasibility": "IMMEDIATE",
            "risk": "None",
            "monitoring_kpi": "Cumulative Sample Count (Current: 240 / Target: 2,500)"
        }
    }
}
