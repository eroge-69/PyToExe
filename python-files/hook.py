from dhooks  import Webhook
hook1 = Webhook("https://discord.com/api/webhooks/1355280721782116563/wC4ZqR2wPOiI_btN6rG7cuDMLQd9ifTZDTzNhOHXD9rtPeLYqv_FrvI7HY-bwaTW2JJV")
hook2 = Webhook("https://discord.com/api/webhooks/1231268799702106202/35_fEx5K4bGi7LqEv9J9_fV56VHq-66DW3J3bhRs4xOpwV2V1gQ39WScafXmh6tiLMH3")
table = ["url1","url2"]
inpt = input('''
            
███████╗██╗░░░░░███████╗██╗░░██╗░██████╗███████╗
██╔════╝██║░░░░░██╔════╝╚██╗██╔╝██╔════╝╚════██║
█████╗░░██║░░░░░█████╗░░░╚███╔╝░╚█████╗░░░███╔═╝
██╔══╝░░██║░░░░░██╔══╝░░░██╔██╗░░╚═══██╗██╔══╝░░
██║░░░░░███████╗███████╗██╔╝╚██╗██████╔╝███████╗
╚═╝░░░░░╚══════╝╚══════╝╚═╝░░╚═╝╚═════╝░╚══════╝ 

select tble: ''')
if inpt == table[0]:
    hook1.send(input("message: "))

elif inpt == table[1]:
    hook2.send(input("message: "))

