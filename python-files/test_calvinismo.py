import tkinter as tk
from tkinter import messagebox

# Preguntas y respuestas (texto, [(opción, puntaje)])
preguntas = [
    ("Respecto al libre albedrío humano:", [
        ("El hombre está totalmente muerto en pecado y jamás puede elegir a Dios por sí mismo. (CR)", 4),
        ("El hombre está incapacitado pero puede ser movido irresistiblemente por la gracia de Dios. (CM)", 3),
        ("El hombre está afectado por el pecado, pero aún puede responder a Dios con ayuda de su gracia. (AM)", 2),
        ("El hombre tiene plena capacidad de elegir a Dios sin necesidad de intervención divina. (AR)", 1)
    ]),
    ("Sobre la elección divina:", [
        ("Dios eligió soberanamente a algunos para salvación y a otros para condenación. (CR)", 4),
        ("Dios eligió a los salvos sin basarse en méritos ni previsión de fe. (CM)", 3),
        ("Dios eligió a los que Él previó que creerían en Cristo. (AM)", 2),
        ("No existe elección previa, la decisión final es solo del hombre. (AR)", 1)
    ]),
    ("La obra de Cristo en la cruz fue:", [
        ("Cristo murió exclusivamente por los elegidos. (CR)", 4),
        ("Cristo murió principalmente por los elegidos, pero su sacrificio tiene valor universal. (CM)", 3),
        ("Cristo murió por toda la humanidad, aunque solo los que creen reciben el beneficio. (AM)", 2),
        ("Cristo murió para ofrecer salvación universal dependiente del libre albedrío. (AR)", 1)
    ]),
    ("La gracia de Dios en la salvación es:", [
        ("La gracia es irresistible; nadie puede oponerse a ella. (CR)", 4),
        ("La gracia siempre alcanza a los elegidos, aunque en distintos tiempos. (CM)", 3),
        ("La gracia es suficiente para todos, pero depende de la aceptación humana. (AM)", 2),
        ("La gracia es solo una invitación general que muchos pueden rechazar. (AR)", 1)
    ]),
    ("Respecto a la perseverancia del creyente:", [
        ("Un verdadero creyente nunca puede perder su salvación. (CR)", 4),
        ("Los elegidos perseveran porque Dios los sostiene hasta el fin. (CM)", 3),
        ("Un creyente puede caer de la gracia si abandona la fe. (AM)", 2),
        ("La salvación depende exclusivamente de la fidelidad constante del hombre. (AR)", 1)
    ]),
    ("El pecado original significa:", [
        ("El hombre está tan depravado que no puede hacer nada bueno en absoluto. (CR)", 4),
        ("El hombre está espiritualmente incapacitado pero puede hacer obras civiles buenas. (CM)", 3),
        ("El hombre conserva cierta libertad para buscar a Dios si responde a la gracia preveniente. (AM)", 2),
        ("El pecado no impide al hombre decidir por Dios cuando lo desee. (AR)", 1)
    ]),
    ("Sobre la justicia de Dios en la condenación:", [
        ("Dios es justo al condenar incluso a los que nunca tuvieron posibilidad de creer. (CR)", 4),
        ("Dios es justo porque los no elegidos muestran su propia rebeldía. (CM)", 3),
        ("Dios es justo porque todos reciben una verdadera oportunidad de creer. (AM)", 2),
        ("Dios sería injusto si no diera oportunidad a cada ser humano. (AR)", 1)
    ]),
    ("El papel del Espíritu Santo en la conversión:", [
        ("El Espíritu Santo regenera al pecador antes de que crea, sin su cooperación. (CR)", 4),
        ("El Espíritu Santo atrae irresistiblemente a los elegidos. (CM)", 3),
        ("El Espíritu Santo ayuda al hombre, pero este puede rechazarlo. (AM)", 2),
        ("El Espíritu Santo solo persuade externamente, sin influir en la decisión humana. (AR)", 1)
    ]),
    ("Respecto a la predestinación:", [
        ("Dios decretó desde la eternidad quién se salvaría y quién no. (CR)", 4),
        ("Dios decretó la salvación de los elegidos, sin prever obras. (CM)", 3),
        ("Dios predestinó a quienes previó que creerían. (AM)", 2),
        ("La predestinación no existe; todo depende del hombre. (AR)", 1)
    ]),
    ("Sobre la expiación:", [
        ("Cristo murió solo por los elegidos. (CR)", 4),
        ("Cristo murió por todos, pero con intención especial hacia los elegidos. (CM)", 3),
        ("Cristo murió por todos, condicionado a la fe. (AM)", 2),
        ("Cristo murió por todos, garantizando salvación si alguien decide. (AR)", 1)
    ]),
    ("La seguridad eterna:", [
        ("Ningún verdadero creyente puede perder la salvación bajo ninguna circunstancia. (CR)", 4),
        ("Dios garantiza que los elegidos perseveren hasta el fin. (CM)", 3),
        ("Un cristiano puede perder su salvación si apostata. (AM)", 2),
        ("La salvación puede perderse incluso por pecados repetidos. (AR)", 1)
    ]),
    ("La gracia común:", [
        ("No salva, solo refrena el pecado. (CR)", 4),
        ("Permite que los hombres hagan el bien externo, aunque no espiritual. (CM)", 3),
        ("Es la gracia que permite a todos responder a Dios. (AM)", 2),
        ("Es suficiente para salvar a cualquiera que decida sin ayuda. (AR)", 1)
    ]),
    ("El evangelio se predica:", [
        ("Para llamar eficazmente solo a los elegidos. (CR)", 4),
        ("Para todos, pero eficaz solo en los elegidos. (CM)", 3),
        ("Para toda la humanidad como invitación. (AM)", 2),
        ("Para ofrecer salvación igual para todos según decidan. (AR)", 1)
    ]),
    ("La voluntad de Dios frente al mal:", [
        ("Dios decreta el mal con un propósito soberano. (CR)", 4),
        ("Dios permite el mal dentro de su plan. (CM)", 3),
        ("Dios no decreta el mal, solo lo permite por libre albedrío. (AM)", 2),
        ("Dios no tiene relación con el mal, que es autónomo. (AR)", 1)
    ]),
    ("El origen de la fe:", [
        ("Es un don irresistible dado solo a los elegidos. (CR)", 4),
        ("Es un don de Dios que inevitablemente se ejerce en los elegidos. (CM)", 3),
        ("Es una respuesta humana a la gracia de Dios. (AM)", 2),
        ("Es un acto completamente humano, independiente de la gracia. (AR)", 1)
    ]),
    ("La relación entre fe y obras:", [
        ("Las obras no cuentan nada, solo la elección divina. (CR)", 4),
        ("Las obras son fruto inevitable de la fe verdadera. (CM)", 3),
        ("Las obras confirman la fe. (AM)", 2),
        ("Las obras son requisito para alcanzar salvación. (AR)", 1)
    ]),
    ("El destino eterno del hombre:", [
        ("Está absolutamente determinado por el decreto soberano de Dios. (CR)", 4),
        ("Está asegurado en los elegidos que perseveran. (CM)", 3),
        ("Depende de la respuesta humana. (AM)", 2),
        ("Depende solo de la decisión y esfuerzo del hombre. (AR)", 1)
    ]),
    ("La misión de la Iglesia:", [
        ("Es proclamar la gloria de Dios en la salvación de los elegidos. (CR)", 4),
        ("Es predicar sabiendo que algunos responderán por elección divina. (CM)", 3),
        ("Es persuadir a todos para que ejerzan su libertad. (AM)", 2),
        ("Es ofrecer salvación universal en igualdad de condiciones. (AR)", 1)
    ]),
    ("La justicia de Dios en la elección:", [
        ("Dios es justo aunque salve a unos y no a otros según su voluntad soberana. (CR)", 4),
        ("Dios es justo al mostrar misericordia a los elegidos. (CM)", 3),
        ("Dios es justo porque todos reciben la misma posibilidad real de creer. (AM)", 2),
        ("Dios sería injusto si no diera idéntica oportunidad a todos. (AR)", 1)
    ]),
    ("El propósito de la elección:", [
        ("Manifestar la gloria de Dios incluso en la condenación de algunos. (CR)", 4),
        ("Exaltar la gracia de Dios en la salvación de los elegidos. (CM)", 3),
        ("Dar salvación a quienes decidan creer en Cristo. (AM)", 2),
        ("Garantizar igualdad universal de acceso a la salvación. (AR)", 1)
    ])
]

class TestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Test Calvinismo vs Arminianismo")
        self.puntaje = 0
        self.indice = 0
        
        self.label = tk.Label(root, text="", wraplength=500, justify="left", font=("Arial", 12))
        self.label.pack(pady=10)
        
        self.var = tk.IntVar()
        self.botones = []
        for i in range(4):
            b = tk.Radiobutton(root, text="", variable=self.var, value=i, wraplength=500, anchor="w", justify="left")
            b.pack(fill="x", padx=20, pady=2)
            self.botones.append(b)
        
        self.btn = tk.Button(root, text="Siguiente", command=self.siguiente)
        self.btn.pack(pady=10)
        
        self.mostrar_pregunta()
    
    def mostrar_pregunta(self):
        pregunta, opciones = preguntas[self.indice]
        self.label.config(text=f"{self.indice+1}. {pregunta}")
        self.var.set(-1)
        for i, (texto, _) in enumerate(opciones):
            self.botones[i].config(text=texto)
    
    def siguiente(self):
        sel = self.var.get()
        if sel == -1:
            messagebox.showwarning("Atención", "Debes seleccionar una respuesta.")
            return
        _, opciones = preguntas[self.indice]
        self.puntaje += opciones[sel][1]
        self.indice += 1
        if self.indice >= len(preguntas):
            self.mostrar_resultado()
        else:
            self.mostrar_pregunta()
    
    def mostrar_resultado(self):
        calv = round(((self.puntaje - 20) / 60) * 100, 1)
        armi = round(100 - calv, 1)
        
        if calv >= 66:
            interpretacion = "Predominantemente Calvinista"
        elif calv >= 34:
            interpretacion = "Mixto / Intermedio"
        else:
            interpretacion = "Predominantemente Arminiano"
        
        messagebox.showinfo("Resultado",
            f"Puntaje total: {self.puntaje}\n"
            f"Porcentaje Calvinismo: {calv}%\n"
            f"Porcentaje Arminianismo: {armi}%\n\n"
            f"Interpretación: {interpretacion}"
        )
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = TestApp(root)
    root.mainloop()
