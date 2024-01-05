# Projet Infrastructure et Systèmes Logiciels - Application de Recommandation de films "Nom final de l'app"

 
## ENSAE Paris - MS Data Science
 
Membres du groupe : 
- Jérémy DREUMONT, Ahmed OUASSOU, Cindy PORFIRIO, Ilias RAZIG, David SERRUYA
 
Ce projet Python a été créé dans le but de fournir à des utilisateurs des recommandations personnalisées de films à regarder sur la base de plusieurs méthodes de recommandation : le filtrage collaboratif et l'utilisation de NLP sur les synopsis des films. Les films, les avis, les synopsis ainsi que les affiches des films proviennent tous de IMDB.com
 
## Fonctionnalités 
 
1. **Recommandation par filtrage collaboratif :** Après la connexion de l'utilisateur, l'utilisateur renseigne les films qu'il a regardé parmi la liste des films ainsi que leurs notes correspondantes. Par la suite un algorithme de filtrage collaboratif basé sur la décomposition de matrice propose des recommandations de films basées sur les notes entrées.
 
2. **Recommandation par NLP :** L'utilisateur interagit avec une boite de dialogue contenant le message "👋! Que voulez-vous voir aujourd'hui ?". L'utilisateur entre par la suite un texte contenant ses envies de films à regarder afin d'obtenir des recommandations basées sur le texte entré.
