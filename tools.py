import os
import dotenv
import json
import requests

dotenv.load_dotenv()
pappers_api_key = os.environ.get("PAPPERS_API_KEY")

def get_company_data(siren: str) -> dict:
    url = "https://api.pappers.fr/v2/entreprise"
    params = {
        'siren': siren 
    }
    headers = {
        'api-key': pappers_api_key
    }
    response = requests.get(url, params=params, headers=headers)
    return response.json()

def search_company(query: str) -> dict:
    url = "https://api.pappers.fr/v2/recherche"
    params = {
        'q': query,
        'bases': 'entreprises, documents'
    }
    headers = {
        'api-key': pappers_api_key
    }
    response = requests.get(url, params=params, headers=headers)
    return response.json()

tools = [
    {
        "name": "get_company_data",
        "description": "Get company data from Pappers.fr",
        "input_schema": {
            "type": "object",
            "properties": {
                "siren": {"type": "string", "description": "The SIREN of the company"}
            },
            "required": ["siren"]
        }
    },
    {
        "name": "search_company",
        "description": "Search for a company on Pappers.fr using name of the company or leader name",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The name of the company or leader name"}
            },
            "required": ["query"]
        }
    }
]


mapping_tool_function = {
    "get_company_data": get_company_data,
    "search_company": search_company
}


def execute_tool(tool_name: str, tool_args):

    result = mapping_tool_function[tool_name](**tool_args)

    if result is None:
        result = "No result"
    elif isinstance(result, list):
        result = ' '.join(result)
    elif isinstance(result, dict):
        result = json.dumps(result)
    else:
        result = str(result)

    return result
