from functions import remove_special_characters,nlp_reco,capitalize_first_letter
from itertools import cycle
import fr_core_news_md
nlp = fr_core_news_md.load()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

with st.chat_message('assistant'):
        st.markdown(f"Hey {capitalize_first_letter(st.session_state['Username'])} 👋! Que voulez-vous voir aujourd'hui ?")


utilisateur_message = st.text_input("Votre message:")
if st.button("GO"):
    with st.spinner("Pas de panique le filtrage prend un peu de temps ..."):
            reco=nlp_reco(utilisateur_message, st.session_state.df_movies, 5,3)
    if isinstance(reco, pd.DataFrame):
        st.session_state.demande_user=utilisateur_message
    st.session_state.messages.append({"role": "assistant", "content": reco})
    st.session_state.messages.append({"role": "user", "content": utilisateur_message})


for message in reversed(st.session_state.messages):
        with st.chat_message(message["role"]):
            if message["role"]=='assistant':
                if not isinstance(message['content'], pd.DataFrame):
                    st.write(message["content"])
                else:
                    cols = cycle(st.columns(5))
                    for index in range(len(message["content"])):
                        row = message["content"].iloc[index]
                        col = next(cols)
                        img_markdown = f"<a href='https://www.imdb.com/search/title/?title={remove_special_characters(row['Title'])}'><img src='{row['Affiche']}' width={200}></a><figcaption>{row['Title']}</figcaption>"
                        col.markdown(img_markdown, unsafe_allow_html=True)
            else:
                st.write(message["content"])



