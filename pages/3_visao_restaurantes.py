#---------------------------------------------------
# ----------- IMPORTS ---------------
#---------------------------------------------------

import pandas as pd
import numpy as np
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
# ----------- FUNÇõES ---------------
#=============================================================

def clean_code(df):
    '''
    Esta função executa a limpeza do dataset
    Tipos de limpeza:
    1- Remoção dos dados NaN
    2- Mudança do tipo da coluna de dados
    3- Remoção dos espaços das variáveis de texto.
    4- Formatação da coluna de datas
    5- Formatação da coluna de tempo (remoção do texta da variavel numerica)
    
    '''

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
    
    return df

#-------------------- VISÃO RESTARAUNTES -------------------------

# Entregadores Únicos
def unique_deliverers(df1):
    return df1.Delivery_person_ID.nunique()

# Distancia Média das Entregas
def media_distancia_entrega(df1):
    df1['Delivery_distance'] = df1.apply( 
        lambda row: haversine(
            (row['Restaurant_latitude'], row['Restaurant_longitude'] ),
            (row['Delivery_location_latitude'], row['Delivery_location_longitude'])
                 ), axis=1 )
    return round( df1.Delivery_distance.mean(), 2)

# Tempo Médio e Desvio Padrão com ou sem festival
def festival_mean_std(df1):
    cols =  [ 'Festival', 'Time_taken(min)' ]

    festival_delivery_mean_timetaken = df1[cols].groupby( 'Festival' ).agg( { 'Time_taken(min)': [ 'mean', 'std' ] } )
    festival_delivery_mean_timetaken.columns = [ 'avg_time', 'std_time' ]
    return festival_delivery_mean_timetaken.reset_index()

# Cria gráfico de Pizza com distancia média por cidade.
def grafico_distancia_media_por_cidade(df1):
    df1['Delivery_distance'] = df1.apply( 
        lambda row: haversine(
            (row['Restaurant_latitude'], row['Restaurant_longitude'] ),
            (row['Delivery_location_latitude'], row['Delivery_location_longitude'])
                 ), axis=1 )
    avg_distance = df1.loc[:, ['City', 'Delivery_distance'] ].groupby('City').mean().reset_index()
    fig = go.Figure(
        data=[ go.Pie( labels= avg_distance['City'], values= avg_distance['Delivery_distance'], pull=[0.05, 0.05, 0.05] ) ]
    )
    return fig

# Cria grafico de barras da media do tempo de entrega com desvio padrão
def grafico_tempo_media_entrega_por_cidade(df1):
    cols = ['City', 'Time_taken(min)']
                                                            #key (coluna a receber funções)    #value (lista de funções)                              
    mean_std_timetaken_by_city = df1[ cols ].groupby( 'City' ).agg( { 'Time_taken(min)': [ 'mean', 'std' ] } )
    mean_std_timetaken_by_city.columns = [ 'avg_time', 'std_time' ]
    mean_std_timetaken_by_city = mean_std_timetaken_by_city.reset_index()
    fig= go.Figure()
    fig.add_trace( go.Bar( name='Control', 
                          x=mean_std_timetaken_by_city['City'],
                          y=mean_std_timetaken_by_city['avg_time'],
                          error_y= dict(type='data', array=mean_std_timetaken_by_city['std_time'])
                         )
    )
    return fig

# Cria grafico sunburst com o tempo medio por cidade e por tipo de trafego.
def sunburst_tempo_medio_tipo_trafego(df1):
    cols = ['City', 'Time_taken(min)', 'Road_traffic_density' ]
                                                                #key (coluna a receber funções)    #value (lista de funções)                                   
    mean_std_timetaken_by_city_and_traffic = df1[ cols ].groupby( ['City', 'Road_traffic_density'] ).agg( { 'Time_taken(min)': [ 'mean', 'std' ] } )
    mean_std_timetaken_by_city_and_traffic.columns = [ 'avg_time', 'std_time' ]
    mean_std_timetaken_by_city_and_traffic = mean_std_timetaken_by_city_and_traffic.reset_index()
    
    sunburst = px.sunburst(
        mean_std_timetaken_by_city_and_traffic, 
        path=['City', 'Road_traffic_density'], 
        values='avg_time',
        color='std_time',
        color_continuous_scale='Oranges',
        color_continuous_midpoint=np.average( mean_std_timetaken_by_city_and_traffic['std_time'] )
    )

    return sunburst

