import streamlit as st
import pandas as pd
import sqlite3
import pydeck as pdk
import joblib

@st.cache_data
def load_data():
    """
    Loads the transformed service request data from the SQLite database.
    Parses datetime columns for further analysis.
    
    Returns:
        pd.DataFrame: The transformed service request data.
    """
    conn = sqlite3.connect('commonwealth_connect.db')
    df = pd.read_sql(
        'SELECT * FROM service_requests_transformed',
        conn,
        parse_dates=[
            'ticket_created_date_time',
            'ticket_closed_date_time',
            'ticket_last_updated_date_time'
        ]
    )
    conn.close()
    return df

# Load data and model
df = load_data()
model = joblib.load('time_to_close_model.joblib')

st.title("Commonwealth Connect Service Requests")

# --- Sidebar filters ---
st.sidebar.header("Filters")

# Date range filter
"""
Allows users to filter service requests by a date range.
The start and end dates are selected using a date input widget.
"""
min_date = df['ticket_created_date_time'].min().date()
max_date = df['ticket_created_date_time'].max().date()
start_date = st.sidebar.date_input(
    "Start Date",
    value=pd.to_datetime("2025-01-01").date(),  # Default to 2025/01/01
    min_value=min_date,
    max_value=max_date
)
end_date = st.sidebar.date_input(
    "End Date",
    value=max_date,
    min_value=min_date,
    max_value=max_date
)

# Ticket status filter
"""
Allows users to filter service requests by their status (e.g., Open, Closed).
The statuses are selected using a multiselect widget.
"""
all_statuses = df['ticket_status'].dropna().unique().tolist()
selected_status = st.sidebar.multiselect(
    "Ticket Status",
    options=sorted(all_statuses),
    default=["Open", "Acknowledged"]  # Default to "Open" and "Acknowledged"
)

# --- Prediction UI ---
st.sidebar.header("Predict Time to Close")
"""
Provides a UI for users to input features (e.g., issue category, weekday, month, hour)
and predict the time to close a service request using the trained model.
"""
pred_cat = st.sidebar.selectbox(
    "Issue Category",
    sorted(df['issue_category'].dropna().unique()),
    index=sorted(df['issue_category'].dropna().unique()).index("Missed Recycling Pickup")  # Default to "Missed Recycling Pickup"
)
pred_weekday = st.sidebar.selectbox(
    "Created Weekday",
    sorted(df['ticket_created_date_time_weekday'].dropna().unique())
)
pred_month = st.sidebar.slider("Created Month (1-12)", 1, 12, value=min_date.month)  # Default to the minimum date's month
pred_hour = st.sidebar.slider("Created Hour (0-23)", 0, 23, value=12)  # Default to 12 PM

# Apply all filters
"""
Applies the selected filters (date range and ticket status) to the dataset.
Displays filtered data and visualizations, including a bar chart and a map.
"""
if start_date > end_date:
    st.sidebar.error("Start date must be on or before end date.")
else:
    mask_date = (
        (df['ticket_created_date_time'].dt.date >= start_date) &
        (df['ticket_created_date_time'].dt.date <= end_date)
    )
    mask_status = df['ticket_status'].isin(selected_status)
    filtered = df.loc[mask_date & mask_status]

    # Display counts with status breakdown
    st.subheader(f"Issue Type Counts ({start_date} → {end_date})")
    st.markdown(f"Showing {len(filtered)} requests with status: {', '.join(selected_status)}")
    
    # Calculate total counts and counts by status
    counts = (
        filtered.groupby(['issue_type', 'ticket_status'])
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )
    counts['total_count'] = counts.iloc[:, 1:].sum(axis=1)  # Sum across all status columns

    # Reorder columns explicitly
    column_order = ['issue_type', 'total_count', 'Open', 'Acknowledged', 'Closed', 'Archived']
    counts = counts.reindex(columns=[col for col in column_order if col in counts.columns], fill_value=0)

    # Sort by total_count
    counts = counts.sort_values(by='total_count', ascending=False)

    # Filter out issues with a total count of less than 1
    counts = counts[counts['total_count'] > 0.5]

    # Restrict to top 20 counts and sort by total_count in descending order
    top_counts = counts.head(20).sort_values(by='total_count', ascending=False)

    st.dataframe(top_counts)
    st.subheader("Top 20 Issue Types by Total Count")  # Adjust title for the bar chart
    st.bar_chart(top_counts.set_index('issue_type')['total_count'])

    # Predictive input and output
    """
    Uses the trained model to predict the time to close a service request based on user inputs.
    Displays the predicted time in hours.
    """
    X_pred = pd.DataFrame([{
        'issue_category': pred_cat,
        'ticket_created_date_time_weekday': pred_weekday,
        'ticket_created_date_time_month': pred_month,
        'ticket_created_date_time_hour': pred_hour
    }])
    pred_hours = model.predict(X_pred)[0]
    st.sidebar.markdown(f"**Predicted time to close:** {pred_hours:.1f} hours")

    # Map of requests
    """
    Displays a map of service requests using PyDeck.
    Each request is represented as a scatterplot point with a tooltip showing details.
    """
    st.subheader("Map of Requests")
    map_df = (
        filtered
        .dropna(subset=['lat', 'lng'])
        .rename(columns={'lng': 'lon'})
        .assign(
            created_str=lambda d: d['ticket_created_date_time'].dt.strftime('%Y-%m-%d %H:%M:%S')
        )
    )
    map_df_small = map_df[['lat', 'lon', 'issue_type', 'ticket_status', 'created_str']]
    midpoint = (map_df_small['lat'].mean(), map_df_small['lon'].mean())

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_df_small,
        get_position=["lon", "lat"],
        get_color=[255, 0, 0, 160],  # Static red color
        get_radius=50,
        pickable=True
    )

    deck = pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state=pdk.ViewState(
            latitude=midpoint[0],
            longitude=midpoint[1],
            zoom=11,
            pitch=50
        ),
        layers=[layer],
        tooltip={
            "html": "<b>Issue:</b> {issue_type}<br/>"
                    "<b>Status:</b> {ticket_status}<br/>"
                    "<b>Created:</b> {created_str}",
            "style": {"color": "white"}
        }
    )

    st.pydeck_chart(deck)
