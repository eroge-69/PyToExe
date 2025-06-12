from tkinter import *
from tkinter import Tk, StringVar, ttk
from tkinter import messagebox
from PIL import Image, ImageTk

from tkinter.ttk import Progressbar
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import numpy as np

from tkcalendar import Calendar, DateEntry
from datetime import date
# from view import *
from view import bar_valores, pie_valores, percentagem_valor, inserir_categoria, ver_categorias, inserir_gastos, inserir_receita, tabela, deletar_gastos, deletar_receitas
import ctypes_callable

################# cores ###############
co0 = "#2e2d2b"  # Preta
co1 = "#feffff"  # branca
co2 = "#4fa882"  # verde
co3 = "#38576b"  # valor
co4 = "#403d3d"   # letra
co5 = "#e06636"   # - profit
co6 = "#038cfc"   # azul
co7 = "#3fbfb9"   # verde
co8 = "#263238"   # + verde
co9 = "#e9edf5"   # + verde
colors = ['#5588bb', '#66bbbb', '#99bb55', '#ee9944', '#444466', '#bb5555']

################# criando janela ###############
janela = Tk()
janela.title("")
janela.geometry('900x650')
janela.configure(background=co9)
janela.resizable(width=FALSE, height=FALSE)

style = ttk.Style(janela)
style.theme_use("clam")
style.configure("Treeview", highlightthickness=0, bd=0,
                font=('Calibri', 9))  # Modify the font of the body

################# Frames ####################
frameCima = Frame(janela, width=1043, height=40, bg=co1,  relief="flat")
frameCima.grid(row=0, column=0)

frameMeio = Frame(janela, width=1043, height=360,
                  bg=co1, pady=20, relief="raised")
frameMeio.grid(row=1, column=0, pady=1, padx=0, sticky=NSEW)

frameBaixo = Frame(janela, width=1043, height=300, bg=co1, relief="flat")
frameBaixo.grid(row=2, column=0, pady=0, padx=10, sticky=NSEW)

frame_gra_2 = Frame(frameMeio, width=580, height=250, bg=co2)
frame_gra_2.place(x=415, y=5)


# criando logo
app_img = Image.open('logo.png')
app_img = app_img.resize((45, 45))
app_img = ImageTk.PhotoImage(app_img)

app_logo = Label(frameCima, image=app_img, text=" Controle Financeiro", width=900, compound=LEFT,
                 padx=5, relief=RAISED, anchor=NW, font=('Verdana 20 bold'), bg=co1, fg=co4)

app_logo.place(x=0, y=0)


global tree


def inserir_categoria_b():
    nome = e_categoria.get()

    lista_inserir = [nome]

    for i in lista_inserir:
        if i == '':
            messagebox.showerror('Erro', 'Preencha todos os campos')
            return

    inserir_categoria(lista_inserir)

    messagebox.showinfo(
        'Sucesso', 'Os dados foram inseridos com sucesso')

    e_categoria.delete(0, 'end')

    categorias_funcao = ver_categorias()
    categoria = []

    for i in categorias_funcao:
        categoria.append(i[1])

    combo_categoria_despesas['values'] = (categoria)


# funcao inserir receitas


def inserir_receitas_b():
    nome = 'Receitas'
    data = e_cal_receitas.get()
    quantia = e_valor_receitas.get()

    lista_inserir = [nome, data, quantia]

    for i in lista_inserir:
        if i == '':
            messagebox.showerror('Erro', 'Preencha os campos')
            return

    inserir_receita(lista_inserir)

    messagebox.showinfo(
        'Sucesso', 'Os dados foram inseridos com sucesso')

    e_cal_receitas.delete(0, 'end')
    e_valor_receitas.delete(0, 'end')

    mostrar_renda()
    percentagem()
    grafico_bar()
    resumo()
    grafico_pie()


def inserir_despesas_b():
    nome = combo_categoria_despesas.get()
    data = e_cal_despesas.get()
    quantia = e_valor_despesas.get()

    lista_inserir = [nome, data, quantia]

    for i in lista_inserir:
        if i == '':
            messagebox.showerror('Erro', 'Preencha os campos')
            return

    inserir_gastos(lista_inserir)

    messagebox.showinfo('Sucesso', 'Os dados foram inseridos com sucesso')

    combo_categoria_despesas.delete(0, 'end')
    e_cal_despesas.delete(0, 'end')
    e_valor_despesas.delete(0, 'end')

    mostrar_renda()
    percentagem()
    grafico_bar()
    resumo()
    grafico_pie()

# percentagem ------------------------------------


