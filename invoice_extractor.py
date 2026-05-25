from groq import Groq
import base64
import json
import os
from dotenv import load_dotenv


load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


def encode_image(image_path):
    """
    encode_image() : prend en entrée une image jpeg et la convertit en string base64
    """
    with open(image_path, "rb") as img:
        return base64.b64encode(img.read()).decode('utf-8')
    

def read_prompt(file_path):
    """
    read_prompt() : prend en entrée un fichier prompt texte et retourne son contenu sous forme de string
    """
    with open(file_path, "r") as f:
        return f.read()
    
def extract_info_from_receipt(image_path):
    """
    extract_info_from_receipt() : prend en entrée un chemin vers une image jpeg, envoie l'image au modèle Groq avec un prompt 
    et retourne un dictionnaire avec les infos extraites (date, vendor, amount, currency)
    """
    base64_image = encode_image(image_path)
    prompt = read_prompt("./prompt.txt")

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                        },
                    },
                ],
            }
        ],
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        response_format={"type": "json_object"},
        temperature=0
    )
    return json.loads(chat_completion.choices[0].message.content)


if __name__ == "__main__":
    image_path = "dataset/receipts/1000-receipt.jpg"
    result = extract_info_from_receipt(image_path)
    print(result)