"""
New Clean Architecture for Geospatial Agent


================================================================================
"""

import os
import requests
import json
import statistics
import re
import traceback
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import tempfile

# LangGraph and LLM imports
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph
from dotenv import load_dotenv

# Geospatial processing imports
import pandas as pd
import geopandas as gpd
import rasterio
from rasterio.mask import mask
from rasterio.merge import merge as rio_merge
from rasterio.mask import mask as rio_mask
from shapely.geometry import Point, box, shape, Polygon
from shapely.ops import transform as shp_transform
import pyproj
from pyproj import CRS, Transformer
from geopy.geocoders import Nominatim
from geopy.distance import geodesic as geopy_geodesic
import numpy as np

import ee
import geemap
 
load_dotenv()

# Initialize Earth Engine
GEE_PROJECT = os.getenv("GEE_PROJECT", "apt-achievment-453417-h6")
try:
    ee.Initialize(project=GEE_PROJECT)
    print(f"✅ Earth Engine initialized with project: {GEE_PROJECT}")
except Exception as e:
    print(f"⚠️  Earth Engine initialization failed: {e}")

# ============================================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
CORE_STACK_API_KEY = os.getenv("CORE_STACK_API_KEY")

if not GEMINI_API_KEY or not CORE_STACK_API_KEY:
    raise ValueError("GEMINI_API_KEY and CORE_STACK_API_KEY must be set in environment")

# API Configuration
BASE_URL = "https://geoserver.core-stack.org/api/v1/"
API_HEADERS = {"X-API-Key": CORE_STACK_API_KEY}


# ============================================================================
# CORESTACK API WRAPPER FUNCTIONS 
# ============================================================================

