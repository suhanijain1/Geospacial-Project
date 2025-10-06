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
import geopandas as gpd
import rasterio
from rasterio.mask import mask
from shapely.geometry import box
import numpy as np
import tempfile
import numpy as np
from rasterio.mask import mask
from shapely.geometry import Point, box
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph
from dotenv import load_dotenv

from artifact import ArtifactRegistry
from geospatial_artifact_registry import GeospatialArtifactRegistry
from geospatial_handlers import GeospatialDataHandler

# Initialize both registries for backward compatibility and new features
artifact_registry = ArtifactRegistry()  # Legacy registry
geo_artifact_registry = GeospatialArtifactRegistry()  # New geospatial registry
import os
DISABLE_REGISTRY = os.getenv('DISABLE_ARTIFACT_REGISTRY') == '1'

if DISABLE_REGISTRY:
    # Create dummy registries that do nothing
    class DummyRegistry:
        def register(self, *args, **kwargs):
            return "dummy_id"
        def get(self, *args, **kwargs):
            return {}
        def get_stats(self, *args, **kwargs):
            return {"total_artifacts": 0, "by_type": {}}
        def register_geospatial_artifact(self, *args, **kwargs):
            return "dummy_id"
        def get_processing_lineage(self, *args, **kwargs):
            return []
    
    artifact_registry = DummyRegistry()
    geo_artifact_registry = DummyRegistry()
else:
    artifact_registry = ArtifactRegistry()
    geo_artifact_registry = GeospatialArtifactRegistry()
    
load_dotenv()
# Initialising API keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
CORE_STACK_API_KEY = os.getenv("CORE_STACK_API_KEY")
print("CORE_STACK_API_KEY is:", CORE_STACK_API_KEY)

class SpatialDataProcessor:
    """Handles raster and vector spatial data processing"""
    
    @staticmethod
    def process_raster_url(url: str, bounds=None):
        """Process raster data via WCS"""
        try:
            # Add coordinate bounds to WCS URL if provided
            if bounds:
                lon_min, lat_min, lon_max, lat_max = bounds
                subset_params = f"&subset=Long({lon_min},{lon_max})&subset=Lat({lat_min},{lat_max})"
                if 'subset=' not in url:
                    url += subset_params
            
            print(f"🌍 Requesting raster data via WCS...")
            response = requests.get(url, verify=False, timeout=60)
            
            if response.status_code != 200:
                print(f"❌ WCS request failed: {response.status_code}")
                return None
            
            content_type = response.headers.get('content-type', '')
            print(f"📄 Content type: {content_type}")
            
            # Verify it's actually a raster file
            if not any(fmt in content_type.lower() for fmt in ['tiff', 'geotiff', 'image']):
                print(f"❌ Not a raster file: {content_type}")
                return None
            
            # Process the actual GeoTIFF content
            return SpatialDataProcessor._process_raster_content(response.content, bounds)
            
        except Exception as e:
            print(f"❌ Raster processing error: {e}")
            return None
    
    @staticmethod
    def _process_raster_content(content: bytes, bounds=None):
        """Process raster content from response"""
        try:
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.tif', delete=False) as temp_file:
                temp_file.write(content)
                temp_file.flush()
                
                with rasterio.open(temp_file.name) as src:
                    if bounds:
                        # Clip to bounds if provided
                        geom = [box(*bounds)]
                        out_image, out_transform = mask(src, geom, crop=True)
                        data = out_image[0]
                    else:
                        data = src.read(1)
                    
                    # Compute statistics
                    valid_data = data[data != src.nodata] if src.nodata is not None else data.flatten()
                    valid_data = valid_data[~np.isnan(valid_data)]
                    
                    if len(valid_data) > 0:
                        return {
                            'mean': float(np.mean(valid_data)),
                            'std': float(np.std(valid_data)),
                            'min': float(np.min(valid_data)),
                            'max': float(np.max(valid_data)),
                            'count': len(valid_data),
                            'bounds': list(src.bounds),
                            'crs': str(src.crs),
                            'processing_method': 'direct_raster'
                        }
                
                # Clean up temp file
                import os
                os.unlink(temp_file.name)
                
        except Exception as e:
            print(f"Error processing raster content: {e}")
        return None
    
    @staticmethod
    def _convert_to_wms_getmap(url: str, bounds=None):
        """Convert various service URLs to WMS GetMap"""
        try:
            if bounds:
                lon_min, lat_min, lon_max, lat_max = bounds
                bbox = f"{lon_min},{lat_min},{lon_max},{lat_max}"
            else:
                bbox = "75.0,25.0,75.2,25.2"  # Default small area
            
            # Basic WMS GetMap parameters
            wms_params = {
                'SERVICE': 'WMS',
                'REQUEST': 'GetMap',
                'FORMAT': 'image/tiff',
                'WIDTH': '256',
                'HEIGHT': '256',
                'SRS': 'EPSG:4326',
                'BBOX': bbox
            }
            
            # Extract base URL and add WMS parameters
            base_url = url.split('?')[0]
            wms_url = f"{base_url}?" + "&".join([f"{k}={v}" for k, v in wms_params.items()])
            
            # Try to extract layer name from original URL
            if 'typeName=' in url:
                layer_name = url.split('typeName=')[1].split('&')[0]
                wms_url += f"&LAYERS={layer_name}"
            
            return wms_url
            
        except Exception as e:
            print(f"Error converting to WMS: {e}")
            return None
    
    @staticmethod
    def _extract_raster_like_stats_from_vector(gdf: gpd.GeoDataFrame, bounds=None):
        """Extract raster-like statistics from vector data"""
        try:
            # Get numeric columns
            numeric_cols = gdf.select_dtypes(include=[np.number]).columns
            
            if len(numeric_cols) == 0:
                return {
                    'feature_count': len(gdf),
                    'message': 'Vector data found - no numeric attributes for raster-like analysis',
                    'processing_method': 'vector_fallback'
                }
            
            # Calculate stats for the first numeric column
            col = numeric_cols[0]
            values = gdf[col].dropna()
            
            if len(values) > 0:
                return {
                    'mean': float(values.mean()),
                    'std': float(values.std()),
                    'min': float(values.min()),
                    'max': float(values.max()),
                    'count': len(values),
                    'feature_count': len(gdf),
                    'analyzed_attribute': col,
                    'processing_method': 'vector_fallback',
                    'message': f'Analyzed numeric attribute "{col}" from vector data'
                }
                
        except Exception as e:
            print(f"Error extracting vector stats: {e}")
        
        return None
    

    
    @staticmethod
    def process_vector_url(url: str, point=None, buffer_km=1.0):
        """Download and process vector data from URL"""
        try:
            # Download GeoJSON
            response = requests.get(url, verify=False)
            
            if response.status_code == 200:
                geojson_data = response.json()
                
                if 'features' not in geojson_data or not geojson_data['features']:
                    return {'feature_count': 0, 'total_area': 0, 'attributes': {}}
                
                gdf = gpd.GeoDataFrame.from_features(geojson_data['features'])
                
                if gdf.empty:
                    return {'feature_count': 0, 'total_area': 0, 'attributes': {}}
                
                # Set CRS if not present
                if gdf.crs is None:
                    gdf.set_crs(epsg=4326, inplace=True)
                
                if point:
                    # Filter features near the point
                    point_geom = Point(point[1], point[0])  # lon, lat
                    point_buffered = point_geom.buffer(buffer_km * 0.009)  # Rough km to degrees
                    gdf = gdf[gdf.intersects(point_buffered)]
                
                # Extract numerical attributes for analysis
                numeric_cols = gdf.select_dtypes(include=[np.number]).columns
                
                results = {
                    'feature_count': len(gdf),
                    'total_area': float(gdf.geometry.area.sum()) if not gdf.empty else 0,
                    'attributes': {}
                }
                
                for col in numeric_cols:
                    if not gdf[col].isna().all():
                        results['attributes'][col] = {
                            'mean': float(gdf[col].mean()),
                            'sum': float(gdf[col].sum()),
                            'min': float(gdf[col].min()),
                            'max': float(gdf[col].max())
                        }
                
                return results
            
            return None
            
        except Exception as e:
            print(f"Error processing vector data: {e}")
            return None

