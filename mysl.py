import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import pydeck as pdk

st.title('Origin-Destination Extracted from iTIC Data')
st.markdown(
'''
This is a demo of a Streamlit app that shows origin-destination
geographical distribution in Bangkok Metropolitan Region from 1 to 5 January 2019.
Use the slider to pick a specific date and time then look at how the charts change.
'''
'''
References:
[Source Code](https://github.com/streamlit/demo-uber-nyc-pickups/blob/master/app.py),
[Source Data](https://github.com/Maplub/odsample)
'''
'''
Created by Bulakorn Laosakul (Student ID: 6030815821).
''')

date = st.slider("Select Date", 1, 5)

if date == 1:
    st.write('Date: 1 January 2019')
    DATA_URL = ('https://raw.githubusercontent.com/Maplub/odsample/master/20190101.csv')
elif date == 2:
    st.write('Date: 2 January 2019')
    DATA_URL = ('https://raw.githubusercontent.com/Maplub/odsample/master/20190102.csv')
elif date == 3:
    st.write('Date: 3 January 2019')
    DATA_URL = ('https://raw.githubusercontent.com/Maplub/odsample/master/20190103.csv')
elif date == 4:
    st.write('Date: 4 January 2019')
    DATA_URL = ('https://raw.githubusercontent.com/Maplub/odsample/master/20190104.csv')
elif date == 5:
    st.write('Date: 5 January 2019')
    DATA_URL = ('https://raw.githubusercontent.com/Maplub/odsample/master/20190105.csv')

@st.cache(persist=True)
def get_data():
    return pd.read_csv(DATA_URL)

hour = st.slider("Select Time by Specific Hour", 0, 23)
st.write('Time:', str(hour) + ':00', 'to', str(hour) + ':59')

option = st.selectbox('Select Data Type',('Origin', 'Destination','Origin-Destination'))

if option == 'Origin':
    lat = 'latstartl'
    lon = 'lonstartl'
    DATE_TIME = 'timestart'
    data = get_data()[[lon, lat, DATE_TIME]].dropna()
elif option == 'Destination':
    lat = 'latstop'
    lon = 'lonstop'
    DATE_TIME = 'timestop'
    data = get_data()[[lon, lat, DATE_TIME]].dropna()
elif option == 'Origin-Destination':
    lat = 'lat'
    lon = 'lon'
    DATE_TIME = 'time'
    data_A = get_data()[['latstartl', 'lonstartl', 'timestart']].dropna()
    data_B = get_data()[['latstop', 'lonstop', 'timestop']].dropna()
    data_B = data_B.rename(columns={'latstop':'latstartl', 'lonstop':'lonstartl', 'timestop':'timestart'})
    frames = [data_A,data_B]
    data = pd.concat(frames)
    data = data.rename(columns={'latstartl':'lat','lonstartl':'lon','timestart':'time'})

data[DATE_TIME] = pd.to_datetime(data[DATE_TIME])
data = data[data[DATE_TIME].dt.hour == hour]

st.subheader("Geographical Distribution from %i:00 to %i:59" % (hour, hour % 24))
midpoint = (np.average(data[lat]), np.average(data[lon]))

st.write(pdk.Deck(
    map_style="mapbox://styles/mapbox/streets-v11",
    initial_view_state={
        "latitude": midpoint[0],
        "longitude": midpoint[1],
        "zoom": 11,
        "pitch": 50,
    },
    layers=[
        pdk.Layer(
            "HexagonLayer",
            data=data,
            get_position=[lon, lat],
            radius=100,
            elevation_scale=4,
            elevation_range=[0, 1000],
            pickable=True,
            extruded=True, 
        ),
    ],
))

st.subheader('Breakdown by Minute from %i:00 to %i:59' % (hour, hour % 24))
filtered = data[
    (data[DATE_TIME].dt.hour >= hour) & (data[DATE_TIME].dt.hour < (hour + 1))
]
hist = np.histogram(filtered[DATE_TIME].dt.minute, bins=60, range=(0, 60))[0]
chart_data = pd.DataFrame({'Minute': range(60), 'Total Pickups': hist})

st.altair_chart(alt.Chart(chart_data)
    .mark_area(
        interpolate='step-after',
    ).encode(
        x=alt.X('Minute:Q', scale=alt.Scale(nice=False)),
        y=alt.Y('Total Pickups:Q'),
        tooltip=['Minute', 'Total Pickups']
    ), use_container_width=True)

if st.checkbox('Show Raw Data', False):
    st.subheader('Raw Data by Minute from %i:00 to %i:59' % (hour, hour % 24))
    st.write(data)

st.subheader('Total Data: %i columns' % (data.count()[0]))