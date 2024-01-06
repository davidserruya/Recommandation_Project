# Projet Infrastructure et Systèmes Logiciels - Application de Recommandation de films Cinématch

 
## ENSAE Paris - MS Data Science
 
Membres du groupe : 
- Jérémy DREUMONT, Ahmed OUASSOU, Cindy PORFIRIO, Ilias RAZIG, David SERRUYA

## Objectif

Ce projet Python a été créé dans le but de fournir à des utilisateurs des recommandations personnalisées de films à regarder sur la base de plusieurs méthodes de recommandation : le filtrage collaboratif et l'utilisation de NLP sur les synopsis des films. Ce dernier se traduit par une application web où vous trouverez le lien vers la démo youtube ici : https://youtu.be/lYTnrR0yYwE


## Fonctionnalités générales
 
1. *Recommandation par filtrage collaboratif :* Après s'être connecté, l'utilisateur renseigne les films qu'il a regardés parmi la liste des films ainsi que leurs notes associées. Par la suite un algorithme de filtrage collaboratif basé sur la décomposition de matrice propose des recommandations de films basés sur les notes entrées. Cette approche identifie les utilisateurs similaires en fonction de leurs historiques de notation pour faire des recommandations.
   
     De manière générale, il est à noter que cette méthode est confrontée à plusieurs limites dont le problème de démarrage à froid signifiant que les nouveaux utilisateurs doivent noter suffisamment de films pour que le système puisse déterminer leurs préférences. Par ailleurs, les nouveaux films n'ayant pas encore été suffisamment notés ne peuvent être recommandés de manière fiable.
Une seconde limite qu'on pourrait appeler "homogénéisation des recommandations" est l'idée selon laquelle l'algorithme tend à recommander des films populaires et biens notés, conduisant à une certaine uniformité des recommandations et ainsi une sous-représentation des films de niche. Enfin, les évaluations de films peuvent connaître des inexactitudes dues au manque d'implication des utilisateurs au moment de la notation, ce qui introduit des biais et réduit la pertinence des recommandations générées par le système.


4. *Recommandation par NLP :* L'utilisateur interagit avec une boite de dialogue contenant le message :

Que voulez-vous voir aujourd'hui ? 👋"

L'utilisateur entre par la suite un texte contenant ses envies de films à regarder afin d'obtenir des recommandations personnalisées. Cette étape implique l'extraction des mots-clés pertinents. Par exemple, si un utilisateur écrit "Je veux un film d'aventures", le système identifie un ou des éléments clé tels qu' "aventure". Néanmoins, cette méthodologie est confrontée à plusieurs limites pour interpréter correctement les préférences de l'utilisateur notamment pour les demandes complexes ou très spécifiques.

## Fonctionnalités détaillées


### Connexion et Gestion des utilisateurs

L'utilisateur établit une première connexion à une base de données PostgresSQL. Cette étape gère l'état de la session d'authentification et ajoute un nouvel utilisateur à la base de données après avoir vérifié que le nom d'utilisateur n'est pas déjà pris.

### Gestion des films

Dans un premier temps, l'utilisateur doit noter les films dans l'onglet "Mes Films" afin que le système puisse recommander des nouveaux films. L'utilisateur est invité à rechercher les films manuellement les films qu'il a déjà vu. Suite à ça, la base de données sera mise à jour avec les nouveaux films ou notes ajoutés par un utilisateur.

### Recommandations de films

Il est à noter qu'en amont la base de données a été nettoyé (gestion des valeurs aberrantes etc.) mais aussi le texte a été pré-traité en ne conservant que les mots alphanumériques. Autrement dit, les signes de ponctuation et les mots peu informatifs (comme "le", "et", "dans", etc.) sont éliminés réduisant le bruit dans les données.

Dans l'onglet "Recommandation", l'utilisateur exprimera ce qu'il souhaitera regarder par exemple : "Je veux voir un film de basketball".

Puis dans l'onglet accueil, le site affichera : 

