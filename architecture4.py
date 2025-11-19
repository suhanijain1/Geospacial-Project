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
from smolagents import CodeAgent, tool, LiteLLMModel, DuckDuckGoSearchTool

# No need to import executor - it's specified via executor_type parameter
DOCKER_AVAILABLE = True  # Assume Docker is available like in agent.py

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

# Import Earth Engine (like agent.py)
import ee

load_dotenv()

# Initialize Earth Engine
GEE_PROJECT = os.getenv("GEE_PROJECT", "apt-achievment-453417-h6")
try:
    ee.Initialize(project=GEE_PROJECT)
    print(f"✅ Earth Engine initialized with project: {GEE_PROJECT}")
except Exception as e:
    print(f"⚠️  Earth Engine initialization failed: {e}")

# ============================================================================
# DATA PRODUCT NAME CACHE (reduces context length)
# ============================================================================

CORESTACK_DATA_PRODUCTS = {
    "vector_layers": [
        "lcw_conflict", "Admin Boundary", "MWS", "LULC_level_2", "Cropping Intensity",
        "Terrain Vector", "LULC", "Aquifer", "Restoration Vector", "Stream Order",
        "SOGE", "Crop GridXlulc", "Drought Causality", "Hydrology Precipitation",
        "Drainage", "Surface Water Bodies", "Hydrology Evapotranspiration",
        "Hydrology Run Off", "Hydrology", "Change Detection Vector", "NREGA Assets"
    ],
    "raster_layers": [
        "LULC_level_2", "Restoration Raster", "Change Detection Raster", "CLART",
        "LULC_level_3", "LULC_level_1", "Terrain Raster", "NDVI", "Soil Moisture",
        "Temperature", "Rainfall", "Evapotranspiration", "Groundwater Level"
    ],
    "timeseries_metrics": [
        "cropping_intensity", "precipitation", "temperature", "soil_moisture",
        "ndvi", "evapotranspiration", "groundwater_level", "rainfall"
    ]
}

# ============================================================================
# LANGGRAPH AS A TOOL FOR CODEACT  
# ============================================================================

# Module-level cache for layer data (accessed via getattr to avoid validation issues)
LAYER_CACHE = {
    "available_vector_layers": [],
    "available_raster_layers": [],
    "vector_layer_map": {},
    "raster_layer_map": {}
}

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
        JSON string with available layers or timeseries data
    """
    from new_architecture import build_graph
    import json
    import sys
    
    # Access the module-level cache (will be available in the parent process)
    # Get reference to this module's LAYER_CACHE
    this_module = sys.modules.get('architecture4')
    if this_module and hasattr(this_module, 'LAYER_CACHE'):
        cache = this_module.LAYER_CACHE
    else:
        cache = LAYER_CACHE  # fallback to direct reference
    
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
            
            # Cache layer data using getattr to avoid validation issues
            cache["available_vector_layers"] = [l.get("layer_name") for l in vector_layers]
            cache["available_raster_layers"] = [l.get("layer_name") for l in raster_layers]
            cache["vector_layer_map"] = {l.get("layer_name"): l for l in vector_layers}
            cache["raster_layer_map"] = {l.get("layer_name"): l for l in raster_layers}
            
            # ONLY return layer names (not full data) to reduce context length
            response["spatial_data"] = {
                "available_vector_layers": cache["available_vector_layers"],
                "available_raster_layers": cache["available_raster_layers"],
                "total_layers": len(vector_layers) + len(raster_layers),
                "note": "Access layer data via LAYER_CACHE['vector_layer_map'][layer_name]"
            }
            
            print(f"✅ Retrieved {response['spatial_data']['total_layers']} layers ({len(vector_layers)} vector, {len(raster_layers)} raster)")
            print(f"💾 Cached layer names only (reduced memory)")
            
        elif data_type == "timeseries":
            # Return timeseries data
            response["timeseries_data"] = result_state.get("timeseries_raw", {})
            response["watershed_info"] = result_state.get("watershed_info", {})
            print(f"✅ Retrieved timeseries data for watershed {response['watershed_info'].get('uid', 'unknown')}")
        
        # Return compact JSON
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
You are a geospatial analysis agent with access to:
1. fetch_corestack_data - CoreStack geospatial database (India-specific layers) 
2. web_search - DuckDuckGo search for general information
3. Python libraries: geopandas, shapely, matplotlib, numpy, pandas, rasterio, requests, ee (Earth Engine)

CRITICAL RULE: For ANY query about India or Indian locations, you MUST call fetch_corestack_data FIRST.
DO NOT use web_search for India-specific geospatial data. CoreStack has the actual data.

AVAILABLE CORESTACK DATA (CALL THE TOOL TO ACCESS):
Vector Layers: {', '.join(CORESTACK_DATA_PRODUCTS['vector_layers'])}
Raster Layers: {', '.join(CORESTACK_DATA_PRODUCTS['raster_layers'])}
Timeseries Metrics: {', '.join(CORESTACK_DATA_PRODUCTS['timeseries_metrics'])}

MANDATORY WORKFLOW FOR INDIA QUERIES:
1. **FIRST ACTION**: Call fetch_corestack_data(query) - this returns actual data, not web results
2. Check the returned JSON - it will have either spatial_data or timeseries_data
3. If CoreStack has the data → use it in Python code
4. **IMPORTANT**: If timeseries API fails, use spatial layers! 
   - Cropping Intensity rasters/vectors have multi-year data
   - Extract values at the point/area for analysis
   - You can still analyze temporal trends from spatial layers
5. ONLY if CoreStack completely fails → try Earth Engine or other sources
6. Write Python code to analyze the data
7. Use final_answer() to return results

USER TASK: {task}

START BY CALLING fetch_corestack_data WITH THE QUERY!
If you get spatial layers, USE THEM even for temporal analysis!


CRS HANDLING (CRITICAL):
- CoreStack data: EPSG:4326 (WGS84 lat/lon)
- India UTM Zone: EPSG:32643 (for area calculations)
- For area: ALWAYS reproject to EPSG:32643 BEFORE calculating
- For buffers: Use geodesic_buffer() function (already available)
- For distance: Use geodesic calculations (geopy or shapely ops)

Example:
```python
import json
import geopandas as gpd
import matplotlib.pyplot as plt
from architecture4 import LAYER_CACHE

# 1. Check CoreStack FIRST (for India data)
result = fetch_corestack_data("water bodies near Bhilwara")
data = json.loads(result)

if data['success'] and data['data_type'] == 'spatial':
    # 2. CoreStack has the data! Use it.
    vector_names = LAYER_CACHE['available_vector_layers']
    print(f"CoreStack layers: {{vector_names}}")
    
    # 3. Get specific layer
    water_layer = LAYER_CACHE['vector_layer_map'].get('Surface Water Bodies')
    if not water_layer:
        water_layer = next((
            LAYER_CACHE['vector_layer_map'][name] 
            for name in vector_names
            if 'water' in name.lower()
        ), None)    if water_layer:
        # 4. Load and process CoreStack data
        gdf = gpd.read_file(water_layer['layer_url'])
        
        # 5. REPROJECT for area calculation
        gdf_utm = gdf.to_crs('EPSG:32643')  # India UTM
        gdf_utm['area_ha'] = gdf_utm.geometry.area / 10000
        
        total_area = gdf_utm['area_ha'].sum()
        print(f"Total water area: {{total_area:.2f}} hectares")
        
        gdf.plot(column='area_ha', legend=True)
        plt.savefig('/app/exports/water_bodies.png')
        
        final_answer(f"Found {{len(gdf)}} water bodies totaling {{total_area:.2f}} hectares")
    else:
        # CoreStack doesn't have this specific layer, try Earth Engine
        import ee
        ee.Initialize(project='apt-achievment-453417-h6')
        # ... use Earth Engine here
else:
    # CoreStack failed or doesn't have data, use Earth Engine
    import ee
    ee.Initialize(project='apt-achievment-453417-h6')
    # ... use Earth Engine here
```

IMPORTANT NOTES:
- Import cache: `from architecture4 import LAYER_CACHE`
- Get layer by name: `LAYER_CACHE['vector_layer_map']['layer_name']`
- Don't print full layer URLs (context length!)
- ALWAYS reproject to UTM (EPSG:32643) before area calculations
- Save plots/exports to /app/exports/ directory (Docker volume mount)

Task: {task}
"""