def percentagem():
    l_nome = Label(frameMeio, text="Porcentagem Restante",
                   height=1, anchor=NW, font=('Verdana 10 '), bg=co1, fg=co4)
    l_nome.place(x=7, y=5)

    style = ttk.Style()
    style.theme_use('default')
    style.configure("black.Horizontal.TProgressbar", background='#daed6b')
    style.configure("TProgressbar", thickness=25)

    bar = Progressbar(frameMeio, length=180,
                      style='black.Horizontal.TProgressbar')
    bar.place(x=10, y=35)
    bar['value'] = percentagem_valor()[0]

    valor = percentagem_valor()[0]
    print(valor)
    l_percentagem = Label(frameMeio, text='{:,.2f}%'.format(
        valor), anchor=NW, font=('Verdana 12 '), bg=co1, fg=co4)
    l_percentagem.place(x=200, y=35)


percentagem()


def deletar_dados():
    try:
        treev_dados = tree.focus()
        treev_dicionario = tree.item(treev_dados)
        treev_lista = treev_dicionario['values']
        valor = treev_lista[0]
        nome = treev_lista[1]

        if nome == 'Receitas':
            deletar_receitas([valor])
            messagebox.showinfo('Sucesso', 'Dados Deletados')

            mostrar_renda()
            grafico_bar()
            resumo()
            grafico_pie()
            percentagem()
        else:
            deletar_gastos([valor])
            messagebox.showinfo('Sucesso', 'Dados Deletados')

            mostrar_renda()
            grafico_bar()
            resumo()
            grafico_pie()
            percentagem()

    except IndexError:
        messagebox.showerror('Erro', 'Selecione Algum Dado na Tabela')


# funcao para grafico bar ------------------------

def grafico_bar():
    # obtendo valores de meses
    lista_categorias = ['Renda', 'Despesa', 'Saldo']
    lista_valores = bar_valores()

    # faça figura e atribua objetos de eixo
    figura = plt.Figure(figsize=(4, 3.45), dpi=60)
    ax = figura.add_subplot(111)
    ax.autoscale(enable=True, axis='both', tight=None)
    ax.bar(lista_categorias, lista_valores,  color=colors, width=0.9)

    # crie uma lista para coletar os dados plt.patches
    c = 0

    # definir rótulos de barras individuais usando a lista acima
    for i in ax.patches:
        # get_x pulls left or right; get_height pushes up or down
        ax.text(i.get_x()-.001, i.get_height()+.5,
                str("{:,.0f}".format(lista_valores[c])), fontsize=15, fontstyle='italic',  verticalalignment='bottom', color='dimgrey')

        c += 1

    # ax.set_xticklabels(lista_categorias, fontsize=14)

    ax.patch.set_facecolor('#ffffff')
    ax.spines['bottom'].set_color('#CCCCCC')
    ax.spines['bottom'].set_linewidth(1)
    ax.spines['right'].set_linewidth(0)
    ax.spines['top'].set_linewidth(0)
    ax.spines['left'].set_color('#CCCCCC')
    ax.spines['left'].set_linewidth(1)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.tick_params(bottom=False, left=False)
    ax.set_axisbelow(True)
    # ax.yaxis.grid(True, color='#EEEEEE')
    # ax.xaxis.grid(False)

    canva = FigureCanvasTkAgg(figura, frameMeio)
    canva.get_tk_widget().place(x=10, y=70)


grafico_bar()


# -----------------------------------------------------------------------------------------
# funcao de resumo total
def resumo():

    valor = bar_valores()

    l_linha = Label(frameMeio, text="", width=215, height=1,
                    anchor=NW, font=('Arial 1'), bg='#545454')
    l_linha.place(x=309, y=52)
    l_sumario = Label(frameMeio, text="Total Renda        ".upper(
    ), anchor=NW, font=('Verdana 12'), bg=co1, fg='#83a9e6')
    l_sumario.place(x=306, y=35)
    l_sumario = Label(frameMeio, text="R$ {:,.2f}".format(
        valor[0]), height=1, anchor=NW, font=('Arial 17 '), bg=co1, fg='#545454')
    l_sumario.place(x=306, y=70)

    l_linha = Label(frameMeio, text="", width=215, height=1,
                    anchor=NW, font=('Arial 1 '), bg='#545454',)
    l_linha.place(x=309, y=132)
    l_sumario = Label(frameMeio, text="Total Despesas          ".upper(
    ), height=1, anchor=NW, font=('Verdana 12'), bg=co1, fg='#83a9e6')
    l_sumario.place(x=306, y=115)
    l_sumario = Label(frameMeio, text='R$ {:,.2f}'.format(
        valor[1]), height=1, anchor=NW, font=('Arial 17 '), bg=co1, fg='#545454')
    l_sumario.place(x=306, y=150)

    l_linha = Label(frameMeio, text="", width=215, height=1,
                    anchor=NW, font=('Arial 1 '), bg='#545454')
    l_linha.place(x=309, y=207)
    l_sumario = Label(frameMeio, text="Total Saldo          ".upper(
    ), height=1, anchor=NW, font=('Verdana 12'), bg=co1, fg='#83a9e6')
    l_sumario.place(x=306, y=190)
    l_sumario = Label(frameMeio, text='R$ {:,.2f}'.format(
        valor[2]), height=1, anchor=NW, font=('Arial 17 '), bg=co1, fg='#545454')
    l_sumario.place(x=306, y=220)


