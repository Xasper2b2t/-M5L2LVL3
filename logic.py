#logic.py
import sqlite3
from config import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

class DB_Map():
    def __init__(self, database):
        self.database = database
    
    def create_user_table(self):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS users_cities (
                                user_id INTEGER,
                                city_id TEXT,
                                FOREIGN KEY(city_id) REFERENCES cities(id)
                            )''')
            conn.commit()

    def add_city(self,user_id, city_name ):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM cities WHERE city=?", (city_name,))
            city_data = cursor.fetchone()
            if city_data:
                city_id = city_data[0]  
                conn.execute('INSERT INTO users_cities VALUES (?, ?)', (user_id, city_id))
                conn.commit()
                return 1
            else:
                return 0

            
    def select_cities(self, user_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT cities.city 
                            FROM users_cities  
                            JOIN cities ON users_cities.city_id = cities.id
                            WHERE users_cities.user_id = ?''', (user_id,))

            cities = [row[0] for row in cursor.fetchall()]
            return cities


    def get_coordinates(self, city_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT lat, lng
                            FROM cities  
                            WHERE city = ?''', (city_name,))
            coordinates = cursor.fetchone()
            return coordinates





    def create_graph(self, path, cities, point_color='red'):
        fig = plt.figure(figsize=(12, 6))
        ax = plt.axes(projection=ccrs.Orthographic())
        
        ax.stock_img()
        ax.coastlines(resolution='110m', color="black", linewidth=1)
        ax.add_feature(cfeature.BORDERS, linestyle=':')
  
        ax.add_feature(cfeature.LAND, facecolor='#e8d7b5') 
        ax.add_feature(cfeature.OCEAN, facecolor='#a0c9f0') 
        
        for city in cities:
            coordinates = self.get_coordinates(city)
            if coordinates is None:
                continue
            
            lat, lng = coordinates
            
        
            ax.plot(lng, lat, marker='o', color=point_color, markersize=10, transform=ccrs.PlateCarree(), alpha=0.9)
            
         
            text_color = 'black' if point_color not in ['black', 'navy'] else 'white'
            ax.text(lng + 5, lat + 5, city, fontsize=10, fontweight='bold', color=text_color, 
                    bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=point_color, lw=1, alpha=0.8),
                    transform=ccrs.PlateCarree())

        fig.savefig(path, dpi=150, bbox_inches='tight')
        plt.close(fig)

    def draw_distance(self, city1, city2):
        coords1 = self.get_coordinates(city1)
        coords2 = self.get_coordinates(city2)

        if not coords1 or not coords2:
            return

        lon1, lat1 = coords1[1], coords1[0]
        lon2, lat2 = coords2[1], coords2[0]

        ax = plt.axes(projection=ccrs.PlateCarree())
        ax.stock_img()
        ax.coastlines()
        ax.add_feature(cfeature.BORDERS, linestyle=':')

        ax.plot([lon1, lon2], [lat1, lat2],
                color='red', linewidth=2, marker='o',
                transform=ccrs.Geodetic())

        ax.text(lon1 - 5, lat1, city1, horizontalalignment='right', transform=ccrs.PlateCarree())
        ax.text(lon2 + 5, lat2, city2, horizontalalignment='left', transform=ccrs.PlateCarree())

        temp_path = "map_distance.png"
        plt.savefig(temp_path, dpi=150, bbox_inches='tight')
        plt.close()


if __name__=="__main__":
    
    m = DB_Map(DATABASE)
    m.create_user_table()
