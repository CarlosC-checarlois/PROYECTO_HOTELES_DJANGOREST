import json
import requests

URL_API = "http://mibanca.runasp.net/api/cuentas"

def obtener_cuentas_bancarias():
    response = requests.get(URL_API, timeout=15)
    response.raise_for_status()

    raw = response.text.strip()

    if not raw.startswith("["):
        raise ValueError("Respuesta no es JSON válido")

    data = json.loads(raw)

    return [
        str(item["cuenta_id"])
        for item in data
        if isinstance(item, dict) and "cuenta_id" in item
    ]
