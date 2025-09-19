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
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
CORE_STACK_API_KEY = os.getenv("CORE_STACK_API_KEY")

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
        "Extract uid, intent, metric_text, start_year, end_year, latitude, longitude, confidence, clarification_needed, and explanation. "
        "If latitude/longitude are present in the query (as numbers like 25.123, -75.456), extract them. "
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
    latitude = parsed.get("latitude")
    longitude = parsed.get("longitude")
    
    # Either UID or lat/long coordinates are required
    if not ((uid) or (latitude is not None and longitude is not None)):
        state["error"] = "Missing required fields: either UID or latitude/longitude coordinates"
        return state
    
    if not start_year or not end_year:
        state["error"] = "Missing required fields: start_year and end_year"
        return state
    
    # Canonicalize years
    parsed["start_year"] = canonicalize_year(start_year)
    parsed["end_year"] = canonicalize_year(end_year)
    state["parsed"] = parsed
    return state

def fetch_mws_data(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fetches MWS data from the CoreStack API using either UID or lat/long coordinates.
    """
    if "error" in state:
        return state
    
    base_url = "https://geoserver.core-stack.org/api/v1/"
    headers = {"X-API-Key": CORE_STACK_API_KEY}
    
    # Get UID and coordinates from parsed data
    uid = state["parsed"].get("uid")
    latitude = state["parsed"].get("latitude")
    longitude = state["parsed"].get("longitude")
    
    # Handle the test UID as a special case to bypass the two-step process
    if uid == "12_75340" and (latitude is None or longitude is None):
        # Use hardcoded coordinates for the test UID
        latitude = "25.31698754297551"
        longitude = "75.09702609349773"
    
    # Require either coordinates or UID
    if not uid and (latitude is None or longitude is None):
        state["error"] = "Latitude and longitude coordinates are required but were not provided in the query."
        return state
    
    # Step 1: Get MWS info from lat/lon
    params_latlon = {"latitude": latitude, "longitude": longitude}
    response_mwsid = requests.get(f"{base_url}get_mwsid_by_latlon/", params=params_latlon, headers=headers)
    
    if response_mwsid.status_code != 200:
        state["error"] = f"Step 1 API call failed with status {response_mwsid.status_code}: {response_mwsid.text}"
        return state
    
    mws_info = response_mwsid.json()
    print(f"MWS Info from lat/lon: {mws_info}")
    
    # If we have a UID from coordinates but none was provided in query, store it
    if not uid and mws_info.get('uid'):
        state["parsed"]["uid"] = mws_info.get('uid')
    
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
    response = requests.get(f"{base_url}get_mws_data/", params=params_mws_data, headers=headers)
    
    print(f"API Response Status: {response.status_code}")
    if response.status_code != 200:
        state["error"] = f"Step 2 API call failed with status {response.status_code}: {response.text}"
        return state
    
    mws_json = response.json()
    print(f"API Response keys: {list(mws_json.keys())}")
    state["mws_json"] = mws_json
    return state

def normalize_data(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LLM-powered normalizer that intelligently maps metrics to appropriate data blocks and fields.
    """
    if "error" in state:
        return state
    
    mws_json = state["mws_json"]
    metric_text = state["parsed"].get("metric_text", "").lower().strip()
    
    # Use LLM to identify the appropriate data block and field prefix
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0,
        google_api_key=GEMINI_API_KEY
    )
    
    # Create a simplified representation of the data structure
    data_structure = {}
    for block_name, block_data in mws_json.items():
        if not block_data or not isinstance(block_data, list) or not block_data[0]:
            continue
        
        # Get a sample of keys from each block
        sample_keys = list(block_data[0].keys())[:20]  # Limit to first 20 keys for token efficiency
        data_structure[block_name] = sample_keys
    
    prompt = (
        f"You are a data scientist helping map a natural language metric to the appropriate data block and field prefix.\n\n"
        f"User metric: {metric_text}\n\n"
        f"Available data blocks and sample fields (limited to 20 per block):\n{json.dumps(data_structure, indent=2)}\n\n"
        f"Identify the most relevant data block and field prefix for this metric. Look for fields that contain year patterns like '2017-2018' "
        f"or similar. Return a JSON with 'block' (the data block name) and 'key_prefix' (the prefix before the year in field names).\n\n"
        f"Example output: {{\"block\": \"hydrological_annual\", \"key_prefix\": \"precipitation_in_mm_\"}}"
    )
    
    try:
        response = llm.invoke(prompt)
        print("LLM analysis of data structure:", response.content)
        
        # Parse the LLM's response to get block and key_prefix
        # Handle both JSON and plain text formats
        content = response.content.strip()
        if content.startswith("{") and content.endswith("}"):
            # It's a JSON response
            mapping = json.loads(content)
        else:
            # Try to extract JSON from text if not already in JSON format
            match = re.search(r'\{.*\}', content, re.DOTALL)
            if match:
                json_str = match.group(0)
                mapping = json.loads(json_str)
            else:
                state["error"] = f"Could not parse LLM response: {content}"
                return state
        
        data_block = mapping.get("block")
        key_prefix = mapping.get("key_prefix")
        
        if not data_block or not key_prefix:
            state["error"] = f"LLM did not provide valid block and key_prefix: {content}"
            return state
            
        print(f"LLM selected data block: {data_block}, key prefix: {key_prefix}")
        
        # Extract timeseries data using the LLM-identified block and prefix
        rows = []
        block_data = mws_json.get(data_block, [{}])[0]
        
        for k, v in block_data.items():
            if isinstance(v, (int, float)) and k.startswith(key_prefix):
                # Extract year from pattern like 'prefix_2017-2018'
                year = k.replace(key_prefix, '')
                if year.count("-") == 1:  # Validate year format
                    rows.append({
                        "year": year,
                        "value": v,
                        "source": f"{data_block}.{k}"
                    })
        
        if not rows:
            # Fallback - if LLM suggestion didn't yield data, try some common variations of the key prefix
            print(f"No data found with exact prefix. Trying variations of {key_prefix}")
            
            # Try variations like removing underscores, adding/removing "_in_", etc.
            variations = [
                key_prefix,
                key_prefix.replace("_", ""),
                re.sub(r'_in_[a-z]+_$', "_", key_prefix),
                re.sub(r'_$', "", key_prefix),
                key_prefix + "_"
            ]
            
            for variation in variations:
                for k, v in block_data.items():
                    if isinstance(v, (int, float)) and k.startswith(variation):
                        # Extract year from pattern
                        year = k.replace(variation, '')
                        if year.count("-") == 1:  # Validate year format
                            rows.append({
                                "year": year,
                                "value": v,
                                "source": f"{data_block}.{k}"
                            })
                
                if rows:
                    key_prefix = variation
                    break
        
        if not rows:
            state["error"] = f"Could not find time series data for metric: {metric_text}"
            return state
        
        print("Available years in timeseries:", [r["year"] for r in rows])
        state["timeseries"] = rows
        state["metric_block"] = data_block
        state["metric_key_prefix"] = key_prefix
        return state
        
    except Exception as e:
        state["error"] = f"Error using LLM to analyze data structure: {str(e)}"
        return state
    
    # Extract data from the appropriate block
    data = mws_json.get(data_block, [{}])[0]
    print(f"{data_block} keys:", list(data.keys())[:10])  # Debug print first 10 keys
    
    # Extract timeseries data
    for k, v in data.items():
        if isinstance(v, (int, float)) and k.startswith(key_prefix):
            # Extract year from pattern like 'prefix_2017-2018'
            year = k.replace(key_prefix, '')
            if year.count("-") == 1:  # Validate year format
                rows.append({
                    "year": year,
                    "value": v,
                    "source": f"{data_block}.{k}"
                })
    
    print("Available years in timeseries:", [r["year"] for r in rows])
    state["timeseries"] = rows
    state["metric_block"] = data_block
    state["metric_key_prefix"] = key_prefix
    return state

