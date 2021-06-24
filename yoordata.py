import os
import pandas as pd
import numpy as np
from suport import *

from wordcloud import WordCloud
import cufflinks as cf
import chart_studio.plotly as py
import seaborn as sns
import matplotlib.pyplot as plt

import json
from pyquery import PyQuery

from PIL import Image

import folium
import folium.plugins
from folium.plugins import HeatMapWithTime as HMWT
from folium.plugins import HeatMap as HM
from folium.plugins import MarkerCluster


import streamlit as st
from streamlit_folium import folium_static
import folium

#!pip install utils
#!pip install xmltojson
#!pip install streamlit
#!pip install python-vlc
#!pip install pyquery

# %matplotlib inline
cf.go_offline()

archivos = os.listdir()  # Extraemos todos los archivos de los zip
archivos_zip = []
for i in archivos:
    if i.endswith(".zip"):
        archivos_zip.append(i)
cwd = os.getcwd()  # guardamos el directorio del proyecto
# for i in archivos_zip:
#zf = ZipFile(i)
# zf.extractall()

os.chdir(cwd + '/' + 'Takeout')
# guardamos el directorio de la carpeta Takeout con la que trabajaremos
Takeout_dir = os.getcwd()

# Extraemos el nombre y mail de la carpeta perfil

perfil_json = open_json(Takeout_dir + '/' + 'Perfil' + '/'+'Perfil.json')
nombre = perfil_json['name']['formattedName']
email = perfil_json['emails'][0]['value']

# Extraemos las páginas web visitadas

chrome_json = open_json(Takeout_dir + '/' + 'Chrome' +
                        '/'+'BrowserHistory.json')
df = pd.DataFrame(chrome_json['Browser History'])

# Limpiamos las URLs

for i in range(len(df.url)):
    if '//' in df.url[i]:
        df.url[i] = df.url[i].split('//')[1]

for i in range(len(df.url)):
    if '/' in df.url[i]:
        df.url[i] = df.url[i].split('/')[0]

# Transformamos a DF para poder sacar la visualización

Top10URL = df.url.value_counts()[0:10]
Top10URL_df = pd.DataFrame(Top10URL)
Top10URL_df_i = Top10URL_df.reset_index()
Top10URL_df_i = Top10URL_df_i.rename(
    columns={'index': 'Página', 'url': 'Visitas'})

# Ploteamos las páginas más visitadas

plt.figure(figsize=(10, 7))
sns.set_style("darkgrid")
TopUrl = sns.barplot(data=Top10URL_df_i, x=Top10URL_df_i['Página'], y=Top10URL_df_i.Visitas, palette='pink').set_title(
    'PÁGINAS MÁS VISITADAS')
plt.xticks(rotation=35)
plt.tight_layout(pad=0)
plt.savefig("TopUrl.png")

# Hacemos una nuve de las páginas

df['sopa'] = df.url.apply(lambda x: x.replace('com', '').replace('www', '').replace('es', '')
                          .replace('org', '').strip())

nadena = ['noapnc', 'oainnaci']
wordcloud = WordCloud(width=1600, height=800, stopwords=nadena, repeat=False,
                      collocations=False).generate(' '.join([e for e in df.sopa]))

plt.figure(figsize=(15, 10), facecolor='k')
plt.imshow(wordcloud)
plt.axis('off')
plt.tight_layout(pad=0)
plt.savefig('wordcloud.png', facecolor='k', bbox_inches='tight')

# Hacemos una nuve de los juegos

os. chdir('Servicios de Juegos de Google Play/Juegos/')
juegos = os.listdir()
juegos_df = pd.DataFrame(juegos)
juegos_df['limpio'] = juegos_df.apply(lambda x: x.replace(' ', '_'))
juegos_df['limpio'] = juegos_df['limpio'].apply(lambda x: x.replace(' ', '_'))

# Preparamos las reseñas extrayendo lat y long para visualizarlo en un mapa

os. chdir(Takeout_dir)
wordcloud = WordCloud(width=1600, height=800, stopwords=nadena, repeat=False,
                      collocations=False).generate(' '.join([e for e in juegos_df['limpio']]))

plt.figure(figsize=(15, 10), facecolor='k')
plt.imshow(wordcloud)
plt.axis('off')
plt.tight_layout(pad=0)
plt.savefig('juegos.jpg', facecolor='k', bbox_inches='tight')

