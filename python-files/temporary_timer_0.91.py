import time
import requests

import channel_checker
import day_cycle_channels_former_91

url_main = 'http://192.168.0.4'
list_of_all_channels = channel_checker.checker(url_main) #[False, False, False, False, False, False, False, False, False, True, True]

warning_numbers = [10, 11]  # Номера инвертированых каналов реле
main_timer_long = 10.0
time_checker = time.time() - main_timer_long
up_time_start = time_checker
list_of_lights_to_on = []



def main_timer(main_timer_long):
	global time_checker
	time_in_sec = time.time()
	if time_in_sec - time_checker >= main_timer_long:
		time_checker = time_in_sec
		#print(time_in_sec)
		return True
	else:
		return False

def list_to_on(url, list1):            #Список команд для включения каналов из списка на включение
	list_to_on = [url + "/update?relay=" + str(i) + "&state=1" for i in list1]
	for x in warning_numbers:  # Цикл поиска и замены инвертированых значений
		if url + "/update?relay=" + str(x) + "&state=1" in list_to_on:
			list_to_on[list_to_on.index(url + "/update?relay=" + str(x) + "&state=1")] = url + "/update?relay=" + str(x) + "&state=0"
	return list_to_on

def list_of_lights_to_off(list_of_all_channels, list_of_lights_to_on): #Список каналов для выключения тех, которых нет в списке на включение
    new_list = [x for x in range(1, len(list_of_all_channels)+1)]
    list_of_lights_to_off = [x for x in new_list if x not in list_of_lights_to_on]
    #print(new_list, list_of_lights_to_off)
    return list_of_lights_to_off

def list_to_off(url):                   #Список команд для выключения тех, которых нет в списке на включение
	list1 = list_of_lights_to_off(list_of_all_channels, list_of_lights_to_on)
	list_to_off = [url + "/update?relay=" + str(i) + "&state=0" for i in list1]
	for x in warning_numbers:  # Цикл поиска и замены инвертированых значений
		if url + "/update?relay=" + str(x) + "&state=0" in list_to_off:
			list_to_off[list_to_off.index(url + "/update?relay=" + str(x) + "&state=0")] = url + "/update?relay=" + str(x) + "&state=1"
	return list_to_off

def list_to_off_all(url, list2):                  #Список команд для выключения всех каналов
	list_to_off_all = [url + "/update?relay=" + str(i) + "&state=0" for i in range(1, len(list2)+1)]
	for x in warning_numbers:
		if url + "/update?relay=" + str(x) + "&state=0" in list_to_off_all:
			list_to_off_all[list_to_off_all.index(url + "/update?relay=" + str(x) + "&state=0")] = url + "/update?relay=" + str(x) + "&state=1"
	return list_to_off_all

def toogle_light(list_of_commands):
	for i in list_of_commands:
		requests.get(i)
		#print(i)
		time.sleep(0.1)

def information():
	current_time = time.time()
	def time_now(time_now):
		time1 = time.ctime(time_now)
		print(time1)
	def uptime(uptime_start, time1):
		uptime = time1 - uptime_start
		print(f'Время с начала работы программы: {str(int(uptime//3600))} часов')

	time_now(current_time)
	uptime(up_time_start,current_time)

#main_check = input('Введите режим работы: 1 - автоматический, 2 - ручной: \n')

toogle_light(list_to_off(url_main))

# if main_check == '1':
while True:
	if main_timer(main_timer_long):                                           #Таймер отсчитал основной интервал цикла:
		information()
		last_list_of_lights_to_on = list_of_lights_to_on                      #Переменная для отсчёта интервала принимает значение текущего времени
		list_of_lights_to_on = day_cycle_channels_former_91.channel_to_on_right_now()            #Переменная получает список каналов для включения

		if list_of_lights_to_on != last_list_of_lights_to_on:                 #Если последний полученный список отличается от текущего:
			last_list_of_lights_to_on = list_of_lights_to_on                  #Переменная с последним списком принимает значение текущего

			if list_of_lights_to_on == []:                                    #Если список пустой:
				turn_off_all_list = list_to_off_all(url_main, list_of_all_channels) #Сформировать команды для выключения всех каналов
				toogle_light(turn_off_all_list)                               #Выключить всё

			else:                                                             #Иначе:
				turn_on_list = list_to_on(url_main, list_of_lights_to_on)     #Сформировать команды для каналов на включение
				turn_off_list = list_to_off(url_main)                         #И на выключение

				toogle_light(turn_on_list)                                    #Включить нужное
				toogle_light(turn_off_list)                                   #Отключить ненужное

# else:
# 	while True:
# 		check = input('Выставьте положение света: 1 - включено, 2 - выключено: \n')
# 		if check == '1':
# 			turn_on_list = list_to_on(url_main, list_of_lights_to_on)  # Сформировать команды для каналов на включение
# 			turn_off_list = list_to_off(url_main)  # И на выключение
#
# 			toogle_light(turn_on_list)  # Включить нужное
# 			toogle_light(turn_off_list)
# 		elif check == '2':
# 			turn_off_all_list = list_to_off_all(url_main, list_of_all_channels)  # Сформировать команды для выключения всех каналов
# 			toogle_light(turn_off_all_list)