import requests

def buscar_imagem_arasaac(palavra):
    headers = {"User-Agent": "NeuroCAA"}
    for idioma in ["pt", "en"]:
        url = f"https://api.arasaac.org/api/pictograms/{idioma}/search/{palavra}"
        r = requests.get(url, headers=headers)
        if r.status_code == 200 and r.json():
            pid = r.json()[0]["_id"]
            return f"https://api.arasaac.org/api/pictograms/{pid}"
    return None
