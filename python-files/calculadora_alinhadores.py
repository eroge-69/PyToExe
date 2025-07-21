
import PySimpleGUI as sg

layout = [
    [sg.Text("Valor do planejamento (R$)"), sg.Input(key='planejamento')],
    [sg.Text("Nº alinhadores superiores"), sg.Input(key='alin_sup')],
    [sg.Text("Nº alinhadores inferiores"), sg.Input(key='alin_inf')],
    [sg.Text("Valor por alinhador (R$)"), sg.Input(key='valor_alinhador')],
    [sg.Text("Valor da consulta (R$)"), sg.Input(key='valor_consulta')],
    [sg.Text("Guia attachment superior (R$)"), sg.Input(key='guia_sup')],
    [sg.Text("Guia attachment inferior (R$)"), sg.Input(key='guia_inf')],
    [sg.Button("Calcular"), sg.Exit()],
    [sg.Text("Valor desta etapa do tratamento:", size=(30,1)), sg.Text("", key='resultado1')],
    [sg.Text("Sugestão mínima de valor:", size=(30,1)), sg.Text("", key='resultado2')]
]

window = sg.Window("Calculadora de Etapas - Alinhadores", layout)

while True:
    event, values = window.read()
    if event in (sg.WINDOW_CLOSED, 'Exit'):
        break
    if event == 'Calcular':
        try:
            planejamento = float(values['planejamento'])
            alin_sup = int(values['alin_sup'])
            alin_inf = int(values['alin_inf'])
            valor_alinhador = float(values['valor_alinhador'])
            valor_consulta = float(values['valor_consulta'])
            guia_sup = float(values['guia_sup'])
            guia_inf = float(values['guia_inf'])

            maior_alinhadores = max(alin_sup, alin_inf)

            etapa = (
                planejamento +
                (alin_sup * valor_alinhador) +
                (alin_inf * valor_alinhador) +
                (valor_consulta * maior_alinhadores) +
                guia_sup +
                guia_inf
            )

            sugestao_minima = etapa - planejamento

            window['resultado1'].update(f"R$ {etapa:,.2f}")
            window['resultado2'].update(f"R$ {sugestao_minima:,.2f}")
        except Exception as e:
            sg.popup_error("Erro nos dados inseridos. Verifique os campos.", str(e))

window.close()
