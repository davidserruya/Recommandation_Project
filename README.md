# Projet Infrastructure et Systèmes Logiciels - Application de Recommandation de films Cinématch

 
## ENSAE Paris - MS Data Science
 
Membres du groupe : 
- Jérémy DREUMONT , Ahmed OUASSOU , Cindy PORFIRIO, Ilias RAZIG, David SERRUYA

## Objectif :
 
Ce projet Python a été créé dans le but de fournir à des utilisateurs des recommandations personnalisées de films à regarder sur la base de plusieurs méthodes de recommandation : le filtrage collaboratif et l'utilisation de NLP sur les synopsis des films. Ce dernier se traduit par une application web où vous trouverez le lien vers la démo youtube ici : 


## Fonctionnalités 
 
1. **Recommandation par filtrage collaboratif :** Après la connexion de l'utilisateur, l'utilisateur renseigne les films qu'il a regardé parmi la liste des films ainsi que leurs notes correspondantes. Par la suite un algorithme de filtrage collaboratif basé sur la décomposition de matrice propose des recommandations de films basé sur les notes entrées. Cette approche identifie les utilisateurs similaires en fonction de leurs historiques de notation pour faire des recommandations.
   
     De manière générale, il est à noter que cette méthode est confrontée à plusieurs limites dont le problème de démarrage à froid signifiant que les nouveaux utilisateurs doivent noter suffisamment de films pour que le système puisse déterminer leurs préférences. Par ailleurs, les nouveaux films n'ayant pas encore été suffisamment notés ne peuvent être recommandés de manière fiable.
Une seconde limite qu'on pourrait appeler "homogénisation des recommandations" est l'idée selon laquelle l'algorithme tend à recommander des films populaires et biens notés, conduisant à une certaine uniformité des recommandations et ainsi une sous-représentation des films de niche. Enfin, les évaluations de films peuvent connaître des inexactitudes dues au manque d'implication des utilisateurs au moment de la notation, ce qui introduit des biais et réduit la pertinence des recommandations générées par le système.


4. **Recommandation par NLP :** L'utilisateur interagit avec une boite de dialogue contenant le message 👋! Que voulez-vous voir aujourd'hui ?" . L'utilisateur entre par la suite un texte contenant ses envies de films à regarder afin d'obtenir des recommandations basées sur le texte entré. Cette étape implique l'extraction des mots-clés pertinents et la détermination des préférences sous-jacentes de l'utilisateur. Par exemple, si un utilisateur écrit "Je veux un film d'aventure", le système identifie un ou des éléments clés tels que "aventure".Néanmoins, cette méthodologie est confronté à des limites lors de l'analyse sémantique. Le système ne peut pas toujours interpréter correctement les préférences de l'utilisateur notamment pour des demandes complexes ou très spécifiques.


## Les étapes pour accéder à l'application 

1.
2. 


## Références

- GroupLens (2019).MovieLens 25M Dataset : https://grouplens.org/datasets/movielens/25m/ & https://www.kaggle.com/datasets/garymk/movielens-25m-dataset
- 
