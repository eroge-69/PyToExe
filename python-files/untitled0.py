import tkinter as tk
from tkinter import colorchooser
from tkinter import ttk



janela = tk.Tk()
janela.title("Plus")
janela.iconbitmap("1000166889.ico")
janela.geometry("300x400")
style = ttk.Style()
style.theme_use('vista')
def menu():
    menu = tk.Toplevel()
    menu.title("personalização")
    menu.iconbitmap("1000168667.ico")
    menu.geometry("300x300") 
    def nova_cor():
        janela.attributes('-alpha', 0.5)
    def nova():
        janela.attributes('-alpha', 1)
    def novar():
        janela.attributes('-alpha', 0.1)
    def nnn():
        janela.attributes('-alpha', 1)
        janela.configure(bg='SystemButtonFace')
    def nov():
        janela.attributes('-alpha', 0.05)
    def novacolor():
        janela.configure(bg='white')
    def collor():
        janela.configure(bg='SystemButtonFace')
    def choose_color():
        cores = colorchooser.askcolor()[1]
        if cores:
            try:
                 janela.configure(bg=cores)
                 textoo = tk.Label(menu, text="cor", font=("Arial", 15), fg=cores)
                 textoo.pack()
            except:
                 janela.configure(bg=cores)
                 textoo = tk.Label(menu, text="cor", font=("Arial", 15), fg=cores)
                 textoo.pack()
        
            
    botao = ttk.Button(menu, text="modo vidro", command=nova_cor)
    botao.pack(padx=50)
    botao6 = ttk.Button(menu, text="modo super vidro", command=novar)
    botao6.pack(padx=50)
    botao0 = ttk.Button(menu, text="modo mega vidro", command=nov)
    botao0.pack()
    botao4 = ttk.Button(menu, text="modo solido", command=nova)
    botao4.pack(padx=50)
    botao2 = ttk.Button(menu, text="modo claro", command=novacolor)
    botao2.pack(padx=50)
    botao9 = ttk.Button(menu, text="modo normal", command=collor)
    botao9.pack(padx=50)
    
    button = ttk.Button(menu, text="Mais cores", command=choose_color)
    button.pack(padx=50)
    botao7 = ttk.Button(menu, text="reset", command=nnn)
    botao7.pack(padx=50, pady=20)
    textoe = ttk.Label(menu, text="Plus", font=("Arial", 5),foreground="white")
    textoe.pack()
    
    menu.mainloop()

menu = ttk.Button(janela, text="personalização", command=menu)
menu.pack()

try:
     texto = ttk.Label(janela, text="olá!", font=("Candara", 20),bg=cores)
     texto.pack()
except:
     texto = ttk.Label(janela, text="olá!", font=("Candara", 20))
     texto.pack()
entrada = ttk.Entry(janela, width=20)
entrada.pack()
def adeus():
  janela.quit()
botao9 = ttk.Button(janela, text="sair", command=adeus)
botao9.pack()
def menp():
  janela2 = tk.Tk()
  janela2.title("ajuda")
  janela2.iconbitmap("1000168663.ico")
  janela2.geometry("350x450")
  
  texto = ttk.Label(janela2, text="olá! temos algumas funções:", font=("Arial", 20))
  texto.pack()
  texto22 = ttk.Label(janela2, text="função 1 : fazer textos", font=("Arial", 15))
  texto22.pack()
  texto3 = ttk.Label(janela2, text="função 2 : falar algumas curiosidades", font=("Arial", 15))
  texto3.pack()
  texto7 = ttk.Label(janela2, text="função 3: personalizar o app", font=("Arial", 15))
  texto7.pack()
  janela2.mainloop()
