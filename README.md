# LITRevu!

Description:
	
LITRevu est une start-up innovante qui souhaite lancer une application web permettant aux utilisateurs de publier, lire et demander des critiques de livres ou d’articles. Le projet vise à fédérer une communauté active autour du contenu littéraire et critique, tout en offrant une interface intuitive et accessible.
# Installation:
# Prérequis

* Python 3.10.11 installé sur votre machine 
* Virtualenv installé sur votre machine
* Django installé sur votre machine

## Etape 1: Clonez le dépôt :

    git clone https://github.com/Laureopen/Projet9.git

## Etape 2: Se mettre à la racine du projet:

    cd Projet9

## Etape 3: Pour créer environnement virtuel :

    python -m venv Projet9

- fonctionne sous windows, Linux et MacOs.

## Pour activer l'environnement sous Linux et MacOS

    source Projet9/bin/activate

## Pour activer l'environnement sous windows

    projet9\Scripts\activate

## Etape 4: Installez les dépendances nécessaires :

    pip install -r requirements.txt

## Etape 5: Mettre les migrations de la base de données

    python manage.py makemigrations
   
    python manage.py migrate

## Etape 6: Créer un superutilisateur (admin)
 
    python manage.py createsuperuser

## Etape 7: Lancer le serveur de développement

    python manage.py runserver

## Etape 8: Accéder à l'application dans le navigateur

   http://127.0.0.1:8000/



