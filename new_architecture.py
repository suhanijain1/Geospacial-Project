"""
New Clean Architecture for Geospatial Agent
Merges LangGraph orchestration with CodeAct execution
Uses Gemini for planning and code generation with clear API tracking

================================================================================
CORESTACK API DOCUMENTATION (from Swagger)
================================================================================

Base URL: https://geoserver.core-stack.org/api/v1/
Authentication: X-API-Key header

API ENDPOINTS & WORKFLOWS:
---------------------------

┌─────────────────────────────────────────────────────────────────────────┐
│ WORKFLOW 1: SPATIAL LAYER ACCESS (for spatial analysis queries)        │
└─────────────────────────────────────────────────────────────────────────┘

Step 1: GET /get_admin_details_by_latlon/
   Input:  latitude (float), longitude (float)
   Output: {"State": str, "District": str, "Tehsil": str}
   Use:    Get administrative boundaries from coordinates
   
Step 2: GET /get_generated_layer_urls/
   Input:  state (str), district (str), tehsil (str)
   Output: List of layer objects with:
           - layer_name: str (e.g., "SOGE", "Drainage", "NDVI")
           - layer_url: str (GeoJSON or GeoTIFF URL)
           - layer_type: str ("vector" or "raster")
   Use:    Get all available spatial layers for the location
   
COUPLING: Must call get_admin_details_by_latlon BEFORE get_generated_layer_urls
USE CASE: "Show water bodies near X", "What's the land use around Y"

┌─────────────────────────────────────────────────────────────────────────┐
│ WORKFLOW 2: WATERSHED TIMESERIES DATA (for temporal analysis queries)  │
└─────────────────────────────────────────────────────────────────────────┘

Step 1: GET /get_mwsid_by_latlon/
   Input:  latitude (float), longitude (float)
   Output: {"uid": str, "state": str, "district": str, "tehsil": str}
   Use:    Get watershed unique identifier from coordinates
   Note:   Only for timeseries! NOT for spatial layers!
   
Step 2: GET /get_mws_data/
   Input:  uid (str)
   Output: Timeseries data object with year/value/source arrays
   Use:    Get temporal metrics (precipitation, groundwater, etc.)
   
COUPLING: Must call get_mwsid_by_latlon BEFORE get_mws_data
USE CASE: "How did X change from 2017 to 2023", "Show precipitation trends"

┌─────────────────────────────────────────────────────────────────────────┐
│ IMPORTANT: These are SEPARATE, INDEPENDENT workflows!                  │
│                                                                         │
│ ✅ For spatial analysis → Use Workflow 1 (admin details → layers)      │
│ ✅ For timeseries → Use Workflow 2 (watershed UID → timeseries)        │
│ ❌ Don't mix them! get_mwsid_by_latlon ≠ get_admin_details_by_latlon  │
└─────────────────────────────────────────────────────────────────────────┘

================================================================================
ARCHITECTURE OVERVIEW
================================================================================

LangGraph Workflow:
  parse_intent → router → [fetch_spatial OR fetch_timeseries] → codeact → format

1. parse_intent: Extract location, metric, time period, data type needed
2. router: Decide between spatial or timeseries workflow
3. fetch_spatial: Call Workflow 1 (admin → layers) for spatial data
4. fetch_timeseries: Call Workflow 2 (watershed → timeseries) for temporal data
5. codeact: Generate and execute Python code for analysis
6. format: Create user-friendly response with LLM

Key Features:
- Proper API coupling (no mixing workflows)
- Clear logging with 📡 API calls and 📦 responses
- CodeAct planning phase (human-readable steps)
- Automatic geocoding for place names
- Fallback search for nearby watersheds
- Error handling and graceful degradation

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
import geopandas as gpd
import rasterio
from rasterio.mask import mask
from shapely.geometry import Point, box, shape, Polygon
from shapely.ops import transform as shp_transform
import pyproj
from pyproj import CRS, Transformer
from geopy.geocoders import Nominatim
from geopy.distance import geodesic as geopy_geodesic
import numpy as np

# Load environment
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
CORE_STACK_API_KEY = os.getenv("CORE_STACK_API_KEY")

if not GEMINI_API_KEY or not CORE_STACK_API_KEY:
    raise ValueError("GEMINI_API_KEY and CORE_STACK_API_KEY must be set in environment")

# API Configuration
BASE_URL = "https://geoserver.core-stack.org/api/v1/"
API_HEADERS = {"X-API-Key": CORE_STACK_API_KEY}


# ============================================================================
# CORESTACK API WRAPPER FUNCTIONS (Following Swagger Spec)
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
    
    def find_nearest_watershed(self, latitude: float, longitude: float, 
                               max_distance_km: float = 10.0) -> Optional[Dict]:
        """
        Find nearest watershed with data using concentric spatial search.
        Useful when exact coordinates don't have watershed coverage.
        
        Parameters:
            latitude: Center latitude
            longitude: Center longitude
            max_distance_km: Maximum search radius in km
        
        Returns: Watershed info with 'distance_km' field, or None if not found
        """
        print(f"\n🔍 SEARCHING FOR NEAREST WATERSHED (max {max_distance_km}km)")
        
        # Try exact location first
        try:
            result = self.get_mwsid_by_latlon(latitude, longitude)
            result['distance_km'] = 0
            result['original_lat'] = latitude
            result['original_lon'] = longitude
            print(f"✅ Found watershed at exact location")
            return result
        except:
            print(f"⚠️  No watershed at exact location, expanding search...")
        
        # Concentric search
        search_radii = [0.5, 1.0, 2.0, 5.0, max_distance_km]
        geod = pyproj.Geod(ellps="WGS84")
        
        for radius_km in search_radii:
            # Search in 4 cardinal directions
            for angle in [0, 90, 180, 270]:  # N, E, S, W
                search_lon, search_lat, _ = geod.fwd(longitude, latitude, angle, radius_km * 1000)
                
                try:
                    result = self.get_mwsid_by_latlon(search_lat, search_lon)
                    result['distance_km'] = radius_km
                    result['original_lat'] = latitude
                    result['original_lon'] = longitude
                    print(f"✅ Found watershed {radius_km}km away at ({search_lat:.5f}, {search_lon:.5f})")
                    return result
                except:
                    continue
        
        print(f"❌ No watershed found within {max_distance_km}km")
        return None


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
            
            # Calculate statistics
            stats = {
                'feature_count': len(gdf),
                'total_area_ha': gdf.geometry.area.sum() / 10000 if len(gdf) > 0 else 0,
                'columns': list(gdf.columns),
                'attributes': {},
                'sample_features': []
            }
            
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
            url: GeoTIFF URL
            bounds: (minx, miny, maxx, maxy) bounding box
            circle_geom_4326: Shapely geometry for masking
        
        Returns:
            Dict with statistics
        """
        print(f"\n📡 PROCESSING RASTER: {url[:100]}...")
        
        try:
            with rasterio.open(url) as src:
                # Get raster info
                print(f"📦 RASTER INFO: {src.width}x{src.height}, CRS: {src.crs}")
                
                # Read data (windowed if bounds provided)
                if bounds:
                    window = src.window(*bounds)
                    data = src.read(1, window=window)
                elif circle_geom_4326:
                    # Mask with geometry
                    out_image, out_transform = mask(src, [circle_geom_4326], crop=True)
                    data = out_image[0]
                else:
                    # Read full raster
                    data = src.read(1)
                
                # Filter nodata
                nodata = src.nodata
                if nodata is not None:
                    valid_data = data[data != nodata]
                else:
                    valid_data = data.flatten()
                
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
                else:
                    stats = {'error': 'No valid data in raster'}
                
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
            model="gemini-2.0-flash",
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
6. For raster data: use process_raster_url()
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