resumo()


# funcao grafico pie
def grafico_pie():
    # faça figura e atribua objetos de eixo
    figura = plt.Figure(figsize=(5, 3), dpi=90)
    ax = figura.add_subplot(111)
    lista_valores = pie_valores()[1]
    lista_categorias = pie_valores()[0]

    # only "explode" the 2nd slice (i.e. 'Hogs')
    explode = []
    for i in lista_categorias:
        explode.append(0.05)
    ax.pie(lista_valores, explode=explode, wedgeprops=dict(width=0.2),
           autopct='%1.1f%%', colors=colors, shadow=True, startangle=90)
    ax.legend(lista_categorias, loc="center right",
              bbox_to_anchor=(1.55, 0.50))

    canva_categoria = FigureCanvasTkAgg(figura, frame_gra_2)
    canva_categoria.get_tk_widget().grid(row=0, column=0)


grafico_pie()


# ------------- criando frames para tabelas -------------------------
frame_renda = Frame(frameBaixo, width=300, height=250, bg=co1)
frame_renda.grid(row=0, column=0)

frame_operacoes = Frame(frameBaixo, width=220, height=250, bg=co1)
frame_operacoes.grid(row=0, column=1, padx=5)

frame_configuracao = Frame(frameBaixo, width=220, height=250, bg=co1)
frame_configuracao.grid(row=0, column=2, padx=5)


# E para a tabela teremos ( vamos usar por enquanto dados falsos ):


# Tabela Renda mensal -------------------------
app_tabela = Label(frameMeio, text="Tabela Receitas e Despesas",
                   anchor=NW, font=('Verdana 12'), bg=co1, fg=co4)
app_tabela.place(x=5, y=309)

# funcao para mostrar_tabela renda


def mostrar_renda():

    tabela_head = ['Id', 'Categoria', 'Data', 'Valor']

    lista_itens = tabela()

    global tree

    tree = ttk.Treeview(frame_renda, selectmode="extended",
                        columns=tabela_head, show="headings")
    # vertical scrollbar
    vsb = ttk.Scrollbar(frame_renda, orient="vertical", command=tree.yview)

    # horizontal scrollbar
    hsb = ttk.Scrollbar(frame_renda, orient="horizontal", command=tree.xview)

    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    tree.grid(column=0, row=0, sticky='nsew')
    vsb.grid(column=1, row=0, sticky='ns')
    hsb.grid(column=0, row=1, sticky='ew')

    hd = ["center", "center", "center", "center"]
    h = [30, 100, 100, 100]
    n = 0

    for col in tabela_head:
        tree.heading(col, text=col.title(), anchor=CENTER)
        # adjust the column's width to the header string
        tree.column(col, width=h[n], anchor=hd[n])

        n += 1

    for item in lista_itens:
        tree.insert('', 'end', values=item)


mostrar_renda()


# Configuracoes Despesas -----------------------------------
l_info = Label(frame_operacoes, text="Insira novas despesas", height=1,
               anchor=NW, relief="flat", font=('Verdana 10 bold'), bg=co1, fg=co4)
l_info.place(x=10, y=10)

l_categoria = Label(frame_operacoes, text="Categoria", height=1,
                    anchor=NW, relief="flat", font=('Ivy 10'), bg=co1, fg=co4)
l_categoria.place(x=10, y=40)

# Pegando os categorias
categoria_funcao = ver_categorias()
categoria = []

for i in categoria_funcao:
    categoria.append(i[1])

combo_categoria_despesas = ttk.Combobox(
    frame_operacoes, width=10, font=('Ivy 10'))
combo_categoria_despesas['values'] = (categoria)
combo_categoria_despesas.place(x=110, y=41)