- *Les "meilleurs films de la plateforme"* : Affiche les films mieux notés de la base de données (c'est-à-dire les films ayant des notes supérieures à 4.1).
  
- *"On pense que vous allez adorer"* : La méthode utilisée est le traitement du langage naturel avec TF-IDF (Term Frequency-Inverse Document Frequency) et Nearest Neighbors.
Cette fonction utilise le NLP pour analyser la description textuelle donnée par l'utilisateur. Elle convertit cette description en vecteurs numériques à l'aide de la méthode TF-IDF, qui mesure l'importance d'un mot dans un document. Ensuite, elle utilise l'algorithme des plus proches voisins (Nearest Neighbors) pour trouver les films dont les synopsis sont les plus similaires à la description de l'utilisateur.


- *"Parce que vous avez regardé et aimé Toy Story"* : Méthode basée sur les notes des utilisateurs et les similarités entre eux avec SVD (Singular Value Decomposition). Elle utilise la décomposition en valeurs singulières (SVD) pour créer un système de recommandation basé sur le filtrage collaboratif. Elle prédit les notes qu'un utilisateur pourrait donner à des films qu'il n'a pas encore vus, basé sur les préférences d'utilisateurs aux goûts similaires.


- *"Parce que vous avez recherché :"* Utilise TF-IDF pour convertir les synopsis des films en vecteurs et puis applique la similarité cosinus pour trouver les films dont les synopsis sont le plus similaire à ceux qu'un   utilisateur a déjà appréciés. On appelle "similarité du cosinus" une mesure mathématique qui détermine à quel point deux vecteurs sont similaires en calculant le cosinus de l'angle entre eux. Une valeur proche de 1 indique une grande similarité, tandis qu'une valeur proche de 0 indique peu ou pas de similarité.






<img src="cosinus.png" height="800">





- *"Plus de ce genre"* : Analyse basée sur le genre autrement dit le système suggère des films dans le genre que l'utilisateur semble préférence au regard de son historique.
  



## Les étapes pour accéder à l'application 


La commande ```git clone``` peut prendre un peu de temps vu le fichier pickle volumineux.

Pour une meilleure expérience, activez le mode dark via le bouton en haut à droite dans settings !


Le script ```automatisation.sh``` permet la creation les environnements et les conteneurs;il vérifie d'abord le nombre d'arguments passés au script. Si l'utilisateur ne fournit pas exactement deux arguments lors de l'exécution du script, il affiche un message d'utilisation indiquant comment utiliser le script. Les deux arguments attendus sont le nom d'utilisateur PostgreSQL ($1) et le mot de passe PostgreSQL ($2).
Après il procedera à la creation des environnements et des conteneurs. pour lancer le script 
```./automatisation.sh POSTGRES_USER POSTGRES_PASSWORD```

L'application se deploie via Docker compose ```docker-compose up -d```, pour que le fichier Docker compose s'éxecute correctement, il faut creer un volume Data: ```docker volume create Data``` et ce volume va contenir le fichier db_sql.csv.
L'utilisateur et le mot de passe de PostgreSQL dans le docker compose sont renseignés dans un fichier caché .env dans le repertoire racine.

## Remarques
Il y a deux fichiers cachés : ```.env``` qui se trouve dans la racine du projet et qui contient l'utilisateur et le mot de passe PostgresSQL.
```
POSTGRES_USER=xxx
POSTGRES_PASSWORD=xxx
```

Il y a aussi un repertoire caché ```.streamlit``` qui contient un fichier ```secrets.toml``` qui permet d'établir la connexion entre streamlit et la base de données PostgreSQL. Ce fichier secret doit avoir le même user et password que le ```.env```.
```
[connections.postgresql]
dialect = "postgresql"
host = "POSTGRES_CONTAINER_NAME"
port = "5432"
database = "recommandations"
username = "xxx"
password = "xxx"
```

## Références

- GroupLens (2019).MovieLens 25M Dataset : https://grouplens.org/datasets/movielens/25m/ & https://www.kaggle.com/datasets/garymk/movielens-25m-dataset
- Tyrrell4innovation.(2010). MiWORD of the Day Is…Cosine Distance! : https://www.tyrrell4innovation.ca/miword-of-the-day-iscosine-distance/
- tmls-2020-recommender-workshop : https://github.com/topspinj/tmls-2020-recommender-workshop
- movie-recommender-system : https://github.com/vivdalal/movie-recommender-system
