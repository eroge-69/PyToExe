import requests

# Укажите список URL API и названий каналов
api_data = [
    ("https://rutube.ru/api/play/options/c58f502c7bb34a8fcdd976b221fca292/", "Первый канал HD"),
    ("https://rutube.ru/api/play/options/c37cd74192c6bc3d6cd6077c0c4fd686/", "НТВ HD"),
    ("https://rutube.ru/api/play/options/546602986e6a424d74d594876ddb3f04/", "ТНТ HD"),
    ("https://rutube.ru/api/play/options/c801a7087e29a097192d74c270fbc6c1/", "ТНТ-4 HD"),
    ("https://rutube.ru/api/play/options/7bf12d9c050f9a7ef3728db5730432ae/", "ТВ-3 HD"),
    ("https://rutube.ru/api/play/options/9f87a9a0cecbe773be6fddcbd93585ac/", "Пятница! HD"),
    ("https://rutube.ru/api/play/options/310744c10a5809da38aa445c952976da/", "Суббота! HD"),
    ("https://rutube.ru/api/play/options/9ae8e8a6dc58bdad66190475f9872ecd/", "Rutube TV HD"),
    ("https://rutube.ru/api/play/options/c9b87c0b00cfff9b37f95b9c8e4eed42/", "Соловьёв Live HD"),
    ("https://rutube.ru/api/play/options/11bbbec75a2ceb8cf446ad16813c6eec/", "Матч! ТВ HD"),
    ("https://rutube.ru/api/play/options/df6fe73494a26f74da51573fd97b9baa/", "Муз-ТВ HD"),
    ("https://rutube.ru/api/play/options/5c9327074e25ca86f3111d4085cbbb65/", "Ю-ТВ HD"),
    ("https://rutube.ru/api/play/options/faa934385b83f9e8a92f5484defae5fa/", "ОТР HD"),
    ("https://rutube.ru/api/play/options/5ab908fccfac5bb43ef2b1e4182256b0/", "Звезда HD"),
    ("https://rutube.ru/api/play/options/afef67d151b5a607dee1ef0aa299a52c/", "Мир HD"),
    ("https://rutube.ru/api/play/options/43269ba8fb179e298b1e497f557e8d2d/", "Мир 24 HD"),
    ("https://rutube.ru/api/play/options/88f6485ee28d56daf13302ac6fe3d931/", "РБК HD"),
    ("https://rutube.ru/api/play/options/1f550a23c44ec7f287324b0b3e4f5a29/", "ОСН HD"),
    ("https://rutube.ru/api/play/options/07beff61e617797db550cc3a5f6ad92b/", "Телеканал 360° HD"),
    ("https://rutube.ru/api/play/options/d14fcf59cb7d07a26c48ebc8c6565f44/", "360° Новости HD"),
    ("https://rutube.ru/api/play/options/f6a6d5c955180d0d0f80c66d0b6150d3/", "Вместе-РФ HD"),
    ("https://rutube.ru/api/play/options/80b308e455f2aceb498e5dccd58ca050/", "Союз HD"),
    ("https://rutube.ru/api/play/options/392b4686b770bae2da6bf5ac4574add5/", "2х2 HD"),
    ("https://rutube.ru/api/play/options/2f052691c75d72b3ed7f3c33ea956a41/", "Смайл ТВ HD"),
    ("https://rutube.ru/api/play/options/66710e44c6f796f0b754794ca2585229/", "Вселенная мультфильмов HD"),
    ("https://rutube.ru/api/play/options/2b06a5c4c688fdc05014acb4cba83de0/", "Moonbug Kids TV HD (eng)"),
    ("https://rutube.ru/api/play/options/0e9e44725d5d5ab7ee92c10b40215419/", "Mr.Bean Cartoon HD (eng)"),
    ("https://rutube.ru/api/play/options/1da5d92af8c55b16241f1eb12a27f00c/", "Охотник и рыболов Int HD"),
    ("https://rutube.ru/api/play/options/406973c72e9d0449feef05ef7811ad01/", "Загородный Int HD"),
    ("https://rutube.ru/api/play/options/5a294ae1ed12c44c7053301fb5fa9ba0/", "ТНТ Music HD"),
    ("https://rutube.ru/api/play/options/f712ae5ff3db23ec09b3674133d44daa/", "VIVA Russia HD"),
    ("https://rutube.ru/api/play/options/965a025e4ebbaf0957415f80c6de8534/", "Музыка Мода ТВ HD"),
    ("https://rutube.ru/api/play/options/ee6a3d5ba98066c2aaace3c428a3170c/", "World Fashion Channel HD"),
    ("https://rutube.ru/api/play/options/47fdffd6ab82bbab0a19039d7018839f/", "Deluxe Dance HD"),
    ("https://rutube.ru/api/play/options/09e51eefa939595a4ac67182c6fb3e4e/", "Кино и Жизнь HD"),
    ("https://rutube.ru/api/play/options/23c568b69e0eada33560850484223739/", "Кинолента 24 HD"),
    ("https://rutube.ru/api/play/options/3b7d1499da9396462bfd17282d758d30/", "Кинолаффка HD"),
    ("https://rutube.ru/api/play/options/4965b7b928c4a143d708ab424be01d37/", "Киножелезо HD"),
    ("https://rutube.ru/api/play/options/dcc02ed1ff97923541c6d4c030c54c65/", "Comedy Hub HD"),
    ("https://rutube.ru/api/play/options/348ebaac61a382f2028e9a1b06f4f2b6/", "Твой 2007 HD"),
    ("https://rutube.ru/api/play/options/99d4597cea881a27cf7dd6e65a74dade/", "Плюс Минус 16 HD")
]

try:
    # Создание текстового файла с плейлистом
    with open('Rutube_TV.m3u8', 'w') as f:
        f.write("#EXTM3U\n")  # Заголовок плейлиста

        # Обработка каждого URL API
        for api_url, channel_name in api_data:
            try:
                response = requests.get(api_url)
                response.raise_for_status()  # Проверка на ошибки
                data = response.json()
                hls_streams = data.get('live_streams', {}).get('hls', [])

                if hls_streams:
                    for stream in hls_streams:
                        stream_url = stream.get('url')
                        print(f"Актуальная ссылка: {stream_url}")
                        f.write(f"#EXTINF:-1,{channel_name}\n")
                        f.write(f"{stream_url}\n")
                else:
                    print(f"Потоки не найдены для {api_url}.")
            except requests.RequestException as inner_e:
                print(f"Ошибка с {api_url}: {inner_e}")  # Пропускаем ссылку

    print("Плейлист создан: Rutube_TV.m3u8")
except Exception as e:
    print(f"Произошла ошибка: {e}")

