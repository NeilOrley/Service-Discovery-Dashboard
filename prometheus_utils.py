import logging
import requests
import datetime
from consul_utils import is_service_in_consul
import configparser

# Load configurations from config.ini
config = configparser.ConfigParser()
config.read('config.ini')
PROMETHEUS_URL = config['DEFAULT']['PROMETHEUS_URL']

# Configuration de la journalisation
app_name = 'Service-Discovery-Dashboard'
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - " + app_name + " - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def query_prometheus_and_extract_os(results,dc):
    if results["infrastructure"][dc]["Node"]["Name"] :
        # Paramètres de la requête
        vm_name = results["infrastructure"][dc]["Node"]["Name"]
        params = {
            'query': 'windows_os_info{hostname=~"' + vm_name + '"} or node_uname_info{hostname=~"' + vm_name + '"}'
        }

        try:
            # Effectuer la requête HTTP GET vers Prometheus de manière synchrone
            response = requests.get(PROMETHEUS_URL, params=params)
            logger.debug(f"Function {query_prometheus_and_extract_os.__name__} Response: {response}")
            if response.status_code == 200:
                data = response.json()
                logger.debug(f"Function {query_prometheus_and_extract_os.__name__} data / result : {data}")
                # Vérifiez si le statut de la réponse est "success"
                if data["status"] == "success":
                    result = data["data"]["result"]                    
                    if result:
                        logger.debug(f"Function {query_prometheus_and_extract_os.__name__} Prom Query Result: {result}")
                        for item in result:
                            if isinstance(item, dict):
                                metric = item.get("metric", {})
                                sysname = metric.get("sysname", "N/A")
                                release = metric.get("release", "N/A")
                                results["infrastructure"][dc]["Node"]["Os"] = sysname
                                results["infrastructure"][dc]["Node"]["Version"] = release
                    else:
                        logger.info("Aucun résultat trouvé.")
            else:
                logger.error(f"La réponse de Prometheus n'est pas un succès. {response.text}")

            logger.debug(f"Function {query_prometheus_and_extract_os.__name__} returns : {results}")
            return results

        except requests.RequestException as exc:
            logger.error(f"Une erreur de requête HTTP s'est produite : {str(exc)}")
            logger.debug(f"Function {query_prometheus_and_extract_os.__name__} returns : {results}")
            return results
        

def query_prometheus_and_extract_container_last_seen(results,dc,registered_services):
    logger.debug(f"Function {query_prometheus_and_extract_container_last_seen.__name__} enter with: {results}")

    if results["infrastructure"][dc]["Node"]["Name"] :
        # Paramètres de la requête
        vm_name = results["infrastructure"][dc]["Node"]["Name"]
        params = {
            'query': 'container_last_seen{hostname="' + vm_name + '"}'
        }

        try:
            # Effectuer la requête HTTP GET vers Prometheus de manière synchrone
            response = requests.get(PROMETHEUS_URL, params=params)
            last_seen_timestamp = 0
            logger.debug(f"Function {query_prometheus_and_extract_container_last_seen.__name__} Response: {response}")
            if response.status_code == 200:
                data = response.json()
                # Vérifiez si le statut de la réponse est "success"
                if data["status"] == "success":
                    result = data["data"]["result"]
                    if result:
                        logger.debug(f"Function {query_prometheus_and_extract_container_last_seen.__name__} Prom Query Result: {result}")
                        for item in result:
                            if isinstance(item, dict):
                                metric = item.get("metric", {})
                                appli = metric.get("appli", "N/A")
                                image = metric.get("image", "N/A")
                                name = metric.get("name", "N/A")
                                if len(item.get("value", [])) >= 2:
                                    last_seen_timestamp = item["value"][0]
                                    last_seen_date = datetime.datetime.fromtimestamp(last_seen_timestamp).strftime('%Y-%m-%d %H:%M:%S')
                                in_consul = is_service_in_consul(name, registered_services)
                                if name != 'N/A':
                                    results["containers"].append({
                                        "VM Name": vm_name,
                                        "App Name": appli,
                                        "Image": image,
                                        "Container Name": name,
                                        "In Consul": in_consul,
                                        "Updated on": last_seen_date
                                    })
                                    logger.debug(f"service in consul {query_prometheus_and_extract_container_last_seen.__name__} returns : {in_consul}")
                    else:
                        logger.info("Aucun résultat trouvé.")
            else:
                logger.error(f"La réponse de Prometheus n'est pas un succès. {response.text}")

            logger.debug(f"Function {query_prometheus_and_extract_container_last_seen.__name__} returns : {results}")
            return results

        except requests.RequestException as exc:
            logger.error(f"Une erreur de requête HTTP s'est produite : {str(exc)}")
            logger.debug(f"Function {query_prometheus_and_extract_container_last_seen.__name__} returns : {results}")
            return results

        

def query_prometheus_and_extract_node_informations(node_name, dc):
    logger.debug(f"Entering function {query_prometheus_and_extract_node_informations.__name__}")
    result = {}
    result[dc] = {}

    # Paramètres de la requête
    params = {
        'query': 'vmware_vm_power_state{vm_name="'+node_name+'"}'
    }
    
    try:
        # Effectuer la requête HTTP GET vers Prometheus de manière synchrone
        response = requests.get(PROMETHEUS_URL, params=params)

        logger.debug(f"Function {query_prometheus_and_extract_node_informations.__name__} Response: {response}")
        if response.status_code == 200:
            data = response.json()
            # Vérifiez si le statut de la réponse est "success"
            if data["status"] == "success":
                prom_response = data["data"]["result"]
                if prom_response:
                    logger.debug(f"Function {query_prometheus_and_extract_node_informations.__name__} Prom Query Result: {result}")
                    # Récupérer les valeurs du premier résultat
                    prom_result = prom_response[0]
                    cluster_name = prom_result["metric"]["cluster_name"]
                    dc_name = prom_result["metric"]["dc_name"]
                    ds_name = prom_result["metric"]["ds_name"]
                    host_name = prom_result["metric"]["host_name"]
                    instance = prom_result["metric"]["instance"]
                    if len(prom_result["value"]) >= 2:
                        last_polling_timestamp = prom_result["value"][0]
                        last_polling_date = datetime.datetime.fromtimestamp(last_polling_timestamp).strftime('%Y-%m-%d %H:%M:%S')
                        vm_status = "UP" if prom_result["value"][1] == "1" else "DOWN"

                    logger.debug(f"Function {query_prometheus_and_extract_node_informations.__name__} values extracted : {cluster_name}, {dc_name}, {ds_name}, {host_name}, {instance}, {last_polling_date}, {vm_status}")

                    # Ajouter ces valeurs à infrastructure_data
                    result[dc]["Cluster Name"] = cluster_name
                    result[dc]["DC Name"] = dc_name
                    result[dc]["Datastore Name"] = ds_name
                    result[dc]["Hypervisor"] = host_name
                    result[dc]["Manager"] = instance
                    result[dc]["VM Status"] = vm_status
                    result[dc]["Updated on"] = last_polling_date
                else:
                    logger.info("Aucun résultat trouvé.")
        else:
            logger.error(f"La réponse de Prometheus est en erreur: {response.text}")

        logger.debug(f"Function {query_prometheus_and_extract_node_informations.__name__} returns : {result}")

    except requests.RequestException as exc:
        logger.error(f"Une erreur de requête HTTP s'est produite : {str(exc)}")

    return result
    