# ============================================================================
# HYBRID AGENT (CodeAct + LangGraph Tool)
# ============================================================================

def run_hybrid_agent(user_query: str, exports_dir: str = None):
    """
    Run CodeAct agent with LangGraph tool + Docker execution (like agent.py).
    
    Uses Gemini model with Docker executor for full geospatial library support.
    Structure exactly mirrors agent.py but with CoreStack tool added.
    """
    # Set up absolute exports directory
    if exports_dir is None:
        exports_dir = os.path.abspath("./exports")
    os.makedirs(exports_dir, exist_ok=True)
    
    print("\n" + "="*70)
    print("🚀 HYBRID AGENT (CodeAct + LangGraph Tool)")
    print(f"📝 Query: {user_query}")
    print("="*70)
    
    # Use LiteLLM for Gemini (smolagents compatible)
    model = LiteLLMModel(
        model_id="gemini/gemini-2.5-flash-lite",
        api_key=os.getenv("GEMINI_API_KEY")
    )
    
    # Create tools list - NOTE: Only CoreStack tool, NO web_search to force using it
    tools = [fetch_corestack_data]
    
    # Use local Python executor (skip Docker complexity)
    print("✅ Using local Python executor")
    agent = CodeAgent(
        model=model,
        tools=tools,
        additional_authorized_imports=[
            "geopandas", "shapely", "rasterio", "matplotlib", 
            "numpy", "pandas", "json", "requests", "pyproj", "ee",
            "fiona", "geopy"
        ]
    )
    
    try:
        # Generate prompt and run agent
        prompt = create_corestack_prompt(user_query)
        
        # Run agent (it will populate LAYER_CACHE when tool is called)
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
    finally:
        # Cleanup Docker container (like agent.py)
        if DOCKER_AVAILABLE and hasattr(agent, 'python_executor'):
            try:
                agent.python_executor.cleanup()
                print("🧹 Docker container cleaned up")
            except:
                pass


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
    print("Running query #1 from CSV (Shirur, Dharwad, Karnataka - correct coords)...")
    print("="*70)
    
    # Query #1: Cropping intensity change over years in Shirur, Dharwad, Karnataka
    # Correct coordinates: 15.23° N, 75.27° E (Kundgol taluk, Dharwad district)
    run_hybrid_agent("Could you show me how cropping intensity in village Shirur at coordinates 15.23, 75.27 in Dharwad district, Karnataka has changed over the years?")
