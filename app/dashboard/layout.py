import dash_core_components as dcc, dash_html_components as html, sqlite3
from app.dashapp1.callbacks import psql_connect
conn = psql_connect()
c = conn.cursor()
c.execute('SELECT DISTINCT location FROM geocoded')
cities = c.fetchall()
cities = [{'label':city[0],  'value':city[0]} for city in [('Average Across Locations', 0)] + cities]
c.execute('SELECT DISTINCT source FROM geocoded')
sources = c.fetchall()
sources = [{'label':source[0],  'value':source[0]} for source in sources]
layout = html.Div([
     html.H1('Scraper Status Dashboard'),
     html.H3('Scraped Data By Location and Date'),
     dcc.Dropdown(id='source-selection',
       options=sources,
       value='Craigslist',
       multi=False),
     dcc.Dropdown(id='my-dropdown',
       options=cities,
       value='Average Across Locations',
       multi=True),
     dcc.Graph(id='scrapers-map'),
     html.H3('Collected Listings By Metro'),
     dcc.Graph(id='listing-graph'),
     html.H3('NA Address Rates By Metro'),
     dcc.Graph(id='log-graph')],
      style={'width': '500'})
if __name__ == '__main__':
    import pandas as pd, os, sqlite3
    os.listdir
    df = pd.read_csv('data/example_data.csv')
    df.columns
    conn = sqlite3.connect('data/clData.db')
    c = conn.cursor()
    c.execute('SELECT listing_loc, COUNT(*) as count FROM listings GROUP BY listing_loc ORDER BY count DESC LIMIT 10')
    cities = c.fetchall()
    cities = [city[0] for city in cities]
