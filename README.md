# SAE_BUT3_BIBLIOGRAPHIE

Guide d'installation et de lancement de l'application

Ce guide vous explique étape par étape comment installer et lancer l'application.

1. Cloner le dépôt GitHub

Si vous êtes familier avec Git, vous pouvez cloner le dépôt en exécutant la commande suivante dans un terminal :

git clone <URL_DU_DEPOT>

Sinon, suivez ces étapes :

Rendez-vous sur le lien du dépôt GitHub.

Cliquez sur le bouton "Code".

Sélectionnez "Télécharger ZIP".

Une fois le fichier ZIP téléchargé, extrayez son contenu sur votre PC.

2. Ouvrir un terminal dans le dossier du projet

Après avoir obtenu le dossier du projet, placez-vous dans l'endroit où il est situé et ouvrez un terminal.

3. Créer un environnement virtuel (venv)

Avant d'installer les dépendances, il est recommandé d'utiliser un environnement virtuel Python :

virtualenv venv

Cette commande crée un environnement virtuel où seront installées les dépendances du projet.

4. Activer l'environnement virtuel

Sous Linux/macOS :

source venv/bin/activate

5. Accéder au dossier de l'application Electron

Une fois l'environnement virtuel activé, accédez au dossier AppElectronJS de l'application :

cd SAE_BUT3_BIBLIOGRAPHIE/AppElectronJS

6. Installer les dépendances Python

Assurez-vous d'avoir Python et pip installés. Si ce n'est pas le cas, consultez un tutoriel d'installation de Python.
Ensuite, installez les dépendances en exécutant :

pip install -r requirements.txt

7. Vérifier l'installation de npm

Assurez-vous que npm est installé sur votre machine en faisant npm -v. Si ce n'est pas le cas, installez-le en suivant les instructions sur le site officiel de Node.js.

8. Lancer l'application

Une fois tout installé, lancez l'application avec la commande suivante :

npm start

Si la commande ne fonctionne pas, essayez d'abord d'installer Electron avec :

npm install electron --save-dev

Puis relancez la commande :

npm start

Votre application devrait maintenant être opérationnelle ! 🚀


