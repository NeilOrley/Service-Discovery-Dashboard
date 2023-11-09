import logging
import re
import httpx
import requests
import configparser

# Load configurations from config.ini
config = configparser.ConfigParser()
config.read('config.ini')
CONSUL_HOST = config['DEFAULT']['CONSUL_HOST']

# Configuration de la journalisation
app_name = 'Service-Discovery-Dashboard'
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - " + app_name + " - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def extract_infrastructure_data_from_consul(consul_response, dc_list) :
    logger.debug(f"Entering function {extract_infrastructure_data_from_consul.__name__}")   
    result = {}
    for dc in dc_list :
        result[dc] = {}
        for service_data in consul_response[dc]:
            node_data = service_data.get("Node", {})   

            ip_address = node_data.get("Address", "")
            node_name = node_data.get("Node", "")    
            result[dc]["IP Address"] = ip_address
            result[dc]["Node Name"] = node_name

        logger.debug(f"Function {extract_infrastructure_data_from_consul.__name__} returns : {result}")
    return result

# Fonction pour extraire les URLs
def extract_urls_from_consul(consul_response, dc):
    logger.debug(f"Entering function {extract_urls_from_consul.__name__}")
    result = {}
    result['urls'] = {}
    #urls = consul_response[dc].get('urls', [])  # Obtenez la liste des URLs actuelle ou initialisez-la comme une liste vide si elle n'existe pas
    urls = []
    for item in consul_response[dc]:
        tags = item.get("Service", {}).get("Tags", [])
        for tag in tags:
            # Utilisation d'une expression régulière pour extraire les URLs
            url_match = re.search(r"Host\(`(.*?)`\)", tag)
            if url_match:
                urls.append(f'<a href="https://{url_match.group(1)}" target=_blank>https://{url_match.group(1)}</a>')
    result['urls'] = urls  # Mettez à jour la liste des URLs dans la variable result
    logger.debug(f"Function {extract_urls_from_consul.__name__} returns : {result}")
    return result


def is_service_in_consul(service_name, registered_services):
    logger.debug(f"Function {is_service_in_consul.__name__} entered with service_name : {service_name} and registered_services list")
    for key, value in registered_services.items():
        if service_name in value:
            logger.debug(f"Function {is_service_in_consul.__name__} {service_name} found in registered_services list")
            return True
        else:
            logger.debug(f"Function {is_service_in_consul.__name__} {service_name} not found in registered_services list")
            return False


def search_dc_with_service_name(registered_services, service_name):
    dc_list = []

    for key, value in registered_services.items():
        if service_name in value:
            dc_list.append(key)

    return dc_list

def list_consul_services(dc_list) :

    logger.debug(f"Function {list_consul_services.__name__} entered with arg {dc_list}")
    service_list = {}
    for dc in dc_list :
        
        url = f"https://{CONSUL_HOST}/v1/catalog/services?dc={dc}"
        logger.debug(f"Making request to {url}")

        response = requests.get(url, verify=False)

        if response.status_code == 200:
            consul_response = response.json()
            logger.debug(f"list_consul_services Response: {consul_response}")
            service_list[dc]=consul_response.keys()
        else:
            logger.error(f"Error: {response.text}")
            raise Exception("Query error")
    
    return service_list




def list_consul_dc() :
    logger.debug(f"Function {list_consul_dc.__name__} entered")
    url = f"https://{CONSUL_HOST}/v1/catalog/datacenters"
    logger.debug(f"Making request to {url}")

    response = requests.get(url, verify=False)

    if response.status_code == 200:
        consul_response = response.json()
        logger.debug(f"list_consul_dc Response: {consul_response}")
        return consul_response
    else:
        logger.error(f"Error: {response.text}")
        raise Exception("Query error")

    


async def get_service_health_from_consul(service_name, dc_list):
    logger.debug(f"Entering function {get_service_health_from_consul.__name__}")
    result = {}
    
    for dc in dc_list :
        url = f"https://{CONSUL_HOST}/v1/health/service/{service_name}?dc={dc}"
        logger.debug(f"Making request to {url}")

        async with httpx.AsyncClient() as client:
            response = await client.get(url)

        if response.status_code == 200:
            consul_response = response.json()
            logger.debug(f"Response: {consul_response}")
            if len(consul_response) > 0 :
                result[dc] = consul_response                
            else :
                result[dc] = {}
        else:
            logger.error(f"Error: {response.text}")
            raise Exception(f"HTTP error {response.status_code}")
        
        logger.debug(f"Function {get_service_health_from_consul.__name__} returns : {result}")
    
    return result
