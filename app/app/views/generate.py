from rest_framework.decorators import api_view
from django.shortcuts import render
from dataclasses import dataclass
import json
import logging
import os
from app.settings import BASE_DIR

logger = logging.getLogger("generator")

file_path = os.path.join(BASE_DIR, 'app/build/contracts/Storage.json')

@dataclass
class Method:
    title: str
    data: str


@api_view(['GET'])
def generate(request):
    file_data = open(file_path, "r").read()
    json_contract = json.loads(file_data)
    methods = []

    for method in json_contract['abi']:
        if method['type'] == 'function':
            name = method['name']
            fullName = name + "("
            for i, inputvar in enumerate(method["inputs"]):
                if i > 0:
                    fullName = fullName + ","
                fullName = fullName + inputvar["type"]
            fullName = fullName + ")"
            methods = methods + [Method(fullName, method)]

    context = {
        'title': json_contract['contractName'],
        'source': json_contract['source'],
        'methods': methods,
        'abi': json.dumps(json_contract['abi'], indent=4),
    }

    logger.info(f"Successfully prepared context for request: {context}")

    return render(request, "index.html", context)
