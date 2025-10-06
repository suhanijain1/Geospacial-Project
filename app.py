import streamlit as st
import sys
from pathlib import Path

# Import your agent
from langgraph_agent import run_agent, graph

st.set_page_config(
    page_title="Geospatial Analysis Agent",
    page_icon="🌍",
    layout="wide"
)

st.title("Geospatial Analysis Agent")
st.markdown("Query geospatial data using natural language")

# Initialize session state
if 'history' not in st.session_state:
    st.session_state.history = []

# Query input
query = st.text_area(
    "Enter your query:",
    placeholder="e.g., How did cropping intensity change from 2017 to 2023 at latitude 25.317, longitude 75.097?",
    height=100
)

# Example queries in sidebar
with st.sidebar:
    st.header("Example Queries")
    
    st.subheader("Timeseries Analysis")
    if st.button("Cropping intensity 2017-2023", use_container_width=True):
        query = "How did cropping intensity change from 2017 to 2023 at latitude 25.31698754297551, longitude 75.09702609349773?"
        st.session_state.selected_query = query
    
    if st.button("Precipitation trend", use_container_width=True):
        query = "What was the precipitation trend from 2017 to 2023 at latitude 25.31698754297551, longitude 75.09702609349773?"
        st.session_state.selected_query = query
    
    st.subheader("Spatial Analysis")
    if st.button("Water bodies count", use_container_width=True):
        query = "How many water bodies are within 1km of coordinates 25.317, 75.097?"
        st.session_state.selected_query = query
    
    if st.button("Vegetation index", use_container_width=True):
        query = "What's the average vegetation index around latitude 25.31, longitude 75.09?"
        st.session_state.selected_query = query
    
    if st.button("Land use analysis", use_container_width=True):
        query = "Analyze land use distribution around latitude 25.317, longitude 75.097"
        st.session_state.selected_query = query

# Use selected query from sidebar if available
if 'selected_query' in st.session_state:
    query = st.session_state.selected_query
    del st.session_state.selected_query

# Submit button
col1, col2, col3 = st.columns([1, 1, 4])
with col1:
    submit = st.button("Analyze", type="primary", use_container_width=True)
with col2:
    clear = st.button("Clear History", use_container_width=True)

if clear:
    st.session_state.history = []
    st.rerun()

# Process query
if submit and query:
    with st.spinner("Processing your query..."):
        try:
            # Run the agent
            state = {"user_query": query}
            app = graph.compile()
            result_state = app.invoke(state)
            
            # Get response
            response = result_state.get("response", "No response generated")
            error = result_state.get("error")
            
            # Add to history
            st.session_state.history.append({
                "query": query,
                "response": response,
                "error": error
            })
            
        except Exception as e:
            st.error(f"Error processing query: {str(e)}")

# Display results
if st.session_state.history:
    st.header("Results")
    
    # Show most recent first
    for idx, item in enumerate(reversed(st.session_state.history)):
        with st.container():
            st.subheader(f"Query {len(st.session_state.history) - idx}")
            
            # Query
            st.markdown("**Your Query:**")
            st.info(item["query"])
            
            # Response
            st.markdown("**Analysis Result:**")
            if item.get("error"):
                st.error(item["error"])
            else:
                # Parse and format the response for better display
                response = item["response"]
                
                # Check if it's a structured timeseries response
                if "—" in response and "changed from" in response.lower():
                    parts = response.split("—", 1)
                    location = parts[0].strip()
                    analysis = parts[1].strip() if len(parts) > 1 else response
                    
                    st.markdown(f"**Location:** {location}")
                    
                    # Extract key metrics
                    lines = []
                    if "changed from" in analysis:
                        # Parse the change information
                        import re
                        
                        # Extract values
                        start_match = re.search(r'from ([\d.]+) \(([\d-]+)\)', analysis)
                        peak_match = re.search(r'peak of ([\d.]+) \(([\d-]+)\)', analysis)
                        end_match = re.search(r'is ([\d.]+) in ([\d-]+)', analysis)
                        change_match = re.search(r'≈ ([-\d.]+)%', analysis)
                        
                        if start_match and end_match:
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric(
                                    label=f"Start ({start_match.group(2)})",
                                    value=start_match.group(1)
                                )
                            
                            with col2:
                                if peak_match:
                                    st.metric(
                                        label=f"Peak ({peak_match.group(2)})",
                                        value=peak_match.group(1)
                                    )
                            
                            with col3:
                                change_val = change_match.group(1) if change_match else "N/A"
                                st.metric(
                                    label=f"Current ({end_match.group(2)})",
                                    value=end_match.group(1),
                                    delta=f"{change_val}% overall change"
                                )
                        
                        # Show data sources in expander
                        if "Data sources:" in analysis:
                            sources = analysis.split("Data sources:")[-1].strip()
                            with st.expander("View Data Sources"):
                                source_list = [s.strip() for s in sources.split(",")]
                                for src in source_list:
                                    st.caption(f"• {src}")
                    else:
                        # Non-timeseries response, show as is
                        st.success(response)
                else:
                    # For spatial or other analysis types
                    st.success(response)
            
            st.divider()
else:
    # Show placeholder when no queries yet
    st.info("Enter a query above or select an example from the sidebar to get started")

# Footer
st.markdown("---")
st.caption("Powered by LangGraph, Gemini, and CoreStack API")