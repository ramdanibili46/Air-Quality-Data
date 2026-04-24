import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from datetime import datetime

sns.set(style='dark')

# Helper function yang dibutuhkan untuk menyiapkan berbagai dataframe

def create_daily_pm25_df(df):
    """Create daily PM2.5 dataframe"""
    daily_pm25_df = df.resample(rule='D', on='datetime').agg({
        "PM2.5": "mean",
        "PM10": "mean",
        "TEMP": "mean",
        "WSPM": "mean"
    })
    daily_pm25_df = daily_pm25_df.reset_index()
    daily_pm25_df.rename(columns={
        "PM2.5": "avg_pm25",
        "PM10": "avg_pm10",
        "TEMP": "avg_temp",
        "WSPM": "avg_wspm"
    }, inplace=True)
    
    # Add rolling average
    daily_pm25_df['pm25_rolling'] = daily_pm25_df['avg_pm25'].rolling(window=7, center=True).mean()
    
    return daily_pm25_df

def create_seasonal_stats_df(df):
    """Create seasonal statistics dataframe"""
    seasonal_stats = df.groupby('season')['PM2.5'].agg(['mean', 'median', 'std', 'max', 'min']).round(1)
    seasonal_stats.columns = ['Mean', 'Median', 'Std Dev', 'Max', 'Min']
    seasons_order = ['Winter', 'Spring', 'Summer', 'Fall']
    seasonal_stats = seasonal_stats.reindex(seasons_order)
    seasonal_stats = seasonal_stats.reset_index()
    seasonal_stats.rename(columns={'index': 'season'}, inplace=True)
    
    return seasonal_stats

def create_hourly_stats_df(df):
    """Create hourly statistics dataframe per season"""
    hourly_stats = df.groupby(['season', 'hour'])['PM2.5'].agg(['mean', 'median', 'std']).round(1)
    hourly_stats = hourly_stats.reset_index()
    hourly_stats.columns = ['season', 'hour', 'mean_pm25', 'median_pm25', 'std_pm25']
    
    return hourly_stats

def create_peak_hours_df(df):
    """Identify peak hours per season"""
    hourly_avg = df.groupby(['season', 'hour'])['PM2.5'].mean().reset_index()
    peak_hours = hourly_avg.loc[hourly_avg.groupby('season')['PM2.5'].idxmax()]
    peak_hours = peak_hours.reset_index(drop=True)
    peak_hours.rename(columns={'PM2.5': 'peak_value'}, inplace=True)
    
    return peak_hours

def create_correlation_df(df, season='Winter'):
    """Create correlation matrix for selected season"""
    corr_cols = ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3', 'TEMP', 'PRES', 'DEWP', 'WSPM']
    corr_matrix = df[df['season'] == season][corr_cols].corr()
    return corr_matrix

def create_meteorology_corr_df(df, season='Winter'):
    """Get correlation of PM2.5 with meteorological factors"""
    season_data = df[df['season'] == season]
    corr_data = {
        'Factor': ['Temperature (TEMP)', 'Pressure (PRES)', 'Dew Point (DEWP)', 'Wind Speed (WSPM)'],
        'Correlation': [
            season_data['PM2.5'].corr(season_data['TEMP']),
            season_data['PM2.5'].corr(season_data['PRES']),
            season_data['PM2.5'].corr(season_data['DEWP']),
            season_data['PM2.5'].corr(season_data['WSPM'])
        ]
    }
    corr_df = pd.DataFrame(corr_data)
    return corr_df

def create_yearly_summary_df(df):
    """Create yearly summary dataframe"""
    yearly_summary = df.groupby('year').agg({
        'PM2.5': ['mean', 'max', 'min'],
        'TEMP': 'mean',
        'WSPM': 'mean'
    }).round(1)
    
    yearly_summary.columns = ['Avg PM2.5', 'Max PM2.5', 'Min PM2.5', 'Avg Temp', 'Avg Wind Speed']
    yearly_summary = yearly_summary.reset_index()
    
    return yearly_summary

