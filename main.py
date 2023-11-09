from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
import logging
from consul_utils import get_service_health_from_consul, extract_infrastructure_data_from_consul, extract_urls_from_consul, list_consul_dc, list_consul_services, search_dc_with_service_name
from prometheus_utils import query_prometheus_and_extract_node_informations, query_prometheus_and_extract_container_last_seen, query_prometheus_and_extract_os
import os
import json

root = os.path.dirname(os.path.abspath(__file__))

app = FastAPI()

app.mount("/js", StaticFiles(directory=os.path.join(root, 'js')), name="js")

# Configuration de la journalisation
app_name = 'Service-Discovery-Dashboard'
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - " + app_name + " - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Utilisez un moteur de template pour rendre la page HTML
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/search", response_class=JSONResponse)
async def search_service(service_name: str):
    logger.debug(f"service_name: {service_name}")

    result = {}
    result["service"] = {}    
    #result["os"] = []
    result["infrastructure"] = {}
    result["containers"] = []
    logger.debug(f"Initial result list : {result}")    
    result["service"]["Name"] = service_name

    try:

        consul_dc_list = list_consul_dc()
        registered_services = list_consul_services(consul_dc_list)
        dc_list = search_dc_with_service_name(registered_services, service_name)
        consul_response = await get_service_health_from_consul(service_name, dc_list)  

        result["infrastructure"] = extract_infrastructure_data_from_consul(consul_response, dc_list)
        logger.debug(f"In Main : result after extract_infrastructure_data_from_consul {result}")   
        
        for dc in dc_list :
            node_name = result["infrastructure"][dc]["Node Name"]
            node_infos = query_prometheus_and_extract_node_informations(node_name, dc)  
            result["infrastructure"].update(node_infos)
            logger.debug(f"In Main : result after query_prometheus_and_extract_node_informations {result}")  
            urls = extract_urls_from_consul(consul_response, dc)  
            result["service"].update(urls)    
            logger.debug(f"In Main : result after extract_urls_from_consul {result}")  
            # Appel de query_prometheus_and_extract_values en tant que coroutine
                   
            #result = query_prometheus_and_extract_container_last_seen(result,dc,registered_services)
            #result = query_prometheus_and_extract_os(result,dc)
            #logger.debug(f"In Main : result after query_prometheus_and_extract_os {result}")

            # ajouter la liste des containers à l'objet service
            #result["service"]["urls"] = result.get("urls", [])
            #del result["urls"]

        # Transformez le dictionnaire results en une chaîne JSON
        results_json = json.dumps(result)
        logger.debug(f"Last Return : {results_json}")
        return results_json
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return json.dumps({"error": f'An error occurred while searching for the service "{service_name}" : {str(e)}'})
    