# Import necessary libraries
import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.exceptions import SnowparkSQLException
import pandas as pd

# --- Page Configuration ---
st.set_page_config(
    page_title="Snowflake Data Explorer",
    page_icon="❄️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Helper Functions ---

@st.cache_data(ttl=3600) # Cache for 1 hour
def get_databases(_session):
    """Fetches a list of databases."""
    st.write("Fetching databases...") # For debugging/user feedback
    databases_df = _session.sql("SHOW DATABASES").collect()
    return [db['name'] for db in databases_df]

@st.cache_data(ttl=3600)
def get_schemas(_session, db_name):
    """Fetches schemas for a given database."""
    if not db_name:
        return []
    st.write(f"Fetching schemas for database: {db_name}...")
    try:
        # Ensure db_name is properly quoted if it contains special characters, though SHOW SCHEMAS usually handles this.
        # However, direct SQL execution might need it. For SHOW commands, it's often not an issue.
        schemas_df = _session.sql(f"SHOW SCHEMAS IN DATABASE \"{db_name}\"").collect()
        return [schema['name'] for schema in schemas_df if schema['name'] not in ['INFORMATION_SCHEMA', 'PUBLIC']] # Exclude common system schemas
    except SnowparkSQLException as e:
        st.error(f"Error fetching schemas for {db_name}: {e}")
        return []

@st.cache_data(ttl=3600)
def get_tables(_session, db_name, schema_name):
    """Fetches tables for a given database and schema."""
    if not db_name or not schema_name:
        return []
    st.write(f"Fetching views for {db_name}.{schema_name}...")
    try:
        tables_df = _session.sql(f"SHOW VIEWS IN SCHEMA \"{db_name}\".\"{schema_name}\"").collect()
        return [table['name'] for table in tables_df]
    except SnowparkSQLException as e:
        st.error(f"Error fetching views for {db_name}.{schema_name}: {e}")
        return []

@st.cache_data(ttl=3600)
def get_columns(_session, db_name, schema_name, table_name):
    """Fetches columns for a given table."""
    if not db_name or not schema_name or not table_name:
        return []
    st.write(f"Fetching columns for {db_name}.{schema_name}.{table_name}...")
    try:
        # Using DESCRIBE TABLE to get column names and types
        columns_df = _session.sql(f"DESCRIBE TABLE \"{db_name}\".\"{schema_name}\".\"{table_name}\"").collect()
        # Return a list of tuples (column_name, data_type)
        return [(col['name'], col['type']) for col in columns_df]
    except SnowparkSQLException as e:
        st.error(f"Error fetching columns for {db_name}.{schema_name}.{table_name}: {e}")
        return []

@st.cache_data(ttl=600) # Cache data for 10 minutes
def get_table_data(_session, db_name, schema_name, table_name, num_rows=100):
    """Fetches a sample of data from the specified table."""
    if not db_name or not schema_name or not table_name:
        return pd.DataFrame()
    st.write(f"Fetching data from {db_name}.{schema_name}.{table_name} (limit {num_rows})...")
    try:
        # Construct the fully qualified table name, ensuring proper quoting
        # Snowflake identifiers are case-insensitive by default but can be case-sensitive if quoted.
        # It's safer to quote them if there's any doubt or if they were created with quotes.
        fully_qualified_name = f'"{db_name}"."{schema_name}"."{table_name}"'
        data_df = _session.table(fully_qualified_name).limit(num_rows).to_pandas()
        return data_df
    except SnowparkSQLException as e:
        st.error(f"Error fetching data from {fully_qualified_name}: {e}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"An unexpected error occurred while fetching data: {e}")
        return pd.DataFrame()

# --- Main Application ---
def main():
    st.title("❄️ Streamlit & Snowflake: Data Explorer 🚀")

    st.markdown("""
    Welcome to the **Snowflake Data Explorer**!
    This app demonstrates how to build interactive applications with Streamlit directly in Snowflake.
    It's designed for Python users who are new to Streamlit, showing you how to:
    - Connect to your Snowflake data.
    - Use interactive widgets to select databases, schemas, and tables.
    - Visualize data with various charts, including maps.

    Let's explore your data!
    """)

    st.info("""
    **How this works (for the curious Pythonista):**
    - We're using the `snowflake.snowpark.context.get_active_session()` to connect to Snowflake.
    - Streamlit functions like `st.selectbox`, `st.button`, `st.dataframe`, `st.bar_chart`, and `st.map` create the interactive UI and visualizations.
    - Data is fetched using Snowpark DataFrames and then often converted to Pandas DataFrames for compatibility with some Streamlit charting elements.
    """, icon="💡")

    # Get Snowflake session
    try:
        session = get_active_session()
        st.sidebar.success("Snowflake session active!")
    except Exception as e:
        st.error(f"Could not get active Snowflake session. Ensure this app is running in a Snowflake environment (e.g., Snowsight, Streamlit-in-Snowflake). Error: {e}")
        st.stop() # Stop execution if no session

    # --- Sidebar for Selections ---
    st.sidebar.header("Data Source Selection")
    st.sidebar.markdown("Choose the database, schema, and table you want to explore.")

    # 1. Database Selection
    try:
        databases = get_databases(session)
        if not databases:
            st.sidebar.warning("No databases found or accessible.")
            st.stop()
        selected_db = st.sidebar.selectbox("Select Database:", databases, index=0 if databases else -1, help="Choose the Snowflake database.")
    except Exception as e:
        st.sidebar.error(f"Error loading databases: {e}")
        selected_db = None
        st.stop()

    # 2. Schema Selection
    selected_schema = None
    if selected_db:
        try:
            schemas = get_schemas(session, selected_db)
            if not schemas:
                st.sidebar.warning(f"No schemas found in database '{selected_db}' (excluding INFORMATION_SCHEMA and PUBLIC).")
            selected_schema = st.sidebar.selectbox("Select Schema:", schemas, index=0 if schemas else -1, help="Choose the schema within the selected database.")
        except Exception as e:
            st.sidebar.error(f"Error loading schemas for {selected_db}: {e}")


    # 3. Table Selection
    selected_table = None
    if selected_db and selected_schema:
        try:
            tables = get_tables(session, selected_db, selected_schema)
            if not tables:
                st.sidebar.warning(f"No tables found in schema '{selected_db}.{selected_schema}'.")
            selected_table = st.sidebar.selectbox("Select Table:", tables, index=0 if tables else -1, help="Choose the table to visualize.")
        except Exception as e:
            st.sidebar.error(f"Error loading tables for {selected_db}.{selected_schema}: {e}")

    # --- Main Panel for Data Display and Visualization ---    
    if selected_db and selected_schema and selected_table:
        st.header(f"Exploring: `{selected_db}`.`{selected_schema}`.`{selected_table}`")

        # Fetch column information
        columns_info = get_columns(session, selected_db, selected_schema, selected_table)
        if not columns_info:
            st.warning("Could not retrieve column information for the selected table.")
            st.stop()

        column_names = [col[0] for col in columns_info]
        column_types = {col[0]: col[1] for col in columns_info}

        # Section 1: Data Preview
        with st.expander("📄 Show Table Data Sample", expanded=False):
            st.markdown(f"""
            Here's a quick look at the first few rows of your selected table: **`{selected_table}`**.
            This uses `st.dataframe()` to display the data.
            """)
            with st.spinner(f"Loading data sample from {selected_table}..."):
                table_data_sample = get_table_data(session, selected_db, selected_schema, selected_table, num_rows=50)
                if not table_data_sample.empty:
                    st.dataframe(table_data_sample, height=300)
                else:
                    st.warning("No data to display or table is empty.")

        # Section 2: Basic Charting
        st.subheader("📊 Basic Column Visualization")
        st.markdown("""
        Select a column and a chart type to visualize its data. This helps in understanding distributions or trends.
        We'll use `st.selectbox` for choices and Streamlit's native charting functions like `st.bar_chart` or `st.line_chart`.
        """)

        # Identify numeric and date/timestamp columns for charting
        numeric_cols = [col for col, dtype in columns_info if any(t in dtype.upper() for t in ['NUMBER', 'INT', 'FLOAT', 'DOUBLE', 'DECIMAL'])]
        date_time_cols = [col for col, dtype in columns_info if any(t in dtype.upper() for t in ['DATE', 'TIMESTAMP'])]

        if not numeric_cols:
            st.warning("No numeric columns found in this table for basic charting.")
        else:
            col_to_viz = st.selectbox("Select a Numeric Column for Visualization:", numeric_cols, index=0 if numeric_cols else -1)

            if col_to_viz:
                chart_type = st.selectbox("Select Chart Type:", ["Bar Chart", "Line Chart", "Area Chart"], help="Choose how to display the selected column's data.")

                # Fetch data for the selected column (can be a larger sample or aggregated)
                # For simplicity, we'll use the initially fetched sample, but in a real app, you might re-query.
                # For this demo, let's assume we want to plot the values directly if they are not too many,
                # or an aggregation if they are.
                # For simplicity, we'll use the existing sample data.
                viz_data_sample = get_table_data(session, selected_db, selected_schema, selected_table, num_rows=1000) # Get a bit more for viz

                if not viz_data_sample.empty and col_to_viz in viz_data_sample.columns:
                    # Ensure the column is numeric for plotting
                    try:
                        viz_data_sample[col_to_viz] = pd.to_numeric(viz_data_sample[col_to_viz], errors='coerce')
                        viz_data_sample.dropna(subset=[col_to_viz], inplace=True) # Remove rows where conversion failed

                        if chart_type == "Bar Chart":
                            st.bar_chart(viz_data_sample[col_to_viz])
                            st.caption(f"Bar chart of '{col_to_viz}'. Shows the magnitude of each data point.")
                        elif chart_type == "Line Chart":
                            st.line_chart(viz_data_sample[col_to_viz])
                            st.caption(f"Line chart of '{col_to_viz}'. Useful for trends if data is ordered (e.g., by time).")
                        elif chart_type == "Area Chart":
                            st.area_chart(viz_data_sample[col_to_viz])
                            st.caption(f"Area chart of '{col_to_viz}'. Similar to line chart but fills the area below the line.")

                        st.markdown(f"""
                        **Streamlit Tip:** The chart above was generated with `st.{chart_type.lower().replace(" ", "_")}(data)`.
                        Streamlit makes it super simple to create charts from Pandas DataFrames or Series!
                        """)
                    except Exception as e:
                        st.error(f"Could not plot column '{col_to_viz}'. Error: {e}")
                else:
                    st.warning(f"Column '{col_to_viz}' not found in the data sample or sample is empty.")

        # Section 3: Map Visualization
        st.subheader("🗺️ Map Visualization")
        st.markdown("""
        If your table has latitude and longitude data, you can plot it on a map!
        `st.map()` is the magic function here. It looks for columns named 'lat', 'latitude', 'lon', or 'longitude' by default.
        If your columns have different names, select them below.
        """)

        # Try to auto-detect common lat/lon column names
        potential_lat_cols = [col for col in column_names if col.strip().lower() in ['lat', 'latitude', 'lat_','latitude_']]
        potential_lon_cols = [col for col in column_names if col.strip().lower() in ['lon', 'long', 'longitude', 'lng', 'lon_', 'long_', 'longitude_', 'lng_']]

        # Allow user to select lat/lon columns
        lat_col_name = st.selectbox(
            "Select Latitude Column:",
            column_names,
            index=column_names.index(potential_lat_cols[0]) if potential_lat_cols else 0,
            help="Choose the column containing latitude values."
        )
        lon_col_name = st.selectbox(
            "Select Longitude Column:",
            column_names,
            index=column_names.index(potential_lon_cols[0]) if potential_lon_cols else 1 if len(column_names) > 1 else 0,
            help="Choose the column containing longitude values."
        )

        if lat_col_name and lon_col_name and lat_col_name != lon_col_name:
            if st.button("📍 Plot Map", help="Click to generate the map with selected latitude and longitude."):
                with st.spinner("Preparing map data..."):
                    # Fetch data again, ensuring lat/lon columns are present
                    # For map, we might want all rows or a significant sample if the table is large
                    map_data_pd = get_table_data(session, selected_db, selected_schema, selected_table, num_rows=10000) # Fetch more rows for map

                    if not map_data_pd.empty and lat_col_name in map_data_pd.columns and lon_col_name in map_data_pd.columns:
                        # Prepare data for st.map - it needs columns named 'lat' and 'lon' or 'latitude' and 'longitude'
                        # Create a copy to avoid modifying the cached DataFrame
                        map_display_data = map_data_pd[[lat_col_name, lon_col_name]].copy()

                        # Convert to numeric and drop NaNs
                        map_display_data[lat_col_name] = pd.to_numeric(map_display_data[lat_col_name], errors='coerce')
                        map_display_data[lon_col_name] = pd.to_numeric(map_display_data[lon_col_name], errors='coerce')
                        map_display_data.dropna(subset=[lat_col_name, lon_col_name], inplace=True)

                        # Rename columns if necessary for st.map compatibility
                        # st.map is flexible, but being explicit can help.
                        # Let's try to use the names as is first, st.map is often smart enough.
                        # If st.map requires specific names 'latitude'/'longitude', uncomment the renaming:
                        # map_display_data.rename(columns={lat_col_name: 'latitude', lon_col_name: 'longitude'}, inplace=True)

                        if not map_display_data.empty:
                            st.map(map_display_data, latitude=lat_col_name, longitude=lon_col_name)
                            st.caption(f"Map showing locations from '{lat_col_name}' and '{lon_col_name}'.")
                            st.markdown("""
                            **Streamlit Tip:** This map was created with `st.map(data, latitude='your_lat_col', longitude='your_lon_col')`.
                            It's that easy to add geospatial visualizations!
                            """)
                        else:
                            st.warning("No valid latitude/longitude pairs found after processing. Check column data types and content.")
                    else:
                        st.error(f"Could not find columns '{lat_col_name}' or '{lon_col_name}' in the table, or table is empty.")
        elif lat_col_name == lon_col_name and lat_col_name is not None:
            st.warning("Latitude and Longitude columns must be different.")
        else:
            st.info("Select valid latitude and longitude columns to plot a map.")

    elif not (selected_db and selected_schema and selected_table):
        st.info("Please select a database, schema, and table from the sidebar to begin exploring.")

    # --- Concluding Remarks ---
    st.sidebar.markdown("---")
    st.sidebar.markdown("Made with ❤️ using [Streamlit](https://streamlit.io/) in [Snowflake](https://www.snowflake.com/).")
    st.sidebar.markdown("This app is a starting point. Explore Streamlit's documentation to discover more features!")

# Entry point for the Streamlit app
if __name__ == "__main__":
    main()