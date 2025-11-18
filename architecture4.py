"""
Hybrid Architecture: CodeAct + LangGraph Tool
==============================================

ARCHITECTURE EVOLUTION:
-----------------------
1. agent.py: 
   - Pure CodeAct agent with Docker execution
   - Uses Earth Engine/OpenStreetMap for data
   - ❌ Problem: Doesn't know how to use CoreStack APIs (no API coupling knowledge)

2. new_architecture.py:
   - Pure LangGraph workflow  
   - Deterministic API traversal (admin→layers, watershed→timeseries)
   - ✅ Solves: Correct API coupling
   - ❌ Problem: Linear workflow, no self-correction, limited to built-in processing

3. hybrid_architecture.py (THIS FILE):
   - CodeAct agent FROM agent.py (same Docker setup, same flexibility)
   - + LangGraph workflow FROM new_architecture.py exposed as a TOOL
   - ✅ Solves BOTH problems:
     * CodeAct can now access CoreStack data (via LangGraph tool)
     * CodeAct retains full flexibility for complex analysis
     * Self-correction when code fails
     * Can combine CoreStack data with other sources (EE, OSM, etc.)

KEY INSIGHT:
------------
Instead of replacing CodeAct with LangGraph, we AUGMENT CodeAct by giving it
access to the LangGraph workflow as a specialized tool for CoreStack API access.
This is like giving the agent a "CoreStack data fetcher" tool that handles all
the API complexity internally.

WORKFLOW:
---------
User Query → CodeAct Agent
             ↓
             ├→ Recognizes need for CoreStack data
             ├→ Calls fetch_corestack_data tool
             │  └→ [LangGraph workflow runs internally]
             │     └→ Returns structured data (layers or timeseries)
             ├→ Generates Python code for analysis
             ├→ Executes code (with self-correction if needed)
             └→ Returns final answer

This maintains the PROGRESSION: we're not creating something new, we're
extending agent.py by adding a single specialized tool.
"""

import os
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Import CodeAct from smolagents (structure from agent.py)
from smolagents import CodeAgent, tool, LiteLLMModel

# Import LangGraph workflow and ALL components from new_architecture.py
from new_architecture import (
    build_graph,
    CoreStackAPI,
    SpatialDataProcessor, 
    geodesic_buffer,
    GEMINI_API_KEY,
    CORE_STACK_API_KEY
)

# Import Gemini for the tool itself
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

# ============================================================================
# LANGGRAPH AS A TOOL FOR CODEACT
# ============================================================================