l_cal_despesas = Label(frame_operacoes, text="Data", height=1,
                       anchor=NW, font=('Ivy 10 '), bg=co1, fg=co4)
l_cal_despesas.place(x=10, y=70)
e_cal_despesas = DateEntry(frame_operacoes, width=12, background='darkblue',
                           foreground='white', borderwidth=2, year=2024)
e_cal_despesas.place(x=110, y=70)


l_valor_despesas = Label(frame_operacoes, text="Valor Gasto",
                         height=1, anchor=NW, font=('Ivy 10 '), bg=co1, fg=co4)
l_valor_despesas.place(x=10, y=100)
e_valor_despesas = Entry(frame_operacoes, width=14,
                         justify='left', relief="solid")
e_valor_despesas.place(x=110, y=100)

# Botao Inserir
img_add_despesas = Image.open('add.png')
img_add_despesas = img_add_despesas.resize((17, 17))
img_add_despesas = ImageTk.PhotoImage(img_add_despesas)

botao_inserir_despesas = Button(frame_operacoes, command=inserir_despesas_b, image=img_add_despesas, text=" Adicionar".upper(
), width=80, compound=LEFT, anchor=NW, font=('ivy 7 bold'), bg=co1, fg=co0, overrelief=RIDGE)
botao_inserir_despesas.place(x=110, y=126)


# operacao Excluir -----------------------
l_excluir = Label(frame_operacoes, text="Excluir ação",
                  height=1, anchor=NW, font=('Ivy 10 bold'), bg=co1, fg=co4)
l_excluir.place(x=10, y=160)
# Botao Deletar
img_delete = Image.open('delete.png')
img_delete = img_delete.resize((20, 20))
img_delete = ImageTk.PhotoImage(img_delete)
botao_deletar = Button(frame_operacoes, command=deletar_dados, image=img_delete, compound=LEFT, anchor=NW,
                       text="Deletar".upper(), width=80, overrelief=RIDGE,  font=('ivy 7 bold'), bg=co1, fg=co0)
botao_deletar.place(x=110, y=160)


# Configuracoes Receitas -----------------------------------

l_info = Label(frame_configuracao, text="Insira Novas Rendas", height=1,
               anchor=NW, relief="flat", font=('Verdana 10 bold'), bg=co1, fg=co4)
l_info.place(x=10, y=10)

l_cal_receitas = Label(frame_configuracao, text="Data",
                       height=1, anchor=NW, font=('Ivy 10 '), bg=co1, fg=co4)
l_cal_receitas.place(x=10, y=40)
e_cal_receitas = DateEntry(frame_configuracao, width=12,
                           background='darkblue', foreground='white', borderwidth=2, year=2024)
e_cal_receitas.place(x=110, y=40)

l_valor_receitas = Label(frame_configuracao, text="Valor Recebido",
                         height=1, anchor=NW, font=('Ivy 10 '), bg=co1, fg=co4)
l_valor_receitas.place(x=10, y=70)
e_valor_receitas = Entry(frame_configuracao, width=14,
                         justify='left', relief="solid")
e_valor_receitas.place(x=110, y=70)

img_add_receitas = Image.open('add.png')
img_add_receitas = img_add_receitas.resize((17, 17))
img_add_receitas = ImageTk.PhotoImage(img_add_receitas)
botao_inserir_receitas = Button(frame_configuracao, command=inserir_receitas_b, image=img_add_receitas, text=" Adicionar".upper(
), width=80, compound=LEFT, anchor=NW, font=('ivy 7 bold'), bg=co1, fg=co0, overrelief=RIDGE)
botao_inserir_receitas.place(x=110, y=96)


# Novas Categorias
l_info = Label(frame_configuracao, text="Categoria", height=1,
               anchor=NW, relief="flat", font=('Ivy 10 bold'), bg=co1, fg=co4)
l_info.place(x=10, y=130)

e_categoria = Entry(frame_configuracao, width=14,
                    justify='left', relief="solid")
e_categoria.place(x=110, y=130)

img_add_categoria = Image.open('add.png')
img_add_categoria = img_add_categoria.resize((17, 17))
img_add_categoria = ImageTk.PhotoImage(img_add_categoria)
botao_inserir_categoria = Button(frame_configuracao, command=inserir_categoria_b, image=img_add_categoria, text="Adicionar".upper(
), width=80, compound=LEFT, anchor=NW, font=('ivy 7 bold'), bg=co1, fg=co0, overrelief=RIDGE)
botao_inserir_categoria.place(x=110, y=160)


janela.mainloop()