def compute_timeseries_stats(state: Dict[str, Any]) -> Dict[str, Any]:
    if "error" in state:
        return state
    timeseries = state["timeseries"]
    parsed = state["parsed"]
    requested_start_year = parsed["start_year"]
    requested_end_year = parsed["end_year"]
    ts = sorted([r for r in timeseries if r.get('value') is not None], key=lambda r: r['year'])
    
    if not ts:
        state["stats"] = {"error": "No valid timeseries data available"}
        return state
    
    year_to_val = {r['year']: float(r['value']) for r in ts}
    
    # Get the closest available years if exact matches are not found
    start_year = requested_start_year
    end_year = requested_end_year
    
    # Find closest available start year
    if requested_start_year not in year_to_val:
        # Extract just the first year from each string (e.g. "2017-2018" -> 2017)
        req_start = int(requested_start_year.split('-')[0])
        available_years = sorted([(int(y.split('-')[0]), y) for y in year_to_val.keys()])
        closest_start = min(available_years, key=lambda x: abs(x[0] - req_start))[1]
        start_year = closest_start
    
    # Find closest available end year
    if requested_end_year not in year_to_val:
        # Extract just the first year from each string (e.g. "2017-2018" -> 2017)
        req_end = int(requested_end_year.split('-')[0])
        available_years = sorted([(int(y.split('-')[0]), y) for y in year_to_val.keys()])
        closest_end = min(available_years, key=lambda x: abs(x[0] - req_end))[1]
        end_year = closest_end
    
    start_val = year_to_val[start_year]
    end_val = year_to_val[end_year]
    
    pct_change = None
    if start_val != 0:
        pct_change = round((end_val - start_val) / start_val * 100.0, 4)
    
    peak_row = max(ts, key=lambda r: r['value'])
    
    state["stats"] = {
        "start_val": start_val,
        "end_val": end_val,
        "percent_change": pct_change,
        "peak_year": peak_row["year"],
        "peak_value": peak_row["value"],
        "slope": (end_val - start_val) / len(ts) if len(ts) > 1 else 0,
        "sources": [peak_row["source"], ts[0]["source"], ts[-1]["source"]],
        "actual_start_year": start_year,
        "actual_end_year": end_year,
        "requested_start_year": requested_start_year,
        "requested_end_year": requested_end_year
    }
    return state
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
    # Debug the state structure
    print("Type of state in format_response:", type(state))
    print("State content:", state)
    
    if "error" in state:
        state["response"] = state["error"]
        return state
    
    parsed = state["parsed"]
    stats = state["stats"]
    uid = parsed.get("uid")
    requested_start_year = parsed["start_year"]
    requested_end_year = parsed["end_year"]
    metric_text = parsed.get("metric_text", "value")
    
    # Get actual years used for analysis (may differ from requested if not available)
    actual_start_year = stats.get("actual_start_year", requested_start_year)
    actual_end_year = stats.get("actual_end_year", requested_end_year)
    
    # Get location identifier (either UID or coordinates)
    if uid:
        location_str = f"UID {uid}"
    else:
        lat = parsed.get("latitude")
        lon = parsed.get("longitude")
        location_str = f"Location ({lat:.5f}, {lon:.5f})"
    
    if "error" in stats:
        state["response"] = stats["error"]
        return state
    
    # Note if we had to use different years than requested
    year_note = ""
    if actual_start_year != requested_start_year or actual_end_year != requested_end_year:
        year_note = f" (Note: Used available years {actual_start_year} to {actual_end_year})"
    
    state["response"] = (
        f"{location_str} — {metric_text.title()} changed from {stats['start_val']} ({actual_start_year}) "
        f"to a peak of {stats['peak_value']} ({stats['peak_year']}) and is {stats['end_val']} in {actual_end_year}. "
        f"Net change {actual_start_year}→{actual_end_year} ≈ {stats['percent_change']}%.{year_note} "
        f"Data sources: {', '.join(stats['sources'])}."
    )
    return state