os. chdir(Takeout_dir)
reseñas_json = open_json(
    Takeout_dir + '/' + 'Maps (Tus sitios)' + '/'+'Reseñas.json')

df_reseñas = pd.DataFrame(reseñas_json["features"])
df_reseñas1 = pd.json_normalize(df_reseñas['properties'])
df_reseñas1["Location.Geo Coordinates.Latitude"] = pd.to_numeric(
    df_reseñas1["Location.Geo Coordinates.Latitude"], downcast="float")
df_reseñas1['Location.Geo Coordinates.Longitude'] = pd.to_numeric(
    df_reseñas1['Location.Geo Coordinates.Longitude'], downcast="float")

# Calculamos la media de tus valoraciones
media_reseñas = df_reseñas1['Star Rating'].mean()

df_reseñas1.ubica = df_reseñas1[[
    'Location.Geo Coordinates.Latitude', 'Location.Geo Coordinates.Longitude']].values

# Ploteamos el mapa con las reseñas

m = folium.Map(
    location=df_reseñas1.ubica[0], zoom_start=12, tiles="Stamen Terrain")
colores = {1: 'red', 2: 'orange', 3: 'yellow', 4: 'darkgreen', 5: 'green'}
for i in range(len(df_reseñas1)):
    folium.Marker(
        location=[df_reseñas1.ubica[i][0], df_reseñas1.ubica[i][1]],
        popup=df_reseñas1['Location.Business Name'][i] +
        ' (' + str(df_reseñas1['Star Rating'][i]) + ')',
        icon=folium.Icon(
            color=colores[df_reseñas1['Star Rating'][i]], icon='check', prefix='fa'),
    ).add_to(m)

# Obtenemos la lista de libros

os. chdir('Google Play Libros')
libros = os.listdir()

os. chdir(Takeout_dir)

# Sacamos del html los últimos videos vistos de Youtube

html = open(Takeout_dir + '/YouTube y YouTube Music/historial/historial-de-reproducciones.html',
            'r').read()  # local html

query = PyQuery(html)
lst = []
for i in range(2000):
    try:
        lst.append(query("a").eq(i).text())
    except:
        break

youtube = pd.DataFrame(lst)

youtube[0] = youtube[0].apply(lambda x: x.replace(' ', '_').replace('com', '').replace('www', '').replace('es', '')
                              .replace('org', '').replace('https', '').strip())

canales = youtube.value_counts()[0:10]  # Obtenemos el top 10
TopCanales_df = pd.DataFrame(canales, columns=['Visitas'])
TopCanales_df_i = TopCanales_df.reset_index()
TopCanales_df_i = TopCanales_df_i.rename(columns={0: 'Canal'})

# Ploteamos los videos de Youtube

plt.figure(figsize=(10, 7))
sns.set_style("darkgrid")
YTcanales = sns.barplot(data=Top10URL_df_i, x=TopCanales_df_i['Canal'], y=TopCanales_df_i.Visitas, palette='pink').set_title(
    'CANALES MÁS VISITADOS ÚLTIMAMENTE')
plt.xticks(rotation=35)
plt.tight_layout(pad=0)
plt.savefig("YTcanales.png")

os.chdir(Takeout_dir + '/' + 'Mi actividad' + '/'+'Voz y Audio')
audios = os.listdir()
os.chdir(Takeout_dir)

ind = np.random.randint(0, len(audios))
# Indices aleatorios para sacar audios aleatorios
ind1 = np.random.randint(0, len(audios))
ind2 = np.random.randint(0, len(audios))
ind3 = np.random.randint(0, len(audios))

# Creamos un mapa con todas tus localizaciones

os.chdir(Takeout_dir + '/' + 'Historial de ubicaciones' +
         '/'+'Semantic Location History')
años = os.listdir()

# Hacemos una lista de tuplas con las localizaciones, la fecha y el nombre

lst = []
for i in años:
    os.chdir(Takeout_dir + '/' + 'Historial de ubicaciones' +
             '/'+'Semantic Location History/' + i)
    meses = os.listdir()
    for j in meses:
        prueba_json = open_json(
            Takeout_dir + '/' + 'Historial de ubicaciones' + '/'+'Semantic Location History/'+i+'/' + j)
        for k in range(len(prueba_json['timelineObjects'])):
            try:
                lst.append((prueba_json['timelineObjects'][k]['placeVisit']['location']['latitudeE7'], prueba_json['timelineObjects'][k]
                           ['placeVisit']['location']['longitudeE7'], prueba_json['timelineObjects'][k]['placeVisit']['location']['name'],  j))
            except:
                pass

