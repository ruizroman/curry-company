import streamlit as st
from PIL import Image

st.set_page_config(
    page_title= "Home",
    page_icon= "🍜"
)

# ---logo---
logo_path = 'logo.jfif'
logo_image = Image.open( logo_path )

st.sidebar.image(
    logo_image,
    width=150
)

# ---title----
st.sidebar.markdown( '# Curry Company' )
st.sidebar.markdown( "## Fast 'n Delicious" )
st.sidebar.markdown( """---""" )

st.write ( "# Curry Company Growth Dashboard" )
st.markdown (
    """
    Growth Dashboard foi construído para acompanhar as métricas de crescimento dos Entregadores e Restaurantes.
    ### Como utilizar esse Growth Dashboard?
    
    - Visão Empresa:
        - Visão Gerencial: Métricas gerais de comportamento.
        - Visão Tática: Indicadores semanais de crescimento.
        - Visão Geográfica: Insights de geolocalização.
        
    - Visão Entregador:
        - Acompanhamento dos indicadores semanais de crescimento dos restaurantes,
        
    - Visão Restaurantes:
        - Indicadores gerais de crescimento dos restaurantes.
    """
)