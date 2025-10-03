string = input("type sentence:")
string_list = string.split()

def list_isolate_digits(list0):
	list_digits= []
	for item in list0:
		if item.isdigit():
		    list_digits.append(int(item))
		else:
			continue 
	return list_digits


print(list_isolate_digits(string_list))