# Geospatial Data Analysis Agent

This project implements a flexible LangGraph-based agent for analyzing geospatial data from the CoreStack API. The agent can process natural language queries about various metrics (e.g., precipitation, water bodies, cropping intensity) for specific locations, extract meaningful insights, and provide human-readable responses.

## Features

- **Natural Language Query Processing**: Ask questions about geospatial data in plain English
- **Dynamic Metric Analysis**: Analyzes various metrics without hard-coded mappings
- **Location-Based Queries**: Supports queries with explicit coordinates or MWS UIDs
- **Trend Analysis**: Calculates trends, percent changes, and peak values
- **LLM-Powered Data Discovery**: Uses Gemini to intelligently map metrics to data structures

## Requirements

- Python 3.x
- LangGraph
- LangChain
- Gemini API access
- CoreStack API access

## Usage

```python
from langgraph_agent import run_agent

# Query with coordinates
response = run_agent("How did water bodies change from 2017 to 2023 at latitude 25.31698754297551, longitude 75.09702609349773?")

# Query with different metric
response = run_agent("What was the precipitation trend from 2017 to 2023 at latitude 25.31698754297551, longitude 75.09702609349773?")

# Query about cropping intensity
response = run_agent("What was the cropping intensity in 2021 at latitude 25.31698754297551, longitude 75.09702609349773?")
```

## Agent Architecture

The agent uses a LangGraph StateGraph with conditional routing between the following nodes:

1. **LLM Intent Parser**: Extracts intent, metrics, coordinates, and time periods from queries
2. **Router**: Conditionally routes to the appropriate next steps based on intent
3. **Fetch MWS ID**: Retrieves the MWS ID based on coordinates if needed
4. **Fetch MWS Data**: Retrieves the relevant data from the CoreStack API
5. **Normalize Data**: Uses LLM to identify the appropriate data structures for the requested metric
6. **Format Response**: Formats the analyzed data into a human-readable response

## Example Queries

- "How did water bodies change from 2017 to 2023 at latitude 25.31, longitude 75.09?"
- "What was the precipitation trend from 2017 to 2023 at latitude 25.31, longitude 75.09?"
- "What was the cropping intensity in 2021 at latitude 25.31, longitude 75.09?"
- "Analyze the change in forest cover between 2018 and 2022 at latitude 25.31, longitude 75.09"
- "What is the water balance for MWS ID 12_75340?"

## Sample Output

```
UID 12_75340 — Water Bodies changed from 27.69 (2017-2018) to a peak of 63.19 (2019-2020) and is 23.26 in 2023-2024. 
Net change 2017-2018→2023-2024 ≈ -15.9986%. 
Data sources: surfaceWaterBodies_annual.total_area_in_ha_2019-2020, surfaceWaterBodies_annual.total_area_in_ha_2017-2018, surfaceWaterBodies_annual.total_area_in_ha_2023-2024.
```

## LLM-Based Data Discovery

Instead of using hard-coded mappings for metrics to data structures, this agent uses Gemini to analyze the API response and intelligently determine:

1. Which data block contains the relevant information (e.g., "hydrological_annual", "surfaceWaterBodies_annual")
2. What key prefix should be used to extract time series data (e.g., "precipitation_in_mm_", "total_area_in_ha_")

This approach makes the agent much more flexible and able to handle a wider range of metrics without requiring code changes.

## Future Work

- RAG-based approach for more robust metric mapping
- Multi-location comparison
- Advanced visualization capabilities
- Integration with more data sources
- More sophisticated statistical analysis
