#!/usr/bin/env python
# coding: utf-8

# In[23]:


import random 

def menu(): 
    print("Hola pishiosha❤️") 
    print("¿Quieres que te diga una cosita?😏\n\n") 
    entrada = input("Si quieres tienes que poner 'chi' si no, pues pon 'no': ").lower().strip() 

    if entrada == "chi":
        print("Uy! te quedaste😊!\n\n")

        entrada2 = int(input("""Vale elige uno: 
        1. Romántico❤️
        2. Tierno💫
        3. Agradecimiento💌
        4. Buenos días o noches🌙
        5. Intenso🌹
        6. Coqueto🥰
        7. Motivador🌈
        8. Complicidad🌻
        9. Cortos💕
        10. Especiales✨ (PROXIMAMENTE)
        👉 Elige un número: """))
        
        return entrada, entrada2

    elif entrada == "no": 
        print("Jo! pues me voy😢") 
        return entrada, None


# Diccionario con todas las frases
frases_dict = {
    1: [
        "Eres mi lugar favorito para estar.",
        "Contigo todo tiene sentido.",
        "Me haces creer en el amor verdadero.",
        "Cada día contigo es mi mejor regalo.",
        "Amarte es lo más fácil que he hecho en la vida.",
        "Eres mi casualidad más bonita.",
        "No sé qué hice para merecerte, pero prometo cuidarte siempre.",
        "Tu sonrisa ilumina mis días.",
        "Mi corazón late más fuerte cada vez que te veo.",
        "No necesito nada más si te tengo a ti."
    ],
    2: [
        "Me haces sentir en casa, aunque estemos lejos.",
        "Eres mi razón favorita para sonreír.",
        "No quiero un final feliz, quiero una vida feliz contigo.",
        "Hasta en mis sueños quiero estar contigo.",
        "Tu abrazo es mi refugio.",
        "Si pudiera pedir un deseo, siempre serías tú.",
        "Me gusta cómo el mundo se calma cuando estás cerca.",
        "Tus ojos son mi lugar seguro.",
        "Eres la parte más bonita de mis días.",
        "En tu voz encuentro paz."
    ],
    3: [
        "Gracias por existir.",
        "Gracias por enseñarme lo que es el amor.",
        "Eres la mejor parte de mi vida.",
        "Gracias por ser mi fuerza en los días difíciles.",
        "Contigo aprendí lo que significa amar de verdad.",
        "Gracias por elegirme cada día.",
        "Me haces mejor persona.",
        "Nunca dejaré de agradecerte por quedarte.",
        "Gracias por ser mi sueño cumplido.",
        "Eres mi regalo del universo."
    ],
    4: [
        "Buen día, amor, que tu día sea tan lindo como tu sonrisa.",
        "Despertar sabiendo que estás en mi vida lo hace todo mejor.",
        "Buenas noches, que sueñes conmigo.",
        "Que tengas un día lleno de cosas tan bonitas como tú.",
        "Dulces sueños, mi amor.",
        "Dormiré feliz solo porque sé que estás en mi vida.",
        "Ojalá pudiera darte los buenos días con un beso.",
        "Que tu noche sea tranquila y tu corazón ligero.",
        "Hoy te pienso antes de dormir, como siempre.",
        "Despertar contigo es mi motivación favorita."
    ],
    5: [
        "Eres mi eternidad disfrazada de instante.",
        "No quiero un “para siempre”, quiero un “cada día” contigo.",
        "Eres mi historia favorita.",
        "Todo lo que busqué siempre lo encontré en ti.",
        "Amarte es como respirar: inevitable.",
        "Si vuelvo a nacer, ojalá vuelvas a cruzarte en mi vida.",
        "Eres la persona con la que quiero envejecer.",
        "Mi futuro suena mejor contigo.",
        "Siempre serás mi elección, incluso en mil vidas más.",
        "No sé de destino, pero sé que el mío eres tú."
    ],
    6: [
        "Me encantas, incluso cuando haces nada.",
        "Tu risa es mi sonido favorito.",
        "No sé qué sería de mí sin tus locuras.",
        "Hasta tus enojos me parecen lindos.",
        "Me derrites con una sola mirada.",
        "Eres mi travesura favorita.",
        "Qué suerte la mía de coincidir contigo.",
        "No tienes idea de lo mucho que me gustas.",
        "Si te beso una vez, quiero mil más.",
        "Me encanta cuando me miras como si fuera tuyo."
    ],
    7: [
        "Confío en ti y en todo lo que puedes lograr.",
        "Estoy orgulloso/a de ti cada día.",
        "Eres más fuerte de lo que crees.",
        "Siempre estaré aquí para apoyarte.",
        "Tú puedes con todo, yo creo en ti.",
        "Cada paso que das me inspira.",
        "Brillas más de lo que imaginas.",
        "Sé que lograrás todo lo que sueñas.",
        "Tu esfuerzo me motiva.",
        "Eres grande, aunque no lo veas aún."
    ],
    8: [
        "Nadie me entiende como tú.",
        "Contigo todo se siente fácil.",
        "Eres mi mejor aventura.",
        "Contigo me atrevo a soñar más grande.",
        "No necesito filtros, contigo soy yo.",
        "Eres mi compañero/a en todo.",
        "Me encanta hacer locuras a tu lado.",
        "Tú y yo somos el mejor equipo.",
        "Contigo, hasta el silencio es bonito.",
        "Nuestra historia es mi favorita."
    ],
    9: [
        "Te amo.",
        "Te extraño.",
        "Te necesito.",
        "Te pienso.",
        "Te quiero cerquita.",
        "Eres mi todo.",
        "Eres mi paz.",
        "Eres mi hogar.",
        "Eres mi sueño.",
        "Eres mi vida."
    ]
    
}


def main(): 
    
    while True: 
        entrada1, entrada2 = menu()

        if entrada1 == "chi":
            if entrada2 == 10:
                print("QUE TRAMPOSA, AHI PONE 'PROXIMAMENTE'😲\n\n") 
            elif entrada2 in frases_dict:
                frase = random.choice(frases_dict[entrada2])
                print(f"\n👉 {frase}\n") 
        elif entrada1 == "no":
            break 


if __name__ == "__main__":
    main()

        


# In[ ]:




