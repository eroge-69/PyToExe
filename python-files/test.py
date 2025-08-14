data_list = []
print("Input data : (press 'ENTER*2' to input ):")

while True:
    data = input()
    if data == '':
        break  # ออกจากลูป
    data_list.append(data)

# format where query
formatted_list = [f"UnitNO like '{data}%'" for data in data_list]

# join list with ' or\n'
result = " or\n".join(formatted_list)
print('where', result)