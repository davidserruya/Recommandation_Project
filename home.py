import streamlit as st
from functions import check_credentials, add_user, deconnexion,get_my_movies,init_resource
from streamlit_option_menu import option_menu
import pandas as pd

st.set_page_config(
        page_title="netflix",
        page_icon="🎞️",
        layout="wide"
    )
st.markdown(""" <style> .block-container {padding-top: 2.5rem; padding-bottom: 0rem;} </style> """, unsafe_allow_html=True)

if "authentication_status" not in st.session_state or st.session_state["authentication_status"]!=True:
    st.markdown('<h1 style="text-align: center;">BIENVENUE SUR NETFLIX</h1><br>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
       with st.form("Connexion"):
          st.write("Connexion")
          username = st.text_input('Username')
          password = st.text_input("Password",type="password")
          submitted = st.form_submit_button("Se connecter")
          if submitted:
             if check_credentials(username, password):
                st.success("Connexion réussie !")
                st.experimental_rerun()
             else:
                if st.session_state["authentication_status"]=='Username':
                     st.error("Nom d'utilisateur incorrect.")
                else:
                    st.error("Mot de passe incorrect.")

    with col2:
       with st.form("Inscription"):
          st.write("Inscription")
          username = st.text_input('Username')
          password = st.text_input("Password",type="password")
          submitted_inscription = st.form_submit_button("S'inscrire")
          if submitted_inscription:
             if add_user(username, password):
                st.success("Inscription réussie !")
             else:
                st.error("Nom d'utilisateur non disponible")

else:
    if st.button('Se déconnecter'):
        deconnexion()
    
    if 'df_user' not in st.session_state and 'df_movies' not in st.session_state:
       st.session_state.df_movies = pd.read_csv('csv/movies.csv')
       st.session_state.df_user = get_my_movies(st.session_state['UserId'])
    nn,model = init_resource()
    
    st.markdown('<h1 style="text-align: center;">NETFLIX</h1><br>', unsafe_allow_html=True)
    menu = option_menu(None, ["Accueil", "Mes films", "Recommandations"], 
             icons=['house', "film", "search"],  orientation="horizontal",
             menu_icon="cast", default_index=0,styles={
             "container": {"font-family": "Arial"},
             "icon": {"font-size": "20px"},
             "nav-link-selected": {"background-color": "#2596be"}
         })

    if menu=="Accueil":
           if "messages" in st.session_state:
                 st.session_state.pop("messages")
           with open("", "r", encoding="utf-8") as file:
             exec(file.read())

    elif menu=="Mes films":
           if "messages" in st.session_state:
                 st.session_state.pop("messages")
           with open("mymovies.py", "r", encoding="utf-8") as file:
             exec(file.read())

    elif menu=="Recommandations":
           with open("recommandations.py", "r", encoding="utf-8") as file:
             exec(file.read())

    