# Load cleaned data
@st.cache_data
def load_data():
    df = pd.read_csv("hasil.csv")
    
    # Convert datetime columns
    df['datetime'] = pd.to_datetime(df['datetime'])
    
    # Sort by datetime
    df = df.sort_values('datetime')
    df = df.reset_index(drop=True)
    
    return df

# Load data
with st.spinner('Loading air quality data...'):
    all_df = load_data()

# Get date range
min_date = all_df["datetime"].min()
max_date = all_df["datetime"].max()

# Side Bar

with st.sidebar:
    st.markdown("## 🌍 Air Quality Analysis")
    st.markdown("---")
    
    # Date range filter
    start_date, end_date = st.date_input(
        label='Date Range',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
    
    st.markdown("---")
    
    # Season filter for correlation
    selected_season = st.selectbox(
        "Select Season for Correlation Analysis",
        options=['Winter', 'Spring', 'Summer', 'Fall']
    )
    
    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.markdown("""
    **Data Source:** Beijing PM2.5 Data (2013-2017)
    
    **Station:** Aotizhongxin, Beijing
    
    **Analysis:** PM2.5 pollution patterns and meteorological factors
    """)

# Filter data based on date range
main_df = all_df[(all_df["datetime"] >= pd.Timestamp(start_date)) & 
                 (all_df["datetime"] <= pd.Timestamp(end_date))]

# Prepare dataframes

daily_pm25_df = create_daily_pm25_df(main_df)
seasonal_stats_df = create_seasonal_stats_df(main_df)
hourly_stats_df = create_hourly_stats_df(main_df)
peak_hours_df = create_peak_hours_df(main_df)
corr_matrix = create_correlation_df(main_df, selected_season)
meteorology_corr_df = create_meteorology_corr_df(main_df, selected_season)
yearly_summary_df = create_yearly_summary_df(main_df)

# Header

st.header('🌍 Air Quality Analysis Dashboard :cloud:')
st.markdown("### PM2.5 Pollution Patterns and Meteorological Factors (2013-2017)")

# ==================== DAILY PM2.5 TREND ====================

st.subheader('📈 Daily PM2.5 Trend')

col1, col2, col3 = st.columns(3)

with col1:
    avg_pm25 = main_df['PM2.5'].mean()
    st.metric("Average PM2.5", value=f"{avg_pm25:.1f} µg/m³")

with col2:
    max_pm25 = main_df['PM2.5'].max()
    st.metric("Maximum PM2.5", value=f"{max_pm25:.0f} µg/m³")

with col3:
    unhealthy_pct = (main_df['PM2.5'] > 100).mean() * 100
    st.metric("Unhealthy Days (>100)", value=f"{unhealthy_pct:.1f}%")

# Plot daily PM2.5 trend
fig, ax = plt.subplots(figsize=(16, 8))

ax.plot(
    daily_pm25_df["datetime"],
    daily_pm25_df["avg_pm25"],
    marker='o',
    linewidth=1.5,
    color="#90CAF9",
    markersize=3,
    alpha=0.5,
    label='Daily PM2.5'
)
ax.plot(
    daily_pm25_df["datetime"],
    daily_pm25_df["pm25_rolling"],
    linewidth=2.5,
    color="#FF6B6B",
    label='7-Day Rolling Average'
)

ax.axhline(y=100, color='red', linestyle='--', linewidth=1.5, alpha=0.7, label='Unhealthy Level (100)')

ax.set_title(f'PM2.5 Trend ({start_date} to {end_date})', fontsize=18, pad=20)
ax.set_xlabel('Date', fontsize=14)
ax.set_ylabel('PM2.5 (µg/m³)', fontsize=14)
ax.tick_params(axis='x', labelsize=10, rotation=45)
ax.tick_params(axis='y', labelsize=12)
ax.legend(loc='upper right', fontsize=12)
ax.grid(True, alpha=0.3)

st.pyplot(fig)

# Seasonal Analysis

st.subheader("🌿 Seasonal Analysis")

col1, col2 = st.columns(2)

with col1:
    # Seasonal statistics table
    st.markdown("### Seasonal PM2.5 Statistics")
    st.dataframe(seasonal_stats_df, use_container_width=True, hide_index=True)

with col2:
    # Seasonal bar chart
    fig, ax = plt.subplots(figsize=(10, 6))
    
    colors_bar = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
    bars = ax.bar(seasonal_stats_df['season'], seasonal_stats_df['Mean'], 
                  color=colors_bar, edgecolor='black', linewidth=1.5)
    
    for bar, value in zip(bars, seasonal_stats_df['Mean']):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                f'{value:.1f}', ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    ax.set_title('Average PM2.5 by Season', fontsize=16, pad=15)
    ax.set_xlabel('Season', fontsize=13)
    ax.set_ylabel('Average PM2.5 (µg/m³)', fontsize=13)
    ax.tick_params(axis='both', labelsize=11)
    ax.set_ylim(0, 110)
    ax.axhline(y=100, color='red', linestyle='--', linewidth=1.5, alpha=0.7, label='Unhealthy Level')
    ax.legend(fontsize=10)
    ax.grid(axis='y', alpha=0.3)
    
    st.pyplot(fig)

# Hourly pattern

st.subheader("⏰ Daily PM2.5 Pattern by Season")

fig, ax = plt.subplots(figsize=(14, 7))

colors_line = {'Winter': '#1f77b4', 'Spring': '#ff7f0e', 'Summer': '#2ca02c', 'Fall': '#d62728'}

for season in ['Winter', 'Spring', 'Summer', 'Fall']:
    data = hourly_stats_df[hourly_stats_df['season'] == season]
    ax.plot(data['hour'], data['mean_pm25'], marker='o', linewidth=2, 
            label=season, color=colors_line[season], markersize=6)

ax.axvline(x=7, color='gray', linestyle='--', alpha=0.5, label='Morning Peak (7 AM)')
ax.axvline(x=21, color='gray', linestyle='--', alpha=0.5, label='Evening Peak (9 PM)')
ax.axhline(y=100, color='red', linestyle='--', linewidth=1.5, alpha=0.7, label='Unhealthy Level')

ax.set_title('Daily PM2.5 Pattern by Season (2013-2017)', fontsize=16, pad=15)
ax.set_xlabel('Hour of Day', fontsize=13)
ax.set_ylabel('Average PM2.5 (µg/m³)', fontsize=13)
ax.tick_params(axis='both', labelsize=11)
ax.legend(loc='upper right', fontsize=11)
ax.grid(True, alpha=0.3)
ax.set_xticks(range(0, 24, 2))

st.pyplot(fig)

# Peak hours table
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### Peak Hours by Season")
    st.dataframe(peak_hours_df, use_container_width=True, hide_index=True)

with col2:
    st.markdown("### 💡 Pattern Insight")
    st.markdown("""
    - **Morning peaks** occur around 7-10 AM (rush hour)
    - **Evening peaks** occur around 9-11 PM
    - **Lower pollution** during afternoon hours (1-5 PM)
    - **Winter** shows most extreme patterns
    - **Summer** has the lowest PM2.5 levels
    """)

# Yearly summary

st.subheader("📊 Yearly Summary")

fig, ax = plt.subplots(figsize=(12, 6))

years = yearly_summary_df['year'].astype(str)
avg_pm25 = yearly_summary_df['Avg PM2.5']
max_pm25 = yearly_summary_df['Max PM2.5']

x = range(len(years))
width = 0.35

bars1 = ax.bar([i - width/2 for i in x], avg_pm25, width, label='Average PM2.5', color='#4ECDC4')
bars2 = ax.bar([i + width/2 for i in x], max_pm25, width, label='Maximum PM2.5', color='#FF6B6B')

for bar, val in zip(bars1, avg_pm25):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
            f'{val:.0f}', ha='center', va='bottom', fontsize=10)

