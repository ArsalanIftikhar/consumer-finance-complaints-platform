# Mart Definitions (Planned)

## mart_complaint_trends_monthly
**Purpose**  
Track longitudinal complaint volume patterns by product and issue categories.

**Grain**  
One row per month, product, issue, and geography (state-level where available).

**Key Dimensions**  
- month
- product / sub_product
- issue / sub_issue
- state

**Key Measures**  
- complaint_count
- unique_company_count
- month_over_month_complaint_change

**Business Questions Answered**  
- Which product/issue combinations are driving complaint growth?
- Where are complaint concentrations shifting geographically?

---

## mart_service_level_monthly
**Purpose**  
Measure response timeliness and dispute-related service performance over time.

**Grain**  
One row per month, product, and company response category.

**Key Dimensions**  
- month
- product
- company_response_to_consumer
- submission_channel

**Key Measures**  
- total_complaints
- timely_response_rate
- dispute_rate
- median_days_to_response (when derivable)

**Business Questions Answered**  
- Are service levels improving or worsening by product category?
- Which response categories correlate with higher dispute rates?

---

## mart_product_issue_risk_monthly
**Purpose**  
Highlight product-issue combinations with elevated complaint intensity and persistence.

**Grain**  
One row per month, product, and issue.

**Key Dimensions**  
- month
- product
- issue

**Key Measures**  
- complaint_count
- rolling_3m_complaint_count
- share_of_total_complaints
- risk_tier_flag (rule-based placeholder)

**Business Questions Answered**  
- Which product/issue areas represent sustained risk hotspots?
- How concentrated is overall complaint risk in top categories?

---

## mart_macro_enriched_monthly
**Purpose**  
Provide complaint trend metrics alongside selected macro indicators for contextual analysis.

**Grain**  
One row per month (optionally segmented by product in downstream use).

**Key Dimensions**  
- month

**Key Measures**  
- complaint_count
- timely_response_rate
- unemployment_rate
- federal_funds_rate
- consumer_price_index

**Business Questions Answered**  
- Do complaint trends move with unemployment, rates, or inflation signals?
- Which macro periods align with notable shifts in complaint behavior?
