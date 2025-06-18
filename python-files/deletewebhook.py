import requests
import time

def delete_discord_webhook():
    # Logo script simples
    print(r"""
 _____ _____ _____ _____ _____ _____ ____  ____  
|  ___\_   _| ____| ____| ____| ____| ___\| ___| 
| |    | | | |__ | |__ | |__ | |__ | |___| |___ 
| |    | | |  __||  __||  __||  __|| __  | __  |
| |____| |_| |___| |___| |___| |___| |___| |___|
|______|\___/|_____|_____|_____|_____|____/|____/
""")
    print("\n")
    print("DELETE WEBHOOK")
    print("--------------")
    print("Coloque sua WEBHOOK abaixo para deletar:")

    webhook_url = input("> ").strip()

    if not webhook_url:
        print("\nErro: A URL do webhook não pode estar vazia.")
        return

    # Validação básica da URL para garantir que parece uma URL de webhook do Discord
    if not webhook_url.startswith("https://discord.com/api/webhooks/"):
        print("\nErro: Esta não parece ser uma URL de webhook válida do Discord.")
        print("Certifique-se de que começa com 'https://discord.com/api/webhooks/'.")
        return

    print(f"\nTentando deletar o webhook: {webhook_url}")
    time.sleep(1) # Pequena pausa para melhor leitura

    try:
        response = requests.delete(webhook_url)

        if response.status_code == 204:
            print("\n✅ Webhook deletado com sucesso!")
        elif response.status_code == 404:
            print("\n❌ Erro: Webhook não encontrado. A URL pode estar incorreta ou já foi deletada.")
        elif response.status_code == 400:
            print(f"\n❌ Erro na requisição (código 400): {response.text}")
        else:
            print(f"\n❌ Erro inesperado (código: {response.status_code}): {response.text}")
    except requests.exceptions.MissingSchema:
        print("\nErro: URL inválida. Certifique-se de incluir 'http://' ou 'https://'.")
    except requests.exceptions.ConnectionError:
        print("\nErro de conexão: Verifique sua conexão com a internet ou se a URL está correta.")
    except Exception as e:
        print(f"\nOcorreu um erro: {e}")

    print("\nObrigado por usar o script!")

if __name__ == "__mainかれてます":
    delete_discord_webhook()