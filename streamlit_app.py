import streamlit as st
import pandas as pd
from datetime import datetime
import altair as alt
import numpy as np

# Set page layout to wide
st.set_page_config(layout="wide")

st.title("ParlaMint NL Topic Detection")
st.write()

# Load data
@st.cache_data
def load_data(scaling_factor = 0.8, name_topics=True):
    df = pd.read_csv('data/processed/debate_topics.csv')
    
    # This is a temporary solution to scale down the data, as the probabilities of the LDA model are too high
    df["Probability"] = df["Probability"] * (scaling_factor + np.random.uniform(-0.1, 0.1))

    # Again a temporary solution as the zero-shot-classifiation model did not work as expected for the candidate topics
    if name_topics:
        num_topics = df['Topic'].nunique()
        random_topic_names = ["security", "geopolitics", "technologies", "energy", "crime", "climate", "defence"]
        topic_mapping = {i: random_topic_names[i % len(random_topic_names)] for i in range(num_topics)}
        df['Topic'] = df['Topic'].map(topic_mapping)

    return df

data = load_data()

# Sidebar widgets
with st.sidebar:
    # Add a toggle switch to switch between daily and weekly views
    view_mode = st.radio(
        "View Mode",
        ('Daily', 'Weekly'),
        index=1,
        key='view_mode_toggle'
    )

    # Date slider
    min_date = datetime.strptime(data['Date'].min(), '%Y-%m-%d')
    max_date = datetime.strptime(data['Date'].max(), '%Y-%m-%d')
    start_date, end_date = st.slider(
        "Select date range",
        min_value=min_date,
        max_value=max_date,
        value=(min_date, max_date),
        format="YYYY MMM DD",
        key="date_slider",
        label_visibility="collapsed"
    )

    # Reduce the width of the slider
    st.markdown(
        """
        <style>
        .stSlider {
            width: 100% !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Add a multiselect widget to filter topics
    selected_topics = st.multiselect(
        "Select topics",
        options=data['Topic'].unique(),
        default=data['Topic'].unique()
    )

### Filter Data


# Filter data based on date range
filtered_data = data[(data['Date'] >= start_date.strftime('%Y-%m-%d')) & (data['Date'] <= end_date.strftime('%Y-%m-%d'))]
filtered_data['Date'] = pd.to_datetime(filtered_data['Date'])

# Add a new column 'Date_dist' to distribute topics equally over the day
def distribute_topics(df, mode=view_mode.lower()):
    if mode == 'daily':
        df['Date_dist'] = df['Date']
        unique_dates = df['Date'].unique()
        for date in unique_dates:
            date_mask = df['Date'] == date
            topics_count = date_mask.sum()
            hours_to_add = np.linspace(3, 21, topics_count, endpoint=False)
            df.loc[date_mask, 'Date_dist'] = df.loc[date_mask, 'Date'] + pd.to_timedelta(hours_to_add, unit='h')
        return df
    elif mode == 'weekly':
        df['Date_dist'] = df['Week']
        unique_weeks = df['Week'].unique()
        for week in unique_weeks:
            week_mask = df['Week'] == week
            topics_count = week_mask.sum()
            days_to_add = np.linspace(1, 5, topics_count, endpoint=False)
            df.loc[week_mask, 'Date_dist'] = df.loc[week_mask, 'Week'] + pd.to_timedelta(days_to_add, unit='d')
        return df


# Filter data based on selected topics
filtered_data = filtered_data[filtered_data['Topic'].isin(selected_topics)]

if view_mode == 'Weekly':
    filtered_data['Week'] = filtered_data['Date'].dt.to_period('W').apply(lambda r: r.start_time)
    filtered_data = filtered_data.groupby(['Week', 'Topic'], as_index=False).max().sort_values(['Week', 'Topic'])
    filtered_data = distribute_topics(filtered_data, mode=view_mode.lower())
    x_axis = alt.X('Date_dist:T', axis=alt.Axis(title='Week', format='%b %d', labelAngle=-45))
else:
    filtered_data = filtered_data.groupby(['Date', 'Topic'], as_index=False).max().sort_values(['Date', 'Topic'])
    filtered_data = distribute_topics(filtered_data, mode=view_mode.lower())
    x_axis = alt.X('Date_dist:T', axis=alt.Axis(title='Date', format='%b %d', labelAngle=-45))

### CHARTS
# Create the bars chart
import plotly.express as px
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events

# Assuming 'filtered_data' is your DataFrame
fig = go.Figure()

# Define a color map for distinct topic colors
color_map = px.colors.qualitative.Plotly

for i, topic in enumerate(filtered_data['Topic'].unique()):
    topic_data = filtered_data[filtered_data['Topic'] == topic]
    # add bars
    fig.add_trace(go.Bar(
        x=topic_data['Date_dist'],
        y=topic_data['Probability'],
        name=topic,
        showlegend=True,
        width=.08,
        marker=dict(
            line=dict(color=color_map[i % len(color_map)], width=1),
            color=color_map[i % len(color_map)],
            opacity=topic_data['Probability'] * 0.8
        ),
        legendgroup=topic,
        customdata=topic_data['Date'],
        hovertemplate='Date: %{customdata}<br>Probability: %{y}<extra></extra>',
    ))
    # Add points
    fig.add_trace(go.Scatter(
        x=topic_data['Date_dist'],
        y=topic_data['Probability'],
        mode='markers',
        name=topic,
        marker=dict(
            color=color_map[i % len(color_map)],
            opacity=topic_data['Probability'] * 0.8,
            size=10
        ),
        showlegend=False,
        legendgroup=topic,
        customdata=topic_data['Date'],
        hovertemplate='Date: %{customdata}<br>Probability: %{y}<extra></extra>',
    ))

fig.update_layout(
    title='Topic Probabilities over Time',
    xaxis_title='Date',
    yaxis_title='Probability',
    height=500
)

# Display the figure using st.plotly_chart
st.plotly_chart(fig)


##### Bottom Page



