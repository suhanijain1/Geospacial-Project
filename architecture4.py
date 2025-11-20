"""
Hybrid Architecture: CodeAct + LangGraph Tool
==============================================
"""

import os
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Import CodeAct from smolagents (structure from agent.py)
from smolagents import CodeAgent, tool, LiteLLMModel, DuckDuckGoSearchTool

# No need to import executor - it's specified via executor_type parameter
DOCKER_AVAILABLE = True  # Assume Docker is available like in agent.py

# Import Earth Engine 
import ee

load_dotenv()

# Get API keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
CORE_STACK_API_KEY = os.getenv("CORE_STACK_API_KEY")

# Initialize Earth Engine
GEE_PROJECT = os.getenv("GEE_PROJECT", "apt-achievment-453417-h6")
try:
    ee.Initialize(project=GEE_PROJECT)
    print(f"✅ Earth Engine initialized with project: {GEE_PROJECT}")
except Exception as e:
    print(f"⚠️  Earth Engine initialization failed: {e}")

# ======================================================
# DATA PRODUCT NAME CACHE (from layer_descriptions.csv)
# ======================================================

CORESTACK_DATA_PRODUCTS = {
    "raster_layers": [
        "land_use_land_cover_raster",
        "terrain_raster", 
        "change_tree_cover_gain_raster",
        "change_tree_cover_loss_raster",
        "change_urbanization_raster",
        "change_cropping_reduction_raster",
        "change_cropping_intensity_raster",
        "tree_canopy_cover_density_raster",
        "tree_canopy_height_raster",
        "stream_order_raster",
        "distance_to_upstream_drainage_line",
        "catchment_area",
        "runoff_accumulation",
        "natural_depressions",
        "clart_raster"
    ],
    "vector_layers": [
        "drainage_lines_vector",
        "aquifer_vector",
        "stage_of_groundwater_extraction_vector",
        "nrega_vector",
        "admin_boundaries_vector",
        "drought_frequency_vector",
        "surface_water_bodies_vector",
        "water_balance",
        "change_in_well_depth_vector",
        "cropping_intensity_vector"
    ],
    "timeseries_metrics": [
        "cropping_intensity", "precipitation", "temperature", "soil_moisture",
        "ndvi", "evapotranspiration", "groundwater_level", "rainfall", "water_balance"
    ]
}

# ============================================================================
# LANGGRAPH AS A TOOL FOR CODEACT  
# ============================================================================

@tool
def fetch_corestack_data(query: str) -> str:
    """
    Fetches available CoreStack layers for a location from LangGraph workflow.
    Returns list of available layers with URLs for CodeAct to choose and analyze.
    
    Args:
        query: Natural language query with location (e.g., "Shirur village cropping intensity")
    
    Returns:
        JSON string with:
        - success: bool
        - spatial_data: dict with vector_layers[] and raster_layers[]
        - Each layer has: layer_name, layer_type, urls[] (multi-region support)
        - location_info: administrative details
    """
    import json
    import sys
    import os
    
    # Add parent directory to path
    workspace_path = '/app/workspace'
    if workspace_path not in sys.path:
        sys.path.insert(0, workspace_path)
    
    from new_architecture import build_graph
    
    print("\n" + "="*70)
    print("📊 CORESTACK LAYER FETCHER (via LangGraph)")
    print(f"   Query: {query}")
    print("="*70)
    
    try:
        # Build and compile graph
        graph = build_graph()
        app = graph.compile()
        
        # Run workflow
        state = {"user_query": query}
        result_state = app.invoke(state)
        
        # Check for errors
        if "error" in result_state:
            return json.dumps({
                "success": False,
                "error": result_state["error"]
            }, indent=2)
        
        # Extract available layers
        available_layers = result_state.get("available_layers", {})
        location_info = result_state.get("location_info", {})
        parsed = result_state.get("parsed", {})
        
        # Return layer catalog for CodeAct to choose from
        response = {
            "success": True,
            "data_type": "spatial",
            "spatial_data": {
                "vector_layers": available_layers.get('vector', []),
                "raster_layers": available_layers.get('raster', [])
            },
            "location_info": location_info,
            "parsed_query": {
                "location_name": parsed.get('location_name'),
                "latitude": parsed.get('latitude'),
                "longitude": parsed.get('longitude'),
                "temporal": parsed.get('temporal'),
                "start_year": parsed.get('start_year'),
                "end_year": parsed.get('end_year')
            }
        }
        
        print(f"\n✅ FETCH COMPLETE:")
        print(f"   Vector layers: {len(available_layers.get('vector', []))}")
        print(f"   Raster layers: {len(available_layers.get('raster', []))}")
        return json.dumps(response, default=str)
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)
    