for bar, val in zip(bars2, max_pm25):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
            f'{val:.0f}', ha='center', va='bottom', fontsize=10)

ax.set_xlabel('Year', fontsize=13)
ax.set_ylabel('PM2.5 (µg/m³)', fontsize=13)
ax.set_title('Yearly PM2.5 Summary (2013-2017)', fontsize=16, pad=15)
ax.set_xticks(x)
ax.set_xticklabels(years)
ax.legend(loc='upper right', fontsize=11)
ax.grid(axis='y', alpha=0.3)

st.pyplot(fig)

# Correlation analysis

st.subheader("🔬 Correlation Analysis: PM2.5 vs Meteorological Factors")

# Correlation heatmap
fig, ax = plt.subplots(figsize=(12, 10))

sns.heatmap(
    corr_matrix,
    annot=True,
    fmt='.2f',
    cmap='RdBu_r',
    center=0,
    square=True,
    linewidths=0.5,
    cbar_kws={"shrink": 0.8},
    ax=ax
)

ax.set_title(f'Correlation Matrix - {selected_season} Season', fontsize=16, pad=20)
ax.tick_params(axis='both', labelsize=10)

st.pyplot(fig)

# Meteorological correlations
col1, col2 = st.columns(2)

with col1:
    st.markdown(f"### PM2.5 Correlations - {selected_season}")
    st.dataframe(meteorology_corr_df, use_container_width=True, hide_index=True)

