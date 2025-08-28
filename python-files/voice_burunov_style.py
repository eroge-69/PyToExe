# voice_burunov_style.py
# Генерация MP3 с выразительной русской озвучкой "в стиле Бурунова" (ирония, паузы, акценты)
# Требуется: pip install edge-tts
#
# Запуск:
#   python voice_burunov_style.py
#
# Результат: ozvuchka_burunov_style.mp3

import asyncio
import edge_tts

VOICE = "ru-RU-DmitryNeural"  # можно попробовать также "ru-RU-SergeiNeural"

# Исходный текст пользователя (сохранён как есть)
RAW_TEXT = """
Награда состоит в том, что мы покажем ваш канал в рекомендациях, если ваши зрители поставят лайк и коммент. Но перед этим мне кое-что нужно уточнить, во благо больших просмотров, месье. Вы укрываете уцелевшие остатки мозга после создания первой части мишка, ведь так? 

Вы прячите их под полом кухни?

Покажите мне где они прячятся? 

Они слышали разговор, но нет никакой возни, значит им сильно досталось от ютуб деятельности.

Я буду говорить медлено, чтобы они показались нам и мы приняли все меры.

Месье мишка! Спасибо за молоко и гостеприимство, полагаю с делами покончено

А милые индусы с модерации, спасибо что защищаете авторские права бедных лейблов

Мы больше не побеспокоим вас мишка

Месье индусы, я прощаюсь с вами и говорю адьес!

Ну наконец то вторая часть!
"""

# SSML: добавлены паузы, акценты и слегка "театральная" подача под пародийный стиль
SSML = f"""
<speak version="1.0" xml:lang="ru-RU">
  <voice name="{VOICE}">
    <prosody rate="medium" pitch="-2st">
      Награда состоит в том, что мы <emphasis level="moderate">покажем ваш канал</emphasis> в рекомендациях,
      если ваши зрители поставят <emphasis level="strong">лайк</emphasis> и <emphasis level="strong">коммент</emphasis>.
      <break time="600ms"/>
      Но перед этим мне кое-что нужно уточнить — <emphasis level="reduced">во благо больших просмотров</emphasis>, месье.
      <break time="700ms"/>
      Вы укрываете уцелевшие остатки мозга после создания <emphasis level="strong">первой части</emphasis> — мишка, ведь так?
      <break time="800ms"/>

      Вы прячите их под полом кухни?
      <break time="600ms"/>

      Покажите мне, <emphasis level="moderate">где они прячятся</emphasis>?
      <break time="700ms"/>

      Они слышали разговор, но <emphasis level="reduced">нет никакой возни</emphasis>,
      значит им сильно досталось от ютуб деятельности.
      <break time="800ms"/>

      Я буду говорить <emphasis level="strong">медлено</emphasis>,
      чтобы они показались нам и мы приняли все меры.
      <break time="900ms"/>

      Месье мишка! Спасибо за молоко и гостеприимство, полагаю — с делами покончено.
      <break time="700ms"/>

      А милые индусы с модерации — спасибо, что защищаете <emphasis level="moderate">авторские права бедных лейблов</emphasis>.
      <break time="700ms"/>

      Мы больше не побеспокоим вас, мишка.
      <break time="600ms"/>

      Месье индусы — я прощаюсь с вами и говорю: <emphasis level="strong">адьес!</emphasis>
      <break time="900ms"/>

      <emphasis level="strong">Ну наконец то — вторая часть!</emphasis>
    </prosody>
  </voice>
</speak>
"""

OUTPUT_FILE = "ozvuchka_burunov_style.mp3"

async def main():
    communicate = edge_tts.Communicate(ssml=SSML, voice=VOICE)
    await communicate.save(OUTPUT_FILE)
    print(f"Готово! Файл сохранён: {OUTPUT_FILE}")

if __name__ == "__main__":
    asyncio.run(main())
