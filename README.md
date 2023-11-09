# Service-Discovery-Dashboard

Service-Discovery-Dashboard est un tableau de bord de découverte de service, permettant une visualisation et une gestion faciles des services dans un système Consul. Ce projet sert à interroger Consul pour obtenir des données d'infrastructure, des URL de service, l'état de santé des services, et bien plus encore.

## Fonctionnalités

- Extraction des données d'infrastructure de Consul pour chaque centre de données
- Récupération et affichage des URLs de services à partir des balises de service Consul
- Vérification de la présence d'un service dans la liste des services enregistrés avec Consul
- Recherche de centres de données qui ont un service spécifique enregistré
- Liste des services disponibles dans un ou plusieurs centres de données spécifiés
- Vérification asynchrone de l'état de santé d'un service dans plusieurs centres de données

## Prérequis

Avant de démarrer, assurez-vous d'avoir installé les logiciels suivants :

- Python 3.6+
- pip (pour installer les dépendances)

## Installation

Pour installer les dépendances du projet, exécutez la commande suivante :

```bash
pip install -r requirements.txt
```

## Configuration

Avant de lancer le tableau de bord, vous devez configurer l'adresse de l'hôte Consul et l'URL de Prometheus dans le fichier `config.ini`. V
oici un exemple de la section à ajouter/modifier dans ce fichier :

```ini
[DEFAULT]
PROMETHEUS_URL = "http://mypromserver/api/v1/query"
CONSUL_HOST = "myconsulfqdn"
```

Remplacez `myconsulfqdn` par l'adresse réelle de votre serveur Consul.
Remplacez `mypromserver` par l'adresse réelle de votre serveur Consul.

## Utilisation

Après la configuration, vous pouvez lancer l'application avec la commande :
```bash
uvicorn main:app --reload
```

## Sécurité

Veuillez noter que pour des raisons de simplicité, la vérification SSL est désactivée (`verify=False`) lors des requêtes HTTP. 
Il est fortement recommandé d'activer la vérification SSL dans un environnement de production pour des raisons de sécurité.

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus d'informations.

## Avertissement

Ce projet est un projet personnel d'expérimentation. Les contributions, ainsi que l'ouverture de problèmes (bugs), ne sont pas acceptées.

---

Ce projet est un travail en cours et peut être sujet à des changements importants. Utilisez-le à vos risques et périls.

```