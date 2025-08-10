from tkinter import *
import webbrowser as wb

Authorised = False
Auth_name = 0
window = Tk()
window.title("Костыль - PENTAGON")
window.geometry('275x350')
connect_to = []


users = ['pashni', '6688', 'killex', '3434', 'kanemi', '5252', 'voltron', '4242', 'ebok', '1012']

auth_id = [0, 0, 1, 1, 2, 2, 3, 3, 4, 4]

links = ['https://meet.google.com/pii-jubu-jph', 'https://meet.google.com/rsg-mqfz-gha',
                'https://meet.google.com/npg-fesq-mak', 'https://meet.google.com/jta-aohc-cnb',
         'https://meet.google.com/pii-jubu-jph', 'https://meet.google.com/iik-ajne-gau',
                'https://meet.google.com/ekv-sotf-xqo', 'https://meet.google.com/wim-ybxg-mjt',
         'https://meet.google.com/rsg-mqfz-gha', 'https://meet.google.com/iik-ajne-gau',
                'https://meet.google.com/jdn-sbth-rxi', 'https://meet.google.com/yrb-sjtc-fec',
         'https://meet.google.com/npg-fesq-mak', 'https://meet.google.com/iik-ajne-gau',
                 'https://meet.google.com/jdn-sbth-rxi', 'https://meet.google.com/ojf-qvpr-piu',
         'https://meet.google.com/jta-aohc-cnb', 'https://meet.google.com/wim-ybxg-mjt',
              'https://meet.google.com/yrb-sjtc-fec', 'https://meet.google.com/ojf-qvpr-piu']

pashni_links = ['pashni', 'https://meet.google.com/pii-jubu-jph', 'https://meet.google.com/rsg-mqfz-gha',
                'https://meet.google.com/npg-fesq-mak', 'https://meet.google.com/jta-aohc-cnb']
killex_links = ['killex', 'https://meet.google.com/pii-jubu-jph', 'https://meet.google.com/iik-ajne-gau',
                'https://meet.google.com/ekv-sotf-xqo', 'https://meet.google.com/wim-ybxg-mjt']
kanemi_links = ['kanemi', 'https://meet.google.com/rsg-mqfz-gha', 'https://meet.google.com/iik-ajne-gau',
                'https://meet.google.com/jdn-sbth-rxi', 'https://meet.google.com/yrb-sjtc-fec']
voltron_links = ['voltron', 'https://meet.google.com/npg-fesq-mak', 'https://meet.google.com/iik-ajne-gau',
                 'https://meet.google.com/jdn-sbth-rxi', 'https://meet.google.com/ojf-qvpr-piu']
ebok_links = ['ebok', 'https://meet.google.com/jta-aohc-cnb', 'https://meet.google.com/wim-ybxg-mjt',
              'https://meet.google.com/yrb-sjtc-fec', 'https://meet.google.com/ojf-qvpr-piu']


lab1 = Label(window, width=20, bg='gray', text='Username')
ent1 = Entry(window, width=20, bg='white')
lab2 = Label(window, width=20, bg='gray', text='Password')
ent2 = Entry(window, width=20, bg='white')
lab3 = Label(window, width=20, height=2, bg='gray', fg='green')

def activate_auth():
    global ch1, ch2, ch3, ch4, ch5, Auth_name, Authorised
    if Authorised:
        if ch1['text'] != Auth_name:
            ch1.config(state=NORMAL)
        if ch2['text'] != Auth_name:
            ch2.config(state=NORMAL)
        if ch3['text'] != Auth_name:
            ch3.config(state=NORMAL)
        if ch4['text'] != Auth_name:
            ch4.config(state=NORMAL)
        if ch5['text'] != Auth_name:
            ch5.config(state=NORMAL)

def deactivate_auth():
    global ch1, ch2, ch3, ch4, ch5, Auth_name, Authorised
    ch1.config(state=DISABLED)
    ch2.config(state=DISABLED)
    ch3.config(state=DISABLED)
    ch4.config(state=DISABLED)
    ch5.config(state=DISABLED)
def auth(username, password):
    global Authorised, lab3, Auth_name, but1
    for i in range(len(users) - 1):
        if username.lower() == users[i]:
            if password == users[i + 1]:
                Authorised = True
                Auth_name = users[i]
                ent1.config(bg='green')
                ent2.config(bg='green')
                lab3.config(fg='green', text=f'Authorised as \n {Auth_name}')
                activate_auth()
                Auth_name = auth_id[i]


            else:
                Auth_name = ' '
                Authorised = False
                ent1.config(bg='red')
                ent2.config(bg='red')
                lab3.config(fg='red', text='Incorrect \n password')
                deactivate_auth()
                break
        else:
            if i != 9:
                i += 1
            else:
                lab3.config(fg='red', text='Non-existent \n username')
                break


def auth_button():
    deactivate_auth()
    auth(ent1.get(), ent2.get())

def connect():
    global Auth_name, connect_to, ch1_var, ch2_var, ch3_var, ch4_var, ch5_var, links
    ch_var_list = [ch1_var.get(), ch2_var.get(), ch3_var.get(), ch4_var.get(), ch5_var.get()]
    ch_var_list.pop(Auth_name)
    j = 4*Auth_name
    for i in ch_var_list:
        if i == 1:
            wb.open_new(links[j])
            j += 1
            continue
        else:
            j += 1
            continue
    but_con.config(state=DISABLED)



but1 = Button(window, width=20, text='Authorise', command=auth_button)
but1.bind("<Button-1>", lambda event: auth_button())
lab4 = Label(window, width=20, bg='gray', text='Connect to:')
ch1_var = IntVar()
ch1 = Checkbutton(window, state=DISABLED, text='pashni', variable=ch1_var)
ch2_var = IntVar()
ch2 = Checkbutton(window, state=DISABLED, text='killex', variable=ch2_var)
ch3_var = IntVar()
ch3 = Checkbutton(window, state=DISABLED, text='kanemi', variable=ch3_var)
ch4_var = IntVar()
ch4 = Checkbutton(window, state=DISABLED, text='voltron', variable=ch4_var)
ch5_var = IntVar()
ch5 = Checkbutton(window, state=DISABLED, text='ebok', variable=ch5_var)
but_con = Button(window, width=20, text='Connect', command=connect)
but_con.bind("<Button-2>", lambda event: connect())

lab1.pack()
ent1.pack()
lab2.pack()
ent2.pack()
lab3.pack()
but1.pack()
lab4.pack()
ch1.pack()
ch2.pack()
ch3.pack()
ch4.pack()
ch5.pack()
but_con.pack()

window.mainloop()
