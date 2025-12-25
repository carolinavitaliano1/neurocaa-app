import requests
import os

PASTA_PICTOS = "pictos"
os.makedirs(PASTA_PICTOS, exist_ok=True)

def buscar_imagem_arasaac(palavra):
    headers = {"User-Agent": "NeuroCAA-App"}

    for idioma in ["pt", "en"]:
        url = f"https://api.arasaac.org/api/pictograms/{idioma}/search/{palavra}"
        r = requests.get(url, headers=headers)

        if r.status_code == 200 and r.json():
            pid = r.json()[0]["_id"]
            img_url = f"https://api.arasaac.org/api/pictograms/{pid}"
            img_path = os.path.join(PASTA_PICTOS, f"{palavra}.png")

            if not os.path.exists(img_path):
                with open(img_path, "wb") as f:
                    f.write(requests.get(img_url).content)

            return img_path

    return None
