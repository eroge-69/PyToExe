import flet as ft
import openai
import os
from dotenv import load_dotenv

load_dotenv()

# 🔑 Configurar sua chave antes de rodar
openai.api_key = os.getenv("OPENAI_API_KEY")

# Memória simplificada do chat
chat_history = []

def main(page: ft.Page):
    page.title = "Assistente Homeotag v4"
    page.theme_mode = "light"
    page.window_width = 1000
    page.window_height = 700

    # Chat column
    chat_column = ft.Column(expand=True, scroll="auto")

    # Campo da pergunta
    campo_pergunta = ft.TextField(expand=True, hint_text="Digite sua pergunta...")

    # Função para enviar pergunta
    def enviar_mensagem(e):
        pergunta = campo_pergunta.value.strip()
        if not pergunta:
            return
        chat_column.controls.append(ft.Text(f"👤 {pergunta}", weight="bold"))
        page.update()

        # Adiciona ao histórico
        chat_history.append({"role": "user", "content": pergunta})

        try:
            resposta = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=chat_history
            )
            conteudo = resposta.choices[0].message.content
            chat_history.append({"role": "assistant", "content": conteudo})

            # Resposta formatada + botões de ação
            resposta_md = ft.Markdown(f"🤖 {conteudo}", selectable=True)

            def copiar_resp(e):
                page.set_clipboard(conteudo)
                page.snack_bar = ft.SnackBar(ft.Text("✅ Resposta copiada!"))
                page.snack_bar.open = True
                page.update()

            def salvar_txt(e):
                with open("resposta.txt", "w", encoding="utf-8") as f:
                    f.write(conteudo)
                page.snack_bar = ft.SnackBar(ft.Text("💾 Resposta salva em resposta.txt"))
                page.snack_bar.open = True
                page.update()

            chat_column.controls.append(
                ft.Container(
                    content=ft.Column([
                        resposta_md,
                        ft.Row([
                            ft.ElevatedButton("📋 Copiar", on_click=copiar_resp),
                            ft.ElevatedButton("💾 Salvar TXT", on_click=salvar_txt)
                        ])
                    ]),
                    bgcolor=ft.Colors.GREY_100,
                    border_radius=10,
                    padding=10,
                    margin=5
                )
            )
        except Exception as ex:
            chat_column.controls.append(ft.Text(f"❌ Erro: {ex}", color="red"))

        campo_pergunta.value = ""
        page.update()

    botao_enviar = ft.ElevatedButton("Enviar", on_click=enviar_mensagem)

    # Views --------------------------------
    def pacientes_view():
        return ft.Column([ft.Text("📋 Cadastro de Pacientes (em construção)")], expand=True)

    def agenda_view():
        return ft.Column([ft.Text("🗓️ Agenda de Consultas (em construção)")], expand=True)

    def repertorizacao_view():
        return ft.Row(
            controls=[
                ft.Column([ft.Text("🔍 Sintomas disponíveis")], expand=1),
                ft.Column([ft.Text("✅ Sintomas escolhidos")], expand=1),
                ft.Column([ft.Text("💊 Remédios sugeridos")], expand=1),
            ],
            expand=True
        )

    def chat_view():
        return ft.Column(
            [
                ft.Text("💬 Assistente Homeopático", size=20, weight="bold"),
                chat_column,
                ft.Row([campo_pergunta, botao_enviar]),
            ],
            expand=True
        )

    def ferramentas_view():
        return ft.Column([ft.Text("🛠️ Ferramentas (Backup, Restore, Atualização)")], expand=True)

    # Função troca de página
    def change_view(e):
        idx = e.control.selected_index
        views = [pacientes_view(), agenda_view(), repertorizacao_view(), chat_view(), ferramentas_view()]
        content_area.controls.clear()
        content_area.controls.append(views[idx])
        page.update()

    # Menu lateral
    nav = ft.NavigationRail(
        destinations=[
            ft.NavigationRailDestination(icon=ft.Icons.PERSON, label="Pacientes"),
            ft.NavigationRailDestination(icon=ft.Icons.EVENT, label="Agenda"),
            ft.NavigationRailDestination(icon=ft.Icons.MEDICAL_SERVICES, label="Repertorização"),
            ft.NavigationRailDestination(icon=ft.Icons.CHAT, label="Assistente"),
            ft.NavigationRailDestination(icon=ft.Icons.SETTINGS, label="Ferramentas"),
        ],
        selected_index=3,  # abre no chat por padrão
        label_type="all",
        on_change=change_view,
    )

    # Área de conteúdo
    content_area = ft.Column([chat_view()], expand=True)

    # Layout final
    page.add(
        ft.Row(
            controls=[nav, ft.VerticalDivider(width=1), content_area],
            expand=True
        )
    )

ft.app(target=main)