with col2:
    # Create correlation bar chart
    fig, ax = plt.subplots(figsize=(8, 5))
    
    colors_corr = ['#45B7D1' if x > 0 else '#FF6B6B' for x in meteorology_corr_df['Correlation']]
    bars = ax.barh(meteorology_corr_df['Factor'], meteorology_corr_df['Correlation'], 
                   color=colors_corr, edgecolor='black', linewidth=1)
    
    for bar, val in zip(bars, meteorology_corr_df['Correlation']):
        ax.text(bar.get_width() + 0.01 if val > 0 else bar.get_width() - 0.08,
                bar.get_y() + bar.get_height()/2, f'{val:.3f}', 
                va='center', fontsize=10)
    
    ax.axvline(x=0, color='black', linewidth=0.8)
    ax.set_xlabel('Correlation Coefficient', fontsize=12)
    ax.set_title(f'PM2.5 Correlation with Meteorological Factors\n({selected_season})', fontsize=12)
    ax.tick_params(axis='y', labelsize=10)
    ax.grid(axis='x', alpha=0.3)
    
    st.pyplot(fig)

# Correlation insights
st.markdown("### 📊 Correlation Insights")
st.markdown(f"""
**Based on {selected_season} season data:**

- **Temperature (TEMP):** {meteorology_corr_df.loc[0, 'Correlation']:.3f} - {'Negative' if meteorology_corr_df.loc[0, 'Correlation'] < 0 else 'Positive'} correlation
- **Pressure (PRES):** {meteorology_corr_df.loc[1, 'Correlation']:.3f} - {'Negative' if meteorology_corr_df.loc[1, 'Correlation'] < 0 else 'Positive'} correlation
- **Dew Point (DEWP):** {meteorology_corr_df.loc[2, 'Correlation']:.3f} - {'Negative' if meteorology_corr_df.loc[2, 'Correlation'] < 0 else 'Positive'} correlation
- **Wind Speed (WSPM):** {meteorology_corr_df.loc[3, 'Correlation']:.3f} - {'Negative' if meteorology_corr_df.loc[3, 'Correlation'] < 0 else 'Positive'} correlation

**Key Findings:**
- Higher humidity (DEWP) tends to increase PM2.5 concentration
- Higher wind speed helps disperse air pollutants
- Temperature shows stronger negative correlation in winter
""")

