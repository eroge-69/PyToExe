Python 3.13.3 (tags/v3.13.3:6280bb5, Apr  8 2025, 14:47:33) [MSC v.1943 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <title>Snake azul con fondo verde</title>
  <style>
    :root {
      --cell: 20px;
      --cols: 30;
      --rows: 25;
    }

    body {
      margin: 0;
      height: 100vh;
      background: #000;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: flex-start;
      font-family: monospace;
      color: white;
    }

    #score-container {
      background: white;
      color: black;
      width: calc(var(--cols) * var(--cell));
      display: flex;
      justify-content: space-between;
      padding: 6px 12px;
      box-sizing: border-box;
      font-size: 18px;
    }

    #game {
      position: relative;
      width: calc(var(--cols) * var(--cell));
      height: calc(var(--rows) * var(--cell));
      display: grid;
      grid-template-columns: repeat(var(--cols), var(--cell));
      grid-template-rows: repeat(var(--rows), var(--cell));
    }

    .cell {
      width: var(--cell);
      height: var(--cell);
    }

    .cell-green-1 {
      background: #0a0;
    }

    .cell-green-2 {
      background: #0f0;
    }

    .pixel {
      position: absolute;
      width: var(--cell);
      height: var(--cell);
    }

    .snake-head {
      background-color: #0050cc;
    }

    .snake-body {
      background-color: #0074FF;
    }

    .food {
      background-color: red;
    }

    #score, #highscore {
      color: black;
    }

    #overlay {
      position: absolute;
      inset: 0;
      background: rgba(0,0,0,0.65);
      color: white;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      font-size: 24px;
      gap: 12px;
      text-align: center;
      z-index: 2;
    }

    button {
      padding: 6px 14px;
      font-size: 18px;
      background: #0f0;
      border: none;
      border-radius: 4px;
      cursor: pointer;
    }
  </style>
</head>
<body>
  <div id="score-container">
    <div id="score">Puntuación: 0</div>
    <div id="highscore">Máxima: 0</div>
  </div>

  <div id="game">
    <div id="overlay">
      <div>Pulsa <b>Espacio</b> para empezar</div>
      <div style="font-size:14px">Flechas o WASD para moverte · Enter reinicia</div>
    </div>
  </div>

  <script>
    const CELL = 20;
    const COLS = 30;
    const ROWS = 25;
    const TICK = 100;

    let snake, dir, nextDir, food, score, highscore = 0, playing, loopId;

    const board = document.getElementById('game');
    const scoreEl = document.getElementById('score');
    const highscoreEl = document.getElementById('highscore');
    const overlay = document.getElementById('overlay');

    function createGridBackground() {
      for (let y = 0; y < ROWS; y++) {
        for (let x = 0; x < COLS; x++) {
          const cell = document.createElement('div');
          cell.className = 'cell ' + ((x + y) % 2 === 0 ? 'cell-green-1' : 'cell-green-2');
          board.appendChild(cell);
        }
      }
    }

    const xyToPos = (x, y) => y * COLS + x;
    const posToXY = pos => [pos % COLS, Math.floor(pos / COLS)];

    function drawPixel(cls, pos) {
      const [x, y] = posToXY(pos);
      const div = document.createElement('div');
      div.className = `pixel ${cls}`;
      div.style.left = x * CELL + 'px';
      div.style.top = y * CELL + 'px';
      board.appendChild(div);
    }

    function resetGame() {
      board.querySelectorAll('.pixel').forEach(p => p.remove());

      const startX = Math.floor(COLS / 2);
      const startY = Math.floor(ROWS / 2);
      const head = xyToPos(startX, startY);
      const mid  = xyToPos(startX - 1, startY);
      const tail = xyToPos(startX - 2, startY);

      snake = [head, mid, tail];
      dir = 1;
      nextDir = dir;
      food = spawnFood();
      score = 0;
      updateScore();
      playing = true;
      overlay.style.display = 'none';
      if (loopId) cancelAnimationFrame(loopId);
      loopId = requestAnimationFrame(gameLoop);
    }

    function spawnFood() {
      let pos;
      do {
        pos = Math.floor(Math.random() * COLS * ROWS);
      } while (snake.includes(pos));
      drawPixel('food', pos);
      return pos;
    }

    let last = 0;
    function gameLoop(timestamp) {
      if (!playing) return;
      if (timestamp - last > TICK) {
        last = timestamp;
        step();
      }
      loopId = requestAnimationFrame(gameLoop);
    }

    function step() {
      dir = nextDir;
      const head = snake[0];
      const [hx, hy] = posToXY(head);
      let nx = hx, ny = hy;
      if (dir === 1) nx++;
      if (dir === -1) nx--;
      if (dir === COLS) ny++;
      if (dir === -COLS) ny--;

      if (nx < 0 || nx >= COLS || ny < 0 || ny >= ROWS) return gameOver();

      const nextPos = xyToPos(nx, ny);
      if (snake.includes(nextPos)) return gameOver();

      snake.unshift(nextPos);
      if (nextPos === food) {
        score += 10;
        updateScore();
        food = spawnFood();
      } else {
        snake.pop();
      }

      redraw();
    }

    function redraw() {
      board.querySelectorAll('.pixel').forEach(p => p.remove());
      drawPixel('food', food);
      if (snake.length > 0) drawPixel('snake-head', snake[0]);
      for (let i = 1; i < snake.length; i++) drawPixel('snake-body', snake[i]);
    }
... 
...     function updateScore() {
...       scoreEl.textContent = `Puntuación: ${score}`;
...       if (score > highscore) {
...         highscore = score;
...         highscoreEl.textContent = `Máxima: ${highscore}`;
...       }
...     }
... 
...     function gameOver() {
...       playing = false;
...       overlay.innerHTML = `<div>GAME OVER</div><div>Puntuación: ${score}</div><button>Reiniciar (Enter)</button>`;
...       overlay.style.display = 'flex';
...     }
... 
...     window.addEventListener('keydown', e => {
...       const key = e.key.toLowerCase();
...       if (!playing && key === ' ') return resetGame();
...       if (!playing && key === 'enter') return resetGame();
...       if (!playing) return;
...       if (key === 'enter') return resetGame();
...       const dirMap = {
...         arrowup: -COLS, w: -COLS,
...         arrowdown: COLS, s: COLS,
...         arrowleft: -1, a: -1,
...         arrowright: 1, d: 1
...       };
...       if (dirMap[key] !== undefined) {
...         const newDir = dirMap[key];
...         if (newDir !== -dir) nextDir = newDir;
...       }
...     });
... 
...     createGridBackground();
...     overlay.querySelector('button')?.addEventListener('click', resetGame);
...   </script>
... </body>
... </html>
