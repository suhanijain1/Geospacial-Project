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
GEE_PROJECT = os.getenv("GEE_PROJECT", "apt-achievment-453417-h6")

if not GEMINI_API_KEY or not CORE_STACK_API_KEY:
    raise ValueError("GEMINI_API_KEY and CORE_STACK_API_KEY must be set in environment")

# API Configuration
BASE_URL = "https://geoserver.core-stack.org/api/v1/"
API_HEADERS = {"X-API-Key": CORE_STACK_API_KEY}

# Initialize Earth Engine
try:
    import ee
    ee.Initialize(project=GEE_PROJECT)
    print(f"✅ Earth Engine initialized with project: {GEE_PROJECT}")
except Exception as e:
    print(f"⚠️  Earth Engine initialization warning: {e}")


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

def geocode_location(location_name: str, district: str = None, state: str = None) -> Optional[Tuple[float, float]]:
    """Geocode a location name to coordinates (latitude, longitude)"""
    try:
        geolocator = Nominatim(user_agent="geospatial_agent")
        
        # Build query with context for disambiguation
        if district and state:
            query = f"{location_name}, {district}, {state}, India"
        elif state:
            query = f"{location_name}, {state}, India"
        else:
            query = f"{location_name}, India"
        
        print(f"🔍 Geocoding: {query}")
        location = geolocator.geocode(query)
        
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
# LAYER DESCRIPTIONS LOADER
# ============================================================================

