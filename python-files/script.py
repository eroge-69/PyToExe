import random
import scratchattach as sa
import webbrowser

hortini = sa.get_user("Hortini")
lilhort = sa.get_user("LittleHort")
hortina = sa.get_user("Hortina")
hortmini = sa.get_user("Hortmini")
joert = sa.get_user("Joert")
messagenum = hortini.message_count() + lilhort.message_count() + hortina.message_count() + hortmini.message_count() + joert.message_count()
print(messagenum)
input("press enter to leave ")
