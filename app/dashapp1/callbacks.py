from datetime import datetime as dt
import plotly.graph_objects as go
import pandas as pd
from dash.dependencies import Input
from dash.dependencies import Output
from datetime import datetime
import psycopg2 as ps
from psycopg2 import sql

def psql_connect():
    with open('cred.txt', 'r') as f:
        cred = f.read()
    username = cred.split(',')[0]
    password = cred.split(',')[1]
    try:
        connection = ps.connect(user = username,
                                  password = password,
                                  host = "127.0.0.1",
                                  port = "5432",
                                  database = "natrent")

        cursor = connection.cursor()
        # Print PostgreSQL Connection properties
        print ( connection.get_dsn_parameters(),"\n")
    
        # Print PostgreSQL version
        cursor.execute("SELECT version();")
        record = cursor.fetchone()
        print("You are connected to - ", record,"\n")
    
    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    return(connection)



def register_callbacks(dashapp):
    @dashapp.callback(Output('listing-graph', 'figure'), [Input('my-dropdown', 'value')])
    def update_graph(selected_dropdown_value):
        conn = psql_connect()
        c = conn.cursor()
        get_avg = '''
        SELECT listing_date, (COUNT(*)/COUNT(DISTINCT listing_loc)) as count 
        FROM clean 
        WHERE listing_date BETWEEN NOW() - INTERVAL '7 DAYS' AND NOW() 
        GROUP BY listing_date
        '''
        df = pd.read_sql(get_avg, conn)
        df['listing_loc'] = 'Average Across Locations'
        if selected_dropdown_value == 'Average Across Locations':
            selected_dropdown_value = [selected_dropdown_value]
        else:
            sql_dropdown_values = [value for value in selected_dropdown_value if value != 'Average Across Locations']
            get_all = sql.SQL("SELECT listing_loc, listing_date, COUNT(*) as count FROM clean WHERE listing_loc IN ({}) AND listing_date BETWEEN NOW() - INTERVAL '7 DAYS' AND NOW() GROUP BY listing_loc, listing_date").format(sql.SQL(', ').join(map(sql.Literal, sql_dropdown_values)))
            df = df.append(pd.read_sql(get_all, conn), sort = True)
        print(selected_dropdown_value)
        print(df.head)
        conn.close()
        df = df.sort_values('listing_date')
        return {
            'data': [{
                'x': df.listing_date[df.listing_loc == loc],
                'y': df.loc[df.listing_loc == loc,'count'],
                #'name' : df.listing_loc,
                'color' : loc,
                'mode' : 'lines+markers',
                'name' : loc
            } for loc in selected_dropdown_value],
            'layout': {'margin': {'l': 40, 'r': 0, 't': 20, 'b': 30}}
        }

    @dashapp.callback(Output('log-graph', 'figure'), [Input('my-dropdown', 'value')])
    def update_graph(selected_dropdown_value):
        conn = psql_connect()
        c = conn.cursor()
        get_avg = '''
        SELECT listing_date, (COUNT(*)/COUNT(DISTINCT listing_loc)) as count 
        FROM clean 
        WHERE listing_date BETWEEN NOW() - INTERVAL '7 DAYS' AND NOW() 
        GROUP BY listing_date
        '''
        df = pd.read_sql(get_avg, conn)
        df['listing_loc'] = 'Average Across Locations'
        if selected_dropdown_value == 'Average Across Locations':
            selected_dropdown_value = [selected_dropdown_value]
        else:
            sql_dropdown_values = [value for value in selected_dropdown_value if value != 'Average Across Locations']
            get_all = sql.SQL("SELECT listing_loc, listing_date, COUNT(*) as count FROM clean WHERE listing_loc IN ({}) AND listing_date BETWEEN NOW() - INTERVAL '7 DAYS' AND NOW() GROUP BY listing_loc, listing_date").format(sql.SQL(', ').join(map(sql.Literal, sql_dropdown_values)))
            df = df.append(pd.read_sql(get_all, conn), sort = True)
        conn.close()
        df = df.sort_values('listing_date')
        return {
            'data': [{
                'x': df.listing_date[df.listing_loc == loc],
                'y': df.loc[df.listing_loc == loc,'count'],
                #'name' : df.listing_loc,
                'color' : loc,
                'mode' : 'lines+markers',
                'name' : loc
            } for loc in selected_dropdown_value],
            'layout': {'margin': {'l': 40, 'r': 0, 't': 20, 'b': 30}}
        }

    @dashapp.callback(Output('scrapers-map', 'figure'), [Input('my-dropdown', 'value')])
    def update_graph(selected_dropdown_value):
        conn = psql_connect()
        sql_command = '''
        SELECT listing_loc, lat, lon, date, date_time, na_total, na_address, na_rent, error FROM city_locs
        JOIN (
            SELECT date, date_time, loc, na_total, na_address, na_rent, error = 'none' as error
            FROM craigslist_log
            JOIN (
                SELECT MAX(date_time) as recent_time, loc AS listing_loc
                FROM craigslist_log WHERE error = 'none'
                GROUP BY listing_loc) SubMax
                ON craigslist_log.loc =  SubMax.listing_loc AND
                craigslist_log.date_time = SubMax.recent_time) log
        ON city_locs.listing_loc = log.loc
        '''
        df = pd.read_sql(sql_command, conn)
        df['text'] = df['listing_loc']
        df['diff'] = datetime.now() - df.date_time
        df.loc[df.date_time > datetime.now(), 'diff'] = pd.Timedelta('0 hours')
        df['diff_text'] = pd.cut(df['diff'], bins = [pd.Timedelta('0 hours'), pd.Timedelta('10 hours'),pd.Timedelta('1 days'),pd.Timedelta('2 days'),pd.Timedelta('5 days'),pd.Timedelta('400 days')], labels = ['Within the last 10 Hours','Within  the last 24 Hours', 'Within 2 days', 'Within 5 days','Before that'])
        colors = ["green","lightseagreen","yellow","orange","crimson","lightgrey","black"]
        limits = ['Within the last 10 Hours','Within  the last 24 Hours', 'Within 2 days', 'Within 5 days', 'Before that', 'error']
        cities = []
        scale = 500
        fig = go.Figure()
        df.fillna({'na_total':0,'na_address':0,'na_rent':0,'diff_text':'Before that'}, inplace=True)
        if selected_dropdown_value != 'Average Across Locations':
            focus_cities = [city for city in selected_dropdown_value if city != 'Average Across Locations']
            df_sub = df[df['listing_loc'].isin(focus_cities)].copy()
            df_sub.diff_text = 'Selected'
            df_sub['size'] = 60
            fig.add_trace(go.Scattergeo(
                locationmode = 'USA-states',
                lon = df_sub['lon'],
                lat = df_sub['lat'],
                text = df_sub['text'],
                marker = dict(
                    size = df_sub['na_total']*scale*3,
                    color = 'yellow',
                    line_color='rgb(40,40,40)',
                    line_width=0,
                    sizemode = 'area'
                ),
                name = 'Selected'))

 
        for lim in [limit for limit in limits if limit in df.diff_text.unique()]:
            i = limits.index(lim)
            df_sub = df[df.diff_text==lim]
            fig.add_trace(go.Scattergeo(
                locationmode = 'USA-states',
                lon = df_sub['lon'],
                lat = df_sub['lat'],
                text = df_sub['text'],
                marker = dict(
                    size = df_sub['na_total']*scale,
                    color = colors[i],
                    line_color='rgb(40,40,40)',
                    line_width=0.5,
                    sizemode = 'area'
                ),
                name = lim))

        fig.update_layout(
                title_text = 'Rental Scraper Status<br>(Click legend to toggle traces)',
                showlegend = True,
                geo = dict(
                    scope = 'usa',
                    landcolor = 'rgb(177, 156, 217)',
                )
            )
        conn.close()
        return {
            'data': fig.data,
            'layout': fig.layout
        }

