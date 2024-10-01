import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Load data
@st.cache_data
def load_data():
    co_data = pd.read_csv('PRSA_Data_Tiantan_20130301-20170228.csv')
    temp_data = pd.read_csv('PRSA_Data_Shunyi_20130301-20170228.csv')
    
    print("Columns in CO dataset:", co_data.columns.tolist())
    print("Columns in Temperature dataset:", temp_data.columns.tolist())
    
    # Process CO and temperature data
    for data in [co_data, temp_data]:
        if all(col in data.columns for col in ['year', 'month', 'day', 'hour']):
            data['datetime'] = pd.to_datetime(data[['year', 'month', 'day', 'hour']])
        else:
            st.error("Required columns (year, month, day, hour) are not present in one of the datasets.")
            st.stop()
    
    return co_data, temp_data

# Main function to run the Streamlit app
def main():
    st.title('Dashboard Kualitas Udara: Analisis CO dan Suhu')

    # Load data
    co_data, temp_data = load_data()

    # Sidebar
    st.sidebar.header('Pengaturan')
    
    # Date range selector
    date_range = st.sidebar.date_input(
        "Pilih rentang tanggal",
        [co_data['datetime'].min().date(), co_data['datetime'].max().date()],
        min_value=co_data['datetime'].min().date(),
        max_value=co_data['datetime'].max().date()
    )

    # Filter data based on date range
    filtered_co_data = co_data[(co_data['datetime'].dt.date >= date_range[0]) & 
                               (co_data['datetime'].dt.date <= date_range[1])]
    filtered_temp_data = temp_data[(temp_data['datetime'].dt.date >= date_range[0]) & 
                                   (temp_data['datetime'].dt.date <= date_range[1])]

    # CO Analysis
    st.header('Analisis CO')

    # Calculate CO counts by hour
    co_counts_by_hour = filtered_co_data.groupby('hour')['CO'].nunique().reset_index()

    # Create bar plot for CO using Plotly
    fig_co = px.bar(co_counts_by_hour, x='hour', y='CO', 
                    title='Jumlah CO Berdasarkan Jam',
                    labels={'hour': 'Jam', 'CO': 'Jumlah CO'},
                    template='plotly_white')
    
    fig_co.update_layout(
        title_font_size=20,
        xaxis_title_font_size=16,
        yaxis_title_font_size=16,
        xaxis=dict(tickmode='linear', tick0=0, dtick=1)
    )

    # Display the CO plot
    st.plotly_chart(fig_co, use_container_width=True)

    # Temperature Analysis
    st.header('Analisis Suhu')

    # Calculate average temperature by hour
    avg_temp_by_hour = filtered_temp_data.groupby('hour')['TEMP'].mean().reset_index()

    # Create bar plot for temperature using Plotly
    fig_temp = px.bar(avg_temp_by_hour, x='hour', y='TEMP',
                      title='Rata-rata Suhu (TEMP) Berdasarkan Jam',
                      labels={'hour': 'Jam', 'TEMP': 'Rata-rata Suhu (°C)'},
                      template='plotly_white',
                      color='TEMP',
                      color_continuous_scale='RdBu_r')  # Red-Blue diverging color scale

    fig_temp.update_layout(
        title_font_size=20,
        xaxis_title_font_size=16,
        yaxis_title_font_size=16,
        xaxis=dict(tickmode='linear', tick0=0, dtick=1)
    )

    # Display the temperature plot
    st.plotly_chart(fig_temp, use_container_width=True)

    # Additional statistics
    st.header('Statistik Tambahan')
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Rata-rata CO", f"{filtered_co_data['CO'].mean():.2f}")
    
    with col2:
        st.metric("CO Maksimum", filtered_co_data['CO'].max())
    
    with col3:
        st.metric("CO Minimum", filtered_co_data['CO'].min())

    col4, col5, col6 = st.columns(3)

    with col4:
        st.metric("Rata-rata Suhu", f"{filtered_temp_data['TEMP'].mean():.2f} °C")
    
    with col5:
        st.metric("Suhu Maksimum", f"{filtered_temp_data['TEMP'].max():.2f} °C")
    
    with col6:
        st.metric("Suhu Minimum", f"{filtered_temp_data['TEMP'].min():.2f} °C")

    # Time series plots
    st.header('Tren CO dan Suhu Sepanjang Waktu')
    
    daily_co_data = filtered_co_data.groupby(filtered_co_data['datetime'].dt.date)['CO'].mean().reset_index()
    daily_temp_data = filtered_temp_data.groupby(filtered_temp_data['datetime'].dt.date)['TEMP'].mean().reset_index()
    
    fig_trend = go.Figure()

    fig_trend.add_trace(go.Scatter(
        x=daily_co_data['datetime'],
        y=daily_co_data['CO'],
        name='CO',
        yaxis='y1'
    ))

    fig_trend.add_trace(go.Scatter(
        x=daily_temp_data['datetime'],
        y=daily_temp_data['TEMP'],
        name='Temperature',
        yaxis='y2'
    ))

    fig_trend.update_layout(
        title='Tren Rata-rata CO dan Suhu Harian',
        xaxis=dict(title='Tanggal'),
        yaxis=dict(title='CO', side='left'),
        yaxis2=dict(title='Suhu (°C)', side='right', overlaying='y'),
        legend=dict(x=0.01, y=0.99, bgcolor='rgba(255, 255, 255, 0.8)'),
        title_font_size=20,
        xaxis_title_font_size=16,
        yaxis_title_font_size=16,
        yaxis2_title_font_size=16
    )
    
    st.plotly_chart(fig_trend, use_container_width=True)

if __name__ == '__main__':
    main()