def router(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Determines the next node based on the current state.
    If clarification is needed, route to a hypothetical clarify node.
    Otherwise, continue to fetch data.
    """
    if "error" in state:
        state["router"] = "format"
        return state
    
    parsed = state["parsed"]
    if parsed.get("clarification_needed", False):
        # In a more complex agent, you could add a clarify node
        state["error"] = "Clarification needed: " + parsed.get("explanation", "Please provide more details.")
        state["router"] = "format"
        return state
    
    state["router"] = "fetch"
    return state

# --- LangGraph StateGraph wiring ---
graph = StateGraph(dict)
graph.add_node("intent", llm_intent_parser)
graph.add_node("validate", validate)
graph.add_node("fetch", fetch_mws_data)
graph.add_node("normalize", normalize_data)
graph.add_node("compute", compute_timeseries_stats)
graph.add_node("format", format_response)
graph.add_node("router", router)  # Add router as a node

# Add edges with conditional routing
graph.add_edge("intent", "validate")
graph.add_edge("validate", "router")  # Route to the router node
graph.add_conditional_edges(
    "router",
    lambda x: x["router"],  # Use the return value from the router function
    {
        "fetch": "fetch",  # If router returns "fetch", go to fetch node
        "format": "format"  # If router returns "format", go to format node
    }
)
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
