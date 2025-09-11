Overview / Use case

You want an agentic conversational interface over coreSTACK get_mws_data that handles one natural-language query and returns a single, auditable answer. Example user query:

“How did cropping intensity change from 2017 to 2023 for uid 12_75340?”

Goal: parse the user intent (LLM parser), fetch the correct API (get_mws_data), normalize the JSON timeseries for the requested metric, run deterministic math (percent change / peak), and return one concise response that includes provenance (exact JSON key names).

Constraints / design rules

LLM only does intent extraction (function-calling JSON).

Deterministic code does all math and canonicalization (unit-tested).

Every numeric claim includes source_key provenance.

Single-turn (no long chat state, no vector DB needed for MVP).

Graph (nodes + edges) — top to bottom (text diagram)
User_UI --> LLM_Intent_Parser --> Validator/Canonicalizer --> API_Selector & Caller --> JSON_Normalizer --> Compute_Node --> Formatter/LLM_Phraser --> User_UI_Response
                           └──────────> Clarify_User_UI (if needed) ──────────┘

Node responsibilities (short)

User_UI: accepts user's single query text and session id.

LLM_Intent_Parser: LLM function-call that returns structured JSON: {uid, intent, metric_text, start_year, end_year, confidence, clarification_needed, explanation}.

Validator/Canonicalizer: regex + rules: validate uid, canonicalize years (2017 → 2017-2018), require confidence threshold. If missing/unclear, send a clarifying prompt.

API_Selector & Caller: call GET /api/v1/get_mws_data?mws_id={uid} (use API key header); or use cached blob for tests.

JSON_Normalizer: extract the relevant block (e.g., croppingIntensity_annual[0]) → produce ordered rows: [{year, value, source_key}].

Compute_Node: deterministic math (percent change, peak, slope, missing data) — this is where all calculations happen.

Formatter/LLM_Phraser: optional low-temp LLM or template that formats the computed numbers into one short reply. Must not recompute numbers.

Audit_Log: store raw JSON, parsed LLM output, compute outputs, and the final user response.

Exact LLM parser schema (function-calling)

Use function-calling with a strict schema so the LLM returns JSON only.

Function name: parse_query
JSON schema (required fields shown):

{
  "uid": ["string","null"],
  "intent": "string",              // one of ["timeseries","single_value","status","compare","unknown"]
  "metric_text": ["string","null"],
  "start_year": ["string","null"], // prefer "YYYY-YYYY" if range exists
  "end_year": ["string","null"],
  "confidence": "number",          // 0.0 - 1.0
  "clarification_needed": "boolean",
  "explanation": ["string","null"]
}


System instruction to LLM (short):

“You are a strict extractor. Return only JSON by calling parse_query. Extract uid, intent, metric_text, start_year, end_year, confidence, clarification_needed, and explanation. Use temperature=0.0. If you cannot infer a field, return null; set clarification_needed true for ambiguities.”

Minimal deterministic compute function (paste into Compute_Node)

This function does the math. Unit-testable and auditable.

def compute_timeseries_stats(timeseries, start_year, end_year):
    """
    timeseries: [{'year':'2017-2018','value':1.54,'source':'croppingIntensity_annual.cropping_intensity_unit_less_2017-2018'}, ...]
    returns: dict with start_val, end_val, percent_change, peak_year, peak_value, slope, sources (list)
    """
    import math, statistics
    # sort and filter
    ts = sorted([r for r in timeseries if r.get('value') is not None], key=lambda r: r['year'])
    year_to_val = {r['year']: float(r['value']) for r in ts}

    if start_year not in year_to_val or end_year not in year_to_val:
        return {"error":"start or end year missing", "available_years": list(year_to_val.keys())}

    start_val = year_to_val[start_year]
    end_val   = year_to_val[end_year]
    pct_change = None
    if start_val != 0:
        pct_change = (end_val - start_val) / start_val * 100.0

    peak_row = max(ts, key=lambda r: r['value'])
    peak_year, peak_value = peak_row['year'], float(peak_row['value'])

    ys = [r['value'] for r in ts]
    xs = list(range(len(ys)))
    slope = 0.0
    if len(xs) >= 2:
        mean_x, mean_y = statistics.mean(xs), statistics.mean(ys)
        num = sum((xi-mean_x)*(yi-mean_y) for xi,yi in zip(xs,ys))
        den = sum((xi-mean_x)**2 for xi in xs)
        slope = num/den if den != 0 else 0.0

    sources = [r['source'] for r in ts if r['year'] in (start_year, end_year, peak_year)]
    return {
        "start_val": start_val,
        "end_val": end_val,
        "percent_change": round(pct_change, 4) if pct_change is not None else None,
        "peak_year": peak_year,
        "peak_value": peak_value,
        "slope": slope,
        "sources": sources
    }