@tool
def fetch_corestack_data(query: str) -> str:
    """
    Fetches geospatial data from CoreStack API using LangGraph workflow.
    
    This tool provides access to CoreStack geospatial database with automatic
    API coupling. It handles the complex workflow of calling multiple APIs in
    the correct sequence.
    
    Args:
        query: Natural language description of what data you need
               Examples:
               - "water bodies near 25.31, 75.09"
               - "cropping intensity 2017-2023 at 25.31, 75.09"
               - "NDVI layers for Rajasthan Bhilwara Mandalgarh"
    
    Returns:
        JSON string with structured data including:
        - For spatial queries: Available layer URLs (vector/raster GeoJSON/GeoTIFF)
        - For timeseries queries: Temporal data with years and values
        - Location information and metadata
    
    The tool automatically:
    1. Parses your query to understand what data type is needed
    2. Calls CoreStack APIs in correct sequence (with proper coupling)
    3. Returns structured data ready for geospatial analysis
    
    Use this tool when you need CoreStack geospatial data. After fetching,
    you can write Python code to analyze the returned data using geopandas,
    rasterio, matplotlib, etc.
    """
    print("\n" + "="*70)
    print("🔧 TOOL: fetch_corestack_data")
    print(f"📝 Query: {query}")
    print("="*70)
    
    try:
        # Build and run LangGraph workflow
        graph = build_graph()
        app = graph.compile()
        
        state = {"user_query": query}
        result_state = app.invoke(state)
        
        # Check for errors
        if "error" in result_state:
            return json.dumps({
                "success": False,
                "error": result_state["error"]
            }, indent=2)
        
        # Extract relevant data
        parsed = result_state.get("parsed", {})
        data_type = parsed.get("data_type_needed", "spatial")
        
        response = {
            "success": True,
            "data_type": data_type,
            "query_interpretation": parsed.get("metric_text", ""),
            "location": {
                "coordinates": {
                    "latitude": parsed.get("latitude"),
                    "longitude": parsed.get("longitude")
                },
                "administrative": result_state.get("location_info", {})
            }
        }
        
        if data_type == "spatial":
            # Return spatial layers with URLs (simplified for tool output)
            available_layers = result_state.get("available_layers", {})
            vector_layers = available_layers.get("vector", [])
            raster_layers = available_layers.get("raster", [])
            
            # Simplify layer info - just return essential data
            response["spatial_data"] = {
                "vector_layers": [
                    {
                        "layer_name": l.get("layer_name"),
                        "layer_type": l.get("layer_type"),
                        "layer_url": l.get("layer_url")
                    } for l in vector_layers
                ],
                "raster_layers": [
                    {
                        "layer_name": l.get("layer_name"),
                        "layer_type": l.get("layer_type"),
                        "layer_url": l.get("layer_url")
                    } for l in raster_layers
                ],
                "total_layers": len(vector_layers) + len(raster_layers)
            }
            print(f"✅ Retrieved {response['spatial_data']['total_layers']} layers ({len(vector_layers)} vector, {len(raster_layers)} raster)")
            
        elif data_type == "timeseries":
            # Return timeseries data
            response["timeseries_data"] = result_state.get("timeseries_raw", {})
            response["watershed_info"] = result_state.get("watershed_info", {})
            print(f"✅ Retrieved timeseries data for watershed {response['watershed_info'].get('uid', 'unknown')}")
        
        # Return compact JSON (no indentation to reduce output size)
        return json.dumps(response, default=str)
        
    except Exception as e:
        error_response = {
            "success": False,
            "error": f"Tool execution failed: {str(e)}"
        }
        print(f"❌ ERROR: {str(e)}")
        return json.dumps(error_response, indent=2)


# ============================================================================
# CODEACT PROMPT (ADAPTED FROM agent.py)
# ============================================================================

def create_corestack_prompt(task: str) -> str:
    """
    Creates the CodeAct prompt, similar to agent.py but adapted for CoreStack.
    
    Key differences from agent.py:
    - Adds CoreStack-specific instructions
    - Includes fetch_corestack_data tool usage
    - Keeps same geospatial analysis structure
    """
    return f"""
You are a geospatial analysis agent, expert at writing Python code to perform geospatial analysis.

You have access to:
1. fetch_corestack_data tool - for accessing CoreStack geospatial database
2. Standard Python libraries: geopandas, shapely, matplotlib, numpy, pandas, rasterio, requests

IMPORTANT - CORESTACK DATA ACCESS:
When you need CoreStack geospatial data, FIRST use the fetch_corestack_data tool.
The tool will return JSON with either:
- spatial_data: Contains vector_layers and raster_layers with URLs
- timeseries_data: Contains temporal metrics with years and values

After getting the data, write Python code to analyze it.

Instructions:
1. If the task requires CoreStack data, call fetch_corestack_data tool first
2. Parse the returned JSON to get layer URLs or timeseries data  
3. Write Python code to:
   - Download and process spatial data (use geopandas for vectors, rasterio for rasters)
   - Analyze timeseries data (use pandas, matplotlib)
   - Always reproject to appropriate CRS before area calculations (EPSG:32643 for India)
4. Export results and visualizations
5. Use the final_answer function to return your response

CRS HANDLING:
- CoreStack data is in EPSG:4326 (WGS84 lat/lon)
- For area calculations, reproject to UTM (EPSG:32643 for India)
- For distance/buffer operations, use geodesic calculations

HELPER FUNCTIONS AVAILABLE:
- SpatialDataProcessor.process_vector_url(url, point=(lat,lon), buffer_km=1.0)
- SpatialDataProcessor.process_raster_url(url, bounds=None, circle_geom_4326=None)
- geodesic_buffer(lon, lat, radius_m, out_crs="EPSG:4326")

Example workflow:
```python
# 1. Fetch CoreStack data
data_json = fetch_corestack_data("water bodies near 25.31, 75.09")
data = json.loads(data_json)

# 2. Extract layer URLs
if data['success'] and data['data_type'] == 'spatial':
    vector_layers = data['spatial_data']['vector_layers']
    
    # Find water bodies layer
    water_layer = next((l for l in vector_layers if 'water' in l['layer_name'].lower()), None)
    
    if water_layer:
        # 3. Process the data
        stats = SpatialDataProcessor.process_vector_url(
            water_layer['layer_url'],
            point=(25.31, 75.09),
            buffer_km=10.0
        )
        
        # 4. Analyze and visualize
        print(f"Found {{stats['feature_count']}} water bodies")
        print(f"Total area: {{stats['total_area_ha']}} hectares")
        
final_answer(f"Analysis complete. Found {{stats['feature_count']}} features.")
```

Task: {task}
"""