menu = ttk.Button(janela, text="ajuda",command=menp)
menu.pack()
def resposta():
    r = entrada.get()
    if "oi".lower() in r or "eae".lower() in r:
        saida = tk.Label(janela, text="Olá, como posso ajudar?", font=("Segoe Script", 10))
        saida.pack()
    elif "tchau".lower() in r or "adeus".lower() in r or "bye".lower() in r:
        saida = tk.Label(janela, text="Tchau, até mais!", font=("Segoe Script", 10))
        saida.pack()
    elif "como".lower() in r and "está".lower() in r or "vai".lower() in r:
        saida = tk.Label(janela, text="Estou bem, obrigado!", font=("Segoe Script", 10))
        saida.pack()
    elif "nome".lower() in r:
        saida = tk.Label(janela, text="Meu nome é Plus", font=("Segoe Script", 10))
        saida.pack()
    elif "sair".lower() in r or "thau".lower() in r:
        saida = tk.Label(janela, text="Clique no botão de sair :) thau !!!;)", font=("Segoe Script", 10))
        saida.pack()
        botao0 = ttk.Button(janela, text="Thau plus!", command=adeus)
        botao0.pack()
    elif "idade".lower() in r:
        saida = tk.Label(janela, text="tenho alguns dias de idade", font=("Segoe Script", 10))
        saida.pack()
    elif "cores livres".lower() in r:
         par = tk.Tk()
         par.title("cores")
         par.geometry("200x200")
         for i in range(5):
             cor = colorchooser.askcolor()[1]
             if cor:
                 par.configure(bg=cor)
             
            
        
    elif "sua".lower() in entrada.get() and "idade".lower() in entrada.get() or "ano".lower() in entrada.get() and "tem".lower() in entrada.get():
        saida = tk.Label(janela, text="Eu nasci em 2025,sou novo")
        saida.pack() 

    elif "tempo".lower() in r:
        saida = tk.Label(janela, text="Veja no canto da tela", font=("Segoe Script", 10))
        saida.pack()
    elif "piada".lower() in r:
        saida = tk.Label(janela, text="Oque o tomate foi fazer no banco?, um extrato!", font=("Segoe Script", 10))
        saida.pack()
    elif "google".lower() in entrada.get():
        resultado = tk.Label(janela, text="O Google é uma empresa de tecnologia americana de browser e motor de busca", font=("Segoe Script", 10))
        resultado.pack()
    elif "microsoft".lower() in entrada.get():
        resultado = tk.Label(janela, text="A Microsoft é uma empresa de tecnologia americana de software", font=("Segoe Script", 10))
        resultado.pack()
    elif "apple".lower() in entrada.get():
        resultado = tk.Label(janela, text="A Apple é uma empresa de tecnologia americana de hardware e software", font=("Segoe Script", 10))
        resultado.pack()
    elif "amazon".lower() in entrada.get():
        resultado = tk.Label(janela, text="A Amazon é uma empresa de tecnologia americana de e-commerce", font=("Segoe Script", 10))
        resultado.pack()
    elif "guarana".lower() in entrada.get():
        resultado = tk.Label(janela, text="A Guaraná é uma bebida gasosa brasileira,e a favorita do desenvolvedor", font=("Segoe Script", 10))
        resultado.pack()
    elif "coca cola".lower() in entrada.get():
        resultado = tk.Label(janela, text="A Coca-Cola é uma bebida gasosa americana geralmente associada a cola,claro não no literal", font=("Segoe Script", 10))
        resultado.pack()
    elif "porque".lower() in entrada.get() or "ou".lower() in r:
        resultado = tk.Label(janela, text="So sei oque nada sei", font=("Segoe Script", 10))
        resultado.pack()
    elif "pepsi".lower() in entrada.get():
        resultado = tk.Label(janela, text="A Pepsi é uma bebida gasosa americana rival da Coca-Cola", font=("Segoe Script", 10))
        resultado.pack()
    elif "duolingo".lower() in entrada.get():
        resultado = tk.Label(janela, text="O Duolingo é um aplicativo de aprendizado de idiomas", font=("Segoe Script", 10))
        resultado.pack()
    elif "desenvolvedor".lower() in entrada.get():
        resultado = tk.Label(janela, text="Meu desenvolvedor é o davi lucas cardoso guedes", font=("Segoe Script", 10))
        resultado.pack()
    elif "criador".lower() in entrada.get():
        resultado = tk.Label(janela, text="Meu criador é o davi lucas cardoso guedes", font=("Segoe Script", 10))
        resultado.pack()
    elif "holy c".lower() in entrada.get():
        resultado = tk.Label(janela, text="O Holy C é uma linguagem de programação criada para o temple os", font=("Segoe Script", 10))
        resultado.pack() 
    elif "python".lower() in entrada.get():
        resultado = tk.Label(janela, text="Python é uma linguagem de programação de alto nível", font=("Segoe Script", 10))
        resultado.pack()
    elif "c++".lower() in entrada.get():
        resultado = tk.Label(janela, text="C++ é uma linguagem de programação de baixo nível", font=("Segoe Script", 10))
        resultado.pack()
    elif "java".lower() in entrada.get():
        resultado = tk.Label(janela, text=r"Java é uma linguagem de programação de alto nível", font=("Segoe Script", 10))
        resultado.pack()
    elif "javascript".lower() in entrada.get():
        resultado = tk.Label(janela, text="JavaScript é uma linguagem de programação de alto nível pra web", font=("Segoe Script", 10))
        resultado.pack() 
    elif "html".lower() in entrada.get():
        resultado = tk.Label(janela, text="HTML é uma linguagem de marcação para web", font=("Segoe Script", 10))
        resultado.pack()  
    elif "css".lower() in entrada.get():
        resultado = tk.Label(janela, text="CSS é uma linguagem de estilo para web", font=("Segoe Script", 10))
        resultado.pack()
    elif "php".lower() in entrada.get():
        resultado = tk.Label(janela, text="PHP é uma linguagem de programação de alto nível para web", font=("Segoe Script", 10))
        resultado.pack() 
    elif "ruby".lower() in entrada.get():
        resultado = tk.Label(janela, text="Ruby é uma linguagem de programação de alto nível", font=("Segoe Script", 10))
        resultado.pack()
    elif "go".lower() == entrada.get():
        resultado = tk.Label(janela, text="Go é uma linguagem de programação de alto nível feito pela google", font=("Segoe Script", 10))
        resultado.pack() 
    elif "rust".lower() in entrada.get():
        resultado = tk.Label(janela, text="Rust é uma linguagem de programação", font=("Segoe Script", 10))
        resultado.pack()
    elif "duo".lower() in entrada.get():
        resultado = tk.Label(janela, text="Duo é o mascote do duolingo sendo uma coruja", font=("Segoe Script", 10))
        resultado.pack() 
    elif "roblox".lower() in entrada.get():
        resultado = tk.Label(janela, text="Roblox é uma plataforma de jogos online", font=("Segoe Script", 10))
        resultado.pack()
    elif "minecraft".lower() in entrada.get():
        resultado = tk.Label(janela, text="Minecraft é um jogo de construção de blocos", font=("Segoe Script", 10))
        resultado.pack() 
    elif "fortnite".lower() in entrada.get():
        resultado = tk.Label(janela, text="Fortnite é um jogo de tiro", font=("Segoe Script", 10))
        resultado.pack()
    elif "android".lower() in entrada.get():
        resultado = tk.Label(janela, text="Android é um sistema operacional para celulares", font=("Segoe Script", 10))
        resultado.pack()
    elif "ios".lower() in entrada.get():
        resultado = tk.Label(janela, text="IOS é um sistema operacional para celulares iphone", font=("Segoe Script", 10))
        resultado.pack()
    elif "windows".lower() in entrada.get():
        resultado = tk.Label(janela, text="Windows é um sistema operacional para computadores", font=("Segoe Script", 10))
        resultado.pack()
    elif "linux".lower() in entrada.get():
        resultado = tk.Label(janela, text="Linux é um sistema operacional para computadores", font=("Segoe Script", 10))
        resultado.pack()
    elif "bot".lower() in entrada.get():
        resultado = tk.Label(janela, text="Eu sou um bot", font=("Segoe Script", 10))
        resultado.pack()
    elif "PLUS".lower() in entrada.get():
        resultado = tk.Label(janela, text="Eu sou o plus como posso te ajudar?", font=("Segoe Script", 10))
        resultado.pack()
    elif "pokemon".lower() in entrada.get():
        resultado = tk.Label(janela, text="Pokemon é uma série de jogos de RPG", font=("Segoe Script", 10))
        resultado.pack()
    elif "mario".lower() in entrada.get():
        resultado = tk.Label(janela, text="Mario é um personagem de jogo", font=("Segoe Script", 10))
        resultado.pack()      
    elif "bot".lower() in r:
        saida = tk.Label(janela, text="Sou um bot", font=("Segoe Script", 10))
        saida.pack()
    elif "trabalho".lower() in r:
        saida = tk.Label(janela, text="Sou um assistente virtual", font=("Segoe Script", 10))
        saida.pack()
    elif "davi".lower() in r:
        saida = tk.Label(janela, text="Davi é um cara muito legal é meu dev", font=("Segoe Script", 10))
        saida.pack()
    elif "python".lower() in r:
        saida = tk.Label(janela, text="Python é uma linguagem de programação de alto nível, interpretada de script, imperativa, orientada a objetos, funcional, de tipagem dinâmica e forte. Foi lançada por Guido van Rossum em 1991. É uma linguagem muito popular para desenvolvimento web, automação, ciência de dados e inteligência artificial.", font=("Segoe Script", 10))
        saida.pack()
    elif "java".lower() in r:
        saida = tk.Label(janela, text="Java é uma linguagem de programação de alto nível, orientada a objetos e de plataforma neutra. Foi desenvolvida pela Sun Microsystems e lançada em 1995. Java é conhecida por sua portabilidade, segurança e robustez.", font=("Segoe Script", 10))
        saida.pack()
    elif "c++".lower() in r:
        saida = tk.Label(janela, text="C++ é uma linguagem de programação de alto nível, orientada a objetos e de plataforma neutra. Foi desenvolvida pela Bell Labs e lançada em 1985. C++ é conhecida por sua eficiência, flexibilidade e desempenho.", font=("Segoe Script", 10))
        saida.pack()
    elif "ajuda".lower() in r:
        saida = tk.Label(janela, text="Como posso ajudar?", font=("Segoe Script", 10))
        saida.pack()
    elif "pod".lower() in r:
        saida = tk.Label(janela, text="Posso ajudar com várias coisas, como responder perguntas, contar piadas, e muito mais!", font=("Segoe Script", 10))
        saida.pack()
    elif "hamburger de siri".lower() in r:
        saida = tk.Label(janela, text="Ok seu-siriquejo", font=("Segoe Script", 10))
        saida.pack()
    elif "alexa".lower() in r:
        saida = tk.Label(janela, text="Alexa é uma assistente virtual desenvolvida pela Amazon.", font=("Segoe Script", 10))
        saida.pack()
    elif "siri".lower() in r:
        saida = tk.Label(janela, text="Siri é uma assistente virtual desenvolvida pela Apple.", font=("Segoe Script", 10))
        saida.pack()
    elif "fa".lower() in r:
        saida = tk.Label(janela, text="Faça o que você quiser!", font=("Segoe Script", 10))
        saida.pack()
    elif "bom".lower() in r:
        saida = tk.Label(janela, text="oi como posso te ajudar", font=("Segoe Script", 10))
        saida.pack()
    elif "imagem".lower() in r:
        saida = tk.Label(janela, text="Não sei fazer isso ainda", font=("Segoe Script", 10))
        saida.pack()
    elif "hobby".lower() in r:
        saida = tk.Label(janela, text="Meu hobby é ajudar as pessoas", font=("Segoe Script", 10))
        saida.pack()
    elif "fala".lower() in r:
        saida = tk.Label(janela, text="Eu não sei falar ainda", font=("Segoe Script", 10))
        saida.pack()
    elif "quer".lower() in r:
        saida = tk.Label(janela, text="Eu não sei fazer isso ainda", font=("Segoe Script", 10))
        saida.pack()
    elif "como".lower() in entrada.get():
        resultado = tk.Label(janela, text="Eu sou um bot, não posso fazer isso", font=("Segoe Script", 10))
        resultado.pack()
    elif "quando".lower() in entrada.get():
        resultado = tk.Label(janela, text="Não sei", font=("Segoe Script", 10))
        resultado.pack()
    elif "onde".lower() in entrada.get():
        resultado = tk.Label(janela, text="Não sei", font=("Segoe Script", 10))
        resultado.pack()  
    elif "porque".lower() in entrada.get():
        resultado = tk.Label(janela, text="So sei oque nada sei", font=("Segoe Script", 10))
        resultado.pack()
    elif "filosofia".lower() in entrada.get():
        resultado = tk.Label(janela, text="A filosofia é a ciência que estuda o ser e o conhecimento", font=("Segoe Script", 10))
        resultado.pack()
    elif "matemática".lower() in entrada.get():
        resultado = tk.Label(janela, text="A matemática é a ciência que estuda os números e as formas", font=("Segoe Script", 10))
        resultado.pack()
    elif "física".lower() in entrada.get():
        resultado = tk.Label(janela, text="A física é a ciência que estuda como o universo funciona", font=("Segoe Script", 10))
        resultado.pack()  
    elif "química".lower() in entrada.get():
        resultado = tk.Label(janela, text="A química é a ciência que estuda a matéria e suas mudanças", font=("Segoe Script", 10))
        resultado.pack() 
    elif "biologia".lower() in entrada.get():
        resultado = tk.Label(janela, text="A biologia é a ciência que estuda a vida", font=("Segoe Script", 10))
        resultado.pack()
    elif "geografia".lower() in entrada.get():
        resultado = tk.Label(janela, text="A geografia é a ciência que estuda a terra", font=("Segoe Script", 10))
        resultado.pack()
    elif "história".lower() in entrada.get():
        resultado = tk.Label(janela, text="A história é a ciência que estuda o passado", font=("Segoe Script", 10))
        resultado.pack()
    elif "literatura".lower() in entrada.get():
        resultado = tk.Label(janela, text="A literatura é escrita e textos", font=("Segoe Script", 10))
        resultado.pack()
    elif "arte".lower() in entrada.get():
        resultado = tk.Label(janela, text="A arte é a forma de se expressar", font=("Segoe Script", 10))
        resultado.pack()
    elif "música".lower() in entrada.get():
        resultado = tk.Label(janela, text="A música é a forma de se expressar com sons", font=("Segoe Script", 10))
        resultado.pack() 
    elif "cinema".lower() in entrada.get():
        resultado = tk.Label(janela, text="O cinema é a forma de se expressar com imagens a cada segundo gerando uma animação ou um filme", font=("Segoe Script", 10))
        resultado.pack()
    elif "pod".lower() in entrada.get():
        resultado = tk.Label(janela, text="Eu sou um bot, não posso fazer isso", font=("Segoe Script", 10))
        resultado.pack()  
    elif "gost".lower() in r:
        saida = tk.Label(janela, text="Apenas gosto de ajudar pessoas do mundo", font=("Segoe Script", 10))
        saida.pack()
    elif "trabalha".lower() in r:
        saida = tk.Label(janela, text="Apenas trabalho para responder", font=("Segoe Script", 10))
        saida.pack()
    elif "traduzi".lower() in r:
        saida = tk.Label(janela, text="Eu não sei fazer isso ainda", font=("Segoe Script", 10))
        saida.pack()
    elif "faz".lower() in r:
        saida = tk.Label(janela, text="Eu faço apenas textos", font=("Segoe Script", 10))
        saida.pack()
    elif "trabalho".lower() in r:
        saida = tk.Label(janela, text="Eu trabalho para ajudar pessoas", font=("Segoe Script", 10))
        saida.pack()
    elif "ter".lower() in r or "tem".lower() in r:
        saida = tk.Label(janela, text="Eu não sei", font=("Segoe Script", 10))
        saida.pack()
    elif "gosta".lower() in r:
        saida = tk.Label(janela, text="Não tenho opinião", font=("Segoe Script", 10))
        saida.pack()
    elif "sab".lower() in r:
        saida = tk.Label(janela, text="Eu sei apenas responder perguntas", font=("Segoe Script", 10))
        saida.pack()
    elif "beta".lower() in r:
        saida = tk.Label(janela, text="Sim,eu sou um beta", font=("Segoe Script", 10))
        saida.pack()
    elif "dar".lower() in r:
        saida = tk.Label(janela, text="Eu faço apenas textos", font=("Segoe Script", 10))
        saida.pack()
    elif "Brasil".lower() in r:
        saida = tk.Label(janela, text="O Brasil é um país localizado na América do Sul, conhecido por sua rica cultura, diversidade biológica e paisagens variadas.", font=("Segoe Script", 10))
        saida.pack()
    elif "calendario".lower() in r:
        saida = tk.Label(janela, text="Não sei", font=("Segoe Script", 10))
        saida.pack()
    elif "data".lower() in r:
        saida = tk.Label(janela, text="Não sei", font=("Segoe Script", 10))
        saida.pack()
    elif "globo".lower() in r:
        saida = tk.Label(janela, text="Rede Globo é uma das maiores redes de televisão do Brasil, conhecida por seus programas de entretenimento, esportes e notícias.", font=("Segoe Script", 10))
        saida.pack()
    else:
        saida = tk.Label(janela, text="Não entendi", font=("Segoe Script", 10))
        saida.pack()

botao = ttk.Button(janela, text="Enviar", command=resposta)
botao.pack()
janela.mainloop()

"""plus"""
