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
    
    # def find_nearest_watershed(self, latitude: float, longitude: float, 
    #                            max_distance_km: float = 10.0) -> Optional[Dict]:
    #     """
    #     Find nearest watershed with data using concentric spatial search.
    #     Useful when exact coordinates don't have watershed coverage.
        
    #     Parameters:
    #         latitude: Center latitude
    #         longitude: Center longitude
    #         max_distance_km: Maximum search radius in km
        
    #     Returns: Watershed info with 'distance_km' field, or None if not found
    #     """
    #     print(f"\n🔍 SEARCHING FOR NEAREST WATERSHED (max {max_distance_km}km)")
        
    #     # Try exact location first
    #     try:
    #         result = self.get_mwsid_by_latlon(latitude, longitude)
    #         result['distance_km'] = 0
    #         result['original_lat'] = latitude
    #         result['original_lon'] = longitude
    #         print(f"✅ Found watershed at exact location")
    #         return result
    #     except:
    #         print(f"⚠️  No watershed at exact location, expanding search...")
        
    #     # Concentric search
    #     search_radii = [0.5, 1.0, 2.0, 5.0, max_distance_km]
    #     geod = pyproj.Geod(ellps="WGS84")
        
    #     for radius_km in search_radii:
    #         # Search in 4 cardinal directions
    #         for angle in [0, 90, 180, 270]:  # N, E, S, W
    #             search_lon, search_lat, _ = geod.fwd(longitude, latitude, angle, radius_km * 1000)
                
    #             try:
    #                 result = self.get_mwsid_by_latlon(search_lat, search_lon)
    #                 result['distance_km'] = radius_km
    #                 result['original_lat'] = latitude
    #                 result['original_lon'] = longitude
    #                 print(f"✅ Found watershed {radius_km}km away at ({search_lat:.5f}, {search_lon:.5f})")
    #                 return result
    #             except:
    #                 continue
        
    #     print(f"❌ No watershed found within {max_distance_km}km")
    #     return None


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
    
    prompt = f"""Extract structured information from this geospatial query.

USER QUERY: "{user_query}"

CRITICAL: Map to correct CoreStack data product:

1. "Cropping intensity over years" → data_type="spatial_vector", layer="cropping_intensity_vector"
   (NOT timeseries! It has yearly columns: cropping_intensity_2017, 2018, ...)

2. "Surface water over years/seasons" → data_type="spatial_vector", layer="surface_water_bodies_vector"
   (Polygon water bodies with seasonal attributes, NOT watershed timeseries)

3. "Tree cover loss" → data_type="change_raster", layer="change_tree_cover_loss_raster"
   (Pre-computed 2017-2022 composite, mask to loss classes)

4. "Cropland to built-up" → data_type="change_raster", layer="change_urbanization_raster"
   (Filter to class 3: Trees/Crops→Built-up)

5. "Drought in tehsils" → data_type="spatial_vector", layer="drought_frequency_vector"
   (Severity: Severe/Moderate/Mild, aggregate to tehsil)

Return JSON:
{{
  "latitude": <float or null>,
  "longitude": <float or null>,
  "location_name": <string or null>,
  "location_type": "village" | "tehsil" | "state" | "coordinates",
  "district": <string or null>,
  "metric": <string>,
  "temporal": <bool>,
  "start_year": <int or null>,
  "end_year": <int or null>,
  "data_type_needed": "spatial_vector" | "change_raster" | "timeseries",
  "analysis_type": "temporal_vector" | "change_detection" | "state_aggregation" | "spatial_summary",
  "recommended_layer": "cropping_intensity_vector" | "surface_water_bodies_vector" | 
                       "change_tree_cover_loss_raster" | "change_urbanization_raster" | 
                       "drought_frequency_vector" | "other",
  "notes": <string with caveats if needed>
}}

RULES:
- If query mentions "years" or "trend" AND metric is cropping/water → data_type="spatial_vector" (NOT timeseries)
- If query mentions "change", "loss", "gain", "conversion" → data_type="change_raster"
- If query mentions state + drought → data_type="spatial_vector", analysis_type="state_aggregation"
- Only use timeseries for watershed-level water balance (rare)
"""

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
    run_agent("How much cropland in Shirur, Dharwad, Karnataka has turned into built up since 2018? can you show me those regions?no")


"""One more thing. I have this geogson of village boundries. Can this help with boundry level flexibility? I need you to spend time understnading the data products we have access to and putting them elegantly into a good workflow that we discussed on top. Understood? """