JSON normalizer example (gist)

Given mws_json, look up croppingIntensity_annual[0] and iterate keys that contain a year substring like 2017-2018. Output rows with source_key = croppingIntensity_annual.<key>.

Example single-query end-to-end (concrete values)

User input:

{"text":"How did cropping intensity change from 2017 to 2023 for uid 12_75340?"}


LLM_Intent_Parser output (example):

{
  "uid":"12_75340",
  "intent":"timeseries",
  "metric_text":"cropping intensity",
  "start_year":"2017-2018",
  "end_year":"2023-2024",
  "confidence":0.95,
  "clarification_needed":false,
  "explanation":"explicit years and uid found"
}


JSON_Normalizer produces rows:

[
  {"year":"2017-2018","value":1.54,"source":"croppingIntensity_annual.cropping_intensity_unit_less_2017-2018"},
  {"year":"2018-2019","value":1.69,"source":"croppingIntensity_annual.cropping_intensity_unit_less_2018-2019"},
  {"year":"2019-2020","value":1.79,"source":"croppingIntensity_annual.cropping_intensity_unit_less_2019-2020"},
  {"year":"2020-2021","value":1.81,"source":"croppingIntensity_annual.cropping_intensity_unit_less_2020-2021"},
  {"year":"2021-2022","value":1.80,"source":"croppingIntensity_annual.cropping_intensity_unit_less_2021-2022"},
  {"year":"2022-2023","value":1.60,"source":"croppingIntensity_annual.cropping_intensity_unit_less_2022-2023"},
  {"year":"2023-2024","value":1.61,"source":"croppingIntensity_annual.cropping_intensity_unit_less_2023-2024"}
]


Compute_Node returns:

{
  "start_val": 1.54,
  "end_val": 1.61,
  "percent_change": 4.5455,
  "peak_year": "2020-2021",
  "peak_value": 1.81,
  "slope": <numeric>,
  "sources": [
    "croppingIntensity_annual.cropping_intensity_unit_less_2017-2018",
    "croppingIntensity_annual.cropping_intensity_unit_less_2023-2024",
    "croppingIntensity_annual.cropping_intensity_unit_less_2020-2021"
  ]
}


Final agent response (single text string):

“UID 12_75340 — Cropping intensity rose from 1.54 (2017–2018) to a peak of 1.81 (2020–2021) and is 1.61 in 2023–2024. Net change 2017→2023 ≈ +4.55%. Data sources: croppingIntensity_annual.cropping_intensity_unit_less_2017-2018, …_2023-2024.”

Tests & acceptance criteria (paste to Copilot tests)

Create automated tests (pytest) to assert the compute function returns expected values when given the normalized rows above.

Example pytest:

def test_compute_cropping_example():
    ts = [
      {"year":"2017-2018","value":1.54,"source":"s1"},
      {"year":"2018-2019","value":1.69,"source":"s2"},
      {"year":"2019-2020","value":1.79,"source":"s3"},
      {"year":"2020-2021","value":1.81,"source":"s4"},
      {"year":"2021-2022","value":1.80,"source":"s5"},
      {"year":"2022-2023","value":1.60,"source":"s6"},
      {"year":"2023-2024","value":1.61,"source":"s7"},
    ]
    out = compute_timeseries_stats(ts, "2017-2018", "2023-2024")
    assert round(out["percent_change"], 4) == 4.5455
    assert out["peak_year"] == "2020-2021"
    assert out["start_val"] == 1.54
    assert out["end_val"] == 1.61


Parser test: mock the LLM response in tests (or stub call_llm_parse to return expected JSON) and assert that Validator/Canonicalizer accepts it (uid regex, years canonicalized, no clarification needed).