Создание полнофункционального веб-приложения, способного генерировать музыку и сохранять её в аудио- и MIDI-файлах, — довольно сложная задача, требующая глубоких знаний в области веб-разработки. Я предложу вам базовый пример веб-приложения, использующего JavaScript, HTML и библиотеку Tone.js для создания и воспроизведения музыки. Мы также создадим возможность экспорта MIDI-файлов с помощью библиотеки @tonejs/midi.

Пример кода простого музыкального генератора
1. Настройка окружения

Создайте структуру вашего проекта:

открытый текст
music-generator/
│
├── index.html
├── style.css
└── script.js
2. index.html
HTML
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Музыкальный Генератор</title>
    <link rel="stylesheet" href="style.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/tone/14.8.37/Tone.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@tonejs/midi@2.0.13"></script>
</head>
<body>
    <h1>Музыкальный Генератор</h1>
    <div>
        <button id="generate">Сгенерировать музыку</button>
        <button id="save-midi">Сохранить MIDI</button>
        <button id="save-audio">Сохранить Аудио</button>
    </div>
    <p id="status"></p>
    
    <script src="script.js"></script>
</body>
</html>
3. style.css
css
body {
    font-family: Arial, sans-serif;
    background-color: #f9f9f9;
    text-align: center;
    padding: 50px;
}

button {
    margin: 10px;
    padding: 10px 20px;
    font-size: 16px;
    cursor: pointer;
}
4. script.js
javascript
let melody = [];
let synth = new Tone.Synth().toDestination();

// Функция для генерации мелодии
function generateMelody() {
    melody = [];
    for (let i = 0; i < 8; i++) {
        const note = Tone.Frequency(Math.random() * 12 + 60, "midi").toNote(); // Генерация ноты
        melody.push(note);
    }
}

// Функция для воспроизведения мелодии
function playMelody() {
    const now = Tone.now();
    melody.forEach((note, index) => {
        synth.triggerAttackRelease(note, 0.5, now + index * 0.5);
    });
}

// Функция для сохранения MIDI
function saveMidi() {
    const midi = new Midi();
    const track = midi.addTrack();

    melody.forEach((note, index) => {
        track.addNote({
            midi: Tone.Frequency(note).toMidi(),
            time: index * 0.5,
            duration: 0.5,
        });
    });

    const midiBlob = new Blob([midi.toArray()], { type: 'audio/midi' });
    const url = URL.createObjectURL(midiBlob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'melody.mid';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a); // чистим
}

// Функция для сохранения аудио
async function saveAudio() {
    const now = Tone.now();
    const track = new Tone.Buffer();
    await track.load('path/to/use/audio'); // Здесь вы указываете путь к вашему аудио файлу

    const recorder = new Tone.Recorder();
    Tone.start();
    recorder.start();

    playMelody();

    recorder.stop().then((recording) => {
        const url = URL.createObjectURL(recording);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'recording.wav';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    });
}

// События для кнопок
document.getElementById('generate').addEventListener('click', () => {
    generateMelody();
    playMelody();
    document.getElementById('status').innerText = "Music generated!";
});

document.getElementById('save-midi').addEventListener('click', saveMidi);
document.getElementById('save-audio').addEventListener('click', saveAudio);
Объяснение кода

HTML: Создаёт интерфейс с кнопками для создания музыки и сохранения в формате MIDI и аудио.

CSS: простейшая стилизация для улучшения внешнего вида интерфейса.

JavaScript:

Tone.js используется для генерации звуков.

@tonejs/midi используется для создания и сохранения MIDI-файлов.

Код включает в себя функции для генерации мелодии, её воспроизведения и сохранения в различных форматах.

Заметка

Вы можете изменить пути к аудиофайлам в функции saveAudio по своему усмотрению или использовать другие методы записи.

Этот код является базовым примером. Для полноценного приложения вам потребуется учесть множество других аспектов, таких как обработка ошибок, более сложное взаимодействие с пользователем и, возможно, хранение данных на сервере.

Если у вас есть вопросы или вам нужно что-то конкретное, дайте знать!