MOCK_RASTER_URLS = {
    # Indian/Rajasthan-specific coordinates (25.31, 75.09)
    "elevation": "https://cloud.sdsc.edu/v1/AUTH_opentopography/Raster/SRTM_GL1/SRTM_GL1_srtm_25_04.tif",
    "landsat_india": "https://landsat-pds.s3.amazonaws.com/c1/L8/148/041/LC08_L1TP_148041_20170101_20170218_01_T1/LC08_L1TP_148041_20170101_20170218_01_T1_B4.TIF",
    "test_raster": "https://github.com/rasterio/rasterio/raw/master/tests/data/RGB.byte.tif"
}

def get_mock_raster_url(layer_name: str, bounds=None):
    """Get a working raster URL for testing - Indian region focused"""
    if "elevation" in layer_name.lower() or "dem" in layer_name.lower():
        return MOCK_RASTER_URLS["elevation"]
    elif "landsat" in layer_name.lower() or "vegetation" in layer_name.lower() or "ndvi" in layer_name.lower():
        return MOCK_RASTER_URLS["landsat_india"] 
    else:
        return MOCK_RASTER_URLS["test_raster"]
    

# --- Node functions ---
def llm_intent_parser(state: Dict[str, Any]) -> Dict[str, Any]:
    user_query = state["user_query"]
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0,
        google_api_key=GEMINI_API_KEY
    )
    prompt = (
        "You are analyzing a geospatial query. Extract and classify the request with high precision. "
        "Return ONLY valid JSON, no markdown, code blocks, or explanatory text.\n\n"
        
        "REQUIRED FIELDS (use null if cannot determine):\n"
        "- uid: string (MWS identifier like '12_75340', extract if present)\n"
        "- latitude: number (decimal degrees, -90 to 90)\n"
        "- longitude: number (decimal degrees, -180 to 180)\n"
        "- metric_text: string (what user wants to analyze)\n"
        "- start_year: number (for temporal queries, extract year only)\n"
        "- end_year: number (for temporal queries, extract year only)\n"
        "- analysis_type: one of ['timeseries', 'spatial_summary', 'change_detection', 'spatial_trend']\n"
        "- data_type_needed: one of ['vector', 'raster', 'both', 'timeseries']\n"
        "- spatial_operation: one of ['point_query', 'area_summary', 'buffer_analysis', 'trend_analysis']\n"
        "- confidence: number (0.0 to 1.0)\n"
        "- clarification_needed: boolean\n"
        "- explanation: string (brief reasoning)\n\n"
        
        "CLASSIFICATION RULES:\n"
        "1. TIMESERIES queries: contain years/time periods + metrics like 'change', 'trend', 'from X to Y'\n"
        "   - data_type_needed: 'timeseries'\n"
        "   - analysis_type: 'timeseries' or 'change_detection'\n\n"
        
        "2. VECTOR queries: spatial features, counts, areas, boundaries\n"
        "   - Keywords: 'water bodies', 'features', 'area', 'count', 'boundary', 'polygon', 'SOGE', 'drainage', 'aquifer'\n"
        "   - data_type_needed: 'vector'\n"
        "   - analysis_type: 'spatial_summary'\n\n"
        
        "3. RASTER queries: continuous data, statistics, values at points\n"
        "   - Keywords: 'vegetation', 'NDVI', 'elevation', 'slope', 'index', 'average', 'statistics', 'distribution'\n"
        "   - data_type_needed: 'raster'\n"
        "   - analysis_type: 'spatial_summary'\n\n"
        
        "4. BUFFER/PROXIMITY queries: 'within X km', 'near', 'around'\n"
        "   - spatial_operation: 'buffer_analysis'\n\n"
        
        "EDGE CASES:\n"
        "- If query has both temporal and spatial elements, prioritize the dominant aspect\n"
        "- If unsure between raster/vector, use 'both'\n"
        "- Set clarification_needed=true if query is ambiguous\n"
        "- Extract coordinates even if mixed with text (e.g., 'near 25.31, 75.09')\n"
        "- For 'uid' or 'UID' followed by numbers/underscores, extract as uid\n\n"
        
        f"QUERY: {user_query}\n\n"
        "OUTPUT (valid JSON only):"
    )
    response = llm.invoke(prompt)
    print('Gemini raw output:', response.content)  # Debug print
    content = response.content.strip()
    content = re.sub(r"^```json\s*|```$", "", content, flags=re.MULTILINE).strip()
    try:
        parsed = json.loads(content)
        state["parsed"] = parsed
        print(f"parsed -> JSON result: {parsed}")
    except Exception as e:
        state["error"] = f"LLM output not valid JSON: {content}"
    
    # Register artifact
    artifact_content = {"user_query": user_query, "parsed": state.get("parsed")}
    if state.get("error"):
        artifact_content["error"] = state["error"]
    artifact_id = artifact_registry.register(
        "llm_intent",
        artifact_content,
        parent_id=state.get("artifact_id")
    )
    state["artifact_id"] = artifact_id
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
    data_type_needed = parsed.get("data_type_needed", "timeseries")
    
    # Check for location identifier (UID or coordinates)
    if not ((uid) or (latitude is not None and longitude is not None)):
        state["error"] = "Missing required fields: either UID or latitude/longitude coordinates must be provided"
        return state
    
    # Validate coordinates if provided
    if latitude is not None:
        try:
            lat_val = float(latitude)
            if not (-90 <= lat_val <= 90):
                state["error"] = f"Invalid latitude: {latitude}. Must be between -90 and 90."
                return state
        except (ValueError, TypeError):
            state["error"] = f"Invalid latitude format: {latitude}. Must be a number."
            return state
    
    if longitude is not None:
        try:
            lon_val = float(longitude)
            if not (-180 <= lon_val <= 180):
                state["error"] = f"Invalid longitude: {longitude}. Must be between -180 and 180."
                return state
        except (ValueError, TypeError):
            state["error"] = f"Invalid longitude format: {longitude}. Must be a number."
            return state
    
    # Validate metric text
    if not metric_text or not metric_text.strip():
        state["error"] = "Missing required field: metric_text (what to analyze)"
        return state
    
    # For timeseries queries, years are required
    if data_type_needed == "timeseries":
        if not start_year or not end_year:
            state["error"] = "For timeseries analysis, both start_year and end_year are required"
            return state
        
        # Validate and canonicalize years
        try:
            start_val = int(start_year)
            end_val = int(end_year)
            
            if start_val > end_val:
                state["error"] = f"Invalid year range: start_year ({start_val}) must be <= end_year ({end_val})"
                return state
            
            if start_val < 1900 or end_val > 2030:
                state["error"] = f"Invalid year range: years must be between 1900 and 2030"
                return state
            
            # Canonicalize years to fiscal year format
            parsed["start_year"] = canonicalize_year(start_year)
            parsed["end_year"] = canonicalize_year(end_year)
            
        except (ValueError, TypeError):
            state["error"] = f"Invalid year format: start_year={start_year}, end_year={end_year}. Must be integers."
            return state
    
    # Validate data_type_needed
    valid_data_types = ['vector', 'raster', 'both', 'timeseries']
    if data_type_needed not in valid_data_types:
        state["error"] = f"Invalid data_type_needed: {data_type_needed}. Must be one of {valid_data_types}"
        return state
    
    state["parsed"] = parsed
    
    # Register artifact
    artifact_content = {"parsed": state.get("parsed")}
    if state.get("error"):
        artifact_content["error"] = state["error"]
    artifact_id = artifact_registry.register(
        "validate",
        artifact_content,
        parent_id=state.get("artifact_id")
    )
    state["artifact_id"] = artifact_id
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
    
    # Handle UID-only or coordinate-only queries
    mws_info = {}
    
    if uid and not (latitude and longitude):
        # UID provided but no coordinates - get location info from UID
        # For now, we'll need coordinates for spatial analysis, so prompt user
        state["error"] = f"UID '{uid}' provided but coordinates needed for spatial analysis. Please also provide latitude and longitude."
        return state
    elif (latitude and longitude) and not uid:
        # Coordinates provided but no UID - get UID from coordinates
        params_latlon = {"latitude": latitude, "longitude": longitude}
        print("CORE_STACK_API_KEY:", CORE_STACK_API_KEY)
        print("Headers being sent:", headers)
        response_mwsid = requests.get(f"{base_url}get_mwsid_by_latlon/", params=params_latlon, headers=headers)
        
        if response_mwsid.status_code != 200:
            state["error"] = f"Could not get UID from coordinates: {response_mwsid.text}"
            return state
        
        mws_info = response_mwsid.json()
        # Store the UID we got from coordinates
        if mws_info.get('uid'):
            state["parsed"]["uid"] = mws_info.get('uid')
            uid = mws_info.get('uid')
    elif uid and latitude and longitude:
        # Both provided - use coordinates to get location info
        params_latlon = {"latitude": latitude, "longitude": longitude}
        response_mwsid = requests.get(f"{base_url}get_mwsid_by_latlon/", params=params_latlon, headers=headers)
        
        if response_mwsid.status_code != 200:
            state["error"] = f"Could not get location info: {response_mwsid.text}"
            return state
        mws_info = response_mwsid.json()
    else:
        state["error"] = "Either UID or latitude/longitude coordinates must be provided"
        return state
    
    print(f"MWS Info: {mws_info}")
    
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
    
    # Register artifact
    artifact_content = {"mws_json": state.get("mws_json")}
    if state.get("error"):
        artifact_content["error"] = state["error"]
    artifact_id = artifact_registry.register(
        "fetch_mws_data",
        artifact_content,
        parent_id=state.get("artifact_id")
    )
    state["artifact_id"] = artifact_id
    return state
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
        f"You are a data analyst expert mapping user queries to database fields. "
        f"Find the correct data block and field prefix for time-series analysis.\n\n"
        
        f"USER METRIC: '{metric_text}'\n\n"
        
        f"AVAILABLE DATA STRUCTURE:\n{json.dumps(data_structure, indent=2)}\n\n"
        
        f"MAPPING RULES:\n"
        f"1. Look for fields with year patterns like 'fieldname_2017-2018', 'fieldname_in_unit_2017-2018'\n"
        f"2. Match user metric to field semantics:\n"
        f"   - 'precipitation' → 'precipitation_in_mm_'\n"
        f"   - 'cropping intensity' → 'cropping_intensity_'\n"
        f"   - 'evapotranspiration' → 'et_in_mm_'\n"
        f"   - 'runoff' → 'runoff_in_mm_'\n"
        f"   - 'groundwater' → 'g_in_mm_' or 'deltag_in_mm_'\n"
        f"   - 'well depth' → 'welldepth_in_m_'\n\n"
        
        f"3. Common data blocks:\n"
        f"   - 'hydrological_annual': water-related metrics\n"
        f"   - 'terrain': topographic data\n"
        f"   - 'aquifer_vector': groundwater/aquifer data\n\n"
        
        f"TASK: Return JSON with:\n"
        f"- 'block': exact data block name containing the metric\n"
        f"- 'key_prefix': field prefix before the year (including trailing underscore)\n"
        f"- 'confidence': float 0.0-1.0 indicating match certainty\n\n"
        
        f"VALIDATION:\n"
        f"- Ensure the block exists in the provided data structure\n"
        f"- Ensure fields with this prefix + year pattern exist\n"
        f"- If no good match, set confidence < 0.5\n\n"
        
        f"Example: {{\"block\": \"hydrological_annual\", \"key_prefix\": \"precipitation_in_mm_\", \"confidence\": 0.9}}"
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
        
        # Register artifact using geospatial registry
        geospatial_data = GeospatialDataHandler.convert_to_geospatial_model({
            "timeseries": rows,
            "metric_text": metric_text
        })
        
        geo_artifact_id = geo_artifact_registry.register_geospatial_artifact(
            artifact_type="normalize_data",
            data=geospatial_data,
            parent_id=state.get("artifact_id"),
            processing_node="normalize_data",
            processing_params={"data_block": data_block, "key_prefix": key_prefix}
        )
        
        # Also register in legacy registry for compatibility
        artifact_content = {"timeseries": state.get("timeseries")}
        if state.get("error"):
            artifact_content["error"] = state["error"]
        artifact_id = artifact_registry.register(
            "normalize_data",
            artifact_content,
            parent_id=state.get("artifact_id")
        )
        state["artifact_id"] = artifact_id
        state["geo_artifact_id"] = geo_artifact_id
        return state
        
    except Exception as e:
        state["error"] = f"Error using LLM to analyze data structure: {str(e)}"
        
        # Register artifact with error
        artifact_id = artifact_registry.register(
            "normalize_data",
            {"timeseries": state.get("timeseries"), "error": state.get("error")},
            parent_id=state.get("artifact_id")
        )
        state["artifact_id"] = artifact_id
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
    
    # Register artifact
    artifact_content = {"stats": state.get("stats")}
    if state.get("error"):
        artifact_content["error"] = state["error"]
    artifact_id = artifact_registry.register(
        "compute_stats",
        artifact_content,
        parent_id=state.get("artifact_id")
    )
    state["artifact_id"] = artifact_id
    return state