EXAMPLE CODE STRUCTURE (RECOMMENDED APPROACH):
```python
# Use find_layer helper for robust layer matching
target_layer = find_layer(vector_layers, 'Cropping Intensity')

if target_layer:
    # Process the layer
    stats = SpatialDataProcessor.process_vector_url(
        target_layer['layer_url'],
        point=(query_lat, query_lon),
        buffer_km=5.0
    )
    
    # Access the results:
    # - stats['feature_count'] → number of features
    # - stats['columns'] → list of all column names
    # - stats['attributes']['doubly_cropped_area_2023']['sum'] → total area
    # - stats['sample_features'][0]['doubly_cropped_area_2023'] → first feature's value
    
    result = {{
        'total_area': stats['attributes']['doubly_cropped_area_2023']['sum']
    }}
else:
    result = {{'error': 'Layer not found'}}
        target_layer = layer
        break

if target_layer:
    point = (query_lat, query_lon) if query_lat and query_lon else None
    stats = SpatialDataProcessor.process_vector_url(target_layer['layer_url'], point, buffer_km=1.0)
    
    result = {{
        'layer': target_layer['layer_name'],
        'feature_count': stats.get('feature_count', 0),
        'total_area_ha': stats.get('total_area_ha', 0)
    }}
else:
    result = {{'error': 'Required layer not found'}}
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
    """Parse user query to extract intent and parameters"""
    print("\n" + "="*70)
    print("🧠 PARSING USER INTENT")
    print("="*70)
    
    user_query = state["user_query"]
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0,
        google_api_key=GEMINI_API_KEY
    )
    
    prompt = f"""Extract structured information from this geospatial query.

USER QUERY: "{user_query}"

Extract:
1. Location (coordinates, place name, district, or UID)
2. Metric/analysis requested
3. Time period if mentioned
4. Data type needed (timeseries/spatial/both)

Return JSON:
{{
  "latitude": <float or null>,
  "longitude": <float or null>,
  "location_name": <string or null>,
  "uid": <string or null>,
  "metric_text": <string>,
  "start_year": <int or null>,
  "end_year": <int or null>,
  "data_type_needed": "timeseries|spatial|both",
  "analysis_type": "spatial_summary|timeseries|complex|simple_query"
}}

MULTIMODAL QUERY HANDLING:
- If BOTH coordinates AND place name are mentioned, extract BOTH
- Coordinates go to latitude/longitude fields
- Place name goes to location_name field
- The agent will reconcile any mismatches later

OTHER RULES:
- If query mentions years/timeline/trends → data_type_needed="timeseries"
- If query mentions "show", "count", "area", "features" → data_type_needed="spatial"
- Keep metric_text as user's original phrasing (e.g., "water bodies", "vegetation cover")
- Extract all information provided, don't drop anything

EXAMPLES:
- "Show water in Bundi at 25.31, 75.09" → lat=25.31, lon=75.09, location_name="Bundi" (keep both!)
- "Show water in Delhi" → lat=null, lon=null, location_name="Delhi"
- "Water at 25.31, 75.09" → lat=25.31, lon=75.09, location_name=null"""

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
                print(f"🗺️  Geocoded '{parsed['location_name']}' → ({coords[0]:.5f}, {coords[1]:.5f})")
        
        # Handle multimodal queries (both coordinates AND location name provided)
        if parsed.get('latitude') and parsed.get('longitude') and parsed.get('location_name'):
            print(f"\n⚠️  MULTIMODAL QUERY DETECTED:")
            print(f"   User mentioned: '{parsed['location_name']}'")
            print(f"   User provided coordinates: ({parsed['latitude']}, {parsed['longitude']})")
            print(f"   → Using coordinates for data fetching (more precise)")
            print(f"   → Location name kept for context in response")
            parsed['user_specified_location'] = parsed['location_name']
        
        state["parsed"] = parsed
        print(f"\n📋 PARSED INTENT:")
        print(f"   Data Type: {parsed.get('data_type_needed')}")
        print(f"   Analysis: {parsed.get('analysis_type')}")
        
        # Format location display
        location_display = parsed.get('location_name')
        if not location_display and parsed.get('latitude') and parsed.get('longitude'):
            location_display = f"({parsed['latitude']}, {parsed['longitude']})"
        print(f"   Location: {location_display}")
        print(f"   Metric: {parsed.get('metric_text')}")
        
    except Exception as e:
        state["error"] = f"Intent parsing failed: {str(e)}"
        print(f"❌ ERROR: {state['error']}")
    
    return state


def fetch_spatial_layers(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fetch available spatial layers for the location.
    Uses COUPLED API workflow: get_admin_details_by_latlon → get_generated_layer_urls
    """
    if "error" in state:
        return state
    
    print("\n" + "="*70)
    print("📡 FETCHING SPATIAL LAYERS")
    print("="*70)
    
    parsed = state["parsed"]
    latitude = parsed.get("latitude")
    longitude = parsed.get("longitude")
    
    if not latitude or not longitude:
        state["error"] = "Coordinates required for spatial analysis"
        print(f"❌ ERROR: {state['error']}")
        return state
    
    try:
        # Use coupled API workflow
        admin_info, layers = api.get_spatial_layers_by_coordinates(latitude, longitude)
        
        # Categorize layers by type
        vector_layers = [l for l in layers if l.get('layer_type') == 'vector']
        raster_layers = [l for l in layers if l.get('layer_type') == 'raster']
        
        state["available_layers"] = {
            'vector': vector_layers,
            'raster': raster_layers,
            'all': layers
        }
        state["location_info"] = admin_info
        
        print(f"\n✅ SUCCESS: Retrieved {len(vector_layers)} vector + {len(raster_layers)} raster layers")
        
    except Exception as e:
        state["error"] = str(e)
        print(f"❌ ERROR: {state['error']}")
    
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
            # Get watershed and timeseries from coordinates
            # Try exact location first, then search nearby
            try:
                watershed_info, timeseries_data = api.get_timeseries_by_coordinates(latitude, longitude)
            except:
                print("⚠️  No watershed at exact location, searching nearby...")
                watershed_info = api.find_nearest_watershed(latitude, longitude, max_distance_km=10.0)
                
                if watershed_info:
                    uid = watershed_info.get('uid')
                    timeseries_data = api.get_mws_data(uid)
                    
                    # Add distance info to parsed state
                    if watershed_info.get('distance_km', 0) > 0:
                        parsed['distance_to_watershed_km'] = watershed_info['distance_km']
                        parsed['original_latitude'] = latitude
                        parsed['original_longitude'] = longitude
                else:
                    raise Exception("No watershed found within 10km")
        else:
            raise Exception("Either UID or coordinates required for timeseries data")
        
        state["timeseries_raw"] = timeseries_data
        state["watershed_info"] = watershed_info
        
        print(f"✅ SUCCESS: Retrieved timeseries data for watershed {watershed_info.get('uid')}")
        
    except Exception as e:
        state["error"] = f"Timeseries fetch failed: {str(e)}"
        print(f"❌ ERROR: {state['error']}")
    
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


# ============================================================================
# LANGGRAPH SETUP
# ============================================================================

def router_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Route to appropriate processing path based on data type needed.
    Routes: timeseries, spatial, or both
    """
    if "error" in state:
        state["next_node"] = "format"
        return state
    
    parsed = state["parsed"]
    data_type = parsed.get("data_type_needed", "spatial")
    
    print("\n" + "="*70)
    print(f"🔀 ROUTING DECISION: {data_type}")
    print("="*70)
    
    if data_type == "timeseries":
        state["next_node"] = "fetch_timeseries"
    elif data_type in ["spatial", "vector", "raster", "both"]:
        state["next_node"] = "fetch_spatial"
    else:
        # Default to spatial for safety
        state["next_node"] = "fetch_spatial"
    
    print(f"➡️  Next node: {state['next_node']}")
    return state


def build_graph() -> StateGraph:
    """Build the LangGraph workflow with router"""
    graph = StateGraph(dict)
    
    # Add nodes
    graph.add_node("parse_intent", llm_intent_parser)
    graph.add_node("router", router_node)
    graph.add_node("fetch_spatial", fetch_spatial_layers)
    graph.add_node("fetch_timeseries", fetch_timeseries_data)
    graph.add_node("codeact", codeact_node)
    graph.add_node("format", format_response)
    
    # Add edges
    graph.add_edge("parse_intent", "router")
    
    # Router conditional edges
    graph.add_conditional_edges(
        "router",
        lambda x: x.get("next_node", "format"),
        {
            "fetch_spatial": "fetch_spatial",
            "fetch_timeseries": "fetch_timeseries",
            "format": "format"
        }
    )
    
    # Both paths lead to CodeAct
    graph.add_edge("fetch_spatial", "codeact")
    graph.add_edge("fetch_timeseries", "codeact")
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
    run_agent("for jharkhand, please provide total degraded land area in hectares as a histogram over the years 2020 to 2023")