# Scatter plots

st.subheader("📉 PM2.5 vs Meteorological Factors")

# Prepare data for selected season
season_data = main_df[main_df['season'] == selected_season]

# Create scatter plots
fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(14, 10))

# Scatter 1: PM2.5 vs Temperature
axes[0, 0].scatter(season_data['TEMP'], season_data['PM2.5'], 
                   alpha=0.3, color='#45B7D1', s=20)
axes[0, 0].axhline(y=100, color='red', linestyle='--', linewidth=1.5, alpha=0.7)
axes[0, 0].set_xlabel('Temperature (°C)', fontsize=12)
axes[0, 0].set_ylabel('PM2.5 (µg/m³)', fontsize=12)
axes[0, 0].set_title(f'PM2.5 vs Temperature ({selected_season})', fontsize=12)
axes[0, 0].grid(True, alpha=0.3)

# Scatter 2: PM2.5 vs Dew Point
axes[0, 1].scatter(season_data['DEWP'], season_data['PM2.5'], 
                   alpha=0.3, color='#FF6B6B', s=20)
axes[0, 1].axhline(y=100, color='red', linestyle='--', linewidth=1.5, alpha=0.7)
axes[0, 1].set_xlabel('Dew Point Temperature (°C)', fontsize=12)
axes[0, 1].set_ylabel('PM2.5 (µg/m³)', fontsize=12)
axes[0, 1].set_title(f'PM2.5 vs Dew Point ({selected_season})', fontsize=12)
axes[0, 1].grid(True, alpha=0.3)

# Scatter 3: PM2.5 vs Pressure
axes[1, 0].scatter(season_data['PRES'], season_data['PM2.5'], 
                   alpha=0.3, color='#96CEB4', s=20)
axes[1, 0].axhline(y=100, color='red', linestyle='--', linewidth=1.5, alpha=0.7)
axes[1, 0].set_xlabel('Pressure (hPa)', fontsize=12)
axes[1, 0].set_ylabel('PM2.5 (µg/m³)', fontsize=12)
axes[1, 0].set_title(f'PM2.5 vs Pressure ({selected_season})', fontsize=12)
axes[1, 0].grid(True, alpha=0.3)

# Scatter 4: PM2.5 vs Wind Speed
axes[1, 1].scatter(season_data['WSPM'], season_data['PM2.5'], 
                   alpha=0.3, color='#4ECDC4', s=20)
axes[1, 1].axhline(y=100, color='red', linestyle='--', linewidth=1.5, alpha=0.7)
axes[1, 1].set_xlabel('Wind Speed (m/s)', fontsize=12)
axes[1, 1].set_ylabel('PM2.5 (µg/m³)', fontsize=12)
axes[1, 1].set_title(f'PM2.5 vs Wind Speed ({selected_season})', fontsize=12)
axes[1, 1].grid(True, alpha=0.3)

plt.tight_layout()
st.pyplot(fig)

# Data preview

st.subheader("📋 Data Preview")

with st.expander("View Raw Data"):
    st.dataframe(main_df.head(100), use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Descriptive Statistics**")
        st.dataframe(main_df.describe(), use_container_width=True)
    
    with col2:
        st.markdown("**Dataset Information**")
        st.markdown(f"- Total records: {len(main_df):,}")
        st.markdown(f"- Date range: {start_date} to {end_date}")
        st.markdown(f"- Columns: {', '.join(main_df.columns)}")
        st.markdown(f"- Stations: {main_df['station'].unique()[0]}")



# ==================== FOOTER ====================

st.markdown("---")
st.caption('Copyright © 2026 | Air Quality Analysis Dashboard | Data Source: https://github.com/marceloreis/HTI/tree/master')
