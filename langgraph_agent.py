"""
LangGraph agent for CoreStack MVP (see readme.md)
- Accepts a user query
- Uses Gemini LLM (via LangChain) for intent extraction
- Validates/canonicalizes
- Calls CoreStack API
- Normalizes JSON
- Computes stats
- Formats concise response
- Uses LangGraph StateGraph for node orchestration
"""

import os
import requests
import json
import statistics
import re
from typing import Dict, Any, List
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph

# Hardcoded API keys
GEMINI_API_KEY = "AIzaSyBzShXkHj_oykdMribVGztXo4WEaLmi7_s"
CORE_STACK_API_KEY = "sQtPsffC.UZ0NdPe1ewdTMM9UWJ3KM577kQdH9Luv"
os.environ["CORE_STACK_API_KEY"] = CORE_STACK_API_KEY

# --- Node functions ---
def llm_intent_parser(state: Dict[str, Any]) -> Dict[str, Any]:
    user_query = state["user_query"]
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0,
        google_api_key=GEMINI_API_KEY
    )
    prompt = (
        "You are a strict extractor. Return only raw JSON, no markdown or code fencing. "
        "Extract uid, intent, metric_text, start_year, end_year, confidence, clarification_needed, and explanation. "
        "Use temperature=0.0. If you cannot infer a field, return null; set clarification_needed true for ambiguities.\n"
        f"User query: {user_query}"
    )
    response = llm.invoke(prompt)
    print('Gemini raw output:', response.content)  # Debug print
    content = response.content.strip()
    content = re.sub(r"^```json\s*|```$", "", content, flags=re.MULTILINE).strip()
    try:
        parsed = json.loads(content)
        state["parsed"] = parsed
    except Exception as e:
        state["error"] = f"LLM output not valid JSON: {content}"
    return state

def canonicalize_year(year):
    try:
        y = int(year)
        return f"{y}-{y+1}"
    except Exception:
        return str(year)

def validate(state: Dict[str, Any]) -> Dict[str, Any]:
    parsed = state["parsed"]
    uid = parsed.get("uid")
    start_year = parsed.get("start_year")
    end_year = parsed.get("end_year")
    metric_text = parsed.get("metric_text")
    if not uid or not start_year or not end_year:
        state["error"] = "Missing required fields"
        return state
    # Canonicalize years
    parsed["start_year"] = canonicalize_year(start_year)
    parsed["end_year"] = canonicalize_year(end_year)
    state["parsed"] = parsed
    return state

def fetch_mws_data(state: Dict[str, Any]) -> Dict[str, Any]:
    if "error" in state:
        return state
    uid = state["parsed"]["uid"]
    base_url = "https://geoserver.core-stack.org/api/v1/"
    headers = {"X-API-Key": CORE_STACK_API_KEY}
    
    # Two-step API process as per notebook
    # For now, use hardcoded lat/lon that corresponds to the test UID
    # In production, you'd extract lat/lon from the user query
    latitude = "25.31698754297551"
    longitude = "75.09702609349773"
    
    # Step 1: Get MWS info from lat/lon
    params_latlon = {"latitude": latitude, "longitude": longitude}
    response_mwsid = requests.get(f"{base_url}get_mwsid_by_latlon/", params=params_latlon, headers=headers)
    
    if response_mwsid.status_code != 200:
        state["error"] = f"Step 1 API call failed with status {response_mwsid.status_code}: {response_mwsid.text}"
        return state
    
    mws_info = response_mwsid.json()
    print(f"MWS Info from lat/lon: {mws_info}")
    
    # Step 2: Get full data using location parameters
    params_mws_data = {
        'state': mws_info.get('State'), 
        'district': mws_info.get('District'),
        'tehsil': mws_info.get('Tehsil'), 
        'mws_id': mws_info.get('uid')
    }
    response = requests.get(f"{base_url}get_mws_data/", params=params_mws_data, headers=headers)
    
    print(f"API Response Status: {response.status_code}")
    if response.status_code != 200:
        state["error"] = f"Step 2 API call failed with status {response.status_code}: {response.text}"
        return state
    
    mws_json = response.json()
    print(f"API Response keys: {list(mws_json.keys())}")
    state["mws_json"] = mws_json
    return state

