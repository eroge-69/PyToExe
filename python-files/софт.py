links_list = input('Введите ссылки: ').split()
print()
print('Кол-во изначальных ссылок:', len(links_list))
print('Кол-во текущих ссылок:', len(set(links_list)))
for link in set(links_list):
  print(link)