df_loc = pd.DataFrame(lst, columns=['lat', 'lon', 'name', 'date'])
df_loc['lat'] = df_loc['lat'].apply(lambda x: x / 10000000)
df_loc['lon'] = df_loc['lon'].apply(lambda x: x / 10000000)

df_loc['date'] = df_loc['date'].apply(
    lambda x: x.replace('_', ' ').replace('.json', ''))
df_loc['date'] = pd.to_datetime(df_loc['date'])
df_loc['month'] = df_loc['date'].apply(lambda x: x.month)
df_loc['year'] = df_loc['date'].apply(lambda x: x.year)

l = folium.Map(
    location=df_reseñas1.ubica[0], zoom_start=3, tiles="Stamen Terrain")

marker_cluster = MarkerCluster().add_to(l)

for i in range(len(df_loc)):
    folium.Marker(
        location=[df_loc.lat[i], df_loc.lon[i]],
        popup=df_loc.name[i] + ' (' + str(df_loc.month[i]) +
        '-' + str(df_loc.year[i]) + ')',
        icon=folium.Icon(color='green', icon='check', prefix='fa'),
    ).add_to(marker_cluster)

os.chdir(cwd)

# Ponemos todo lo que se visualizará en Streamlit

imagen = Image.open("logo.png")
st.image(imagen, use_column_width=True)

st.write("""
# Tu Google Takeout by Yoordata
""")

st.text('Hola ' + nombre + '''.
En esta nueva era en la que vivimos, los datos son el nuevo petroleo.
La información es poder y de alguna forma la información que tienen las grandes empresas
sobre nosotros es poder sobre nosotros. 
Veamos algunas de las cosas que sabe Google sobre ti: ''')

st.write("""
## Google conoce todas las páginas que visitas... 
""")


imagen = Image.open("Takeout/wordcloud.png")
st.image(imagen, use_column_width=True)

st.write("""
## Y cuanto las visitas...
""")
imagen = Image.open("Takeout/TopUrl.png")
st.image(imagen, use_column_width=True)

st.write("""
## Sabe lo que te gusta ver en YouTube...
""")

imagen = Image.open("Takeout/YTcanales.png")
st.image(imagen, use_column_width=True)

st.write("""
## Sabe a que juegas con el movil...
""")
imagen = Image.open("Takeout/juegos.jpg")
st.image(imagen, use_column_width=True)

st.write("""
## Incluso conoce tus gustos...
""")
folium_static(m)
st.write(" Hasta sabe que tu valoracion media es de " + str(media_reseñas) + ''' ¿no
 estarás siendo un poco racanillo con tus valoraciones?''')

st.write("""
## Sabe dónde estás en todo momento...
""")
folium_static(l)

st.write("""
## Escucha atentemente a lo que dices...
...aquí tienes una muestra aleatoria de algunoas de tus peticiones a Google:
""")


audio_file = open(Takeout_dir + '/' + 'Mi actividad' + '/' +
                  'Voz y Audio' + '/' + audios[ind], 'rb')
audio_bytes = audio_file.read()
st.audio(audio_bytes, format='audio/ogg')

audio_file = open(Takeout_dir + '/' + 'Mi actividad' + '/' +
                  'Voz y Audio' + '/' + audios[ind1], 'rb')
audio_bytes = audio_file.read()
st.audio(audio_bytes, format='audio/ogg')

audio_file = open(Takeout_dir + '/' + 'Mi actividad' + '/' +
                  'Voz y Audio' + '/' + audios[ind2], 'rb')
audio_bytes = audio_file.read()
st.audio(audio_bytes, format='audio/ogg')

audio_file = open(Takeout_dir + '/' + 'Mi actividad' + '/' +
                  'Voz y Audio' + '/' + audios[ind3], 'rb')
audio_bytes = audio_file.read()
st.audio(audio_bytes, format='audio/ogg')

st.write("""
## Ahora que sabes lo Google sabe de ti, ¿Vas a seguir aceptando todas las coockies?
## Ahora que ves a que dedicas tus vida, ¿Vas a seguir gastando tu tiempo como hasta ahora en internet?
""")