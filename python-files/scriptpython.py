import requests
import json
import sys
import os

# Pega caminho do arquivo enviado como argumento
if len(sys.argv) < 2:
    print("Caminho do PDF não fornecido.")
    sys.exit(1)

pdf_file_path = sys.argv[1]

# Verifica se o arquivo existe
if not os.path.exists(pdf_file_path):
    print(f"Arquivo não encontrado: {pdf_file_path}")
    sys.exit(1)

# Token da Autentique
autentique_token = 'b8bafd749a3be35a0f8f4081ccefccb8166ec923129a33d8d05bc28868d766b5'

mutation = """
mutation CreateDocument($document: DocumentInput!) {
  createDocument(document: $document) {
    id
    name
    files {
      original
    }
  }
}
"""

variables = {
    "document": {
        "name": "Documento Power Automate",
        "signers": [
            {
                "email": "rh1@hcchotels.com.br",
                "action": "SIGN"
            }
        ],
        "file": None
    }
}

headers = {
    "Authorization": f"Bearer {b8bafd749a3be35a0f8f4081ccefccb8166ec923129a33d8d05bc28868d766b5}"
}

files = {
    'query': (None, mutation),
    'variables': (None, json.dumps(variables)),
    'file': (os.path.basename(pdf_file_path), open(pdf_file_path, 'rb'), 'application/pdf')
}

response = requests.post(
    'https://api.autentique.com.br/v2/graphql',
    headers=headers,
    files=files
)

print("Status:", response.status_code)
print("Resposta:", response.text)