if __name__ == '__main__':
    import numpy as np
    selected_dropdown_value = ['Philadelphia', 'Orlando', 'Average Across Locations']
    loc = 'Philadelphia'
    from geopy import geocoders
    gn = geocoders.GeoNames(username = 'ikennedy')
    city_locs = [(city,gn.geocode(city)) for city in cities]
    loc_df = pd.DataFrame({'listing_loc':[city[0] for city in city_locs], 'geo_data':[city[1] for city in city_locs]})
    loc_df.loc[loc_df.geo_data.isnull(),'geo_data'] = (('',(np.NaN,np.NaN)),('',(np.NaN,np.NaN)),('',(np.NaN,np.NaN)))
    loc_df[['name', 'data']] = pd.DataFrame(loc_df['geo_data'].tolist(), index=loc_df.index)
    loc_df[['lat', 'lon']] = pd.DataFrame(loc_df['data'].tolist(), index=loc_df.index)
    loc_df = loc_df[['listing_loc', 'name', 'lat','lon']]
    loc_df[loc_df.lat.isna()]
    city = gn.geocode('Oneida')
    current_city = 'Utica-Rome-Oneida'
    loc_df.loc[loc_df.listing_loc == current_city, 'name'] = city[0]
    loc_df.loc[loc_df.listing_loc == current_city, 'lat'] = city[1][0]
    loc_df.loc[loc_df.listing_loc == current_city, 'lon'] = city[1][1]
    loc_df.to_sql('city_locs', conn, if_exists = 'replace')
    conn = sqlite3.connect('data/clData.db')
    sql_command = '''
    SELECT listing_loc, lat, lon, date, date_time, na_total, na_address, na_rent, error FROM city_locs
    JOIN (
        SELECT date, date_time, loc, na_total, na_address, na_rent, error != "none" as error
        FROM cl_log
        JOIN (
            SELECT MAX(date_time) as recent_time, loc AS listing_loc
            FROM cl_log WHERE error = "none"
            GROUP BY listing_loc) SubMax
            ON cl_log.loc =  SubMax.listing_loc AND
            cl_log.date_time = SubMax.recent_time) log
    ON city_locs.listing_loc = log.loc
    '''
    sql_command = '''
    SELECT date, date_time, loc, na_total, na_address, na_rent, error != "none" as error
    FROM cl_log
    JOIN (
        SELECT MAX(date_time) as recent_time, loc AS listing_loc
        FROM cl_log WHERE error = "none"
        GROUP BY listing_loc) SubMax
        ON cl_log.loc =  SubMax.listing_loc AND
        cl_log.date_time = SubMax.recent_time
    '''
    df = pd.read_sql(sql_command, conn)
    cities = df['loc'].unique().tolist()
