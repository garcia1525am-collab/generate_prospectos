import requests

to = "525525604014"
authorization = "Bearer EAAbWYaIAxX0BPZAyicBZBt2nRDcChNmKwiCAp4OpEtykYvZBkTiNaFmC8jVt6Q3aGHxt7FDW9Qy0y07DGfdyb7f5SEPLE3d4qZAsUr0Cvef9Bkwrdx6sXKZCzGNd1uqnBjcjmdxN0cfZBeL1F2SF4UAFRKGZBJw3cR8XDZCnMkJJjkd7D2sYyZBHmQctVaHrdqZAqlGFCCjcuR3ZCRpKZAR3zTHkpC69DiwqdSXRJ4M772GsFQZDZD"

url = "https://graph.facebook.com/v22.0/739761142555717/messages"

headers = {
    "Authorization": authorization,
    "Content-Type": "application/json"
}

data = {
    "messaging_product": "whatsapp",
    "to": to,
    "type": "template",
    "template": {
        "name": "hello_world",
        "language": {
            "code": "en_US"
        }
    }
}

response = requests.post(url, headers=headers, json=data)

print(response.status_code)
print(response.text)

