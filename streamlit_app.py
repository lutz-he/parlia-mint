import streamlit as st
import pandas as pd
from datetime import datetime
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Set page layout to wide
st.set_page_config(layout="wide")

# Custom CSS to change the default red color to navy blue
st.markdown(
    """
    <style>
    .stSlider > div > div > div > div > div {
        background: navy !important;
    }
    .stRadio > div > div > div > div > div {
        background: navy !important;
    }
    .stDateInput > div > div > div > div > div {
        background: navy !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("ParliaMint Prototype Dashboard")
with st.expander("ℹ️ Disclaimer", expanded=False):
    st.markdown("This dashboard is a prototype and is intended for demonstration purposes only.\nThe data displayed here is not real-time data and is for illustrative purposes only.")
    st.markdown("Using the date slider, you can select a date range to view the topics discussed in the parliament.\nYou can also switch between daily and weekly views using the toggle switch.")
    st.markdown("The bar chart shows the probability of topics discussed in the parliament over the selected date range.")
    st.markdown("The bottom section shows the summary, top 5 speakers, and topics discussed for each debate on the a selected date.")
    

# Load data
@st.cache_data
def load_data(scaling_factor=0.8, name_topics=True):
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

# Date slider
min_date = datetime.strptime(data['Date'].min(), '%Y-%m-%d')
max_date = datetime.strptime(data['Date'].max(), '%Y-%m-%d')
start_date, end_date = st.slider(
    "Select date range",
    min_value=min_date,
    max_value=max_date,
    value=(datetime(2022, 1, 22), datetime(2022, 4, 7)),
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

# Add a toggle switch to switch between daily and weekly views
view_mode = st.radio(
    "View Mode",
    ('Daily', 'Weekly'),
    index=1,
    key='view_mode_toggle'
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
    title='Which of the relevant topics are discussed in the parliament?',

    annotations=[
        dict(
            text="Data Source: ParliaMint",
            x=1,
            y=-0.15,
            showarrow=False,
            xref="paper",
            yref="paper",
            xanchor="right",
            yanchor="top",
            font=dict(size=12, color="gray")
        )
    ],
    xaxis_title='Date',
    yaxis_title='Probability',
    height=500,
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="left",
        x=0
    )
)

# Display the figure using st.plotly_chart
st.plotly_chart(fig)

##### Bottom Page
# Load summarise.csv
@st.cache_data
def load_summary_data():
    data = pd.read_csv('data/processed/summaries.csv')
    data['date'] = pd.to_datetime(data['date'])
    return data

@st.cache_data
def load_speaker_count_data():
    data = pd.read_csv('data/processed/speaker_count.csv')
    data['Date'] = pd.to_datetime(data['Date'])
    return data

summary_data = load_summary_data()
speaker_count_data = load_speaker_count_data()

# Date picker for summary data
summary_date = st.date_input(
    "Select date for summary data",
    min_value=filtered_data['Date'].min(),
    max_value=filtered_data['Date'].max(),
    value=filtered_data['Date'].min(),
    key="summary_date_picker"
)

# Reduce the width of the date input field
st.markdown(
    """
    <style>
    .stDateInput {
        width: 20% !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Filter summary data based on selected date
filtered_summary_data = summary_data[summary_data['date'] == pd.to_datetime(summary_date)]
filtered_speaker_count_data = speaker_count_data[speaker_count_data['Date'] == pd.to_datetime(summary_date)]
filtered_topic_data = data[pd.to_datetime(data['Date']) == pd.to_datetime(summary_date)]

# Display text boxes for each unique debate_num in filtered_summary_data
unique_debate_nums = filtered_summary_data['debate_num'].unique()

for debate_num in unique_debate_nums:
    debate_data = filtered_summary_data[filtered_summary_data['debate_num'] == debate_num]
    debate_data_speakers = filtered_speaker_count_data[filtered_speaker_count_data['Debate_Num'] == debate_num]
    debate_data_topics = filtered_topic_data[filtered_topic_data['Debate_Num'] == debate_num]
    
    with st.expander(f"**Debate Number: {debate_num}** | {debate_data['chamber'].values[0].capitalize()}", expanded=True):
        col1, col2, col3 = st.columns([15, 35, 50])

        with col1:
            st.markdown("### Topics")
            sorted_debate_data_topics = debate_data_topics.sort_values(by='Probability', ascending=False)
            for _, row in sorted_debate_data_topics.iterrows():
                topic = row['Topic']
                probability = row['Probability']
                color = color_map[filtered_data['Topic'].unique().tolist().index(topic) % len(color_map)]
                opacity = probability * 0.8
                st.markdown(
                    f"""
                    <div style='display: inline-block; padding: 5px 10px; margin: 5px; border-radius: 15px; background-color: {color}; opacity: {opacity}; color: white;'>
                    {topic}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        with col2:
            st.markdown("### Top 5 Speakers")
            top_5_speakers = debate_data_speakers.sort_values('size', ascending=False).head(5)[['Speaker_name', 'Speaker_party', 'Speaker_role']]
            st.write(top_5_speakers.to_html(index=False, header=False, border=0, classes='table-no-border'), unsafe_allow_html=True)
            st.markdown(
                """
                <style>
                .table-no-border {
                    border-collapse: collapse;
                }
                .table-no-border td, .table-no-border th {
                    border: none !important;
                }
                </style>
                """,
                unsafe_allow_html=True
            )

        with col3:
            st.markdown("### Summary")
            st.text(debate_data['summary'].values[0])
