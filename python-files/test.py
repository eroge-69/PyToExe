or_x,or_y,or_z = input('Введите координаты снега: ').split()
x,y,z = input('Введите координаты цели: ').split()
final_y = int(input('Введите нижнюю границу выстрела: '))

or_x,or_y,or_z = int(or_x),int(or_y),int(or_z)
x,y,z = int(x),int(y),int(z)
final_y = int(final_y)

print(round((x-or_x)/0.784375))

print(f'''\nЗагрузить:
    Payload [{(y-final_y+6)//64} стаков {(y-final_y+6)%64} предметов]
    Prop [{(round((or_y-final_y)/0.248))//64} стаков {(round((or_y-final_y)/0.248))%64}]
    Forward [{(round((x-or_x)/0.784375))//64} стаков {(round((x-or_x)/0.784375))//64}]
    Side [{((round((z-or_z)/0.784375))-9)//64} стаков {((round((z-or_z)/0.784375))-9)%64}]''')