def load_layer_descriptions() -> str:
    """
    Load layer descriptions from CSV for LLM context
    """
    try:
        csv_path = os.path.join(os.path.dirname(__file__), 'layer_descriptions.csv')
        import csv
        
        descriptions = []
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                descriptions.append(
                    f"- {row['layer_name']}: {row['layer_description'][:200]}..."
                )
        
        return "\n".join(descriptions)
    except Exception as e:
        print(f"⚠️  Could not load layer descriptions: {e}")
        return """
CoreStack provides:
- land_use_land_cover_raster: LULC with 12 classes including cropping intensity (classes 8-11)
- change_tree_cover_loss_raster: Pre-computed tree loss 2017-2022
- change_tree_cover_gain_raster: Pre-computed tree gain 2017-2022
- change_urbanization_raster: Built-up expansion 2017-2022 (class 3 = Crops→BuiltUp)
- change_cropping_reduction_raster: Cropland degradation 2017-2022
- change_cropping_intensity_raster: Cropping intensity transitions 2017-2022
- cropping_intensity_vector: Vector with yearly cropping intensity values
- surface_water_bodies_vector: Water bodies with seasonal availability
- drought_frequency_vector: Drought severity mapping
- water_balance: Fortnightly timeseries at watershed level
"""


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
    """Parse user query using LLM with full CoreStack layer knowledge"""
    print("\n" + "="*70)
    print("🧠 PARSING USER INTENT (LLM-Driven)")
    print("="*70)
    
    user_query = state["user_query"]
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0,
        google_api_key=GEMINI_API_KEY
    )
    
    # Load layer descriptions for LLM context
    layer_descriptions = load_layer_descriptions()
    
    prompt = f"""You are a geospatial data routing agent for CoreStack API.

USER QUERY: "{user_query}"

AVAILABLE CORESTACK LAYERS:
{layer_descriptions}

TASK: Analyze this query and extract:

1. LOCATION INFORMATION:
   - Type: village|tehsil|district|state|coordinates
   - Name (if place name mentioned)
   - Coordinates (if lat/lon mentioned)
   - Does this location likely span multiple administrative boundaries? 
     (Village names often span multiple tehsils - set multi_region_likely: true for villages)

2. METRIC/ANALYSIS:
   - What is being measured? (cropping intensity, tree cover, water, drought, etc.)
   - Is this a CHANGE DETECTION query? (keywords: "change", "loss", "gain", "since", "turned into")
   - Is this a TEMPORAL TREND query? (keywords: "over years", "trends", "how has X changed")
   - Time period (years mentioned)

3. DATA SOURCE ROUTING:
   - Which CoreStack layers are most relevant? Pick from the layer descriptions above.
   - Prioritize PRE-COMPUTED layers when available:
     a) CHANGE DETECTION LAYERS (2017-2022): change_tree_cover_loss_raster, change_urbanization_raster, etc.
     b) TEMPORAL VECTOR LAYERS: cropping_intensity_vector (has yearly attributes), surface_water_bodies_vector
     c) TIMESERIES API: water_balance, precipitation (via get_mws_data at watershed level)
     d) STATIC SPATIAL: SOGE, aquifer, drought_frequency_vector
   
   - Routing decision:
     * If pre-computed change layer exists → "corestack_spatial"
     * If vector has temporal attributes → "corestack_spatial"
     * If needs watershed timeseries (water_balance, precipitation) → "corestack_timeseries"
     * Default → "corestack_spatial"

4. MULTI-REGION DETECTION:
   - If location_type is "village" → set multi_region_likely: true (villages often span tehsils)
   - If location_type is "coordinates" → set multi_region_likely: false
   - If location_type is "tehsil" or higher → set multi_region_likely: false

Return ONLY valid JSON:
{{
  "latitude": <float or null>,
  "longitude": <float or null>,
  "location_name": <string or null>,
  "district_name": <string or null>,
  "state_name": <string or null>,
  "location_type": "village|tehsil|district|state|coordinates",
  "metric_text": <string>,
  "start_year": <int or null>,
  "end_year": <int or null>,
  "is_change_detection": <boolean>,
  "is_temporal_trend": <boolean>,
  "target_layers": ["layer_name_1", "layer_name_2"],
  "data_source_type": "corestack_spatial|corestack_timeseries|hybrid",
  "multi_region_likely": <boolean>,
  "reasoning": "Brief explanation of routing decision"
}}

EXAMPLES:

Query: "Cropping intensity in Shirur village, Dharwad over the years"
→ {{
  "location_name": "Shirur",
  "district_name": "Dharwad",
  "state_name": "Karnataka",
  "location_type": "village",
  "metric_text": "cropping intensity",
  "is_temporal_trend": true,
  "target_layers": ["cropping_intensity_vector"],
  "data_source_type": "corestack_spatial",
  "multi_region_likely": true,
  "reasoning": "cropping_intensity_vector has yearly attributes; villages often span tehsils"
}}

Query: "Tree cover loss since 2018 in Shirur, Dharwad, Karnataka"
→ {{
  "location_name": "Shirur",
  "location_type": "village",
  "metric_text": "tree cover loss",
  "start_year": 2018,
  "is_change_detection": true,
  "target_layers": ["change_tree_cover_loss_raster"],
  "data_source_type": "corestack_spatial",
  "multi_region_likely": true,
  "reasoning": "Pre-computed change layer available for 2017-2022, masks to loss classes"
}}

Query: "Cropland to built-up in Shirur since 2018"
→ {{
  "location_name": "Shirur",
  "location_type": "village",
  "metric_text": "cropland to built-up conversion",
  "start_year": 2018,
  "is_change_detection": true,
  "target_layers": ["change_urbanization_raster"],
  "data_source_type": "corestack_spatial",
  "multi_region_likely": true,
  "reasoning": "change_urbanization_raster class 3 = Crops→BuiltUp"
}}

Query: "Surface water availability over years in Shirur"
→ {{
  "location_name": "Shirur",
  "location_type": "village",
  "metric_text": "surface water availability",
  "is_temporal_trend": true,
  "target_layers": ["surface_water_bodies_vector"],
  "data_source_type": "corestack_spatial",
  "multi_region_likely": true,
  "reasoning": "surface_water_bodies_vector has seasonal availability and area over years"
}}

Query: "Drought affected tehsils in Jharkhand"
→ {{
  "location_name": "Jharkhand",
  "location_type": "state",
  "metric_text": "drought frequency",
  "target_layers": ["drought_frequency_vector"],
  "data_source_type": "corestack_spatial",
  "multi_region_likely": false,
  "reasoning": "State-level query using drought_frequency_vector"
}}

Query: "Water balance trends at 15.23, 75.27"
→ {{
  "latitude": 15.23,
  "longitude": 75.27,
  "location_type": "coordinates",
  "metric_text": "water balance",
  "is_temporal_trend": true,
  "data_source_type": "corestack_timeseries",
  "multi_region_likely": false,
  "reasoning": "Timeseries API provides fortnightly water balance per watershed"
}}
"""

    try:
        response = llm.invoke(prompt)
        content = response.content
        
        # Extract JSON from response
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', content, re.DOTALL)
        if json_match:
            parsed = json.loads(json_match.group())
        else:
            parsed = json.loads(content)
        
        state["parsed"] = parsed
        
        # Geocode location name if provided but no coordinates
        if parsed.get("location_name") and not parsed.get("latitude"):
            coords = geocode_location(
                parsed["location_name"],
                district=parsed.get("district_name"),
                state=parsed.get("state_name")
            )
            if coords:
                state["parsed"]["latitude"], state["parsed"]["longitude"] = coords
                print(f"📍 Geocoded '{parsed['location_name']}' to {coords}")
        
        print(f"\n✅ LLM Routing Decision:")
        print(f"   Location: {parsed.get('location_name', 'N/A')} ({parsed.get('location_type')})")
        print(f"   Coordinates: ({parsed.get('latitude')}, {parsed.get('longitude')})")
        print(f"   Metric: {parsed.get('metric_text')}")
        print(f"   Target Layers: {parsed.get('target_layers', [])}")
        print(f"   Data Source: {parsed.get('data_source_type')}")
        print(f"   Multi-Region Likely: {parsed.get('multi_region_likely', False)}")
        print(f"   Reasoning: {parsed.get('reasoning', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Intent parsing failed: {e}")
        state["error"] = f"Intent parsing failed: {str(e)}"
    
    return state


