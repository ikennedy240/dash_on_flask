import dash_core_components as dcc
import dash_html_components as html
import sqlite3




conn = sqlite3.connect('data/clData.db')
c = conn.cursor()
c.execute('SELECT listing_loc, COUNT(*) as count FROM listings GROUP BY listing_loc ORDER BY count DESC LIMIT 10')
cities = c.fetchall()
cities = [{'label': city[0], 'value': city[0]} for city in [('Average Across Locations',0)]+cities]

layout = html.Div([
    html.H3('Scraper Status Dashboard'),
    dcc.Graph(id='scrapers_map'),
    html.H1('Scraped Data By Location and Date'),
    dcc.Dropdown(
        id='my-dropdown',
        options = cities,
        value='Average Across Locations',
        multi=True
    ),
    dcc.Graph(id='my-graph')
], style={'width': '500'})

if __name__ == '__main__':
    import pandas as pd
    import os
    import sqlite3

    os.listdir
    df = pd.read_csv('data/example_data.csv')
    df.columns
    conn = sqlite3.connect('data/clData.db')
    c = conn.cursor()
    c.execute('SELECT listing_loc, COUNT(*) as count FROM listings GROUP BY listing_loc ORDER BY count DESC LIMIT 10')
    cities = c.fetchall()
    cities = [city[0] for city in cities]
