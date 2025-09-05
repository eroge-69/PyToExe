sentence = input("문장 : ")
result = []

gansa = False
temp = []
for word in sentence.split():
	if gansa:
		temp.append(word)
		gansa = False
		result.append(" ".join(temp))
		temp = []
	else:
		if word.lower() == "a":
			gansa = True
			temp.append(word)
		elif word.lower() == "an":
			gansa = True
			temp.append(word)
		elif word.lower() == "the":
			gansa = True
			temp.append(word)
		else:
			result.append(word)
		

print("/")
for r in result:
	print(r, end=' / ')