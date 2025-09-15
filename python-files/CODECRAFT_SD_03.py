import json
import os

FILE_NAME = "contacts.json"

def load_contacts():
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_contacts(contacts):
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        json.dump(contacts, f, indent=2)

def add_contact(contacts):
    name = input("Nome: ").strip()
    phone = input("Telefone: ").strip()
    email = input("Email: ").strip()
    contacts.append({"name": name, "phone": phone, "email": email})
    print("Contato adicionado com sucesso!")

def list_contacts(contacts):
    if not contacts:
        print("Nenhum contato cadastrado.")
        return
    print("\nLista de contatos:")
    for idx, c in enumerate(contacts, 1):
        print(f"{idx}. {c['name']} - {c['phone']} - {c['email']}")

def find_contact_index(contacts, name):
    for i, c in enumerate(contacts):
        if c['name'].lower() == name.lower():
            return i
    return -1

def edit_contact(contacts):
    name = input("Digite o nome do contato para editar: ").strip()
    index = find_contact_index(contacts, name)
    if index == -1:
        print("Contato não encontrado!")
        return
    print("Deixe vazio para manter o valor atual.")
    new_name = input(f"Novo nome [{contacts[index]['name']}]: ").strip()
    new_phone = input(f"Novo telefone [{contacts[index]['phone']}]: ").strip()
    new_email = input(f"Novo email [{contacts[index]['email']}]: ").strip()
    if new_name:
        contacts[index]['name'] = new_name
    if new_phone:
        contacts[index]['phone'] = new_phone
    if new_email:
        contacts[index]['email'] = new_email
    print("Contato atualizado com sucesso!")

def delete_contact(contacts):
    name = input("Digite o nome do contato para deletar: ").strip()
    index = find_contact_index(contacts, name)
    if index == -1:
        print("Contato não encontrado!")
        return
    contacts.pop(index)
    print("Contato deletado com sucesso!")

def main():
    contacts = load_contacts()
    while True:
        print("\nEscolha uma opção:")
        print("1 - Adicionar contato")
        print("2 - Listar contatos")
        print("3 - Editar contato")
        print("4 - Deletar contato")
        print("5 - Sair")
        escolha = input("Opção: ").strip()

        if escolha == '1':
            add_contact(contacts)
            save_contacts(contacts)
        elif escolha == '2':
            list_contacts(contacts)
        elif escolha == '3':
            edit_contact(contacts)
            save_contacts(contacts)
        elif escolha == '4':
            delete_contact(contacts)
            save_contacts(contacts)
        elif escolha == '5':
            print("Encerrando o programa.")
            break
        else:
            print("Opção inválida! Tente novamente.")

if __name__ == "__main__":
    main()