def format_response(state: Dict[str, Any]) -> Dict[str, Any]:
    """Enhanced response formatter for all data types: timeseries, raster, and vector"""
    # Debug the state structure
    print("Type of state in format_response:", type(state))
    print("State content keys:", list(state.keys()) if isinstance(state, dict) else "Not a dict")
    
    if "error" in state:
        state["response"] = state["error"]
        
        # Register artifact
        artifact_content = {"response": state.get("response")}
        if state.get("error"):
            artifact_content["error"] = state["error"]
        artifact_id = artifact_registry.register(
            "format_response",
            artifact_content,
            parent_id=state.get("artifact_id")
        )
        state["artifact_id"] = artifact_id
        return state
    
    parsed = state["parsed"]
    
    # Handle different response types
    if "spatial_analysis_results" in state:
        # Spatial analysis response
        results = state["spatial_analysis_results"]
        metric_text = parsed.get("metric_text", "analysis")
        
        # Get location info
        location_info = state.get("location_info", {})
        if parsed.get("uid"):
            location_str = f"UID {parsed['uid']}"
        else:
            lat = parsed.get("latitude", "unknown")
            lon = parsed.get("longitude", "unknown")
            location_str = f"Location ({lat}, {lon})"
        
        # Use LLM to intelligently interpret and format the spatial analysis results
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.3,  # Slightly creative for better formatting
            google_api_key=GEMINI_API_KEY
        )
        
        # Prepare the data for LLM interpretation
        analysis_data = {
            "user_query": state["user_query"],
            "metric_requested": metric_text,
            "location": location_str,
            "spatial_results": results
        }
        
        prompt = (
            f"You are a geospatial data analyst. The user asked: '{state['user_query']}'\n\n"
            
            f"ANALYSIS RESULTS:\n{json.dumps(analysis_data, indent=2, default=str)}\n\n"
            
            f"INSTRUCTIONS:\n"
            f"1. Create a clear, informative response that directly answers the user's question\n"
            f"2. Focus on the most relevant insights from the data\n"
            f"3. Use appropriate emojis and formatting for readability\n"
            f"4. For land use queries: categorize and summarize land use types\n"
            f"5. For agricultural queries: focus on farming statistics and areas\n"
            f"6. For raster data: explain what the values represent in context\n"
            f"7. For vector data: summarize features and key attributes meaningfully\n"
            f"8. Keep it concise but informative (aim for 5-10 key points)\n"
            f"9. Don't dump raw statistics - interpret what they mean\n"
            f"10. Use hectares for areas, include totals and percentages where relevant\n\n"
            
            f"CONTEXT HINTS:\n"
            f"- 'doubly_cro' = double cropping areas\n"
            f"- 'single_kha' = single cropping (kharif season)\n"
            f"- 'built-up' = urban/residential areas\n"
            f"- 'tree_fores' = forest cover\n"
            f"- 'barrenland' = unused/barren land\n"
            f"- 'k_water' = kharif water bodies\n"
            f"- 'kr_water' = rabi water bodies\n"
            f"- Area values are typically in hectares\n\n"
            
            f"Generate a response that would be helpful to a researcher or policymaker:"
        )
        
        try:
            llm_response = llm.invoke(prompt)
            formatted_response = llm_response.content.strip()
            
            # Clean up any markdown formatting if present
            formatted_response = re.sub(r"^```.*\n|```$", "", formatted_response, flags=re.MULTILINE).strip()
            
            state["response"] = formatted_response
            
        except Exception as e:
            print(f"Error in LLM formatting: {e}")
            # Fallback to simple summary
            response_parts = [f"Spatial analysis for {metric_text} at {location_str}:\n"]
            
            for layer_name, result in results.items():
                if result['type'] == 'vector':
                    data = result['data']
                    response_parts.append(f"• {layer_name}: {data['feature_count']} features analyzed")
                elif result['type'] == 'raster':
                    data = result['data']
                    response_parts.append(f"• {layer_name}: mean={data['mean']:.2f}, range=[{data['min']:.2f}, {data['max']:.2f}]")
            
            if not results:
                response_parts.append("No matching spatial data found for this query.")
            
            state["response"] = "\n".join(response_parts)
        
        # Register artifact
        artifact_content = {"response": state.get("response")}
        artifact_id = artifact_registry.register(
            "format_response",
            artifact_content,
            parent_id=state.get("artifact_id")
        )
        state["artifact_id"] = artifact_id
        
    elif "stats" in state:
        # Timeseries analysis response (existing logic)
        stats = state["stats"]
        uid = parsed.get("uid")
        requested_start_year = parsed.get("start_year")
        requested_end_year = parsed.get("end_year")
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
            location_str = f"Location ({lat:.5f}, {lon:.5f})" if lat and lon else "Unknown location"
        
        if "error" in stats:
            state["response"] = stats["error"]
        else:
            # Note if we had to use different years than requested
            year_note = ""
            if (requested_start_year and requested_end_year and 
                (actual_start_year != requested_start_year or actual_end_year != requested_end_year)):
                year_note = f" (Note: Used available years {actual_start_year} to {actual_end_year})"
            
            state["response"] = (
                f"{location_str} — {metric_text.title()} changed from {stats['start_val']} ({actual_start_year}) "
                f"to a peak of {stats['peak_value']} ({stats['peak_year']}) and is {stats['end_val']} in {actual_end_year}. "
                f"Net change {actual_start_year}→{actual_end_year} ≈ {stats['percent_change']}%.{year_note} "
                f"Data sources: {', '.join(stats['sources'])}."
            )
        
        # Register artifact
        artifact_content = {"response": state.get("response")}
        if state.get("error"):
            artifact_content["error"] = state["error"]
        artifact_id = artifact_registry.register(
            "format_response",
            artifact_content,
            parent_id=state.get("artifact_id")
        )
        state["artifact_id"] = artifact_id
        
    else:
        # Fallback response
        state["response"] = "Analysis completed, but no results were generated."
        
        # Register artifact
        artifact_id = artifact_registry.register(
            "format_response",
            {"response": state.get("response")},
            parent_id=state.get("artifact_id")
        )
        state["artifact_id"] = artifact_id
    
    return state

