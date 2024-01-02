from functions import best_movies,remove_special_characters,more_genres,tdidf_recom,nlp_reco,extraire_mot_cle
from itertools import cycle

if len(st.session_state.df_user)==0:
    st.markdown("### Nous n'avons pas de recommandations pour le moment.")
    st.markdown("#### N'attendez plus! Ajoutez plus de films à votre liste et laissez nous vous recommander")

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
        demande=extraire_mot_cle(st.session_state.demande_user)
        df_nlp=nlp_reco(model,nn,demande)
        st.markdown(f"### Parce que vous avez recherché: films {demande}")
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
