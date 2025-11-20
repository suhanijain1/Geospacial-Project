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
    FIXED: Fetches and merges geospatial data using improved LangGraph workflow.
    Returns clean, clipped data ready for CodeAct analysis.
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
    print("📊 CORESTACK DATA FETCHER (via LangGraph)")
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
        
        # Extract results
        merged_data_type = result_state.get("merged_data_type")
        
        if merged_data_type == "vector":
            # Return vector data info
            merged_gdf = result_state.get("merged_data")
            
            response = {
                "success": True,
                "data_type": "vector",
                "feature_count": len(merged_gdf),
                "columns": list(merged_gdf.columns),
                "sample_features": merged_gdf.head(3).to_dict(),
                "geojson_path": result_state.get("merged_data_path"),
                "bounds": str(merged_gdf.total_bounds)
            }
            
        elif merged_data_type == "raster":
            # Return raster data info
            import rasterio
            
            raster_path = result_state.get("merged_data_path")
            with rasterio.open(raster_path) as src:
                response = {
                    "success": True,
                    "data_type": "raster",
                    "shape": (src.height, src.width),
                    "crs": str(src.crs),
                    "bounds": src.bounds,
                    "raster_path": raster_path,
                    "dtype": str(src.dtypes[0]),
                    "nodata": src.nodata
                }
            
        else:
            response = {
                "success": True,
                "message": "Data fetched but no merged data available"
            }
        
        print(f"\n✅ FETCH COMPLETE: {response}")
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

**MULTI-REGION DATA MERGING** (when layer has merge_required=True):
When village spans multiple tehsils, some layers will have a 'merge_required' flag and 'merge_sources' list.
Check layer.get('merge_required') and if True, read all URLs from layer['merge_sources'], then concat the GeoDataFrames.

2. **CORESTACK USAGE** (for India queries):
    ```python
    import json
    import os
    
    # ALWAYS create exports directory first
    os.makedirs('./exports', exist_ok=True)
    
    result = fetch_corestack_data("your query about India")
    data = json.loads(result)
    
    if data['success'] and data['data_type'] == 'spatial':
        # Access layer data from result
        vector_layers = data['spatial_data']['vector_layers']
        raster_layers = data['spatial_data']['raster_layers']
        
        # CHANGE DETECTION EXAMPLE: Tree cover loss
        for layer in raster_layers:
            if 'change_tree_cover_loss' in layer['layer_name']:
                import rasterio
                with rasterio.open(layer['layer_url']) as src:
                    loss_data = src.read(1)
                    # Mask to class 1 (loss areas)
                    loss_mask = (loss_data == 1)
                    loss_area_pixels = loss_mask.sum()
                    # Convert to hectares using pixel size
                    pixel_area = src.transform[0] * abs(src.transform[4])
                    loss_area_ha = loss_area_pixels * pixel_area / 10000
                    print(f"Tree cover loss: {{loss_area_ha:.2f}} hectares")
        
        # TEMPORAL VECTOR EXAMPLE: Cropping intensity over years
        for layer in vector_layers:
            if 'cropping_intensity' in layer['layer_name']:
                gdf = gpd.read_file(layer['layer_url'])
                
                # IMPORTANT: Extract years from column names (e.g., 'cropping_intensity_2017')
                import re
                year_cols = [col for col in gdf.columns if 'cropping_intensity_' in col and re.search(r'\d{4}', col)]
                
                # Parse year from column name: 'cropping_intensity_2017' -> 2017
                years_data = []
                for col in sorted(year_cols):
                    year_match = re.search(r'(\d{4})', col)
                    if year_match:
                        year = int(year_match.group(1))
                        avg_value = gdf[col].mean()
                        years_data.append((year, avg_value))
                
                # Sort by year and plot
                years_data.sort()
                years = [y[0] for y in years_data]
                values = [y[1] for y in years_data]
                
                plt.figure(figsize=(10, 6))
                plt.plot(years, values, marker='o')
                plt.xlabel('Year')
                plt.ylabel('Average Cropping Intensity')
                plt.title('Cropping Intensity Over Years')
                plt.savefig('./exports/cropping_intensity_over_years.png')
                print(f"Years: {years}")
                print(f"Values: {values}")
                
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