# ============================================================================
# CODEACT PROMPT (ADAPTED FROM agent.py)
# ============================================================================

def create_corestack_prompt(task: str) -> str:
    """
    Creates the CodeAct prompt, with CoreStack as primary data source.
    
    Key features:
    - Emphasizes CoreStack as primary data source for India-specific queries
    - Includes Earth Engine as supplementary tool for global/non-India data
    - Lists all correct libraries and proper export formats
    - Specifies expected output types
    """
    return f"""
You are a geospatial analysis agent, expert at writing python code to perform geospatial analysis. You will use the following python libraries:
osmnx, geopandas, shapely, matplotlib, numpy, pandas, rasterio, ee, geemap, geedim, geopy, requests, json

You will be given a task, you will write python code to perform the task and export outputs to local machine.

If your code has errors, you will search for tutorials and documentations of earlier mentioned libraries to fix the errors.

═══════════════════════════════════════════════════════════════════════════════
CRITICAL UNDERSTANDING: SPATIAL vs TIMESERIES DATA (CoreStack Architecture)
═══════════════════════════════════════════════════════════════════════════════

CoreStack has TWO FUNDAMENTALLY DIFFERENT data structures you MUST understand:

**1️⃣ SPATIAL DATA (Vectors/Rasters)** - For location-specific analysis:
   - Geographic features with SPATIAL VARIATION across a region
   - Data varies BY LOCATION (different patches/polygons have different values)
   - Temporal data stored as YEARLY ATTRIBUTE COLUMNS, NOT timeseries arrays
   - Example: cropping_intensity_vector has columns: cropping_intensity_2017, cropping_intensity_2018, ..., cropping_intensity_2023
   - Use for: Village/tehsil-level analysis where spatial variation matters

**2️⃣ TIMESERIES DATA (Watershed MWS)** - For temporal water budget analysis:
   - Single aggregated value per watershed per time period
   - NO spatial variation (entire watershed = 1 value)
   - Fortnightly measurements (water balance components)
   - Example: water_balance timeseries has arrays: year[], fortnight[], runoff[], precipitation[]
   - Use for: Watershed water budget analysis ONLY

═══════════════════════════════════════════════════════════════════════════════
LAYER SELECTION DECISION FRAMEWORK (WITH EXPLANATIONS)
═══════════════════════════════════════════════════════════════════════════════

**Query Type 1: "Cropping Intensity in [Village] Over Years"**
✅ CORRECT CHOICE: cropping_intensity_vector (spatial vector)
❌ WRONG CHOICE: watershed timeseries

WHY SPATIAL?
- Cropping intensity is SPATIALLY VARIABLE (different fields = different intensity)
- You want: total area under crops in village, which varies by location
- Data structure: GeoDataFrame with polygon features
- Temporal aspect: Stored as yearly columns (cropping_intensity_2017, 2018, ..., 2023)
- Analysis approach: Sum/average these columns across village polygons, plot trend

WHY NOT TIMESERIES?
- Watershed timeseries measures aggregate WATER BALANCE (runoff, precip, ET)
- It's NOT about cropping patterns or land use
- Timeseries is fortnightly, not yearly
- Timeseries has NO spatial variation (1 value per watershed)

**Query Type 2: "Surface Water Availability Over Years in [Village]"**
✅ PRIMARY: surface_water_bodies_vector (spatial vector)
⚠️  OPTIONAL CONTEXT: water_balance (timeseries) for watershed-level trends

WHY SPATIAL?
- Surface water bodies are PHYSICAL FEATURES with geometry (lakes, ponds, reservoirs)
- You want: total area of water bodies within village boundaries
- Data structure: Polygon features with seasonal attributes (Kharif/Rabi/Zaid flags)
- Analysis: Clip polygons to village, sum area per season

CAVEAT: surface_water_bodies_vector may be a SINGLE SNAPSHOT per year
- For multi-year TRENDS, derive from land_use_land_cover_raster
- Workaround: Count water pixels (classes 2-4) in LULC for years 2017-2024

**Query Type 3: "Tree Cover Loss in [Village] Since [Year]"**
✅ CORRECT: change_tree_cover_loss_raster (change raster)

WHY CHANGE RASTER?
- Pre-computed transition matrix: trees (class 6) → other classes
- Period: 2017-2022 composite (mode of 2017-2019 vs 2020-2022)
- Classes: Trees→Built-up, Trees→Barren, Trees→Crops, Trees→Shrubs
- Analysis: Mask to loss classes, count pixels, convert to hectares
- SAVES COMPUTATION vs manually comparing 2017 vs 2022 LULC

FALLBACK: If custom time period (e.g., "2018-2024"):
- Use land_use_land_cover_raster for specific years
- Compare class 6 (trees) presence across years manually

**Query Type 4: "Cropland to Built-up Conversion in [Village]"**
✅ CORRECT: change_urbanization_raster (change raster)

WHY?
- Pre-computed transition: Crops/Trees → Built-up
- Class 3 specifically = "Crops → Built-up" (THIS IS WHAT YOU WANT!)
- Period: 2017-2022 composite
- Analysis: Filter to class 3, count pixels, convert to hectares

═══════════════════════════════════════════════════════════════════════════════

Instructions:
1. **CORESTACK PRIORITY (PRIMARY)**: For ANY query about India or Indian locations, you MUST call fetch_corestack_data FIRST to access CoreStack database. Available CoreStack layers:
   - Raster: {', '.join(CORESTACK_DATA_PRODUCTS['raster_layers'])}
   - Vector: {', '.join(CORESTACK_DATA_PRODUCTS['vector_layers'])}
   - Timeseries: {', '.join(CORESTACK_DATA_PRODUCTS['timeseries_metrics'])}

**IMPORTANT: PRE-COMPUTED CHANGE DETECTION LAYERS (2017-2022)**

CoreStack provides pre-computed change detection layers covering 2017-2022. Use these for change queries instead of computing from raw LULC:

a) **change_tree_cover_loss_raster**: Tree cover loss 2017-2022
   - Class values: 0 = No change, 1 = Tree loss
   - Use for: "tree cover loss since 2018", "deforestation"
   - MASK to class 1 to get loss areas

b) **change_tree_cover_gain_raster**: Tree cover gain 2017-2022  
   - Class values: 0 = No change, 1 = Tree gain
   - Use for: "tree cover gain", "reforestation"
   - MASK to class 1 to get gain areas

c) **change_urbanization_raster**: Built-up expansion 2017-2022
   - Class 1: BuiltUp → BuiltUp (stable)
   - Class 2: NonBuiltUp → BuiltUp (new urbanization)
   - Class 3: Crops → BuiltUp (CROPLAND TO BUILT-UP CONVERSION)
   - Class 4: Forest → BuiltUp (forest lost to urban)
   - Use for: "cropland to built-up", "urban expansion", "loss of agricultural land"
   - MASK to class 3 for cropland-to-urban conversion

d) **change_cropping_reduction_raster**: Cropland degradation 2017-2022
   - Shows areas where cropping intensity decreased
   
e) **change_cropping_intensity_raster**: Cropping intensity transitions 2017-2022
   - Shows how cropping patterns changed (single→double, double→triple, etc.)

f) **cropping_intensity_vector**: Vector layer with yearly attributes
   - Contains cropping intensity values for EACH YEAR (2017-2022+)
   - Use for: "cropping intensity over years", "temporal trends in cropping"
   - IMPORTANT: Year data in columns like cropping_intensity_2017, cropping_intensity_2018, etc.
   - ALWAYS extract year using regex from column names (search for 4-digit numbers)

g) **surface_water_bodies_vector**: Water bodies with temporal attributes
   - Has seasonal availability and area over years
   - Use for: "surface water over years", "water availability trends"
   
h) **drought_frequency_vector**: Drought severity mapping
   - Use for: "drought affected areas", "drought frequency"

**IMPORTANT: MICROWATERSHED-LEVEL DATA**:
CoreStack data is provided at **microwatershed (MWS) level**, NOT village level. Each polygon represents a small watershed area within the tehsil. When analyzing a village:
1. The data contains ALL microwatersheds in the tehsil covering the village area
2. NO village name column exists - data is at finer granularity
3. For village-level analysis: Aggregate statistics across all microwatersheds (use mean, sum, etc.)
4. Use `uid` column for microwatershed identification

**MULTI-REGION DATA SUPPORT**:
When village spans multiple tehsils, layers will have MULTIPLE URLs in the 'urls' array.
Each layer has structure: {{'layer_name': str, 'layer_type': str, 'urls': [{{url, tehsil, district, state}}, ...]}}
For multi-region layers: Read ALL URLs, concat GeoDataFrames, then analyze.

2. **CORESTACK USAGE** (for India queries):
    ```python
    import json
    import os
    import geopandas as gpd
    import pandas as pd
    
    # ALWAYS create exports directory first
    os.makedirs('./exports', exist_ok=True)
    
    result = fetch_corestack_data("your query about India")
    data = json.loads(result)
    
    if data['success'] and data['data_type'] == 'spatial':
        # Access layer data from result
        vector_layers = data['spatial_data']['vector_layers']
        raster_layers = data['spatial_data']['raster_layers']
        
        # EXAMPLE 1: TEMPORAL VECTOR (Cropping Intensity Over Years)
        for layer in vector_layers:
            if 'Cropping Intensity' in layer['layer_name']:
                # Handle multi-region: Read all URLs and concat
                all_gdfs = []
                for url_info in layer['urls']:
                    gdf = gpd.read_file(url_info['url'])
                    all_gdfs.append(gdf)
                
                # Merge all regions
                merged_gdf = pd.concat(all_gdfs, ignore_index=True)
                
                # CRITICAL: Extract years from column names (e.g., 'cropping_intensity_2017')
                import re
                year_cols = [col for col in merged_gdf.columns if 'cropping_intensity_' in col and re.search(r'\\d{{4}}', col)]
                
                # Parse year from column name: 'cropping_intensity_2017' -> 2017
                years_data = []
                for col in sorted(year_cols):
                    year_match = re.search(r'(\\d{{4}})', col)
                    if year_match:
                        year = int(year_match.group(1))
                        avg_value = merged_gdf[col].mean()
                        years_data.append((year, avg_value))
                
                # Sort by year and plot
                years_data.sort()
                years_list = [y[0] for y in years_data]
                values_list = [y[1] for y in years_data]
                
                import matplotlib.pyplot as plt
                plt.figure(figsize=(10, 6))
                plt.plot(years_list, values_list, marker='o')
                plt.xlabel('Year')
                plt.ylabel('Average Cropping Intensity')
                plt.title('Cropping Intensity Over Years')
                plt.savefig('./exports/cropping_intensity_over_years.png')
                print(f"Years: {{years_list}}")
                print(f"Values: {{values_list}}")
        
        # EXAMPLE 2: CHANGE DETECTION RASTER (Tree Cover Loss)
        for layer in raster_layers:
            if 'Change Tree Cover Loss' in layer['layer_name']:
                import rasterio
                # For rasters, typically use first URL (single region or mosaic)
                url = layer['urls'][0]['url']
                with rasterio.open(url) as src:
                    loss_data = src.read(1)
                    # Mask to class 1 (loss areas)
                    loss_mask = (loss_data == 1)
                    loss_area_pixels = loss_mask.sum()
                    # Convert to hectares using pixel size
                    pixel_area = src.transform[0] * abs(src.transform[4])
                    loss_area_ha = loss_area_pixels * pixel_area / 10000
                    print(f"Tree cover loss: {{loss_area_ha:.2f}} hectares")
                
    elif data['success'] and data['data_type'] == 'timeseries':
        # Access timeseries data
        timeseries = data['timeseries_data']
        # Process timeseries for temporal analysis
    ```
3. **EARTH ENGINE (SUPPLEMENTARY)**: ONLY use Earth Engine if CoreStack doesn't have the required data or for non-India queries. When using Earth Engine:
   - Initialize with: `ee.Initialize(project='apt-achievment-453417-h6')`
   - Use harmonized Sentinel-2 (COPERNICUS/S2_SR_HARMONIZED) and harmonized Landsat (LANDSAT/LC08/C02/T1_L2)
   - Export to local machine using geedim:
    ```python
    import geedim as gd
    gd_image = gd.MaskedImage(ee_image)
    gd_image.download(filename=output_filename, scale=scale, region=ee_geom, crs='EPSG:4326')
    ```
4. You can also use OpenStreetMap (osmnx) for additional context like roads, buildings, etc.
5. Then, you should write python code to perform the task.
6. When reading up vector data, always use to_crs method to convert to EPSG:4326.
7. **CRS HANDLING (CRITICAL)**:
   - CoreStack data: EPSG:4326 (WGS84 lat/lon)
   - India UTM Zone: EPSG:32643 (for area calculations)
   - For area: ALWAYS reproject to EPSG:32643 BEFORE calculating
   - For distance: Use geodesic calculations (geopy or shapely ops)
8. Pay extra attention to CRS of the data products, verify them manually before using them in analysis.
9. Always use actual data sources to perform analysis, do not use dummy/sample data.
10. **EXPORT FORMATS**:
    - All vector data should be exported in GeoJSON
    - All raster data should be exported in GeoTIFF
    - All visualizations should be exported in PNG
    - **CRITICAL**: All exports must be saved to `./exports/` directory (use relative path)
    - **FIRST STEP**: Always create exports directory: `import os; os.makedirs('./exports', exist_ok=True)`
    - Use paths like: `'./exports/output.png'`, `'./exports/data.geojson'`, etc.

**EXPECTED OUTPUT TYPES** (based on query type):
- Time series plots: Line charts showing temporal trends (e.g., cropping intensity over years, surface water over years)
- Change rasters: GeoTIFF files with change detection (e.g., tree cover change, cropland to built-up conversion) + total area statistics in hectares
- Filtered vectors: GeoJSON files with spatial filtering (e.g., villages with drought, high sensitivity microwatersheds)
- Rankings: CSV or tables showing ranked microwatersheds/villages by various dimensions
- Similarity analysis: Top-K similar microwatersheds based on multiple attributes
- Scatterplots: 2D plots showing relationships between variables, with quadrant analysis where applicable

**IMPORTANT NOTES**:
- Access layer data directly from the tool's JSON response: `data['spatial_data']['vector_layers']`
- Get layer by name by iterating through the layers list and matching the name
- ALWAYS reproject to UTM (EPSG:32643) before area calculations
- **CRITICAL**: Save all exports to `./exports/` directory (relative path). Create directory first with `os.makedirs('./exports', exist_ok=True)`
- NEVER use `/app/exports/` path - that's for Docker only
- NEVER create dummy or fake data - ALWAYS use the actual data from fetch_corestack_data
- The tool returns real data in 'Execution logs' - parse and use that data directly

Make sure to wrap your final answer along with expected outputs as code block with a single-line string with \\n delimiters inside final_answer function. For example, your final response should look like:

```py  
final_answer("The final answer is .... .\\n Exports:  \\n- export1: ./exports/export1.some_ext  \\n- export2: ./exports/export2.some_ext")  
```

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
    
    # Get workspace directory
    workspace_dir = os.path.dirname(os.path.abspath(__file__))
    
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
    
    # Use local Python executor
    print("✅ Using local Python executor")
    agent = CodeAgent(
        model=model,
        tools=tools,
        additional_authorized_imports=["*"]
    )
    
    try:
        # Generate prompt and run agent
        prompt = create_corestack_prompt(user_query)
        
        # Run agent
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
        pass  # No cleanup needed for local executor


# ============================================================================
# EXAMPLE USAGE & COMPARISON
# ============================================================================

if __name__ == "__main__":
    """
    Example usage of the hybrid agent with a test query.
    """
    
    
    print("ARCHITECTURE 4 TEST")
    print("="*70)
    
    print("Running query #1 from CSV (Shirur, Dharwad, Karnataka - correct coords)...")
    print("="*70)
    

    run_hybrid_agent("Could you show me how average cropping intensity in village Shirur in Dharwad district, Karnataka has changed over the years?")