def fetch_spatial_layers(state: Dict[str, Any]) -> Dict[str, Any]:
    """Fetch available spatial layers for the location"""
    if "error" in state:
        return state
    
    base_url = "https://geoserver.core-stack.org/api/v1/"
    headers = {"X-API-Key": CORE_STACK_API_KEY}
    
    # Get location info (same as existing logic)
    latitude = state["parsed"].get("latitude")
    longitude = state["parsed"].get("longitude")
    uid = state["parsed"].get("uid")
    
    
    # Step 1: Get MWS info from coordinates or use test UID coordinates
    location_info = {}
    if latitude and longitude:
        params_latlon = {"latitude": latitude, "longitude": longitude}
        response_mwsid = requests.get(f"{base_url}get_mwsid_by_latlon/", 
                                      params=params_latlon, headers=headers)
        
        if response_mwsid.status_code == 200:
            location_info = response_mwsid.json()
            if not uid and location_info.get('uid'):
                state["parsed"]["uid"] = location_info.get('uid')
            state["location_info"] = location_info
        else:
            state["error"] = f"Could not get location info: {response_mwsid.text}"
            return state
    elif uid:
        # For UID-only queries, we need coordinates to proceed with spatial analysis
        # In a full implementation, you'd have a UID->coordinates lookup API
        state["error"] = f"UID '{uid}' provided but coordinates needed for spatial analysis. Please also provide latitude and longitude."
        return state
    else:
        state["error"] = "Need either UID or location coordinates to fetch spatial layers"
        return state
    
    params_layers = {
        'state': location_info.get('State', location_info.get('state')), 
        'district': location_info.get('District', location_info.get('district')),
        'tehsil': location_info.get('Tehsil', location_info.get('tehsil'))
    }
    
    response = requests.get(f"{base_url}get_generated_layer_urls/", 
                           params=params_layers, headers=headers)
    
    if response.status_code == 200:
        layers = response.json()
        
        # Categorize layers by type
        vector_layers = [l for l in layers if l.get('layer_type') == 'vector']
        raster_layers = [l for l in layers if l.get('layer_type') == 'raster']
        
        state["available_layers"] = {
            'vector': vector_layers,
            'raster': raster_layers,
            'all': layers
        }
        
        print(f"Found {len(vector_layers)} vector and {len(raster_layers)} raster layers")
        
        # # Debug: Show sample raster layer URLs
        # if raster_layers:
        #     print("Sample raster layer structure:")
        #     for i, layer in enumerate(raster_layers[:2]):
        #         print(f"  Layer {i+1}: {layer}")
        #         break
        
        # Register artifact
        artifact_content = {"available_layers": state.get("available_layers")}
        artifact_id = artifact_registry.register(
            "fetch_spatial_layers",
            artifact_content,
            parent_id=state.get("artifact_id")
        )
        state["artifact_id"] = artifact_id
        
    else:
        state["error"] = f"Could not fetch layers: {response.text}"
    
    return state

