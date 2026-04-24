# Air Quality Analysis Dashboard 
## Overview  


This project provides an interactive dashboard for analyzing PM2.5 air pollution patterns and meteorological factors in Beijing's Aotizhongxin station from 2013 to 2017. The dashboard visualizes PM2.5 trends, seasonal patterns, hourly fluctuations, and correlations with weather factors such as temperature, humidity, pressure, and wind speed. The analysis helps understand pollution patterns and supports data-driven decision-making for public health and environmental policies.

## Features  
- **Interactive Dashboard**: Built with Streamlit for data exploration.
- **Data Processing**: Loads and cleans PM2.5 data directly from the source URL
- **Seasonal Analysis**: Displays PM2.5 statistics for Winter, Spring, Summer, and Fall.
- **Correlation Analysis**: Heatmaps and scatter plots showing relationships between PM2.5 and meteorological factors:
  - Temperature (TEMP)
  - Pressure (PRES)
  - Dew Point (DEWP/Humidity)
  - Wind Speed (WSPM)
- **Yearly Trends**: Summary of PM2.5 averages and maximum per year.
- **Data Preview**: Raw data display and descriptive statistics.
## Algorithm Explanation  
### Data Loading and Cleaning  
- Load Beijing's Aotizhongxin station air quality data from https://github.com/marceloreis/HTI/blob/master/PRSA_Data_20130301-20170228/PRSA_Data_Aotizhongxin_20130301-20170228.csv
- Creates a `datetime` column from year, month, day, and hour components.
- Sorts data chronologically for time series analysis.

### Missing Value Handling
- Uses **linear interpolation** to fill missing values in numeric columns (PM2.5, PM10, SO2, NO2, CO, O3, TEMP, PRES, DEWP, RAIN, WSPM).
- Ensures continuous and complete data for accurate trend analysis.
### Season Classification
- Maps months to seasons using the following logic:
  - **Winter**: December, January, February
  - **Spring**: March, April, May
  - **Summer**: June, July, August
  - **Fall**: September, October, November
### Statistical Analysis
- Computes mean, median, standard deviation, maximum, and minimum PM2.5 for each season.
- Calculates hourly averages to identify peak pollution times.
- Generates correlation matrices to measure relationships between PM2.5 and meteorological factors.  
### Visualitzation
- Daily Trend Chart: Line plot with 7-day rolling average for PM2.5.
- Seasonal Bar Chart: Average PM2.5 comparison across seasons.
- Hourly Pattern Chart: Line plot showing PM2.5 variation by hour for each season.
- Correlation Heatmap: Color-coded matrix showing Pearson correlations.
- Scatter Plots: PM2.5 vs Temperature, Dew Point, Pressure, and Wind Speed.
## Output Format
The script generates a `hasil.csv` and streamlit dashboard  
## Future Improvements
- **Multi-station analysis**: Compare data from multiple monitoring stations in Beijing.

## Author
Bili Ramdani - [Github Profile](https://github.com/ramdanibili46)  
Built as submission for Dicoding's "Belajar Analisis Data dengan Python" course
## Setup Environment - Anaconda
```
conda create --name main-ds python=3.11
conda activate main-ds
pip install -r requirements.txt
```

## Setup Environment - Shell/Terminal
```
mkdir air-quality-analysis
cd air-quality-analysis
pipenv install
pipenv shell
pip install -r requirements.txt
```

## Run steamlit app
```
streamlit run dashboard.py
```