def resolve_geometry(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Resolve exact geometry for multi-region locations using microwatershed boundaries.
    Only runs if LLM flagged multi_region_likely=True.
    """
    
    if "error" in state:
        return state
    
    parsed = state["parsed"]
    
    # Skip if not multi-region
    if not parsed.get("multi_region_likely", False):
        print("\n⏭️  Skipping geometry resolution - single region query")
        return state
    
    print("\n" + "="*70)
    print("🗺️  RESOLVING MULTI-REGION GEOMETRY")
    print("="*70)
    
    location_name = parsed.get("location_name")
    location_type = parsed.get("location_type")
    
    if not location_name:
        print("⚠️  No location name for geometry resolution")
        return state
    
    try:
        if location_type == "village":
            print(f"🔍 Looking up village: {location_name}")
            district = parsed.get('district_name')
            state_name = parsed.get('state_name')
            latitude = parsed.get('latitude')
            longitude = parsed.get('longitude')
            
            # Use local microwatershed boundaries instead of GEE
            import geopandas as gpd
            from shapely.geometry import Point
            from shapely.ops import transform as shp_transform
            import pyproj
            
            mws_path = "/Users/suhanijain/Desktop/sem 7/Geospacial agent/agent-env/Microwatershed_boundries_v2.geojson"
            
            print(f"📂 Loading microwatershed boundaries from local file...")
            # Load with low_memory=False to handle large file
            mws_gdf = gpd.read_file(mws_path)
            print(f"✅ Loaded {len(mws_gdf)} microwatershed polygons")
            
            # Try to find village by name in microwatershed attribute data
            # MWS data may have village_name, village, or similar columns
            village_cols = [col for col in mws_gdf.columns if 'village' in col.lower()]
            
            village_geom = None
            if village_cols:
                # Try to find village by name
                for col in village_cols:
                    matches = mws_gdf[mws_gdf[col].str.contains(location_name, case=False, na=False)]
                    if len(matches) > 0:
                        print(f"   ✅ Found {len(matches)} microwatersheds in village '{location_name}' using column '{col}'")
                        village_geom = matches.unary_union
                        break
            
            # Fallback: Use coordinate-based buffer to approximate village area
            if village_geom is None and latitude and longitude:
                print(f"   ⚠️  Village name not found in MWS data. Using coordinate buffer...")
                center = Point(longitude, latitude)
                
                # Create 2km buffer around coordinates (typical village size)
                wgs84 = pyproj.CRS('EPSG:4326')
                utm = pyproj.CRS('EPSG:32643')  # India UTM
                project_to_utm = pyproj.Transformer.from_crs(wgs84, utm, always_xy=True).transform
                project_to_wgs = pyproj.Transformer.from_crs(utm, wgs84, always_xy=True).transform
                
                center_utm = shp_transform(project_to_utm, center)
                buffer_utm = center_utm.buffer(2000)  # 2km radius
                village_geom = shp_transform(project_to_wgs, buffer_utm)
                print(f"   📍 Created 2km buffer around ({latitude:.4f}, {longitude:.4f})")
            
            if village_geom is None:
                print(f"⚠️  Village '{location_name}' not found in microwatershed boundaries")
                print(f"   → Will fetch data at TEHSIL level and aggregate across all microwatersheds")
                state["geometry_info"] = {
                    "type": "village_fallback_to_tehsil",
                    "name": location_name,
                    "note": "Village boundary not available - using tehsil-level MWS aggregation"
                }
                return state
            
            # Get village geometry bounds
            minx, miny, maxx, maxy = village_geom.bounds
            
            # Find all tehsils intersecting with village using coordinate-based API lookup
            # Sample points within village geometry to find all intersecting admin units
            import numpy as np
            
            # Sample points in a grid across village area
            num_samples = 5  # 5x5 grid
            lons = np.linspace(minx, maxx, num_samples)
            lats = np.linspace(miny, maxy, num_samples)
            
            intersecting_admin = set()
            for lat in lats:
                for lon in lons:
                    point = Point(lon, lat)
                    if village_geom.contains(point):
                        # Get admin details for this point
                        admin = api.get_admin_details_by_latlon(lat, lon)
                        admin_key = f"{admin['State']}|{admin['District']}|{admin['Tehsil']}"
                        intersecting_admin.add(admin_key)
            
            # Parse admin units from coordinate sampling
            admin_units = []
            for admin_key in intersecting_admin:
                parts = admin_key.split('|')
                admin_units.append({
                    'State': parts[0],
                    'District': parts[1],
                    'Tehsil': parts[2]
                })
            
            print(f"✅ Found {len(admin_units)} intersecting admin units:")
            for unit in admin_units:
                print(f"   - {unit['Tehsil']}, {unit['District']}, {unit['State']}")
            
            state["geometry_info"] = {
                "type": "village",
                "name": location_name,
                "geometry": village_geom,
                "intersecting_units": admin_units,
                "multi_region": len(admin_units) > 1
            }
        
        elif location_type == "tehsil":
            # For tehsil-level queries, could get tehsil boundary
            # But usually not needed for multi-region handling
            pass
    
    except Exception as e:
        print(f"⚠️  Geometry resolution failed: {e}")
        import traceback
        traceback.print_exc()
        print("   Falling back to coordinate-based lookup")
    
    return state
def fetch_spatial_layers(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fetch available spatial layers for the location.
    Uses COUPLED API workflow: get_admin_details_by_latlon → get_generated_layer_urls
    """
    if "error" in state:
        return state
    
    print("\n" + "="*70)
    print("📡 FETCHING SPATIAL LAYERS (Target-Filtered)")
    print("="*70)
    
    parsed = state["parsed"]
    latitude = parsed.get("latitude")
    longitude = parsed.get("longitude")
    target_layers = parsed.get("target_layers", [])
    geometry_info = state.get("geometry_info")
    
    if not latitude or not longitude:
        state["error"] = "Coordinates required for spatial analysis"
        print(f"❌ ERROR: {state['error']}")
        return state
    
    try:
        all_layers = []
        
        # Determine admin units to query
        if geometry_info and geometry_info.get("multi_region"):
            # Multi-region: fetch from all intersecting admin units
            admin_units = geometry_info["intersecting_units"]
            print(f"🌍 Multi-region query: Fetching from {len(admin_units)} admin units")
        else:
            # Single region: use coordinate lookup
            admin_info = api.get_admin_details_by_latlon(latitude, longitude)
            admin_units = [admin_info]
        
        # Fetch layers from each admin unit and tag with source
        for admin_info in admin_units:
            state_name = admin_info["State"]
            district_name = admin_info["District"]
            tehsil_name = admin_info["Tehsil"]
            
            print(f"   📍 Fetching from: {tehsil_name}, {district_name}, {state_name}")
            
            layers = api.get_generated_layer_urls(state_name, district_name, tehsil_name)
            
            # Filter to target layers if specified
            # LLM already chose the exact layers we need - just filter by exact name match
            if target_layers:
                # Case-insensitive partial matching for robustness
                filtered_layers = []
                for layer in layers:
                    layer_name = layer.get('layer_name', '').lower().replace(' ', '_').replace('-', '_')
                    for target in target_layers:
                        target_clean = target.lower().replace('_vector', '').replace('_raster', '')
                        # Match if target is substring of layer name (e.g., "cropping_intensity" matches "Cropping Intensity")
                        if target_clean in layer_name:
                            # Tag layer with source tehsil for merging
                            layer['source_tehsil'] = tehsil_name
                            layer['source_district'] = district_name
                            layer['source_state'] = state_name
                            filtered_layers.append(layer)
                            break
                layers = filtered_layers
                print(f"      → LLM selected {len(layers)} layers from {tehsil_name}: {[l.get('layer_name') for l in layers[:3]]}")
            
            all_layers.extend(layers)
        
        # Group layers by name for potential merging (when multi-region)
        from collections import defaultdict
        layers_by_name = defaultdict(list)
        for layer in all_layers:
            layers_by_name[layer['layer_name']].append(layer)
        
        # Mark layers that need merging (same name from multiple tehsils)
        merged_layers = []
        for layer_name, layer_group in layers_by_name.items():
            if len(layer_group) > 1:
                # Multiple sources - needs merging
                print(f"   🔗 Layer '{layer_name}' found in {len(layer_group)} tehsils - will merge")
                # Use first as representative, but add merge metadata
                representative = layer_group[0].copy()
                representative['merge_required'] = True
                representative['merge_sources'] = [{
                    'url': l['layer_url'],
                    'tehsil': l.get('source_tehsil'),
                    'district': l.get('source_district'),
                    'state': l.get('source_state')
                } for l in layer_group]
                merged_layers.append(representative)
            else:
                merged_layers.append(layer_group[0])
        
        # Categorize layers by type
        vector_layers = [l for l in merged_layers if l.get('layer_type') == 'vector']
        raster_layers = [l for l in merged_layers if l.get('layer_type') == 'raster']
        
        state["available_layers"] = {
            'vector': vector_layers,
            'raster': raster_layers,
            'all': merged_layers
        }
        state["location_info"] = admin_units[0] if admin_units else {}
        
        print(f"\n✅ SUCCESS: Retrieved {len(vector_layers)} vector + {len(raster_layers)} raster layers")
        if target_layers:
            print(f"   🎯 Filtered to target layers: {target_layers}")
        if geometry_info and geometry_info.get("multi_region"):
            multi_source_count = sum(1 for l in merged_layers if l.get('merge_required'))
            print(f"   🔗 {multi_source_count} layers require multi-tehsil merging")
        
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
    data_source = parsed.get("data_source_type", "corestack_spatial")
    
    # Prepare data based on type
    if data_source == "corestack_timeseries":
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
        
        # STEP 3: Generate code (using selected/filtered layers only)
        code = agent.generate_code(query, plan, selected_layers)
        
        # STEP 4: Prepare execution context with ONLY the target layers
        # This prevents overwhelming CodeAct with all 66 layers when only 1-2 are needed
        context = {
            'query_lat': parsed.get('latitude'),
            'query_lon': parsed.get('longitude'),
            'vector_layers': selected_layers.get('vector', []),  # Already filtered by plan
            'raster_layers': selected_layers.get('raster', []),  # Already filtered by plan
            'query': query,
            'target_layer_names': parsed.get('target_layers', [])  # Pass LLM's layer selection
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
    Simple router based on LLM's data_source_type decision.
    The heavy lifting was done in intent parsing.
    """
    if "error" in state:
        state["next_node"] = "format"
        return state
    
    parsed = state["parsed"]
    data_source = parsed.get("data_source_type", "corestack_spatial")
    
    print("\n" + "="*70)
    print(f"🔀 ROUTING: {data_source}")
    print("="*70)
    
    # Trust LLM's routing decision
    routing_map = {
        "corestack_spatial": "fetch_spatial",
        "corestack_timeseries": "fetch_timeseries",
        "hybrid": "fetch_spatial"  # Fetch spatial first, timeseries in codeact if needed
    }
    
    state["next_node"] = routing_map.get(data_source, "fetch_spatial")
    
    print(f"➡️  Next node: {state['next_node']}")
    return state


def build_graph(skip_codeact: bool = False) -> StateGraph:
    """Build the LangGraph workflow with router and geometry resolution
    
    Args:
        skip_codeact: If True, skip CodeAct node (used when called as tool from Architecture4)
    """
    graph = StateGraph(dict)
    
    # Add nodes
    graph.add_node("parse_intent", llm_intent_parser)
    graph.add_node("resolve_geometry", resolve_geometry)
    graph.add_node("router", router_node)
    graph.add_node("fetch_spatial", fetch_spatial_layers)
    graph.add_node("fetch_timeseries", fetch_timeseries_data)
    
    if not skip_codeact:
        graph.add_node("codeact", codeact_node)
        
    graph.add_node("format", format_response)
    
    # Add edges
    graph.add_edge("parse_intent", "resolve_geometry")
    graph.add_edge("resolve_geometry", "router")
    
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
    
    # Connect fetch nodes to either codeact or format
    if skip_codeact:
        # When used as tool: fetch → format (skip codeact)
        graph.add_edge("fetch_spatial", "format")
        graph.add_edge("fetch_timeseries", "format")
    else:
        # When standalone: fetch → codeact → format
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
