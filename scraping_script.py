# Import des librairies 
from bs4 import BeautifulSoup
import pandas as pd
import requests

# Function permettant de charger la page 
def retrieve_movies_results(url):
    try:
        # On crée une session de navigation web
        session = requests.Session()
        response = session.get(url)
        
        # On récupère les paramètres de cookies
        cookies_dictionary = session.cookies.get_dict()

        # On construire le cookie
        cookie = '; '.join([f'{key}={value}' for key, value in cookies_dictionary.items()])

        # On récupère le contenu dans l'url avec la configuration indiquée dans le header
        USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0"
        headers = {"user-agent": USER_AGENT, "cookie": cookie}  # Ajouter le cookie au header
        html_text = requests.get(url, headers=headers, timeout=20).text

        return html_text
    except :
        print('La requête a échouée')
        return None
    
 # Fonction permettant de mettre en forme les résultats de la page    
def process_results(html_text):
    # La libraire BeautifulSoup permet de parser le texte que nous avons extrait de la page web
    soup = BeautifulSoup(html_text, features= "lxml")
    # On recherche tous les éléments html <div> qui indiquent des divisions vers la classe que nous cherchons à importer 
    #results = soup.find_all('div', {'class' : 'ipc-html-content-inner-div'})
    data = [synopsis.text for synopsis in soup.find_all('div', {'class' : 'ipc-html-content-inner-div'})]
    #titles  = [title.text for title in soup.find_all('h3', {'class' : 'ipc-title__text'})]  Pour importer les titres mais le soucis est que les titres n'ont pas toujours de descriptions ce qui implique un mismatch de longeur des deux listes.
    results = pd.DataFrame({'Synopsis' : data})
                            #'Titre' : titles})
        
    return results

# Fonction permettant de matcher dans un dataframe le premier résultat de la recherche ainsi que le nom du film recherché
def merging(url, movies) :
    synops = []
    i = 0
    for val in movies.unique() :
        try :
            movie = val.replace(" ", "%20")
            complete_url = url+movie
            html_text = retrieve_movies_results(complete_url)
            results_df = process_results(html_text)
            synops.append(results_df['Synopsis'][0])   
        except : # Parfois un film ne comporte pas de description référencée sur IMDB et parfois soucis de matching entre les noms de la base et ceux de IMDB
            synops.append("Description non available")
        i = i+1
        print("Scraping du " + str(i) + "e film : " + val)
    match = pd.DataFrame({'Synopsis' : synops,
                                'title' : movies.unique()})
    return match

# Import des noms des films
def movie_names_import (path):
    names = pd.read_csv(path)
    return names

#On récupère les films déjà scrapés 
def load_existing_base (file = "descriptions.csv"):
    # On essaie de charger la base de données existante
    try :
        base = pd.read_csv(file)
    #... sinon on la crée 
    except :
        # on crée un dataframe avec les bonnes colonnes
        columns = ["", "Synopsis", "title"]
        base = pd.DataFrame(columns=columns)
        # on l'enregistre au format csv
        base.to_csv(file)
    return base["title"]

existing_base = load_existing_base (file = "descriptions.csv")
all_movies = movie_names_import("movies_final.csv")
all_movies = all_movies[~all_movies['title'].isin(existing_base.values.tolist())]


# On définit la fréquence de stockage du nombre de films
def iter(freq = 100) : 
    num_subsets = len(all_movies) // freq + 1
    j = 0
    # On intère
    for i in range(num_subsets):
        print(str(i)+"e itération")
        start_idx = j
        end_idx = j+freq - 1
        sub_movies = all_movies.iloc[start_idx:end_idx]
        # Lancement du scraping et stockage dans un csv 
        synopsis_base = merging(url = 'https://www.imdb.com/search/title/?title=', movies = sub_movies["title"])
        old_df = pd.read_csv("descriptions.csv")
        new_df = pd.concat([old_df,synopsis_base],ignore_index=True)
        new_df.to_csv("descriptions.csv")
        j = j+freq

iter(freq = 100) 




