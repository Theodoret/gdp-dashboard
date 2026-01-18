import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import math
from pathlib import Path

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='Indonesia Food Price',
    page_icon=':earth_americas:', # This is an emoji shortcode. Could be a URL too.
)

# -----------------------------------------------------------------------------
# Declare some useful functions.

@st.cache_data
def get_gdp_data():
    """Grab GDP data from a CSV file.

    This uses caching to avoid having to read the file every time. If we were
    reading from an HTTP endpoint instead of a file, it's a good idea to set
    a maximum age to the cache with the TTL argument: @st.cache_data(ttl='1d')
    """
    
    # Instead of a CSV on disk, you could read from an HTTP endpoint here too.
    DATA_FILENAME = Path(__file__).parent/'data/indonesia_food_prices.csv'
    df = pd.read_csv(DATA_FILENAME)
    df = df.astype({'date':'datetime64[ns]'})

    print(df['date'].min())
    MIN_YEAR = df['date'].min().year
    MAX_YEAR = df['date'].max().year
    
    df['Year'] = df['date'].dt.year

    return df

df = get_gdp_data()

# -----------------------------------------------------------------------------
# Draw the actual page

# Set the title that appears at the top of the page.
'''
# :earth_americas: Indonesia Food Price

The dataset of Indonesia food price is from [Global Food Prices](https://www.kaggle.com/datasets/adrianjuliusaluoch/global-food-prices). The dataset contains Countries, Commodities and Markets data, sourced from the World Food Programme Price Database.

The World Food Programme Price Database covers foods such as maize, rice, beans, fish, and sugar for 98 countries and some 3000 markets. It is updated weekly but contains to a large extent monthly data.
'''

# Add some spacing
''
''

min_value = df['Year'].min()
max_value = df['Year'].max()

from_year, to_year = st.slider(
    'Which years are you interested in?',
    min_value=min_value,
    max_value=max_value,
    value=[min_value, max_value])

target_column_name = "category"
target_column_uniques = df[target_column_name].unique()

if not len(target_column_uniques):
    st.warning("Select at least one "+target_column_uniques)

selected_uniques = st.multiselect(
    'Which ' + target_column_name + ' would you like to view?',
    target_column_uniques,
    target_column_uniques)

''
''
''

# Filter the data
filtered_df = df[
    (df[target_column_name].isin(selected_uniques)) & 
    (df['Year'] <= to_year) & 
    (from_year <= df['Year'])
].groupby(["date", target_column_name])[['price_usd','local_price']].mean()
filtered_df = filtered_df.reset_index()

st.header('USD Price change over time', divider='gray')

# ''

st.line_chart(
    filtered_df,
    x='date',
    y='price_usd',
    y_label='USD',
    color=target_column_name
)

''
''
''

st.header('IDR Price change over time', divider='gray')

# ''

st.line_chart(
    filtered_df,
    x='date',
    y='local_price',
    y_label='IDR',
    color=target_column_name
)


''
''

filtered_df = df[
    (df[target_column_name].isin(selected_uniques)) & 
    (df['Year'] <= to_year) & 
    (from_year <= df['Year'])
].groupby(["Year", target_column_name])[['price_usd']].mean()
filtered_df = filtered_df.reset_index()

first_year = filtered_df[filtered_df['Year'] == from_year]
last_year = filtered_df[filtered_df['Year'] == to_year]

st.header(f'USD price change from {from_year} to {to_year}', divider='gray')

''

cols = st.columns(4)

for i, country in enumerate(selected_uniques):
    col = cols[i % len(cols)]

    with col:
        first_gdp = first_year[first_year[target_column_name] == country]['price_usd'].iat[0]
        last_gdp = last_year[last_year[target_column_name] == country]['price_usd'].iat[0]
    
        if math.isnan(first_gdp):
            growth = 'n/a'
            delta_color = 'off'
        else:
            growth = f'{last_gdp / first_gdp:,.2f}x'
            delta_color = 'normal'

        st.metric(
            label=f'{country}',
            value=f'{last_gdp:,.2f}',
            delta=growth,
            delta_color=delta_color
        )