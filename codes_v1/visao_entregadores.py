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
# ----------- IMPORTANDO DATASET -----------------------------
#=============================================================

df_raw = pd.read_csv('F:\\Ruiz\\comunidade-ds\\ciclo-basico\\ftc\\dados\\train.csv')


#=============================================================
# ----------- PREPARAÇÃO DO DATASET --------------------------
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
# ----------- ANALISE DE DADOS  -----------------------------
#=============================================================


#-------------------- VISÃO ENTREGADORES -------------------------

#---A menor e maior idade entre os entregadores---

# Mais novo
def youngest_deliverer(df1):
    return df1.Delivery_person_Age.min()

# Mais velho
def oldest_deliverer(df1):
    return df1.Delivery_person_Age.max()

#---A pior e a melhor condição de veículos---

# Melhor condiçãos
def best_vehicle_condition(df1):
    return df1.Vehicle_condition.max()

# Pior Condição
def worst_vehicle_condition(df1):
    return df1.Vehicle_condition.min()

#---A avaliação médida por entregador---

def deliverer_ratings_mean(df1):
    return df1.groupby( 'Delivery_person_ID' ).Delivery_person_Ratings.mean().round(2)

#---A avaliação média e o desvio padrão por tipo de tráfego---

def rating_mean_std_by_traffic(df1):
    mean_std_rating_by_traffic = df1.groupby( 'Road_traffic_density' ).Delivery_person_Ratings.agg( ['mean', 'std'] )
    mean_std_rating_by_traffic.columns = [ 'Avaliação Média', 'Desvio Padrão' ]
    mean_std_rating_by_traffic = mean_std_rating_by_traffic.reset_index()
    
    return round(mean_std_rating_by_traffic, 2)

#---A avaliação média e o desvio padrão por condição climática---

def rating_mean_std_by_weather(df1):
    mean_std_rating_by_weather = df1.groupby( 'Weatherconditions' ).Delivery_person_Ratings.agg( ['mean', 'std'] )
    mean_std_rating_by_weather.columns = [ 'Avaliação Média', 'Desvio Padrão' ]
    mean_std_rating_by_weather = mean_std_rating_by_weather.reset_index()
    
    return round(mean_std_rating_by_weather, 2)
                                     
    
#--- 10 Entregadores mais rápidos por cidade ---    
def faster_deliverers_by_city(df1):
    faster_deliverers_by_city = pd.DataFrame(df1.groupby( [ 'City', 'Delivery_person_ID'] )['Time_taken(min)'].mean())
    faster_deliverers_by_city = faster_deliverers_by_city.sort_values(['City', 'Time_taken(min)']).reset_index()
    
    urban_faster_deliverers = faster_deliverers_by_city.query('City == "Urban"').head(10)
    semiurban_faster_deliverers = faster_deliverers_by_city.query('City == "Semi-Urban"').head(10)
    metropolitian_faster_deliverers = faster_deliverers_by_city.query('City == "Metropolitian"').head(10)
    
    faster_deliverers_by_city = pd.concat( [ urban_faster_deliverers, semiurban_faster_deliverers, metropolitian_faster_deliverers ] ).reset_index(drop=True)
    return round(faster_deliverers_by_city)

#--- 10 Entregadores mais lentos por cidade ---    
def slower_deliverers_by_city(df1):
    slower_deliverers_by_city = pd.DataFrame(df1.groupby( [ 'City', 'Delivery_person_ID'] )['Time_taken(min)'].mean())
    slower_deliverers_by_city = slower_deliverers_by_city.sort_values(['City', 'Time_taken(min)'], ascending=False).reset_index()
    
    urban_slower_deliverers = slower_deliverers_by_city.query('City == "Urban"').head(10)
    semiurban_slower_deliverers = slower_deliverers_by_city.query('City == "Semi-Urban"').head(10)
    metropolitian_slower_deliverers = slower_deliverers_by_city.query('City == "Metropolitian"').head(10)
    
    slower_deliverers_by_city = pd.concat( [ urban_slower_deliverers, semiurban_slower_deliverers, metropolitian_slower_deliverers ] ).reset_index(drop=True)
    return round(slower_deliverers_by_city)




#=============================================================
# ----------- STREAMLIT -------------------------------------
#=============================================================


# ----------- SIDEBAR--------------------------------
#====================================================

# ---logo---
logo_path = 'images\logo.jfif'
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

# INTERVALO DE DATA
df1 =  df1.query('Order_Date >= @date_slider[0] & Order_Date <= @date_slider[-1]')

# CIDADES
df1 = df1.query('City in @city_options')

# TIPOS DE TRANSITO
df1 = df1.query('Weatherconditions in @weather_options')

# TIPOS DE CLIMA
df1 = df1.query('Weatherconditions in @weather_options')



# ----------- LAYOUT VISAO ENTREGADORES -------------------------
#================================================================

st.header( 'Marketplace - Visão Entregadores' )

tab1, = st.tabs( ['Visão Gerencial'] )

# Primeira Aba
with tab1:
    
    # Container superior
    with st.container():
        st.markdown("<h1 style='text-align: center; color: grey;'>Métricas Gerais</h1>", unsafe_allow_html=True)
        
        # 4 Colunas
        col1, col2, col3, col4 = st.columns( 4 ) 
        with col1:
            st.metric('Entregador mais novo', f' {youngest_deliverer(df1)} anos' )
        
        with col2:
            st.metric('Entregador mais velho', f' {oldest_deliverer(df1)} anos' )
            
        with col3:
            st.metric('Pior condição de veículo', worst_vehicle_condition(df1) )
        
        with col4:
            st.metric('Melhor condição de veículo', best_vehicle_condition(df1) )
            
        st.markdown("""---""")
    
    
    # Container do meio
    with st.container():
        
        col1, col2 = st.columns( 2 )
        
        with col1:
            st.markdown( 'Avaliação Média dos Entregadores' )
            st.dataframe( 
                deliverer_ratings_mean(df1),
                column_config={
                            'Delivery_person_ID': 'ID do Entregador',
                            'Delivery_person_Ratings': 'Avaliação Média'
                            })
        
        with col2:
            
            # Container 1 da segunda coluna
            with st.container():
                
                st.markdown( 'Avaliação Média e Desvio Padrão por tipo de tráfego' )
                st.dataframe(
                    rating_mean_std_by_traffic(df1),
                    hide_index=True,
                    column_config={
                        'Road_traffic_density': 'Tráfego'}
                )
                
            
            # Container 2 da segunda coluna
            with st.container():
                
                st.markdown( 'Avaliação Média e Desvio Padrão por condição climática' )
                st.dataframe(
                    rating_mean_std_by_weather(df1),
                    hide_index=True,
                    column_config={
                        'Weatherconditions': 'Clima'}
                )
                
        st.markdown("""---""")
        
    with st.container():
        
        col1, col2 = st.columns( 2 )
        
        with col1:
            
            st.markdown( '10 Entregadores mais RÁPIDOS por Cidade' )
            st.dataframe(
                faster_deliverers_by_city(df1),
                hide_index=True,
                column_config={
                    'City': 'Cidade',
                    'Delivery_person_ID': 'ID do Entregador',
                    'Time_taken(min)': 'Tempo(min)'
                }
            )
        
        with col2:
                        
            st.markdown( '10 Entregadores mais LENTOS por Cidade' )
            st.dataframe(
                slower_deliverers_by_city(df1),
                hide_index=True,
                column_config={
                    'City': 'Cidade',
                    'Delivery_person_ID': 'ID do Entregador',
                    'Time_taken(min)': 'Tempo(min)'
                }
            )
