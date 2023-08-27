#---------------------------------------------------
# ----------- IMPORTS ---------------
#---------------------------------------------------
import pandas as pd
import streamlit as st
import datetime
import re
import plotly.express as px
import plotly.graph_objects as go
from haversine import haversine
from PIL import Image
import folium
from streamlit_folium import folium_static


#=============================================================
# ----------- IMPORTANDO DATASET ---------------
#=============================================================

df_raw = pd.read_csv('F:\\Ruiz\\comunidade-ds\\ciclo-basico\\ftc\\dados\\train.csv')


#=============================================================
# ----------- PREPARAÇÃO DO DATASET ---------------
#=============================================================

# Fazendo cópia do dataframe lido
df = df_raw.copy()

# Conversao de texto para data
df['Order_Date'] = pd.to_datetime( df['Order_Date'], format='%d-%m-%Y' )
df['Order_Date'] = df['Order_Date'].apply( lambda x: x.date() )

## Remover spaco da string 
cols = ['ID', 'Road_traffic_density', 'Type_of_order', 'Type_of_vehicle', 'City', 'Festival']
df.loc[:, cols] = df.loc[:, cols].apply(lambda x: x.str.strip())


## Remover 'conditions ' da string
df.loc[:, 'Weatherconditions'] = df.loc[:, 'Weatherconditions'].str.strip('conditions ')

# Excluir as linhas com a idade dos entregadores vazia
# ( Conceitos de seleção condicional )
linhas_vazias = df['Delivery_person_Age'] != 'NaN '
df = df.loc[linhas_vazias, :]

# Excluir as linhas com tipo de trafego vazio
# ( Conceitos de seleção condicional )
linhas_vazias = df['Road_traffic_density'] != 'NaN'
df = df.loc[linhas_vazias, :]

# Excluir as linhas com cidade vazio
# ( Conceitos de seleção condicional )
linhas_vazias = df['City'] != 'NaN'
df = df.loc[linhas_vazias, :]

# Excluir as linhas com Festival vazio
# ( Conceitos de seleção condicional )
linhas_vazias = df['Festival'] != 'NaN'
df = df.loc[linhas_vazias, :]


# Conversao de texto/categoria/string para numeros inteiros
df['Delivery_person_Age'] = df['Delivery_person_Age'].astype( int )

# Conversao de texto/categoria/strings para numeros decimais
df['Delivery_person_Ratings'] = df['Delivery_person_Ratings'].astype( float )


# Remove as linhas da culuna multiple_deliveries que tenham o 
# conteudo igual a 'NaN '
linhas_vazias = df['multiple_deliveries'] != 'NaN '
df = df.loc[linhas_vazias, :]
df['multiple_deliveries'] = df['multiple_deliveries'].astype( int )

# Comando para remover o texto de números
df = df.reset_index( drop=True )
df['Time_taken(min)'] = df['Time_taken(min)'].apply(lambda x: re.findall( r'\d+', x )[0]).astype(int)


# Criando coluna de semana do pedido
df['Week_of_year'] = pd.to_datetime(df['Order_Date']).dt.isocalendar().week



df1 = df.copy()

#=============================================================
# ----------- ANALISE DE DADOS  ----------------------
#=============================================================


#-------------------- VISÂO EMPRESA -------------------------

#  ---Quantidade de pedidos por dia---


def daily_orders_graph(df1):
    cols = [ 'ID', 'Order_Date' ]
    daily_orders = df1[ cols ].groupby( 'Order_Date' ).count().reset_index().rename( columns={ 'ID': 'Orders' } )

    return px.bar( daily_orders, x='Order_Date', y='Orders' )


#---Quantidade de pedidos por semana----
def weekly_orders_graph(df1):
    cols = [ 'ID', 'Week_of_year' ]
    weekly_orders = df1[ cols ].groupby( 'Week_of_year' ).count().reset_index()
    
    # reordenando colunas
    weekly_orders = weekly_orders[ cols ].rename( columns={'ID': 'Orders'} )
    
    return px.bar( weekly_orders, x='Week_of_year', y='Orders' )
    
    


# ---Distribuição dos pedidos por tipo de tráfego---

def graph_orders_by_traffic_type(df1):
    cols = [ 'ID','Road_traffic_density' ]
    dist_by_traffic_density = df1[ cols ].groupby( ['Road_traffic_density'] ).count().rename( columns={'ID': 'Orders'} ).reset_index()
    
    return px.pie( dist_by_traffic_density, names='Road_traffic_density', values='Orders' )


# ---Comparação do volume de pedidos por cidade e tipo de tráfego---

def graph_orders_by_city_and_traffic(df1):
    cols = [ 'ID', 'City', 'Road_traffic_density' ]
    dist_by_city_traffic_density = df1[ cols ].groupby( ['City', 'Road_traffic_density'] ).count().rename(columns={'ID': 'Count'}).reset_index()
    
    return px.scatter( dist_by_city_traffic_density, x='City', y='Road_traffic_density', size='Count', color='City')