# ============================================================================
# HYBRID AGENT (CodeAct + LangGraph Tool)
# ============================================================================

def run_hybrid_agent(user_query: str, exports_dir: str = "./exports"):
    """
    Run CodeAct agent with LangGraph tool.
    
    Uses HuggingFace model with gemini endpoint.
    Structure inspired by agent.py but adapted for Gemini via HF.
    """
    print("\n" + "="*70)
    print("🚀 HYBRID AGENT (CodeAct + LangGraph Tool)")
    print(f"📝 Query: {user_query}")
    print("="*70)
    
    # Use LiteLLM for Gemini (smolagents compatible)
    # Using gemini-1.5-flash instead of experimental model for better quota
    model = LiteLLMModel(
        model_id="gemini/gemini-2.5-flash-lite",
        api_key=os.getenv("GEMINI_API_KEY")
    )
    
    # Create CodeAct agent with LangGraph tool (structure from agent.py)
    agent = CodeAgent(
        model=model,
        tools=[fetch_corestack_data], 
        additional_authorized_imports=[
            "geopandas", "shapely", "rasterio", "matplotlib", 
            "numpy", "pandas", "json", "requests", "pyproj"
        ]
        # Note: Can add Docker execution like agent.py if needed
    )
    
    try:
        # Generate prompt and run agent
        prompt = create_corestack_prompt(user_query)
        result = agent.run(prompt)
        
        print("\n" + "="*70)
        print("✅ AGENT COMPLETED")
        print("="*70)
        print(result)
        print("="*70)
        
        return result
        
    except Exception as e:
        error_msg = f"Agent execution failed: {str(e)}"
        print(f"\n❌ ERROR: {error_msg}")
        raise e


# ============================================================================
# EXAMPLE USAGE & COMPARISON
# ============================================================================

if __name__ == "__main__":
    """
    ARCHITECTURE COMPARISON DEMO
    ============================
    
    Query: "Show water bodies within 50km of 25.31, 75.09"
    
    1. agent.py approach:
       - CodeAct tries to write code to access CoreStack APIs
       - ❌ Doesn't know the API coupling (admin→layers workflow)
       - ❌ Will likely fail or use wrong API sequence
    
    2. new_architecture.py approach:
       - LangGraph handles API coupling correctly
       - ✅ Gets the data successfully
       - ❌ But limited to built-in processing, no self-correction
    
    3. hybrid_architecture.py (THIS FILE):
       - CodeAct calls fetch_corestack_data tool
       - Tool runs LangGraph workflow (correct API coupling)
       - ✅ Gets data successfully
       - CodeAct then generates custom analysis code
       - ✅ Full flexibility + correct APIs + self-correction
    """
    
    test_queries = [
        # Spatial analysis requiring custom computation
        "Calculate total area of water bodies within 50km of coordinates 25.31698754297551, 75.09702609349773 and show size distribution histogram",
        
        # Multi-layer comparison (impossible with just LangGraph)
        "Compare NDVI values with water body locations near 25.31, 75.09 within 10km",
        
        # Timeseries visualization
        "Plot precipitation trends from 2017-2023 at 25.31698754297551, 75.09702609349773 as a line chart",
        
        # Complex spatial query
        "Find all drainage features within 5km of 25.31, 75.09 and calculate their total length",
    ]
    
    print("\n" + "="*70)
    print("🧪 HYBRID ARCHITECTURE TEST")
    print("="*70)
    print("\nAvailable test queries:")
    for i, q in enumerate(test_queries, 1):
        print(f"{i}. {q}")
    
    print("\n" + "="*70)
    print("Running first query...")
    print("="*70)
    
    # Run first query
    run_hybrid_agent("Could you show me how cropping intensity in bhilwara has changed over the years?")