class CoreStackAPI:
    """
    Wrapper for all CoreStack API endpoints with proper coupling.
    Based on official Swagger documentation.
    """
    
    def __init__(self, api_key: str, base_url: str = BASE_URL):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {"X-API-Key": api_key}
    
    # ========================================================================
    # GROUP 1: SPATIAL LAYER ACCESS (Coupled APIs)
    # ========================================================================
    
    def get_admin_details_by_latlon(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """
        Get administrative details (state, district, tehsil) from coordinates.
        
        Swagger: GET /get_admin_details_by_latlon/
        Parameters: latitude (float), longitude (float)
        Returns: {"State": str, "District": str, "Tehsil": str}
        
        Use case: Required before calling get_generated_layer_urls
        """
        print(f"\n📡 API CALL: get_admin_details_by_latlon")
        print(f"   Params: latitude={latitude}, longitude={longitude}")
        
        params = {"latitude": latitude, "longitude": longitude}
        response = requests.get(
            f"{self.base_url}get_admin_details_by_latlon/",
            params=params,
            headers=self.headers
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"📦 RESPONSE: State={result.get('State')}, District={result.get('District')}, Tehsil={result.get('Tehsil')}")
            return result
        else:
            error_msg = f"Admin details lookup failed: {response.text}"
            print(f"❌ ERROR: {error_msg}")
            raise Exception(error_msg)
    
    def get_generated_layer_urls(self, state: str, district: str, tehsil: str) -> List[Dict[str, Any]]:
        """
        Get all available spatial layers for a location.
        
        Swagger: GET /get_generated_layer_urls/
        Parameters: state (str), district (str), tehsil (str)
        Returns: List of {layer_name: str, layer_url: str, layer_type: str}
        
        Dependencies: Requires state/district/tehsil from get_admin_details_by_latlon
        """
        print(f"\n📡 API CALL: get_generated_layer_urls")
        print(f"   Params: state={state}, district={district}, tehsil={tehsil}")
        
        params = {
            'state': state,
            'district': district,
            'tehsil': tehsil
        }
        response = requests.get(
            f"{self.base_url}get_generated_layer_urls/",
            params=params,
            headers=self.headers
        )
        
        if response.status_code == 200:
            layers = response.json()
            vector_count = sum(1 for l in layers if l.get('layer_type') == 'vector')
            raster_count = sum(1 for l in layers if l.get('layer_type') == 'raster')
            print(f"📦 RESPONSE: {len(layers)} total layers ({vector_count} vector, {raster_count} raster)")
            # Print layer names only (not full details)
            layer_names = [l.get('layer_name', 'Unknown') for l in layers[:5]]
            if len(layers) > 5:
                print(f"   First 5 layers: {', '.join(layer_names)} ... (+{len(layers)-5} more)")
            else:
                print(f"   Layers: {', '.join(layer_names)}")
            return layers
        else:
            error_msg = f"Layer fetch failed: {response.text}"
            print(f"❌ ERROR: {error_msg}")
            raise Exception(error_msg)
    
    def get_spatial_layers_by_coordinates(self, latitude: float, longitude: float) -> Tuple[Dict, List[Dict]]:
        """
        COUPLED API: Get spatial layers for coordinates (combines both APIs).
        
        Workflow:
        1. get_admin_details_by_latlon(lat, lon) → state/district/tehsil
        2. get_generated_layer_urls(state, district, tehsil) → layers
        
        Returns: (admin_info, layers)
        """
        print("\n" + "="*70)
        print("🔗 COUPLED API WORKFLOW: Spatial Layers by Coordinates")
        print("="*70)
        
        # Step 1: Get admin boundaries
        admin_info = self.get_admin_details_by_latlon(latitude, longitude)
        
        # Step 2: Get layers using admin info
        layers = self.get_generated_layer_urls(
            state=admin_info.get('State', admin_info.get('state')),
            district=admin_info.get('District', admin_info.get('district')),
            tehsil=admin_info.get('Tehsil', admin_info.get('tehsil'))
        )
        
        return admin_info, layers
    
    # ========================================================================
    # GROUP 2: WATERSHED TIMESERIES DATA (Coupled APIs)
    # ========================================================================
    
    def get_mwsid_by_latlon(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """
        Get watershed UID from coordinates.
        
        Swagger: GET /get_mwsid_by_latlon/
        Parameters: latitude (float), longitude (float)
        Returns: {"uid": str, "state": str, "district": str, "tehsil": str}
        
        Use case: Required before calling get_mws_data for timeseries
        Note: NOT for spatial layers! Use get_admin_details_by_latlon instead.
        """
        print(f"\n📡 API CALL: get_mwsid_by_latlon")
        print(f"   Params: latitude={latitude}, longitude={longitude}")
        
        params = {"latitude": latitude, "longitude": longitude}
        response = requests.get(
            f"{self.base_url}get_mwsid_by_latlon/",
            params=params,
            headers=self.headers
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"📦 RESPONSE: UID={result.get('uid')}")
            return result
        else:
            error_msg = f"Watershed lookup failed: {response.text}"
            print(f"❌ ERROR: {error_msg}")
            raise Exception(error_msg)
    
    def get_mws_data(self, uid: str) -> Dict[str, Any]:
        """
        Get timeseries data for a watershed.
        
        Swagger: GET /get_mws_data/
        Parameters: uid (str)
        Returns: Timeseries data with year/value/source arrays
        
        Dependencies: Requires UID from get_mwsid_by_latlon
        """
        print(f"\n📡 API CALL: get_mws_data")
        print(f"   Params: uid={uid}")
        
        params = {"uid": uid}
        response = requests.get(
            f"{self.base_url}get_mws_data/",
            params=params,
            headers=self.headers
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"📦 RESPONSE: Timeseries data retrieved")
            return result
        else:
            error_msg = f"Timeseries fetch failed: {response.text}"
            print(f"❌ ERROR: {error_msg}")
            raise Exception(error_msg)
    
    def get_timeseries_by_coordinates(self, latitude: float, longitude: float) -> Tuple[Dict, Dict]:
        """
        COUPLED API: Get timeseries data for coordinates (combines both APIs).
        
        Workflow:
        1. get_mwsid_by_latlon(lat, lon) → uid
        2. get_mws_data(uid) → timeseries
        
        Returns: (watershed_info, timeseries_data)
        """
        print("\n" + "="*70)
        print("🔗 COUPLED API WORKFLOW: Timeseries by Coordinates")
        print("="*70)
        
        # Step 1: Get watershed UID
        watershed_info = self.get_mwsid_by_latlon(latitude, longitude)
        
        # Step 2: Get timeseries data
        uid = watershed_info.get('uid')
        timeseries_data = self.get_mws_data(uid)
        
        return watershed_info, timeseries_data
    

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def geocode_location(location_name: str) -> Optional[Tuple[float, float]]:
    """Geocode a location name to coordinates (latitude, longitude)"""
    try:
        geolocator = Nominatim(user_agent="geospatial_agent")
        location = geolocator.geocode(location_name)
        if location:
            return (location.latitude, location.longitude)
    except Exception as e:
        print(f"Geocoding error: {e}")
    return None


def geodesic_buffer(lon: float, lat: float, radius_m: float, out_crs: str = "EPSG:4326") -> Polygon:
    """
    Create a circular buffer around a point using geodesic distance.
    
    Args:
        lon: Longitude of center point
        lat: Latitude of center point
        radius_m: Buffer radius in meters
        out_crs: Output coordinate reference system
    
    Returns:
        Shapely Polygon representing the buffer
    """
    from pyproj import Geod
    geod = Geod(ellps="WGS84")
    angles = np.linspace(0, 360, 64)
    circle_points = []
    
    for angle in angles:
        end_lon, end_lat, _ = geod.fwd(lon, lat, angle, radius_m)
        circle_points.append((end_lon, end_lat))
    
    circle = Polygon(circle_points)
    
    if out_crs != "EPSG:4326":
        project = pyproj.Transformer.from_crs("EPSG:4326", out_crs, always_xy=True).transform
        circle = shp_transform(project, circle)
    
    return circle


# Initialize API wrapper
api = CoreStackAPI(api_key=CORE_STACK_API_KEY)


# ============================================================================
# SPATIAL DATA PROCESSOR
# ============================================================================

class SpatialDataProcessor:
    """Handles vector and raster data processing"""
    
    @staticmethod
    def process_vector_url(url: str, point: Optional[tuple] = None, buffer_km: float = 1.0) -> Dict:
        """
        Process vector data from URL
        
        Args:
            url: GeoJSON URL
            point: (lat, lon) tuple for filtering
            buffer_km: Buffer radius in km
        
        Returns:
            Dict with statistics and sample features
        """
        print(f"\n📡 DOWNLOADING VECTOR: {url[:100]}...")
        
        try:
            gdf = gpd.read_file(url)
            print(f"📦 LOADED: {len(gdf)} features")
            print(f"📋 COLUMNS: {list(gdf.columns)}")
            
            # Filter by buffer if point provided
            if point:
                lat, lon = point
                buffer_geom = geodesic_buffer(lon, lat, buffer_km * 1000, out_crs=gdf.crs)
                gdf = gdf[gdf.intersects(buffer_geom)]
                print(f"🔍 FILTERED: {len(gdf)} features within {buffer_km}km")
            
            # Calculate statistics (reproject to UTM for accurate area calculation)
            stats = {
                'feature_count': len(gdf),
                'columns': list(gdf.columns),
                'attributes': {},
                'sample_features': []
            }
            
            # Calculate area in hectares (reproject to UTM zone for India: EPSG:32643)
            if len(gdf) > 0:
                try:
                    gdf_projected = gdf.to_crs('EPSG:32643')  # UTM Zone 43N for India
                    stats['total_area_ha'] = gdf_projected.geometry.area.sum() / 10000  # m² to ha
                except:
                    stats['total_area_ha'] = 0
                    stats['area_calculation_error'] = 'Could not reproject for area calculation'
            else:
                stats['total_area_ha'] = 0
            
            # Extract numeric attributes
            for col in gdf.columns:
                if col != 'geometry':
                    try:
                        # Check if column is numeric
                        if np.issubdtype(gdf[col].dtype, np.number):
                            stats['attributes'][col] = {
                                'mean': float(gdf[col].mean()),
                                'sum': float(gdf[col].sum()),
                                'min': float(gdf[col].min()),
                                'max': float(gdf[col].max())
                            }
                    except:
                        pass  # Skip non-numeric columns
            
            # Add sample features (first 3) for inspection
            if len(gdf) > 0:
                for idx in range(min(3, len(gdf))):
                    feature_dict = {}
                    for col in gdf.columns:
                        if col != 'geometry':
                            feature_dict[col] = gdf.iloc[idx][col]
                    stats['sample_features'].append(feature_dict)
            
            return stats
            
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def process_raster_url(url: str, bounds: Optional[tuple] = None, 
                          circle_geom_4326: Optional[Any] = None) -> Dict:
        """
        Process raster data from URL using HTTP range requests
        
        Args:
            url: GeoTIFF URL (will be automatically prefixed with /vsicurl/ if needed)
            bounds: (minx, miny, maxx, maxy) bounding box
            circle_geom_4326: Shapely geometry for masking
        
        Returns:
            Dict with statistics
        """
        print(f"\n📡 PROCESSING RASTER: {url[:100]}...")
        print(f"🔍 DEBUG: Function called with circle_geom={circle_geom_4326 is not None}, bounds={bounds}")
        
        # Prefix with /vsicurl/ if it's an HTTP URL without it
        if url.startswith('http') and not url.startswith('/vsicurl/'):
            url = f'/vsicurl/{url}'
            print(f"🔍 DEBUG: Added /vsicurl/ prefix")
        
        try:
            # Enable GDAL options for better WCS support
            import os
            os.environ['GDAL_HTTP_UNSAFESSL'] = 'YES'
            os.environ['CPL_VSIL_CURL_ALLOWED_EXTENSIONS'] = '.tif,.tiff,.vrt'
            print(f"🔍 DEBUG: Set GDAL environment variables")
            
            print(f"🔍 DEBUG: Opening raster with rasterio...")
            with rasterio.open(url) as src:
                # Get raster info
                print(f"📦 RASTER INFO: {src.width}x{src.height}, CRS: {src.crs}")
                
                # Read data (windowed if bounds provided)
                if bounds:
                    window = src.window(*bounds)
                    data = src.read(1, window=window)
                elif circle_geom_4326:
                    # Get window from circle bounds
                    minx, miny, maxx, maxy = circle_geom_4326.bounds
                    print(f"📦 Circle bounds: ({minx:.4f}, {miny:.4f}, {maxx:.4f}, {maxy:.4f})")
                    try:
                        window = src.window(minx, miny, maxx, maxy)
                        data = src.read(1, window=window)
                        print(f"📦 Window read: {data.shape}, non-zero pixels: {np.count_nonzero(data)}")
                    except Exception as e:
                        print(f"⚠️  Window read failed, trying full read with mask: {e}")
                        # Fallback: read full and mask
                        from rasterio.mask import mask as rio_mask
                        out_image, out_transform = rio_mask(src, [circle_geom_4326], crop=True, filled=False)
                        data = out_image[0]
                else:
                    # Read full raster
                    data = src.read(1)
                
                # Filter nodata
                nodata = src.nodata
                print(f"📦 Nodata value: {nodata}")
                print(f"📦 Data shape: {data.shape}, dtype: {data.dtype}")
                print(f"📦 Data range: min={np.min(data)}, max={np.max(data)}")
                print(f"📦 Unique values: {np.unique(data)[:10]}")  # First 10 unique values
                
                # Filter nodata - handle multiple common nodata values
                if nodata is not None:
                    valid_data = data[data != nodata]
                else:
                    # Common nodata values if not specified
                    valid_data = data[(data != 0) & (data != -9999) & (data != 255) & (~np.isnan(data))]
                
                print(f"📦 Valid pixels: {len(valid_data)} out of {data.size}")
                
                # Calculate statistics
                if len(valid_data) > 0:
                    stats = {
                        'mean': float(np.mean(valid_data)),
                        'median': float(np.median(valid_data)),
                        'std': float(np.std(valid_data)),
                        'min': float(np.min(valid_data)),
                        'max': float(np.max(valid_data)),
                        'pixel_count': int(len(valid_data))
                    }
                    print(f"✅ Stats: mean={stats['mean']:.2f}, pixels={stats['pixel_count']}")
                else:
                    stats = {'error': 'No valid data in raster', 'total_pixels': int(data.size), 'nodata_value': nodata}
                    print(f"❌ No valid data found!")
                
                return stats
                
        except Exception as e:
            return {'error': str(e)}


# ============================================================================
# CODEACT AGENT
# ============================================================================

class CodeActAgent:
    """Clean CodeAct implementation with planning and execution"""
    
    def __init__(self, gemini_api_key: str):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-lite",
            temperature=0.1,
            google_api_key=gemini_api_key
        )
    
    def generate_plan(self, query: str, available_layers: Dict[str, list]) -> Dict[str, Any]:
        """Generate human-readable execution plan"""
        print("\n" + "="*70)
        print("🧠 GENERATING EXECUTION PLAN")
        print("="*70)
        
        # Simplify layer info for LLM
        vector_layers = [f"{l['layer_name']} (vector)" for l in available_layers.get('vector', [])]
        raster_layers = [f"{l['layer_name']} (raster)" for l in available_layers.get('raster', [])]
        
        prompt = f"""You are a geospatial analyst. Create a clear execution plan.

USER QUERY: "{query}"

AVAILABLE DATA:
Vector Layers: {', '.join(vector_layers) if vector_layers else 'None'}
Raster Layers: {', '.join(raster_layers) if raster_layers else 'None'}

TASK: Create a step-by-step plan to answer the query.

RULES:
1. Each step should be clear and specific
2. Identify which data layers to use
3. Specify operations needed (filter, intersect, mask, calculate, etc.)
4. Keep it simple - aim for 3-6 steps

OUTPUT FORMAT (JSON):
{{
  "steps": [
    "Step 1: Download and load cropping intensity vector layer",
    "Step 2: Filter features where intensity > threshold",
    "Step 3: Calculate total area of filtered regions"
  ],
  "data_needed": ["Cropping Intensity", "LULC_level_1"]
}}

Generate plan now:"""

        try:
            response = self.llm.invoke(prompt)
            content = response.content.strip()
            content = re.sub(r"^```json\s*|```$", "", content, flags=re.MULTILINE).strip()
            plan = json.loads(content)
            
            print("\n📋 EXECUTION PLAN:")
            for i, step in enumerate(plan.get('steps', []), 1):
                print(f"  {i}. {step}")
            print(f"\n📦 DATA NEEDED: {', '.join(plan.get('data_needed', []))}")
            
            return plan
            
        except Exception as e:
            print(f"❌ Plan generation error: {e}")
            return {"steps": ["Error generating plan"], "data_needed": []}
    
    def generate_code(self, query: str, plan: Dict[str, Any], selected_layers: Dict[str, list]) -> str:
        """Generate Python code based on the plan"""
        print("\n" + "="*70)
        print("💻 GENERATING PYTHON CODE")
        print("="*70)
        
        # Build context about available data WITH SCHEMA INFORMATION
        layer_context = []
        
        # For vector layers, try to fetch schema information
        for layer in selected_layers.get('vector', []):
            layer_info = f"VECTOR: '{layer['layer_name']}' at URL: {layer['layer_url']}"
            
            # Try to get column information (quick peek)
            try:
                import geopandas as gpd
                gdf_sample = gpd.read_file(layer['layer_url'], rows=1)  # Just read 1 row for schema
                columns = [col for col in gdf_sample.columns if col != 'geometry']
                layer_info += f"\n       Columns: {columns[:20]}"  # Show first 20 columns
            except:
                layer_info += "\n       Columns: (could not fetch)"
            
            layer_context.append(layer_info)
        
        for layer in selected_layers.get('raster', []):
            layer_context.append(f"RASTER: '{layer['layer_name']}' at URL: {layer['layer_url']}")
        
        prompt = f"""You are a Python code generator for geospatial analysis.

USER QUERY: "{query}"

EXECUTION PLAN:
{chr(10).join(f"{i+1}. {step}" for i, step in enumerate(plan.get('steps', [])))}

AVAILABLE DATA:
{chr(10).join(layer_context)}

AVAILABLE FUNCTIONS:
- SpatialDataProcessor.process_vector_url(url, point=None, buffer_km=1.0) → Returns dict with:
    - 'feature_count': number of features
    - 'total_area_ha': total area in hectares
    - 'columns': list of all column names
    - 'attributes': dict mapping column names to stats (mean, sum, min, max)
    - 'sample_features': list of first 3 feature dicts (without geometry)
- SpatialDataProcessor.process_raster_url(url, bounds=None, circle_geom_4326=None) → dict with stats
- geodesic_buffer(lon, lat, radius_m, out_crs="EPSG:4326") → circle geometry (standalone function!)
  **IMPORTANT**: For raster analysis, use radius_m >= 1000 (1km+) to capture sufficient pixels
- find_layer(layer_list, search_term) → dict (helper to find layers with fuzzy matching - RECOMMENDED!)

VARIABLES IN SCOPE:
- query_lat: float (user's latitude if provided)
- query_lon: float (user's longitude if provided)
- vector_layers: list of dicts with 'layer_name' and 'layer_url'
- raster_layers: list of dicts with 'layer_name' and 'layer_url'
- SpatialDataProcessor: class with static methods for processing layers
- geodesic_buffer: standalone function for creating buffers
- find_layer: helper function for robust layer search

CODE GENERATION RULES:
1. Write clean Python code (no markdown, no explanations)
2. Use the provided helper functions to download/process data
3. Store final result in variable called 'result' (dict or string)
4. Handle errors gracefully (try-except where needed)
5. For vector data: use process_vector_url()
6. For raster data: use process_raster_url() with geodesic_buffer(lon, lat, radius_m)
   - **CRITICAL**: Use radius_m >= 1000 (at least 1km) for rasters to capture enough pixels
   - For point queries: use 1000-5000m radius
   - For "around/near" queries: use 5000-10000m radius
7. DO NOT import additional libraries beyond what's available
8. Keep it simple and focused on answering the query
9. **CRITICAL**: When searching for layers, use EXACT MATCHING with the layer names provided above
10. Layer names are case-sensitive and may have spaces (e.g., "Cropping Intensity", not "crop_intensity")

LAYER MATCHING EXAMPLES:
- **RECOMMENDED**: Use find_layer() helper for robust matching:
  target_layer = find_layer(vector_layers, 'Cropping Intensity')
  target_layer = find_layer(raster_layers, 'NDVI')
  
- Manual exact match: if layer['layer_name'] == 'Cropping Intensity'
- Manual case-insensitive: if 'cropping intensity' in layer['layer_name'].lower()

EXAMPLE CODE FOR VECTOR DATA:
```python
# Use find_layer helper for robust layer matching
target_layer = find_layer(vector_layers, 'Cropping Intensity')

if target_layer:
    stats = SpatialDataProcessor.process_vector_url(
        target_layer['layer_url'],
        point=(query_lat, query_lon),
        buffer_km=5.0
    )
    
    result = {{
        'total_area': stats['attributes']['doubly_cropped_area_2023']['sum']
    }}
else:
    result = {{'error': 'Layer not found'}}
```

EXAMPLE CODE FOR RASTER DATA:
```python
# Find LULC or NDVI raster layer
lulc_layer = find_layer(raster_layers, 'LULC_level_1')

if lulc_layer:
    # Create buffer geometry (use 1-10km radius for rasters!)
    buffer_geom = geodesic_buffer(query_lon, query_lat, 5000, out_crs="EPSG:4326")
    
    # Process raster
    stats = SpatialDataProcessor.process_raster_url(
        lulc_layer['layer_url'],
        circle_geom_4326=buffer_geom
    )
    
    result = {{
        'mean_value': stats.get('mean'),
        'pixel_count': stats.get('pixel_count')
    }}
else:
    result = {{'error': 'Layer not found'}}
```

NOW GENERATE CODE (Python only, no markdown):"""

        try:
            response = self.llm.invoke(prompt)
            code = response.content.strip()
            code = re.sub(r"^```python\s*|^```\s*|```$", "", code, flags=re.MULTILINE).strip()
            
            print("\n📝 GENERATED CODE:")
            print("─" * 70)
            print(code)
            print("─" * 70)
            
            return code
            
        except Exception as e:
            print(f"❌ Code generation error: {e}")
            return "result = {'error': 'Code generation failed'}"
    
    def execute_code(self, code: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the generated code in a controlled environment"""
        print("\n" + "="*70)
        print("🚀 EXECUTING CODE")
        print("="*70)
        
        # Helper function to find layers by name (case-insensitive, partial match)
        def find_layer(layer_list: List[Dict], search_term: str) -> Optional[Dict]:
            """
            Find a layer by name with fuzzy matching.
            Returns the best match or None.
            """
            search_lower = search_term.lower()
            
            # First try exact match (case-insensitive)
            for layer in layer_list:
                if layer['layer_name'].lower() == search_lower:
                    return layer
            
            # Then try partial match
            for layer in layer_list:
                if search_lower in layer['layer_name'].lower():
                    return layer
            
            # Last resort: try matching individual words
            search_words = search_lower.split()
            for layer in layer_list:
                layer_name_lower = layer['layer_name'].lower()
                if all(word in layer_name_lower for word in search_words):
                    return layer
            
            return None
        
        # Prepare safe execution environment
        safe_globals = {
            '__builtins__': __builtins__,
            'SpatialDataProcessor': SpatialDataProcessor,
            'geodesic_buffer': geodesic_buffer,
            'find_layer': find_layer,  # Add helper function
            'gpd': gpd,
            'np': np,
            'json': json
        }
        
        # Add context variables
        safe_globals.update(context)
        
        try:
            exec(code, safe_globals)
            result = safe_globals.get('result', {'error': 'No result variable found'})
            
            print("✅ CODE EXECUTED SUCCESSFULLY")
            print(f"📊 RESULT: {result}")
            
            return {'result': result, 'error': None}
            
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            print(f"❌ EXECUTION ERROR: {error_msg}")
            print("\n🔍 TRACEBACK:")
            print(traceback.format_exc())
            
            return {'result': None, 'error': error_msg}


# ============================================================================
# LANGGRAPH NODES
# ============================================================================

def llm_intent_parser(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    FIXED: Parse user query with proper data product classification.
    Maps queries to actual CoreStack layers.
    """
    print("\n" + "="*70)
    print("🧠 PARSING INTENT")
    print("="*70)
    
    user_query = state["user_query"]
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0,
        google_api_key=GEMINI_API_KEY
    )
    
    prompt = f"""Extract structured information from this geospatial query and map to the CORRECT CoreStack data product.

USER QUERY: "{user_query}"

═══════════════════════════════════════════════════════════════════════════════
CRITICAL UNDERSTANDING: SPATIAL vs TIMESERIES DATA PRODUCTS
═══════════════════════════════════════════════════════════════════════════════

CoreStack has TWO FUNDAMENTALLY DIFFERENT data structures:

1️⃣ SPATIAL DATA (Vectors/Rasters):
   - Geographic features with SPATIAL VARIATION across a region
   - Data varies BY LOCATION (different patches/polygons have different values)
   - Temporal data stored as YEARLY ATTRIBUTE COLUMNS, not timeseries arrays
   - Example: cropping_intensity_vector has columns: cropping_intensity_2017, cropping_intensity_2018, ..., cropping_intensity_2023
   - Use for: Village/tehsil-level analysis where spatial variation matters

2️⃣ TIMESERIES DATA (Watershed MWS):
   - Single aggregated value per watershed per time period
   - NO spatial variation (entire watershed = 1 value)
   - Fortnightly measurements (water balance components)
   - Example: water_balance timeseries has arrays: year[], fortnight[], runoff[], precipitation[]
   - Use for: Watershed water budget analysis only

═══════════════════════════════════════════════════════════════════════════════
DECISION FRAMEWORK WITH EXPLANATIONS
═══════════════════════════════════════════════════════════════════════════════

Query 1: "Cropping Intensity in [Village] Over Years"
───────────────────────────────────────────────────────
✅ CORRECT: cropping_intensity_vector (spatial_vector)
❌ WRONG: watershed timeseries

WHY SPATIAL?
- Cropping intensity is SPATIALLY VARIABLE (different fields have different intensity)
- You want: total area under crops in village, which varies by location
- Data structure: GeoDataFrame with polygon features
- Temporal aspect: Stored as yearly columns (cropping_intensity_2017, 2018, ..., 2023)
- Analysis: Sum/average these columns across village polygons

WHY NOT TIMESERIES?
- Watershed timeseries measures aggregate WATER BALANCE (runoff, precip, ET)
- It's NOT about cropping patterns or land use
- Timeseries is fortnightly, not yearly
- Timeseries has NO spatial variation (1 value per watershed)

RECOMMENDED LAYER: "Cropping Intensity" (exact name from CoreStack)
DATA TYPE: spatial_vector
ANALYSIS TYPE: temporal_vector (yearly columns)

───────────────────────────────────────────────────────

Query 2: "Surface Water Availability Over Years in [Village]"
───────────────────────────────────────────────────────
✅ PRIMARY: surface_water_bodies_vector (spatial_vector)
⚠️  OPTIONAL CONTEXT: water_balance (timeseries) for watershed-level trends

WHY SPATIAL?
- Surface water bodies are PHYSICAL FEATURES with geometry (lakes, ponds, reservoirs)
- You want: total area of water bodies within village boundaries
- Data structure: Polygon features with seasonal attributes (Kharif/Rabi/Zaid flags)
- Analysis: Clip polygons to village, sum area per season

WHY NOT JUST TIMESERIES?
- Watershed water_balance is AGGREGATE (entire watershed, not village-level)
- Water balance doesn't tell you WHERE water bodies are located
- You need spatial polygons to answer "how much water in THIS village"

CRITICAL CAVEAT:
- surface_water_bodies_vector may be a SINGLE SNAPSHOT per year (from LULC conversion)
- For multi-year TRENDS, you may need to derive from land_use_land_cover_raster
- Workaround: Count water pixels (classes 2-4) in LULC for years 2017-2024

RECOMMENDED LAYER: "Surface Water Bodies" (exact name from CoreStack)
DATA TYPE: spatial_vector (primary) + optional timeseries context
ANALYSIS TYPE: temporal_vector (if multi-year versions exist) OR spatial_summary (single snapshot)

───────────────────────────────────────────────────────

Query 3: "Tree Cover Loss in [Village] Since [Year]"
───────────────────────────────────────────────────────
✅ CORRECT: change_tree_cover_loss_raster (change_raster)

WHY CHANGE RASTER?
- Pre-computed transition matrix: trees (class 6) → other classes
- Period: 2017-2022 composite (mode of 2017-2019 vs 2020-2022)
- Classes: Trees→Built-up, Trees→Barren, Trees→Crops, Trees→Shrubs
- Analysis: Mask to loss classes, count pixels, convert to hectares

WHY NOT LULC YEARLY RASTERS?
- Change rasters are PRE-COMPUTED and optimized for this exact query
- Saves computation (no need to manually compare 2017 vs 2022 LULC)
- Already has transition classes ready to filter

FALLBACK: If custom time period (e.g., "2018-2024"):
- Use land_use_land_cover_raster for specific years
- Compare class 6 (trees) presence across years manually

RECOMMENDED LAYER: "Change Tree Cover Loss" (exact name from CoreStack)
DATA TYPE: change_raster
ANALYSIS TYPE: change_detection

───────────────────────────────────────────────────────

Query 4: "Cropland to Built-up Conversion in [Village] Since [Year]"
───────────────────────────────────────────────────────
✅ CORRECT: change_urbanization_raster (change_raster)

WHY CHANGE RASTER?
- Pre-computed transition: Crops/Trees → Built-up (class 3 in urbanization raster)
- Period: 2017-2022 composite
- Analysis: Filter to class 3, count pixels, convert to hectares

CRITICAL: Class 3 specifically = "Trees/Crops → Built-up"
- Other classes in this raster: Built-up expansion, Barren→Built-up
- Must filter correctly to answer "cropland to built-up" query

RECOMMENDED LAYER: "Change Urbanization" (exact name from CoreStack)
DATA TYPE: change_raster
ANALYSIS TYPE: change_detection

───────────────────────────────────────────────────────

Query 5: "Drought-Affected Tehsils in [State]"
───────────────────────────────────────────────────────
✅ CORRECT: drought_frequency_vector (spatial_vector)

WHY SPATIAL?
- Drought frequency is SPATIALLY VARIABLE (different MWS/villages have different severity)
- Data structure: Polygon features with drought severity attributes
- Categories: Severe/Moderate/Mild drought weeks
- Analysis: Aggregate to tehsil level, filter by severity threshold

DEFINITION: Drought = #moderate weeks + #severe weeks >= 5

WHY NOT TIMESERIES?
- Timeseries water_balance has precipitation/runoff but NOT drought classification
- You'd need to compute drought index yourself from timeseries
- Drought frequency vector is PRE-COMPUTED spatial layer

RECOMMENDED LAYER: "Drought Frequency" OR "Drought Causality" (exact name from CoreStack)
DATA TYPE: spatial_vector
ANALYSIS TYPE: state_aggregation (aggregate MWS/villages to tehsil)

═══════════════════════════════════════════════════════════════════════════════
AVAILABLE CORESTACK LAYERS (EXACT NAMES - CASE SENSITIVE)
═══════════════════════════════════════════════════════════════════════════════

SPATIAL VECTORS:
- "Cropping Intensity" (yearly columns: cropping_intensity_2017, ..., 2023)
- "Surface Water Bodies" (seasonal flags: Kharif/Rabi/Zaid)
- "Drought Frequency" (severity: Severe/Moderate/Mild)
- "Drought Causality" (alternative drought layer)
- "NREGA" (rural employment scheme assets)
- "LULC" (vectorized land use polygons)
- "Aquifer" (groundwater aquifer boundaries)
- "Terrain Clusters" (elevation/slope groupings)
- "SOGE" (state of groundwater estimation)
- "Change Vector Degradation" (land degradation polygons)

CHANGE RASTERS (2017-2022 composites):
- "Change Tree Cover Loss" (trees → other classes)
- "Change Tree Cover Gain" (other → trees)
- "Change Urbanization" (any class → built-up)
- "Change Cropping Reduction" (crops → other classes)
- "Change Cropping Intensity" (intensity increase/decrease)

LAND USE RASTERS (yearly, 10m resolution):
- "LULC_level_1" (12 classes: Built-up, Water, Trees, Crops, etc.)
- "LULC_level_2" (detailed classes)
- "Tree Canopy Density High" (yearly)
- "Tree Canopy Density Low" (yearly)

TIMESERIES (Watershed MWS only):
- water_balance (fortnightly: precipitation, runoff, ET, soil moisture)
- NOT for spatial queries or village-level analysis

═══════════════════════════════════════════════════════════════════════════════
OUTPUT FORMAT
═══════════════════════════════════════════════════════════════════════════════

Return JSON:
{{
  "latitude": <float or null>,
  "longitude": <float or null>,
  "location_name": <string or null>,
  "location_type": "village" | "tehsil" | "state" | "coordinates",
  "district": <string or null>,
  "metric": <string describing what user wants to measure>,
  "temporal": <bool - true if query asks about trends/changes over time>,
  "start_year": <int or null>,
  "end_year": <int or null>,
  "data_type_needed": "spatial_vector" | "change_raster" | "timeseries" | "land_use_raster",
  "analysis_type": "temporal_vector" | "change_detection" | "state_aggregation" | "spatial_summary",
  "recommended_layer": <exact layer name from list above>,
  "notes": <string explaining caveats, e.g., "Single snapshot, use LULC for multi-year trends" or "Pre-computed 2017-2022 only, use LULC for custom periods">
}}

DECISION RULES:
1. If query mentions "over years" + spatial metric (cropping, water bodies) → spatial_vector (NOT timeseries)
2. If query mentions "change"/"loss"/"gain" + 2017-2022 period → change_raster
3. If query mentions custom time period (2018-2024) or non-standard years → land_use_raster + notes
4. If query is about watershed water budget → timeseries
5. If query is about state-level aggregation → spatial_vector + state_aggregation
6. ALWAYS use exact layer names from the list above (case-sensitive)
7. Add caveats in notes if data limitations exist (single snapshot, composite period, etc.)

NOW PARSE THE QUERY:"""

    try:
        response = llm.invoke(prompt)
        content = response.content.strip()
        content = re.sub(r"^```json\s*|```$", "", content, flags=re.MULTILINE).strip()
        parsed = json.loads(content)
        
        # Geocode if needed
        if parsed.get('location_name') and not parsed.get('latitude'):
            coords = geocode_location(parsed['location_name'])
            if coords:
                parsed['latitude'], parsed['longitude'] = coords
                print(f"🌍 Geocoded '{parsed['location_name']}' → ({coords[0]:.5f}, {coords[1]:.5f})")
        
        # Map recommended_layer to exact CoreStack layer names (if abbreviated)
        layer_name_mapping = {
            "cropping_intensity_vector": "Cropping Intensity",
            "surface_water_bodies_vector": "Surface Water Bodies",
            "change_tree_cover_loss_raster": "Change Tree Cover Loss",
            "change_urbanization_raster": "Change Urbanization",
            "drought_frequency_vector": "Drought Frequency",
            "change_cropping_reduction_raster": "Change Cropping Reduction",
            "change_tree_cover_gain_raster": "Change Tree Cover Gain",
            "land_use_land_cover_raster": "LULC_level_1",
            "lulc_vector": "LULC"
        }
        
        # Normalize layer name to exact CoreStack format
        recommended = parsed.get('recommended_layer', '')
        if recommended in layer_name_mapping:
            parsed['recommended_layer'] = layer_name_mapping[recommended]
        
        state["parsed"] = parsed
        
        print(f"\n✅ PARSED INTENT:")
        print(f"   Data Type: {parsed.get('data_type_needed')}")
        print(f"   Analysis Type: {parsed.get('analysis_type')}")
        print(f"   Layer: {parsed.get('recommended_layer')}")
        location_display = parsed.get('location_name') or f"({parsed.get('latitude')}, {parsed.get('longitude')})"
        print(f"   Location: {location_display}")
        
    except Exception as e:
        state["error"] = f"Intent parsing failed: {str(e)}"
        print(f"❌ ERROR: {state['error']}")
    
    return state


def fetch_spatial_layers_multiregion(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fetch spatial layers from ALL intersecting regions.
    Accumulates URLs from multiple tehsils if village spans them.
    """
    
    if "error" in state:
        return state
    
    print("\n" + "="*70)
    print("📥 FETCHING SPATIAL LAYERS (MULTI-REGION)")
    print("="*70)
    
    parsed = state["parsed"]
    resolved = state.get("resolved_geometry", {})
    tehsil_list = resolved.get("tehsil_list", [])
    recommended_layer = parsed.get("recommended_layer", "")
    
    if not tehsil_list:
        state["error"] = "No tehsils resolved"
        return state
    
    print(f"\n🔄 Fetching from {len(tehsil_list)} regions...")
    print(f"   Target layer: {recommended_layer}")
    
    data_urls = {'vector': [], 'raster': []}
    location_info = {}
    
    for tehsil_info in tehsil_list:
        state_name = tehsil_info['state']
        district_name = tehsil_info['district']
        tehsil_name = tehsil_info['tehsil']
        
        print(f"\n   🔍 Fetching: {tehsil_name} ({district_name}, {state_name})")
        
        try:
            # Get representative point from tehsil geometry
            centroid = tehsil_info['geometry'].centroid
            lat, lon = centroid.y, centroid.x
            
            # Call CoreStack API for this specific tehsil
            admin_info = api.get_admin_details_by_latlon(
                latitude=lat,
                longitude=lon
            )
            
            layers = api.get_generated_layer_urls(
                state=state_name,
                district=district_name,
                tehsil=tehsil_name
            )
            
            location_info = admin_info  # Store last location info
            
            # Filter to recommended layer
            found_count = 0
            for layer in layers:
                if layer['layer_name'] == recommended_layer:
                    layer_info = {
                        'tehsil': tehsil_name,
                        'district': district_name,
                        'state': state_name,
                        'layer_name': layer['layer_name'],
                        'url': layer['layer_url'],
                        'type': layer.get('layer_type', 'vector')
                    }
                    
                    if layer.get('layer_type') == 'vector':
                        data_urls['vector'].append(layer_info)
                    elif layer.get('layer_type') == 'raster':
                        data_urls['raster'].append(layer_info)
                    
                    found_count += 1
                    print(f"      ✅ Found: {layer['layer_name']}")
            
            if found_count == 0:
                print(f"      ⚠️  Layer '{recommended_layer}' not found in this tehsil")
        
        except Exception as e:
            print(f"      ⚠️  Error fetching from {tehsil_name}: {str(e)}")
            continue
    
    print(f"\n✅ FETCHING COMPLETE:")
    print(f"   Vector layers: {len(data_urls['vector'])}")
    print(f"   Raster layers: {len(data_urls['raster'])}")
    
    if len(data_urls['vector']) == 0 and len(data_urls['raster']) == 0:
        state["error"] = f"Layer '{recommended_layer}' not found in any region"
        print(f"❌ ERROR: {state['error']}")
        return state
    
    state["data_urls"] = data_urls
    state["location_info"] = location_info
    
    return state

def fetch_timeseries_data(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fetch timeseries data for the location.
    Uses COUPLED API workflow: get_mwsid_by_latlon → get_mws_data
    """
    if "error" in state:
        return state
    
    print("\n" + "="*70)
    print("� FETCHING TIMESERIES DATA")
    print("="*70)
    
    parsed = state["parsed"]
    latitude = parsed.get("latitude")
    longitude = parsed.get("longitude")
    uid = parsed.get("uid")
    
    try:
        if uid:
            # Direct UID provided
            print(f"🔑 Using provided UID: {uid}")
            timeseries_data = api.get_mws_data(uid)
            watershed_info = {"uid": uid}
        elif latitude and longitude:
            # Get watershed and timeseries from coordinates (direct lookup only, no search)
            watershed_info, timeseries_data = api.get_timeseries_by_coordinates(latitude, longitude)
        else:
            raise Exception("Either UID or coordinates required for timeseries data")
        
        state["timeseries_raw"] = timeseries_data
        state["watershed_info"] = watershed_info
        
        print(f"✅ SUCCESS: Retrieved timeseries data for watershed {watershed_info.get('uid')}")
        
    except Exception as e:
        state["error"] = f"Timeseries fetch failed: {str(e)}"
        print(f"❌ ERROR: {state['error']}")
    
    return state

def merge_and_clip_spatial_data(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    NEW CRITICAL FUNCTION: Merge multi-region data and clip to exact boundary.
    Handles both vector union and raster mosaic.
    """
    
    if "error" in state:
        return state
    
    print("\n" + "="*70)
    print("🔗 MERGING & CLIPPING DATA")
    print("="*70)
    
    data_urls = state.get("data_urls", {})
    resolved = state.get("resolved_geometry", {})
    village_geom = resolved.get("village_geom")
    location_name = resolved.get("location_name")
    
    if not village_geom or (len(data_urls.get('vector', [])) == 0 and len(data_urls.get('raster', [])) == 0):
        state["error"] = "No data to merge"
        return state
    
    try:
        # VECTOR MERGING PATH
        if data_urls['vector']:
            print(f"\n📦 Vector merging: {len(data_urls['vector'])} layers")
            
            all_gdf_list = []
            for layer_info in data_urls['vector']:
                print(f"   Loading: {layer_info['tehsil']} - {layer_info['layer_name']}")
                gdf = gpd.read_file(layer_info['url'])
                all_gdf_list.append(gdf)
            
            # Union all GeoDataFrames
            print(f"   Unioning {len(all_gdf_list)} GeoDataFrames...")
            merged_gdf = gpd.GeoDataFrame(
                pd.concat(all_gdf_list, ignore_index=True),
                crs=all_gdf_list[0].crs
            )
            
            # Remove exact duplicates (same geometry)
            print(f"   Removing duplicates...")
            merged_gdf = merged_gdf.drop_duplicates(subset=['geometry'])
            print(f"   Before dedup: {len(pd.concat(all_gdf_list))}, After: {len(merged_gdf)}")
            
            # Clip to village boundary
            print(f"   Clipping to village boundary...")
            clipped_gdf = gpd.clip(merged_gdf, village_geom)
            
            print(f"   ✅ Result: {len(clipped_gdf)} features within {location_name}")
            
            # Save for CodeAct
            clipped_gdf.to_file('./exports/merged_clipped_data.geojson', driver='GeoJSON')
            state["merged_data"] = clipped_gdf
            state["merged_data_type"] = "vector"
            state["merged_data_path"] = './exports/merged_clipped_data.geojson'
        
        # RASTER MERGING PATH
        elif data_urls['raster']:
            print(f"\n🖼️  Raster merging: {len(data_urls['raster'])} layers")
            
            import rasterio
            from rasterio.merge import merge as rio_merge
            from rasterio.mask import mask as rio_mask
            from rasterio.vrt import WarpedVRT
            
            raster_paths = []
            
            # Download rasters (in real implementation, use /vsicurl/)
            for layer_info in data_urls['raster']:
                print(f"   Accessing: {layer_info['tehsil']} - {layer_info['layer_name']}")
                # For HTTP URLs, use /vsicurl/ prefix for GDAL
                url = layer_info['url']
                if url.startswith('http') and not url.startswith('/vsicurl/'):
                    url = f'/vsicurl/{url}'
                raster_paths.append(url)
            
            # Mosaic rasters
            if len(raster_paths) > 1:
                print(f"   Mosaicking {len(raster_paths)} rasters...")
                mosaicked, out_transform = rio_merge(raster_paths)
                
                with rasterio.open(raster_paths[0]) as src:
                    merged_profile = src.profile
                    merged_profile.update({
                        'height': mosaicked.shape[1],
                        'width': mosaicked.shape[2],
                        'transform': out_transform
                    })
                
                merged_path = './exports/merged_raster.tif'
                with rasterio.open(merged_path, 'w', **merged_profile) as dst:
                    dst.write(mosaicked)
            else:
                merged_path = raster_paths[0]
                print(f"   Single raster, using as-is")
            
            # Clip to village boundary
            print(f"   Clipping to village boundary...")
            with rasterio.open(merged_path) as src:
                try:
                    clipped, clipped_transform = rio_mask(
                        src,
                        [village_geom],
                        crop=True,
                        filled=True
                    )
                    
                    clipped_profile = src.profile
                    clipped_profile.update({
                        'height': clipped.shape[1],
                        'width': clipped.shape[2],
                        'transform': clipped_transform
                    })
                    
                    clipped_path = './exports/merged_clipped_raster.tif'
                    with rasterio.open(clipped_path, 'w', **clipped_profile) as dst:
                        dst.write(clipped)
                    
                    print(f"   ✅ Clipped raster saved: {clipped_path}")
                    
                except Exception as e:
                    print(f"   ⚠️  Clipping failed: {e}, using full raster")
                    clipped_path = merged_path
            
            state["merged_data_path"] = clipped_path
            state["merged_data_type"] = "raster"
        
        print(f"\n✅ MERGE & CLIP COMPLETE")
        
    except Exception as e:
        state["error"] = f"Merge and clip failed: {str(e)}"
        print(f"❌ ERROR: {state['error']}")
        import traceback
        traceback.print_exc()
    
    return state

def codeact_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    CodeAct node for complex analysis.
    Handles both spatial and timeseries data.
    """
    if "error" in state:
        return state
    
    print("\n" + "="*70)
    print("🤖 CODEACT AGENT")
    print("="*70)
    
    # Initialize CodeAct agent
    agent = CodeActAgent(gemini_api_key=GEMINI_API_KEY)
    
    # Get inputs
    query = state["user_query"]
    parsed = state.get("parsed", {})
    data_type = parsed.get("data_type_needed", "spatial")
    
    # Prepare data based on type
    if data_type == "timeseries":
        # Timeseries analysis
        timeseries_raw = state.get("timeseries_raw", {})
        watershed_info = state.get("watershed_info", {})
        
        # Simple timeseries formatting (can be enhanced with CodeAct if needed)
        result_data = {
            'watershed_uid': watershed_info.get('uid'),
            'data': timeseries_raw,
            'analysis': 'Timeseries data retrieved'
        }
        
        state["codeact_result"] = result_data
        state["used_codeact"] = False  # Simple pass-through
        
    else:
        # Spatial analysis (existing logic)
        available_layers = state.get("available_layers", {})
        
        # STEP 1: Generate plan
        plan = agent.generate_plan(query, available_layers)
        
        # STEP 2: Filter layers
        needed_layer_names = plan.get('data_needed', [])
        selected_layers = {
            'vector': [l for l in available_layers.get('vector', []) if l['layer_name'] in needed_layer_names],
            'raster': [l for l in available_layers.get('raster', []) if l['layer_name'] in needed_layer_names]
        }
        
        # Fallback: use all if none selected
        if not selected_layers['vector'] and not selected_layers['raster']:
            selected_layers = available_layers
        
        # STEP 3: Generate code
        code = agent.generate_code(query, plan, selected_layers)
        
        # STEP 4: Prepare execution context
        context = {
            'query_lat': parsed.get('latitude'),
            'query_lon': parsed.get('longitude'),
            'vector_layers': selected_layers.get('vector', []),
            'raster_layers': selected_layers.get('raster', []),
            'query': query
        }
        
        # STEP 5: Execute code
        execution_result = agent.execute_code(code, context)
        
        # STEP 6: Store result
        if execution_result['error']:
            state["error"] = f"CodeAct execution failed: {execution_result['error']}"
        else:
            state["codeact_result"] = execution_result['result']
        
        state["used_codeact"] = True
        state["execution_plan"] = plan
    
    return state


def format_response(state: Dict[str, Any]) -> Dict[str, Any]:
    """Format final response for all data types"""
    
    # Handle errors
    if "error" in state:
        state["response"] = f"❌ Error: {state['error']}"
        return state
    
    # Check if response already formatted
    if "response" in state:
        return state
    
    print("\n" + "="*70)
    print("📝 FORMATTING RESPONSE")
    print("="*70)
    
    query = state["user_query"]
    result_data = state.get("codeact_result")
    parsed = state.get("parsed", {})
    
    if not result_data:
        state["response"] = "Analysis completed but no results were generated."
        return state
    
    # Use LLM to format the response intelligently
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0.3,
        google_api_key=GEMINI_API_KEY
    )
    
    format_prompt = f"""You are a geospatial analyst presenting results to a user.

USER QUERY: "{query}"

ANALYSIS RESULTS:
{json.dumps(result_data, indent=2, default=str)}

LOCATION INFO:
{json.dumps(state.get('location_info', {}), indent=2, default=str)}

TASK: Format a clear, informative response that directly answers the user's question.

FORMATTING RULES:
1. Start with a direct answer to the question
2. Include key statistics and metrics
3. Use emojis for readability (🌊 water, 🌾 crops, 🏞️ land, 📊 stats, etc.)
4. For areas: use hectares (ha) and include totals
5. For counts: be specific with numbers
6. For timeseries: show trends and changes
7. Add context when helpful (e.g., "This represents X% of the total area")
8. Keep it concise but informative (5-10 key points)
9. If errors in data, mention them briefly
10. End with location context if relevant

AVOID:
- Raw JSON dumps
- Technical jargon without explanation
- Overly verbose explanations

Generate a user-friendly response:"""

    try:
        format_response = llm.invoke(format_prompt)
        state["response"] = format_response.content.strip()
        print(f"✅ Response formatted successfully")
    except Exception as e:
        print(f"⚠️  LLM formatting failed, using fallback: {e}")
        state["response"] = f"Analysis complete:\n{json.dumps(result_data, indent=2, default=str)}"
    
    return state

def resolve_geometry_v2(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    NEW CRITICAL FUNCTION: Resolve multi-region geometry.
    Finds which tehsils/watersheds a village spans.
    Returns exact boundary for clipping.
    """
    
    if "error" in state:
        return state
    
    print("\n" + "="*70)
    print("🗺️  GEOMETRY RESOLUTION")
    print("="*70)
    
    parsed = state["parsed"]
    location_type = parsed.get("location_type")
    location_name = parsed.get("location_name")
    latitude = parsed.get("latitude")
    longitude = parsed.get("longitude")
    district = parsed.get("district")
    
    try:
        if location_type == "village":
            # Load village boundaries from YOUR GeoJSON
            try:
                village_gdf = gpd.read_file('./village_boundaries.geojson')
            except:
                # Fallback: load from GEE if local file not available
                print("⚠️  Local village GeoJSON not found, loading from GEE...")
                village_fc = ee.FeatureCollection("projects/ext-datasets/assets/datasets/Village_pan_india")
                # This will be slow, but at least works
                village_gdf = geemap.ee_to_geopandas(village_fc)
            
            # Filter to specific village
            if district:
                village = village_gdf[
                    (village_gdf['village_name'].str.lower() == location_name.lower()) &
                    (village_gdf['district'].str.lower() == district.lower())
                ]
            else:
                village = village_gdf[village_gdf['village_name'].str.lower() == location_name.lower()]
            
            if len(village) == 0:
                state["error"] = f"Village '{location_name}' in {district} not found"
                print(f"❌ ERROR: {state['error']}")
                return state
            
            village_geom = village.iloc[0].geometry
            print(f"✅ Found village: {location_name}")
            print(f"   Area: {village_geom.area:.4f} square degrees")
        
        elif location_type == "coordinates":
            # Create small buffer around point
            from shapely.geometry import Point
            village_geom = Point(longitude, latitude).buffer(0.01)
            print(f"✅ Using buffer around: ({latitude}, {longitude})")
        
        elif location_type == "state":
            # Load state boundary
            state_fc = ee.FeatureCollection("projects/ext-datasets/assets/datasets/State_pan_india")
            state_gdf = geemap.ee_to_geopandas(state_fc)
            state_geom = state_gdf[state_gdf['state_name'].str.lower() == location_name.lower()].geometry.iloc[0]
            print(f"✅ Using state: {location_name}")
            village_geom = state_geom
        
        elif location_type == "tehsil":
            # Load tehsil boundary
            tehsil_fc = ee.FeatureCollection("projects/ext-datasets/assets/datasets/SOI_tehsil")
            tehsil_gdf = geemap.ee_to_geopandas(tehsil_fc)
            tehsil = tehsil_gdf[tehsil_gdf['name'].str.lower() == location_name.lower()].iloc[0]
            print(f"✅ Using tehsil: {location_name}")
            village_geom = tehsil.geometry
        
        # Find intersecting tehsils
        print(f"\n🔍 Finding intersecting tehsils...")
        tehsil_fc = ee.FeatureCollection("projects/ext-datasets/assets/datasets/SOI_tehsil")
        tehsil_gdf = geemap.ee_to_geopandas(tehsil_fc)
        
        intersecting_tehsils = tehsil_gdf[tehsil_gdf.geometry.intersects(village_geom)]
        
        tehsil_list = []
        for idx, row in intersecting_tehsils.iterrows():
            tehsil_list.append({
                'state': row.get('state_name', row.get('state')),
                'district': row.get('district_name', row.get('district')),
                'tehsil': row.get('name'),
                'geometry': row.geometry
            })
        
        print(f"✅ Found {len(tehsil_list)} intersecting tehsils:")
        for t in tehsil_list:
            print(f"   - {t['tehsil']} ({t['district']}, {t['state']})")
        
        # Find intersecting watersheds (optional)
        print(f"\n🔍 Finding intersecting watersheds...")
        watershed_fc = ee.FeatureCollection("projects/ext-datasets/assets/datasets/Watershed_pan_india")
        watershed_gdf = geemap.ee_to_geopandas(watershed_fc)
        
        intersecting_watersheds = watershed_gdf[watershed_gdf.geometry.intersects(village_geom)]
        watershed_list = intersecting_watersheds['uid'].tolist() if 'uid' in intersecting_watersheds.columns else []
        
        print(f"✅ Found {len(watershed_list)} intersecting watersheds")
        
        state["resolved_geometry"] = {
            'village_geom': village_geom,
            'tehsil_list': tehsil_list,
            'watershed_list': watershed_list,
            'location_name': location_name,
            'location_type': location_type
        }
        
        print(f"\n✅ GEOMETRY RESOLUTION COMPLETE")
        
    except Exception as e:
        state["error"] = f"Geometry resolution failed: {str(e)}"
        print(f"❌ ERROR: {state['error']}")
        import traceback
        traceback.print_exc()
    
    return state
# ============================================================================
# LANGGRAPH SETUP
# ============================================================================

def router_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    FIXED: Route based on analysis type, always include geometry resolution.
    """
    
    if "error" in state:
        print("🚫 Error detected, skipping to format")
        state["next_node"] = "format"
        return state
    
    print("\n" + "="*70)
    print("🚦 ROUTING DECISION")
    print("="*70)
    
    parsed = state["parsed"]
    analysis_type = parsed.get("analysis_type")
    
    print(f"   Analysis Type: {analysis_type}")
    
    # ALL queries go through geometry resolution first
    state["next_node"] = "resolve_geometry"
    
    print(f"   → Next: resolve_geometry")
    
    return state


def build_graph() -> StateGraph:
    """
    FIXED: Complete workflow with proper data collection phases.
    """
    graph = StateGraph(dict)
    
    # Add nodes
    graph.add_node("parse_intent", llm_intent_parser)
    graph.add_node("router", router_node)
    
    # NEW NODES (data collection)
    graph.add_node("resolve_geometry", resolve_geometry_v2)
    graph.add_node("fetch_spatial", fetch_spatial_layers_multiregion)
    graph.add_node("merge_clip", merge_and_clip_spatial_data)
    
    # Existing nodes (execution)
    graph.add_node("codeact", codeact_node)
    graph.add_node("format", format_response)
    
    # Add edges (LINEAR FLOW: no branching needed)
    graph.add_edge("parse_intent", "router")
    graph.add_edge("router", "resolve_geometry")          # NEW
    graph.add_edge("resolve_geometry", "fetch_spatial")   # NEW
    graph.add_edge("fetch_spatial", "merge_clip")         # NEW
    graph.add_edge("merge_clip", "codeact")
    graph.add_edge("codeact", "format")
    
    # Set entry and finish points
    graph.set_entry_point("parse_intent")
    graph.set_finish_point("format")
    
    return graph

# ============================================================================
# MAIN RUNNER
# ============================================================================

def run_agent(user_query: str):
    """Run the geospatial agent"""
    print("\n" + "="*70)
    print(f"🚀 STARTING GEOSPATIAL AGENT")
    print(f"📝 QUERY: {user_query}")
    print("="*70)
    
    # Build and compile graph
    graph = build_graph()
    app = graph.compile()
    
    # Run agent
    state = {"user_query": user_query}
    result_state = app.invoke(state)
    
    # Print result
    print("\n" + "="*70)
    print("✅ FINAL RESPONSE")
    print("="*70)
    print(result_state.get("response", "No response generated"))
    print("\n" + "="*70)
    
    return result_state


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    """
    Test queries demonstrating all API workflows:
    
    SPATIAL LAYER WORKFLOW (get_admin_details_by_latlon → get_generated_layer_urls):
    - Queries about features, areas, counts at a location
    
    TIMESERIES WORKFLOW (get_mwsid_by_latlon → get_mws_data):
    - Queries about trends, changes over time
    """
    
    test_queries = [
        # SPATIAL QUERIES (uses admin details → layer URLs workflow)
        # Using coordinates in BHILWARA district (the correct location)
        "Show me the water bodies near coordinates 25.31698754297551, 75.09702609349773",
        "What's the vegetation cover around coordinates 25.31, 75.09?",
        "How many drainage features are within 2km of coordinates 25.317, 75.097?",
        "Analyze land use distribution near coordinates 25.31698754297551, 75.09702609349773",
        
        # TIMESERIES QUERIES (uses watershed UID → timeseries workflow)
        "How did cropping intensity change from 2017 to 2023 at coordinates 25.31698754297551, 75.09702609349773?",
        "What was the precipitation trend from 2018 to 2022 near coordinates 25.317, 75.097?",
        "Show groundwater depletion between 2017-2023 at coordinates 25.31, 75.09",
    ]
    
    print("\n" + "="*70)
    print("🧪 GEOSPATIAL AGENT TEST SUITE")
    print("="*70)
    print("\nAvailable test queries:")
    for i, q in enumerate(test_queries, 1):
        query_type = "📊 TIMESERIES" if "change" in q.lower() or "trend" in q.lower() else "🗺️  SPATIAL"
        print(f"{i}. [{query_type}] {q}")
    
    print("\n" + "="*70)
    print("Running first query (spatial analysis)...")
    print("="*70)
    
    # Run first spatial query
    run_agent("How much cropland in Shirur, Dharwad, Karnataka has turned into built up since 2018? can you show me those regions?no")