#---A quantidade de pedidos por entregador por semana----
def graph_weekly_orders_by_deliverer(df1):
    cols = [ 'Week_of_year', 'Delivery_person_ID']
    weekly_unique_deliverers = df1[ cols ].groupby( 'Week_of_year' ).Delivery_person_ID.nunique()
    weekly_count = df1[ cols ].groupby( 'Week_of_year' ).Delivery_person_ID.count()
    
    weekly_orders_by_deliverer = pd.DataFrame(weekly_count / weekly_unique_deliverers).reset_index().rename(columns={'Delivery_person_ID': 'Weekly_orders_by_deliverer'})
    return px.line(weekly_orders_by_deliverer, x='Week_of_year', y='Weekly_orders_by_deliverer')




#---A localização central de cada cidade por tipo de tráfego---
def map_central_traffic_location(df1):
    cols = ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']
    dfaux = df1[cols].groupby(['City', 'Road_traffic_density']).median().reset_index()
    
    map = folium.Map()
    
    # folium.Marker ( [latitude, longitude ) ]
    for i, row in dfaux.iterrows():
        folium.Marker([
        row.Delivery_location_latitude,
        row.Delivery_location_longitude
        ], popup=[row.City, row.Road_traffic_density]).add_to( map )
    
    return map
                                     

#=============================================================
# ----------- STREAMLIT -------------------------------------
#=============================================================


# ----------- SIDEBAR--------------------------------
#====================================================


# ---logo---
logo_path = 'images\logo.jfif'
logo_image = Image.open( logo_path )

st.sidebar.image(
    logo_image,
    width=150
)

# ---title----
st.sidebar.markdown( '# Curry Company' )
st.sidebar.markdown( "## Fast 'n Delicious" )
st.sidebar.markdown( """---""" )

# ---Slider---

min_date = df1.Order_Date.min()
max_date = df1.Order_Date.max()

date_slider = st.sidebar.slider(
    'Selecione um intervalo de data:',
    value=( min_date, max_date ), 
    format='DD-MM-YYYY'
)

st.sidebar.markdown( """---""" )

# --- multi seleção ---

city_options = st.sidebar.multiselect(
    'Quais as condições de transito?',
    options=list(df1.City.unique()),
    default=list(df1.City.unique())
         
)

st.sidebar.markdown( """---""" )

traffic_options = st.sidebar.multiselect(
    'Quais as condições de transito?',
    options=list(df1.Road_traffic_density.unique()),
    default=list(df1.Road_traffic_density.unique())
         
)

st.sidebar.markdown( """---""" )

weather_options = st.sidebar.multiselect(
    'Quais as condições climáticas?',
    options=list(df1.Weatherconditions.unique()),
    default=list(df1.Weatherconditions.unique())
         
)

st.sidebar.markdown( """---""" )


# --- sidebar bottom ---

st.sidebar.markdown('Powered by Ruiz Roman')


#-----------FiLTROS---------------

# INTERVALO DE DATA
df1 =  df1.query('Order_Date >= @date_slider[0] & Order_Date <= @date_slider[-1]')

# TIPOS DE CLIMA
df1 = df1.query('City in @city_options')

# TIPOS DE TRANSITO
df1 = df1.query('Weatherconditions in @weather_options')

# TIPOS DE CLIMA
df1 = df1.query('Weatherconditions in @weather_options')


# ----------- LAYOUT VISAO EMPRESA -------------------------
#============================================================
st.header( 'Marketplace - Visão Empresa' )

tab1, tab2, tab3 = st.tabs(
    ['Visão Gerencial', 'Visão Tática', 'Visão Geográfica']
)

with tab1:
    # Container 1
    with st.container():
        # ---Daily Orders---
        st.markdown( 'PEDIDOS POR DIA' )
        st.plotly_chart( daily_orders_graph(df1), use_container_width=True )
        
        
    # Container 2
    with st.container():
        col1, col2 = st.columns( 2 )
        
        # COLUNA 1
        with col1:
            st.markdown( 'PEDIDOS POR TIPO DE TRÁFEGO' )
            st.plotly_chart( graph_orders_by_traffic_type(df1), use_container_width=True )
        
        # COLUNA 2
        with col2:
            st.markdown( 'VOLUME DE PEDIDOS POR TIPO DE TRÁFEGO EM CADA CIDADE' )
            st.plotly_chart( graph_orders_by_city_and_traffic(df1), use_container_width=True )
    

    
with tab2:
    st.markdown( 'VOLUME SEMANAL DE PEDIDOS' )
    st.plotly_chart( weekly_orders_graph(df1), use_container_width=True )
    
    with st.container():
        # ---A quantidade de pedidos por entregador por semana----
        st.markdown( 'VOLUME SEMANAL DE PEDIDOS POR ENTREGADOR' )
        st.plotly_chart( graph_weekly_orders_by_deliverer(df1), use_container_width=True )

        
    
with tab3:
    with st.container():
        folium_static( map_central_traffic_location(df1), width=1200, height=600 )







