import random

subs = 0

print('welcome to Python FYSC')

for x in range(500000000000000000):
    commandinput = input('commands: !video, !endfysc. Type the command here: ')
    if commandinput == '!video': 
	    randomsub = random.randrange(100, 500)
	    print('a video is published! You gained',randomsub, 'subs!')
	    subs += randomsub
	    print('You have', subs, 'subscribers right now.')
    elif commandinput == '!endfysc':
	    print('ending fysc now...')
	    break
    else:
	    print('invaild command. Try another command.')
