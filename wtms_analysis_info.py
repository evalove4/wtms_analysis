import streamlit as st
import pandas as pd
import plotly.express as px

# Page configuration
st.set_page_config(page_title='Sensor Signals Visualization', layout='wide')
st.title('수질TMS 측정상수 시각화APP')

# File uploader
uploaded_file = st.file_uploader('Upload Excel file', type=['xlsx'])

if uploaded_file:
    # Read Excel, use second row (index 1) as header
    df = pd.read_excel(uploaded_file, header=1)
    
    # Rename key columns to English
    df.rename(columns={
        '방류구': 'Discharge Gate',
        '측정항목': 'Measurement Item',
        '단위': 'Unit',
        '측정일자': 'Date',
        '측정시간': 'Time',
        '기준치': 'Standard Value',
        '측정치': 'Measured Value',
        '상태정보': 'Status',
        'DUMP여부': 'Dump Flag'
    }, inplace=True)
    
    # Combine Date and Time into Datetime
    df['Time_clean'] = df['Time'].astype(str).str.replace('시', '').str.replace('분', '')
    df['Datetime'] = pd.to_datetime(df['Date'].astype(str) + ' ' + df['Time_clean'], errors='coerce')
    df.set_index('Datetime', inplace=True)
    
    # Measurement items to visualize
    items = ['TOC', 'SS', 'T-N', 'T-P', 'pH']
    scale_options = [1, 2, 5, 10, 20, 100]
    
    # Iterate through each measurement item
    for item in items:
        st.header(f'{item} Sensor Signals')
        df_item = df[df['Measurement Item'] == item]
        
        if df_item.empty:
            st.write(f'No data available for {item}.')
            continue
        
        # Define sensor columns per item
        sensors = ['MSIG', 'MSAM']
        if item == 'TOC':
            sensors.append('MFC')
        if item == 'pH':
            sensors.append('MTM1')
        else:
            sensors.append('MTM2')
        sensors.append('Measured Value')
        
        # Collect individual multipliers for each sensor
        multipliers = {}
        st.subheader('Select Scale Multiplier per Signal')
        cols = st.columns(len(sensors))
        for i, sensor in enumerate(sensors):
            multipliers[sensor] = cols[i].selectbox(
                f'{sensor}',
                scale_options,
                index=0,
                format_func=lambda x: f'X{x}',
                key=f'{item}_{sensor}_scale'
            )
        
        # Apply scaling per sensor
        df_plot = df_item[sensors].copy()
        for sensor in sensors:
            df_plot[sensor] = df_plot[sensor] * multipliers[sensor]
        # Rename columns to reflect scaling
        df_plot.rename(columns={sensor: f'{sensor} X{multipliers[sensor]}' for sensor in sensors}, inplace=True)
        
        # Plot with Plotly Express
        fig = px.line(
            df_plot,
            x=df_plot.index,
            y=list(df_plot.columns),
            labels={
                'value': 'Scaled Signal Value',
                'variable': 'Sensor / Value',
                'Datetime': 'Time'
            },
            title=f'{item} Sensor Signals Over Time'
        )
        
        st.plotly_chart(fig, use_container_width=True)