def normalize_cropping_intensity(state: Dict[str, Any]) -> Dict[str, Any]:
    if "error" in state:
        return state
    mws_json = state["mws_json"]
    ci = mws_json.get("croppingIntensity_annual", [{}])[0]
    print("croppingIntensity_annual keys:", list(ci.keys())[:10])  # Debug print first 10 keys
    rows = []
    for k, v in ci.items():
        if isinstance(v, (int, float)) and k.startswith('cropping_intensity_unit_less_'):
            # Extract year from pattern like 'cropping_intensity_unit_less_2017-2018'
            year = k.replace('cropping_intensity_unit_less_', '')
            if year.count("-") == 1:  # Validate year format
                rows.append({
                    "year": year,
                    "value": v,
                    "source": f"croppingIntensity_annual.{k}"
                })
    print("Available years in timeseries:", [r["year"] for r in rows])  # Debug print
    state["timeseries"] = rows
    return state

def compute_timeseries_stats(state: Dict[str, Any]) -> Dict[str, Any]:
    if "error" in state:
        return state
    timeseries = state["timeseries"]
    parsed = state["parsed"]
    start_year = parsed["start_year"]
    end_year = parsed["end_year"]
    ts = sorted([r for r in timeseries if r.get('value') is not None], key=lambda r: r['year'])
    year_to_val = {r['year']: float(r['value']) for r in ts}
    if start_year not in year_to_val or end_year not in year_to_val:
        state["stats"] = {"error":"start or end year missing", "available_years": list(year_to_val.keys())}
        return state
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
    state["stats"] = {
        "start_val": start_val,
        "end_val": end_val,
        "percent_change": round(pct_change, 4) if pct_change is not None else None,
        "peak_year": peak_year,
        "peak_value": peak_value,
        "slope": slope,
        "sources": sources
    }
    return state

def format_response(state: Dict[str, Any]) -> Dict[str, Any]:
    if "error" in state:
        state["response"] = state["error"]
        return state
    parsed = state["parsed"]
    stats = state["stats"]
    uid = parsed["uid"]
    start_year = parsed["start_year"]
    end_year = parsed["end_year"]
    if "error" in stats:
        state["response"] = stats["error"]
        return state
    state["response"] = (
        f"UID {uid} — Cropping intensity rose from {stats['start_val']} ({start_year}) "
        f"to a peak of {stats['peak_value']} ({stats['peak_year']}) and is {stats['end_val']} in {end_year}. "
        f"Net change {start_year}→{end_year} ≈ {stats['percent_change']}%. "
        f"Data sources: {', '.join(stats['sources'])}."
    )
    return state

# --- LangGraph StateGraph wiring ---
graph = StateGraph(dict)
graph.add_node("intent", llm_intent_parser)
graph.add_node("validate", validate)
graph.add_node("fetch", fetch_mws_data)
graph.add_node("normalize", normalize_cropping_intensity)
graph.add_node("compute", compute_timeseries_stats)
graph.add_node("format", format_response)

graph.add_edge("intent", "validate")
graph.add_edge("validate", "fetch")
graph.add_edge("fetch", "normalize")
graph.add_edge("normalize", "compute")
graph.add_edge("compute", "format")

graph.set_entry_point("intent")
graph.set_finish_point("format")

# --- Main MVP agent runner ---
def run_agent(user_query: str):
    state = {"user_query": user_query}
    app = graph.compile()
    result_state = app.invoke(state)
    print("\n--- Final Agent Response ---\n")
    print(result_state["response"])

# --- Example usage ---
if __name__ == "__main__":
    user_query = "How did cropping intensity change from 2017 to 2023 for uid 12_75340?"
    run_agent(user_query)