#Cria grafico sunburst com tempo por cidade e por tipo de pedido.
def tempo_medio_tipo_pedido(df1):
    cols = ['City', 'Time_taken(min)', 'Type_of_order' ]
                                                                #key (coluna a receber funções)    #value (lista de funções)                                   
    mean_std_timetaken_by_city_and_typeoforder = df1[ cols ].groupby( ['City', 'Type_of_order'] ).agg( { 'Time_taken(min)': [ 'mean', 'std' ] } )
    mean_std_timetaken_by_city_and_typeoforder.columns = [ 'avg_time', 'std_time' ]
    mean_std_timetaken_by_city_and_typeoforder = mean_std_timetaken_by_city_and_typeoforder.reset_index()
    
    sunburst = px.sunburst(
        mean_std_timetaken_by_city_and_typeoforder, 
        path=['City', 'Type_of_order'], 
        values='avg_time',
        color='std_time',
        color_continuous_scale='Oranges',
        color_continuous_midpoint=np.average( mean_std_timetaken_by_city_and_typeoforder['std_time'] )
    )
    
    
    return mean_std_timetaken_by_city_and_typeoforder
   
#-----------FiLTROS---------------
def filters(df1):  
    '''
    Esta função aplica os filtros da barra lateral.
    1-Filtro de datas
    2-Filtro de cidades
    3-Filtro de tipos de trafego
    4-Filtro de climas
    
    '''
    
    df1 = df1.query('Order_Date >= @date_slider[0] & Order_Date <= @date_slider[-1] \
                    & City in @city_options \
                    & Road_traffic_density in @traffic_options \
                    & Weatherconditions in @weather_options')

    return df1

#=============================================================
# ----------- IMPORTANDO DATASET -----------------------------
#=============================================================

df_raw = pd.read_csv('dados/train.csv')

df1 = clean_code(df_raw)



#
#=============================================================
# ----------- STREAMLIT -------------------------------------
#=============================================================
st.set_page_config(
    page_title= "Home",
    page_icon= "🍜",
    layout="wide"
)
                    

# ----------- SIDEBAR--------------------------------
#====================================================

# ---logo---
logo_path = 'logo.jfif'
logo_image = Image.open( logo_path )

st.sidebar.image( logo_image, width=180 )

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

# Cidades
city_options = st.sidebar.multiselect(
    'Quais as condições de transito?',
    options=list(df1.City.unique()),
    default=list(df1.City.unique())
         
)

# Tipos de Trafego
st.sidebar.markdown( """---""" )

traffic_options = st.sidebar.multiselect(
    'Quais as condições de transito?',
    options=list(df1.Road_traffic_density.unique()),
    default=list(df1.Road_traffic_density.unique())
         
)

# Tipos de Clima
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

df1= filters(df1)


# ----------- LAYOUT VISAO RESTAURANTES -------------------------
#================================================================

st.header( 'Marketplace - Visão Restaurantes' )

tab1, tab2, tab3 = st.tabs( ['Visao Gerencial', '_', '_'] )

with tab1:
    
    #------ Metricas Gerais ----------
    with st.container():
        st.title('Metricas Gerais')
        
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            col1.metric( 'Entregadores Únicos', unique_deliverers(df1) )
    
        with col2:
            col2.metric( 'Distância Média', media_distancia_entrega(df1))  
        
        with col3:
            col3.metric( 'Tempo Média de Entrega c/ Festival', np.round( festival_mean_std(df1).avg_time[0], 2) )
        
        with col4:
            col4.metric( 'Desvio Padrão c/ Festival', np.round( festival_mean_std(df1).std_time[0], 2) )
            
        with col5:
            col5.metric( 'Tempo Média de Entrega s/ Festival', np.round( festival_mean_std(df1).avg_time[1], 2) )
        
        with col6:
            col6.metric( 'Desvio Padrão de Entrega s/ Festival', np.round( festival_mean_std(df1).std_time[1], 2) )
            
    #--------------------------------        
    
    with st.container():
        st.markdown( '''___''')

        st.markdown('Distancia Média de Entrega Por Cidade')
        st.plotly_chart( grafico_distancia_media_por_cidade(df1) )
    
        
    with st.container():
        st.markdown( '''___''')
        st.title('Distribuição do Tempo')
        
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('Tempo de Entrega por Cidade')
            st.plotly_chart( grafico_tempo_media_entrega_por_cidade(df1) )
        
        with col2:
            st.markdown('#### col 2')
            st.plotly_chart( sunburst_tempo_medio_tipo_trafego(df1) )
    
    with st.container():
        st.markdown( '''___''')
        st.title('Distribuição da Distancia')
        st.table(tempo_medio_tipo_pedido(df1))
