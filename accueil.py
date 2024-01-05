from functions import best_movies,remove_special_characters,more_genres,tdidf_recom,nlp_reco,collab_reco,get_df_ratings,preprocess_sentence
from itertools import cycle
import fr_core_news_md
nlp = fr_core_news_md.load()

if len(st.session_state.df_user)==0:

    col1, col2, col3 = st.columns([2, 5, 2]) 
    with col2:
        st.subheader("🎞️ N'attendez plus pour vivre l'expérience CinéExplore 🎞️")
        st.markdown("#### Ajoutez vos films et découvrez de nouvelles recommandations!")

        st.write("1. Cliquez sur l'onglet Mes Films.")
        st.image('mesfilms.png',width=500)
        st.write("2. Sélectionnez des films grâce au menu déroulant.")
        st.image('menuderoulant.png',width=500)
        st.write("3. Notez les films.",width=500)
        st.image('note.png',width=500)
        st.write("4. Cliquez sur le bouton 'Sauvergarder Films'.")
        st.image('sauvegarder.png',width=500)
        st.write("5. Revenez sur la page d'accueil pour plus de recommandations.")
        st.image('accueil.png',width=500)

else:
    st.markdown("### Les meilleurs films de la plateforme")

    df_best= best_movies(st.session_state.df_movies)

    cols = cycle(st.columns(8))
    for index in range(len(df_best)):
        # recuperate the movie
        row = df_best.iloc[index]
        col = next(cols)
        # Image
        img_markdown = f"<a href='https://www.imdb.com/search/title/?title={remove_special_characters(row['Title'])}'><img src='{row['Affiche']}' width={150}></a><figcaption>{row['Title']}</figcaption>"
        col.markdown(img_markdown, unsafe_allow_html=True)
    
    st.markdown("### On pense que vous allez adorer ...")
    with st.spinner("Pas de panique le filtrage prend un peu de temps ..."):
        df_collab=collab_reco(get_df_ratings(),st.session_state['UserId'],8,50)
    cols = cycle(st.columns(8))
    for index in range(len(df_collab)):
            # recuperate the movie
            row = df_collab.iloc[index]
            col = next(cols)
            # Image
            img_markdown = f"<a href='https://www.imdb.com/search/title/?title={remove_special_characters(row['Title'])}'><img src='{row['Affiche']}' width={150}></a><figcaption>{row['Title']}</figcaption>"
            col.markdown(img_markdown, unsafe_allow_html=True)

    df_tdidf,movie_tdidf=tdidf_recom()
    st.markdown(f"### Parce que vous avez regardé et aimé {movie_tdidf}")

    cols = cycle(st.columns(8))
    for index in range(len(df_tdidf)):
        # recuperate the movie
        row = df_tdidf.iloc[index]
        col = next(cols)
        # Image
        img_markdown = f"<a href='https://www.imdb.com/search/title/?title={remove_special_characters(row['Title'])}'><img src='{row['Affiche']}' width={150}></a><figcaption>{row['Title']}</figcaption>"
        col.markdown(img_markdown, unsafe_allow_html=True)


    if "demande_user" in st.session_state:
        demande=preprocess_sentence(st.session_state.demande_user,1, pos=["NOUN", "ADJ"])
        st.markdown(f"### Parce que vous avez recherché: films {demande}")
        with st.spinner("Pas de panique le filtrage prend un peu de temps ..."):
            df_nlp=nlp_reco(demande, st.session_state.df_movies, 8,1)
        cols = cycle(st.columns(8))
        for index in range(len(df_nlp)):  
            # recuperate the movie
            row = df_nlp.iloc[index]
            col = next(cols)
            # Image
            img_markdown = f"<a href='https://www.imdb.com/search/title/?title={remove_special_characters(row['Title'])}'><img src='{row['Affiche']}' width={150}></a><figcaption>{row['Title']}</figcaption>"
            col.markdown(img_markdown, unsafe_allow_html=True)
        


    best_genre,df_genres=more_genres(st.session_state.df_user,st.session_state.df_movies)
    st.markdown(f"### Plus de {best_genre}")

    cols = cycle(st.columns(8))
    for index in range(len(df_genres)):
        # recuperate the movie
        row = df_genres.iloc[index]
        col = next(cols)
        # Image
        img_markdown = f"<a href='https://www.imdb.com/search/title/?title={remove_special_characters(row['Title'])}'><img src='{row['Affiche']}' width={150}></a><figcaption>{row['Title']}</figcaption>"
        col.markdown(img_markdown, unsafe_allow_html=True)