def analyze_spatial_data(state: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze spatial data based on query requirements"""
    if "error" in state:
        return state
    
    parsed = state["parsed"]
    layers = state.get("available_layers", {})
    data_type_needed = parsed.get("data_type_needed", "timeseries")
    analysis_type = parsed.get("analysis_type", "spatial_summary")
    metric_text = parsed.get("metric_text", "").lower()
    
    results = {}
    
    # Use LLM to match metric to appropriate layers
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0,
        google_api_key=GEMINI_API_KEY
    )
    
    layer_names = [l.get('layer_name', '') for l in layers.get('all', [])]
    
    if not layer_names:
        state["error"] = "No spatial layers available for this location"
        return state
    
    prompt = (
        f"You are a geospatial data expert. Match the user's analysis request to the most relevant data layers.\n\n"
        f"USER REQUEST: '{metric_text}'\n"
        f"DATA TYPE NEEDED: {data_type_needed}\n"
        f"ANALYSIS TYPE: {analysis_type}\n\n"
        
        f"AVAILABLE LAYERS:\n{layer_names}\n\n"
        
        f"MATCHING RULES:\n"
        f"- Vegetation/NDVI/greenness → look for 'NDVI', 'vegetation', 'land_cover', 'green' layers\n"
        f"- Water/hydrology → look for 'water', 'drainage', 'river', 'stream', 'hydro' layers\n"
        f"- Agriculture/farming → look for 'crop', 'SOGE', 'agriculture', 'farming' layers\n"
        f"- Terrain/elevation → look for 'elevation', 'slope', 'DEM', 'terrain', 'topography' layers\n"
        f"- Groundwater/aquifer → look for 'aquifer', 'groundwater', 'well', 'water_table' layers\n"
        f"- Administrative → look for 'boundary', 'admin', 'district', 'state' layers\n"
        f"- Infrastructure → look for 'road', 'settlement', 'built', 'infrastructure' layers\n\n"
        
        f"SELECTION CRITERIA:\n"
        f"- Select 1-3 most relevant layers (avoid selecting everything)\n"
        f"- Prioritize exact keyword matches\n"
        f"- If no exact match, select semantically closest layers\n"
        f"- If user request is very general, select 2-3 diverse layers\n\n"
        
        f"Return valid JSON with:\n"
        f"- 'selected_layers': array of layer names (exactly as provided)\n"
        f"- 'reasoning': brief explanation of why these layers were chosen\n\n"
        
        f"Example output:\n"
        f'{{"selected_layers": ["SOGE", "Drainage"], "reasoning": "SOGE for agricultural analysis, Drainage for water flow patterns"}}'
    )
    
    try:
        response = llm.invoke(prompt)
        content = response.content.strip()
        content = re.sub(r"^```json\s*|```$", "", content, flags=re.MULTILINE).strip()
        
        # Handle potential JSON parsing issues
        try:
            layer_selection = json.loads(content)
        except json.JSONDecodeError as e:
            print(f"JSON parsing error in layer selection: {e}")
            print(f"Raw content: {content}")
            # Fallback: try to extract layer names from content
            layer_selection = {'selected_layers': [], 'reasoning': 'JSON parsing failed'}
        
        selected_layer_names = layer_selection.get('selected_layers', [])
        reasoning = layer_selection.get('reasoning', 'No reasoning provided')
        
        print(f"LLM selected layers: {selected_layer_names}")
        print(f"Reasoning: {reasoning}")
        
        # Validate that selected layers actually exist
        available_layer_names = {l.get('layer_name', '') for l in layers.get('all', [])}
        valid_selected_layers = [name for name in selected_layer_names if name in available_layer_names]
        
        if not valid_selected_layers and selected_layer_names:
            print(f"Warning: None of the selected layers {selected_layer_names} exist in available layers")
            # Fallback: select first available layer that matches metric keywords
            metric_keywords = metric_text.lower().split()
            for layer in layers.get('all', []):
                layer_name = layer.get('layer_name', '').lower()
                if any(keyword in layer_name for keyword in metric_keywords):
                    valid_selected_layers = [layer.get('layer_name')]
                    print(f"Fallback selection: {valid_selected_layers}")
                    break
        
        selected_layer_names = valid_selected_layers
        
        # Process selected layers
        for layer in layers.get('all', []):
            if layer.get('layer_name') in selected_layer_names:
                layer_url = layer.get('layer_url')
                layer_type = layer.get('layer_type')
                
                if layer_type == 'vector' and data_type_needed in ['vector', 'both']:
                    # Process vector data
                    point = None
                    if parsed.get('latitude') and parsed.get('longitude'):
                        point = (float(parsed['latitude']), float(parsed['longitude']))
                    
                    vector_result = SpatialDataProcessor.process_vector_url(layer_url, point)
                    if vector_result:
                        results[layer['layer_name']] = {
                            'type': 'vector',
                            'data': vector_result
                        }
                
                elif layer_type == 'raster' and data_type_needed in ['raster', 'both']:
                    # Process raster data with GEE asset path
                    bounds = None
                    if parsed.get('latitude') and parsed.get('longitude'):
                        # Create small bounds around point
                        lat, lon = float(parsed['latitude']), float(parsed['longitude'])
                        buffer = 0.01  # ~1km buffer  
                        bounds = (lon-buffer, lat-buffer, lon+buffer, lat+buffer)
                    
                    print(f"Processing raster layer: {layer['layer_name']}")
                    gee_asset_path = layer.get('gee_asset_path')
                    raster_result = SpatialDataProcessor.process_raster_url(
                        layer_url, bounds 
                    )
                    if raster_result:
                        results[layer['layer_name']] = {
                            'type': 'raster',
                            'data': raster_result
                        }
                        print(f"Successfully processed raster layer: {layer['layer_name']}")
        
        state["spatial_analysis_results"] = results
        
        # Register artifact using geospatial registry
        if results:
            geospatial_data = GeospatialDataHandler.convert_to_geospatial_model({
                "spatial_results": results,
                "metric_text": metric_text
            })
            
            geo_artifact_id = geo_artifact_registry.register_geospatial_artifact(
                artifact_type="analyze_spatial_data",
                data=geospatial_data,
                parent_id=state.get("artifact_id"),
                processing_node="analyze_spatial_data",
                processing_params={"data_type_needed": data_type_needed, "selected_layers": selected_layer_names}
            )
            state["geo_artifact_id"] = geo_artifact_id
        
        # Also register in legacy registry for compatibility
        artifact_content = {"spatial_analysis_results": state.get("spatial_analysis_results")}
        if state.get("error"):
            artifact_content["error"] = state["error"]
        artifact_id = artifact_registry.register(
            "analyze_spatial_data",
            artifact_content,
            parent_id=state.get("artifact_id")
        )
        state["artifact_id"] = artifact_id
        
    except Exception as e:
        state["error"] = f"Error in spatial analysis: {str(e)}"
        
        # Register artifact with error
        artifact_id = artifact_registry.register(
            "analyze_spatial_data",
            {"spatial_analysis_results": state.get("spatial_analysis_results"), "error": state.get("error")},
            parent_id=state.get("artifact_id")
        )
        state["artifact_id"] = artifact_id
    
    return state

def router(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Determines the next node based on the current state and data type needed.
    Routes to appropriate processing path: timeseries or spatial.
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
    
    # Route based on data type needed
    data_type_needed = parsed.get("data_type_needed", "timeseries")
    
    if data_type_needed == "timeseries":
        state["router"] = "fetch_timeseries"
    elif data_type_needed in ["vector", "raster", "both"]:
        state["router"] = "fetch_spatial"
    else:
        # Default to timeseries for backward compatibility
        state["router"] = "fetch_timeseries"
    
    print(f"Router decision: {state['router']} (data_type_needed: {data_type_needed})")
    return state

# --- Enhanced LangGraph StateGraph wiring ---
graph = StateGraph(dict)

# Add all nodes
graph.add_node("intent", llm_intent_parser)
graph.add_node("validate", validate)
graph.add_node("router", router)
graph.add_node("fetch_timeseries", fetch_mws_data)  
graph.add_node("fetch_spatial", fetch_spatial_layers)  
graph.add_node("analyze_spatial", analyze_spatial_data)  
graph.add_node("normalize", normalize_data)
graph.add_node("compute", compute_timeseries_stats)
graph.add_node("format", format_response)

# Add edges with conditional routing
graph.add_edge("intent", "validate")
graph.add_edge("validate", "router")

# Router decides between timeseries and spatial paths
graph.add_conditional_edges(
    "router",
    lambda x: x["router"],
    {
        "fetch_timeseries": "fetch_timeseries",
        "fetch_spatial": "fetch_spatial",
        "format": "format"
    }
)

# Timeseries path (existing)
graph.add_edge("fetch_timeseries", "normalize")
graph.add_edge("normalize", "compute")
graph.add_edge("compute", "format")

# Spatial path (new)
graph.add_edge("fetch_spatial", "analyze_spatial")
graph.add_edge("analyze_spatial", "format")

graph.set_entry_point("intent")
graph.set_finish_point("format")

# --- Main MVP agent runner ---
def run_agent(user_query: str):
    state = {"user_query": user_query}
    app = graph.compile()
    result_state = app.invoke(state)
    print("\n--- Final Agent Response ---\n")
    print(result_state["response"])
    
    # Show artifact lineage
    artifact_id = result_state.get("artifact_id")
    geo_artifact_id = result_state.get("geo_artifact_id")
    
    if artifact_id:
        print("\n--- Legacy Artifact Lineage ---")
        lineage = []
        current_id = artifact_id
        
        # Build lineage chain backwards
        while current_id:
            artifact = artifact_registry.get(current_id)
            if not artifact:
                break
            lineage.append(artifact)
            current_id = artifact["parent_id"]
        
        # Print lineage in chronological order (oldest to newest)
        for i, artifact in enumerate(reversed(lineage)):
            print(f"\n{i+1}. Artifact: {artifact['type']} | ID: {artifact['id']}")
            print(f"   Content keys: {list(artifact['content'].keys()) if isinstance(artifact['content'], dict) else 'Non-dict content'}")
            if artifact.get('parent_id'):
                print(f"   Parent ID: {artifact['parent_id']}")
    
    if geo_artifact_id:
        print("\n--- Geospatial Artifact Lineage ---")
        geo_lineage = geo_artifact_registry.get_processing_lineage(geo_artifact_id)
        
        for i, step in enumerate(geo_lineage):
            print(f"\n{i+1}. Processing: {step['operation']} | Data Type: {step['data_type']}")
            print(f"   Artifact ID: {step['artifact_id']}")
            print(f"   Node: {step['processing_node']}")
            if step['parameters']:
                print(f"   Parameters: {step['parameters']}")
    
    # Show registry stats
    print(f"\n--- Legacy Registry Stats ---")
    stats = artifact_registry.get_stats()
    print(f"Total artifacts: {stats['total_artifacts']}")
    print("By type:", stats['by_type'])
    
    print(f"\n--- Geospatial Registry Stats ---")
    geo_stats = geo_artifact_registry.get_stats()
    print(f"Total artifacts: {geo_stats['total_artifacts']}")
    print("By processing type:", geo_stats['by_processing_type'])
    print("By data type:", geo_stats['by_data_type'])
    if geo_stats['spatial_statistics']:
        print("Spatial statistics:", geo_stats['spatial_statistics'])

# --- Enhanced example usage ---
if __name__ == "__main__":
    # Example queries the enhanced agent can handle
    test_queries = [
        # Timeseries queries 
        "How did cropping intensity change from 2017 to 2023 at latitude 25.31698754297551, longitude 75.09702609349773?",
        "What was the precipitation trend from 2017 to 2023 at latitude 25.31698754297551, longitude 75.09702609349773?",
        "Show me groundwater depletion rates between 2018-2022 near coordinates 25.317, 75.097",
        
        # Vector data queries 
        "How many water bodies are within 1km of coordinates 25.31698754297551, 75.09702609349773?",
        #"What's the total agricultural area around uid 12_75340?",
        "Analyze drainage network density near latitude 25.31, longitude 75.09",
        "Count the number of SOGE features within 3km of my location at 25.317, 75.097",
        
        # Raster data queries 
        "What's the average vegetation index around latitude 25.31, longitude 75.09?",
        "Analyze elevation patterns within 2km of uid 12_75340",
        "What are the slope statistics for the watershed at coordinates 25.317, 75.097?",
        "Show me NDVI distribution in a 5km radius of latitude 25.31, longitude 75.09",
        
        # Advanced spatial queries 
        "What are the terrain characteristics near coordinates 25.31698754297551, 75.09702609349773?",
        "Analyze land use distribution around uid 12_75340",
        "Show aquifer characteristics within 1km of latitude 25.31, longitude 75.09"
    ]
    
    print("=== Enhanced Geospatial Agent Testing ===\n")
    print("Available query types:")
    print("1. Timeseries Analysis")
    print("2. Vector Data Analysis")
    print("3. Raster Data Analysis")
    
    # Run 
    #run_agent(test_queries[0])
    

    # Test the land use distribution query:
    run_agent("How did cropping intensity change from 2017 to 2023 at latitude 25.31698754297551, longitude 75.09702609349773?")
