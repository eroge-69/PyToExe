import sys
import os
import tempfile
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Wednors Таблицы</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', 'Roboto', sans-serif;
        }
        
        body {
            background: linear-gradient(135deg, #1a2a6c, #b21f1f, #fdbb2d);
            color: #333;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            overflow: hidden;
            display: flex;
            flex-direction: column;
            height: calc(100vh - 40px);
        }
        
        .header {
            background: linear-gradient(to right, #2c3e50, #4ca1af);
            color: white;
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #ddd;
        }
        
        .logo {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .logo-icon {
            font-size: 28px;
            font-weight: bold;
            color: #ffdd40;
        }
        
        .logo-text {
            font-size: 24px;
            font-weight: 700;
        }
        
        .toolbar {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        
        .toolbar button {
            background: linear-gradient(to bottom, #f6f8f9, #e5ebee);
            border: 1px solid #cad1d7;
            border-radius: 6px;
            padding: 8px 15px;
            color: #2c3e50;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            gap: 5px;
        }
        
        .toolbar button:hover {
            background: linear-gradient(to bottom, #e5ebee, #dde3e8);
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        }
        
        .toolbar button:active {
            transform: translateY(1px);
        }
        
        .toolbar button i {
            font-size: 16px;
        }
        
        .formula-bar {
            display: flex;
            align-items: center;
            padding: 8px 15px;
            background: #eef2f5;
            border-bottom: 1px solid #ddd;
            gap: 10px;
        }
        
        .cell-reference {
            min-width: 80px;
            padding: 8px;
            background: white;
            border: 1px solid #cad1d7;
            border-radius: 4px;
            font-weight: 600;
            text-align: center;
        }
        
        .formula-input {
            flex: 1;
            padding: 8px 12px;
            border: 1px solid #cad1d7;
            border-radius: 4px;
            font-family: 'Consolas', monospace;
        }
        
        .spreadsheet-container {
            display: flex;
            flex: 1;
            overflow: hidden;
        }
        
        .row-headers {
            background: #f1f5f8;
            overflow: hidden;
            border-right: 1px solid #ddd;
        }
        
        .row-header {
            width: 45px;
            height: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            color: #2c3e50;
            border-bottom: 1px solid #ddd;
            user-select: none;
        }
        
        .column-headers {
            display: flex;
            background: #f1f5f8;
            border-bottom: 1px solid #ddd;
        }
        
        .column-header {
            width: 100px;
            height: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            color: #2c3e50;
            border-right: 1px solid #ddd;
            user-select: none;
        }
        
        .corner-cell {
            width: 45px;
            min-width: 45px;
            height: 30px;
            background: #e3e8ed;
            border-right: 1px solid #ddd;
            border-bottom: 1px solid #ddd;
        }
        
        .table-content {
            flex: 1;
            overflow: auto;
            position: relative;
        }
        
        .spreadsheet {
            border-collapse: collapse;
            table-layout: fixed;
        }
        
        .spreadsheet td {
            border: 1px solid #ddd;
            min-width: 100px;
            height: 30px;
            padding: 5px;
            position: relative;
            transition: background-color 0.2s;
        }
        
        .spreadsheet td:focus {
            outline: 2px solid #4ca1af;
            outline-offset: -2px;
            z-index: 2;
        }
        
        .spreadsheet td.selected {
            background-color: #e6f7ff;
        }
        
        .status-bar {
            background: linear-gradient(to right, #2c3e50, #4ca1af);
            color: white;
            padding: 8px 15px;
            display: flex;
            justify-content: space-between;
            font-size: 14px;
        }
        
        .theme-selector {
            display: flex;
            gap: 5px;
        }
        
        .theme-btn {
            width: 20px;
            height: 20px;
            border-radius: 50%;
            border: 2px solid white;
            cursor: pointer;
        }
        
        .theme-blue { background: linear-gradient(135deg, #1a2a6c, #4ca1af); }
        .theme-green { background: linear-gradient(135deg, #004d40, #66bb6a); }
        .theme-purple { background: linear-gradient(135deg, #4a148c, #9c27b0); }
        .theme-dark { background: linear-gradient(135deg, #263238, #546e7a); }
        
        .cell-format-toolbar {
            display: flex;
            padding: 8px 15px;
            background: #eef2f5;
            border-bottom: 1px solid #ddd;
            gap: 10px;
            flex-wrap: wrap;
        }
        
        .format-btn {
            background: white;
            border: 1px solid #cad1d7;
            border-radius: 4px;
            padding: 5px 10px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 5px;
        }
        
        .format-btn:hover {
            background: #f1f5f8;
        }
        
        .zoom-controls {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-left: auto;
        }
        
        .zoom-btn {
            background: white;
            border: 1px solid #cad1d7;
            border-radius: 4px;
            width: 30px;
            height: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            font-weight: bold;
        }
        
        .zoom-value {
            font-weight: 600;
            min-width: 40px;
            text-align: center;
        }
        
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            z-index: 100;
            align-items: center;
            justify-content: center;
        }
        
        .modal-content {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
            width: 400px;
            max-width: 90%;
        }
        
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid #eee;
        }
        
        .modal-title {
            font-size: 18px;
            font-weight: 600;
        }
        
        .close-modal {
            background: none;
            border: none;
            font-size: 20px;
            cursor: pointer;
            color: #777;
        }
        
        .modal-body {
            margin-bottom: 15px;
        }
        
        .modal-footer {
            display: flex;
            justify-content: flex-end;
            gap: 10px;
        }
        
        .btn {
            padding: 8px 16px;
            border-radius: 4px;
            border: 1px solid #cad1d7;
            cursor: pointer;
            font-weight: 600;
        }
        
        .btn-primary {
            background: linear-gradient(to bottom, #4ca1af, #2c3e50);
            color: white;
        }
        
        .form-group {
            margin-bottom: 15px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: 600;
        }
        
        .form-control {
            width: 100%;
            padding: 8px 12px;
            border: 1px solid #cad1d7;
            border-radius: 4px;
        }
        
        .color-preview {
            width: 30px;
            height: 30px;
            border: 1px solid #ccc;
            border-radius: 4px;
        }
        
        .font-preview {
            padding: 8px;
            border: 1px solid #cad1d7;
            border-radius: 4px;
            height: 40px;
            display: flex;
            align-items: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">
                <div class="logo-icon">W</div>
                <div class="logo-text">Wednors Таблицы</div>
            </div>
            <div class="toolbar">
                <button id="newFile"><i>📄</i> Новый</button>
                <button id="openFile"><i>📂</i> Открыть</button>
                <button id="saveFile"><i>💾</i> Сохранить</button>
                <button id="addRow"><i>⬇️</i> Добавить строку</button>
                <button id="addColumn"><i>➡️</i> Добавить столбец</button>
                <button id="exportBtn"><i>📊</i> Экспорт</button>
                <button id="printBtn"><i>🖨️</i> Печать</button>
            </div>
        </div>
        
        <div class="cell-format-toolbar">
            <div class="format-btn" data-format="bold"><i>B</i></div>
            <div class="format-btn" data-format="italic"><i>I</i></div>
            <div class="format-btn" data-format="underline"><i>U</i></div>
            <div class="format-btn" data-format="alignLeft"><i> 左</i></div>
            <div class="format-btn" data-format="alignCenter"><i> 中</i></div>
            <div class="format-btn" data-format="alignRight"><i> 右</i></div>
            <div class="format-btn" id="cellColor"><i>🎨</i></div>
            <div class="format-btn" id="fontSize"><i>A</i> Размер</div>
            
            <div class="zoom-controls">
                <div class="zoom-btn" id="zoomOut">-</div>
                <div class="zoom-value" id="zoomValue">100%</div>
                <div class="zoom-btn" id="zoomIn">+</div>
            </div>
        </div>
        
        <div class="formula-bar">
            <div class="cell-reference" id="activeCell">A1</div>
            <input type="text" class="formula-input" id="formulaInput" placeholder="Введите формулу или значение">
        </div>
        
        <div class="spreadsheet-container">
            <div class="row-headers" id="rowHeaders"></div>
            <div class="table-content">
                <div class="column-headers" id="columnHeaders">
                    <div class="corner-cell"></div>
                </div>
                <table class="spreadsheet" id="spreadsheet"></table>
            </div>
        </div>
        
        <div class="status-bar">
            <div id="cellInfo">Готово</div>
            <div class="theme-selector">
                <div class="theme-btn theme-blue" data-theme="blue"></div>
                <div class="theme-btn theme-green" data-theme="green"></div>
                <div class="theme-btn theme-purple" data-theme="purple"></div>
                <div class="theme-btn theme-dark" data-theme="dark"></div>
            </div>
        </div>
    </div>

    <div class="modal" id="formatModal">
        <div class="modal-content">
            <div class="modal-header">
                <div class="modal-title">Формат ячеек</div>
                <button class="close-modal">&times;</button>
            </div>
            <div class="modal-body">
                <div class="form-group">
                    <label>Цвет фона</label>
                    <input type="color" class="form-control" id="bgColorPicker" value="#ffffff">
                </div>
                <div class="form-group">
                    <label>Цвет текста</label>
                    <input type="color" class="form-control" id="textColorPicker" value="#000000">
                </div>
                <div class="form-group">
                    <label>Размер шрифта</label>
                    <select class="form-control" id="fontSizeSelect">
                        <option value="12">12px</option>
                        <option value="14" selected>14px</option>
                        <option value="16">16px</option>
                        <option value="18">18px</option>
                        <option value="20">20px</option>
                        <option value="24">24px</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Пример текста</label>
                    <div class="font-preview" id="fontPreview">
                        Пример текста
                    </div>
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn" id="cancelFormat">Отмена</button>
                <button class="btn btn-primary" id="applyFormat">Применить</button>
            </div>
        </div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const spreadsheet = document.getElementById('spreadsheet');
            const rowHeaders = document.getElementById('rowHeaders');
            const columnHeaders = document.getElementById('columnHeaders');
            const activeCellRef = document.getElementById('activeCell');
            const formulaInput = document.getElementById('formulaInput');
            const cellInfo = document.getElementById('cellInfo');
            const zoomValue = document.getElementById('zoomValue');
            const formatModal = document.getElementById('formatModal');
            
            let rows = 30;
            let cols = 15;
            let activeCell = null;
            let zoomLevel = 100;
            let cellData = {};
            let currentTheme = 'blue';
            
            function initSpreadsheet() {
                createColumnHeaders();
                createRowHeaders();
                createGrid();
                setupEventListeners();
                updateZoom();
            }
            
            function createColumnHeaders() {
                columnHeaders.innerHTML = '';
                const cornerCell = document.createElement('div');
                cornerCell.className = 'corner-cell';
                columnHeaders.appendChild(cornerCell);
                
                for (let i = 0; i < cols; i++) {
                    const colHeader = document.createElement('div');
                    colHeader.className = 'column-header';
                    colHeader.textContent = numberToColumnLetter(i);
                    columnHeaders.appendChild(colHeader);
                }
            }
            
            function createRowHeaders() {
                rowHeaders.innerHTML = '';
                for (let i = 1; i <= rows; i++) {
                    const rowHeader = document.createElement('div');
                    rowHeader.className = 'row-header';
                    rowHeader.textContent = i;
                    rowHeaders.appendChild(rowHeader);
                }
            }
            
            function createGrid() {
                spreadsheet.innerHTML = '';
                for (let i = 1; i <= rows; i++) {
                    const row = document.createElement('tr');
                    for (let j = 0; j < cols; j++) {
                        const cell = document.createElement('td');
                        cell.dataset.row = i;
                        cell.dataset.col = j;
                        cell.contentEditable = true;
                        cell.addEventListener('focus', () => setActiveCell(cell));
                        cell.addEventListener('blur', () => saveCellValue(cell));
                        cell.addEventListener('input', () => updateFormulaInput(cell));
                        
                        const cellId = `${numberToColumnLetter(j)}${i}`;
                        if (cellData[cellId]) {
                            cell.innerHTML = cellData[cellId].value || '';
                            if (cellData[cellId].style) {
                                Object.assign(cell.style, cellData[cellId].style);
                            }
                        }
                        
                        row.appendChild(cell);
                    }
                    spreadsheet.appendChild(row);
                }
            }
            
            function setActiveCell(cell) {
                if (activeCell) {
                    activeCell.classList.remove('selected');
                }
                
                activeCell = cell;
                activeCell.classList.add('selected');
                
                const colLetter = numberToColumnLetter(parseInt(cell.dataset.col));
                const rowNum = cell.dataset.row;
                const cellId = `${colLetter}${rowNum}`;
                
                activeCellRef.textContent = cellId;
                
                if (cellData[cellId] && cellData[cellId].formula) {
                    formulaInput.value = cellData[cellId].formula;
                } else {
                    formulaInput.value = cell.textContent;
                }
                
                formulaInput.focus();
                cellInfo.textContent = `Ячейка: ${cellId}`;
            }
            
            function saveCellValue(cell) {
                const colLetter = numberToColumnLetter(parseInt(cell.dataset.col));
                const rowNum = cell.dataset.row;
                const cellId = `${colLetter}${rowNum}`;
                
                if (!cellData[cellId]) {
                    cellData[cellId] = {};
                }
                
                cellData[cellId].value = cell.textContent;
                
                if (formulaInput.value.startsWith('=')) {
                    cellData[cellId].formula = formulaInput.value;
                    evaluateFormula(cell, formulaInput.value);
                } else {
                    delete cellData[cellId].formula;
                }
            }
            
            function updateFormulaInput(cell) {
                formulaInput.value = cell.textContent;
            }
            
            function evaluateFormula(cell, formula) {
                try {
                    if (formula.startsWith('=SUM(')) {
                        const range = formula.match(/\((.*?)\)/)[1];
                        const [start, end] = range.split(':');
                        
                        if (start && end) {
                            const sum = calculateSum(start, end);
                            cell.textContent = sum;
                            cellData[`${cell.dataset.col}${cell.dataset.row}`].value = sum;
                        }
                    } else if (formula.startsWith('=AVG(')) {
                        const range = formula.match(/\((.*?)\)/)[1];
                        const [start, end] = range.split(':');
                        
                        if (start && end) {
                            const avg = calculateAverage(start, end);
                            cell.textContent = avg.toFixed(2);
                            cellData[`${cell.dataset.col}${cell.dataset.row}`].value = avg.toFixed(2);
                        }
                    } else if (formula.startsWith('=CONCAT(')) {
                        const range = formula.match(/\((.*?)\)/)[1];
                        const [start, end] = range.split(':');
                        
                        if (start && end) {
                            const concat = concatenateRange(start, end);
                            cell.textContent = concat;
                            cellData[`${cell.dataset.col}${cell.dataset.row}`].value = concat;
                        }
                    } else {
                        const result = eval(formula.substring(1));
                        cell.textContent = result;
                        cellData[`${cell.dataset.col}${cell.dataset.row}`].value = result;
                    }
                } catch (error) {
                    console.error('Ошибка вычисления формулы:', error);
                    cell.textContent = '#ОШИБКА!';
                    cellData[`${cell.dataset.col}${cell.dataset.row}`].value = '#ОШИБКА!';
                }
            }
            
            function calculateSum(start, end) {
                const [startCol, startRow] = parseCellReference(start);
                const [endCol, endRow] = parseCellReference(end);
                
                let sum = 0;
                for (let row = startRow; row <= endRow; row++) {
                    for (let col = startCol; col <= endCol; col++) {
                        const cellId = `${numberToColumnLetter(col)}${row}`;
                        if (cellData[cellId] && cellData[cellId].value) {
                            sum += parseFloat(cellData[cellId].value) || 0;
                        }
                    }
                }
                return sum;
            }
            
            function calculateAverage(start, end) {
                const [startCol, startRow] = parseCellReference(start);
                const [endCol, endRow] = parseCellReference(end);
                
                let sum = 0;
                let count = 0;
                
                for (let row = startRow; row <= endRow; row++) {
                    for (let col = startCol; col <= endCol; col++) {
                        const cellId = `${numberToColumnLetter(col)}${row}`;
                        if (cellData[cellId] && cellData[cellId].value) {
                            sum += parseFloat(cellData[cellId].value) || 0;
                            count++;
                        }
                    }
                }
                
                return count > 0 ? sum / count : 0;
            }
            
            function concatenateRange(start, end) {
                const [startCol, startRow] = parseCellReference(start);
                const [endCol, endRow] = parseCellReference(end);
                
                let result = '';
                for (let row = startRow; row <= endRow; row++) {
                    for (let col = startCol; col <= endCol; col++) {
                        const cellId = `${numberToColumnLetter(col)}${row}`;
                        if (cellData[cellId] && cellData[cellId].value) {
                            result += cellData[cellId].value + ' ';
                        }
                    }
                }
                return result.trim();
            }
            
            function parseCellReference(ref) {
                const colPart = ref.replace(/[0-9]/g, '');
                const rowPart = ref.replace(/[A-Z]/g, '');
                
                const col = columnLetterToNumber(colPart);
                const row = parseInt(rowPart);
                
                return [col, row];
            }
            
            function numberToColumnLetter(num) {
                let letter = '';
                while (num >= 0) {
                    letter = String.fromCharCode(65 + (num % 26)) + letter;
                    num = Math.floor(num / 26) - 1;
                }
                return letter;
            }
            
            function columnLetterToNumber(letters) {
                return letters.split('').reduce((r, a) => r * 26 + parseInt(a, 36) - 9, 0) - 1;
            }
            
            function addRow() {
                rows++;
                createRowHeaders();
                createGrid();
                cellInfo.textContent = `Добавлена строка ${rows}`;
            }
            
            function addColumn() {
                cols++;
                createColumnHeaders();
                createGrid();
                cellInfo.textContent = `Добавлен столбец ${numberToColumnLetter(cols-1)}`;
            }
            
            function updateZoom() {
                zoomValue.textContent = `${zoomLevel}%`;
                spreadsheet.style.transform = `scale(${zoomLevel / 100})`;
                spreadsheet.style.transformOrigin = '0 0';
            }
            
            function setupEventListeners() {
                document.getElementById('addRow').addEventListener('click', addRow);
                document.getElementById('addColumn').addEventListener('click', addColumn);
                
                document.getElementById('zoomIn').addEventListener('click', function() {
                    if (zoomLevel < 150) {
                        zoomLevel += 10;
                        updateZoom();
                    }
                });
                
                document.getElementById('zoomOut').addEventListener('click', function() {
                    if (zoomLevel > 50) {
                        zoomLevel -= 10;
                        updateZoom();
                    }
                });
                
                formulaInput.addEventListener('keydown', function(e) {
                    if (e.key === 'Enter' && activeCell) {
                        activeCell.textContent = formulaInput.value;
                        saveCellValue(activeCell);
                        
                        const nextRow = parseInt(activeCell.dataset.row) + 1;
                        if (nextRow <= rows) {
                            const nextCell = document.querySelector(`td[data-row="${nextRow}"][data-col="${activeCell.dataset.col}"]`);
                            if (nextCell) {
                                nextCell.focus();
                            }
                        }
                        
                        e.preventDefault();
                    }
                });
                
                document.querySelectorAll('.theme-btn').forEach(btn => {
                    btn.addEventListener('click', function() {
                        currentTheme = this.dataset.theme;
                        applyTheme(currentTheme);
                    });
                });
                
                document.getElementById('cellColor').addEventListener('click', function() {
                    formatModal.style.display = 'flex';
                });
                
                document.querySelector('.close-modal').addEventListener('click', function() {
                    formatModal.style.display = 'none';
                });
                
                document.getElementById('cancelFormat').addEventListener('click', function() {
                    formatModal.style.display = 'none';
                });
                
                document.getElementById('applyFormat').addEventListener('click', function() {
                    if (activeCell) {
                        const bgColor = document.getElementById('bgColorPicker').value;
                        const textColor = document.getElementById('textColorPicker').value;
                        const fontSize = document.getElementById('fontSizeSelect').value;
                        
                        activeCell.style.backgroundColor = bgColor;
                        activeCell.style.color = textColor;
                        activeCell.style.fontSize = `${fontSize}px`;
                        
                        const colLetter = numberToColumnLetter(parseInt(activeCell.dataset.col));
                        const rowNum = activeCell.dataset.row;
                        const cellId = `${colLetter}${rowNum}`;
                        
                        if (!cellData[cellId]) {
                            cellData[cellId] = {};
                        }
                        
                        if (!cellData[cellId].style) {
                            cellData[cellId].style = {};
                        }
                        
                        cellData[cellId].style.backgroundColor = bgColor;
                        cellData[cellId].style.color = textColor;
                        cellData[cellId].style.fontSize = `${fontSize}px`;
                        
                        formatModal.style.display = 'none';
                    }
                });
                
                document.getElementById('newFile').addEventListener('click', function() {
                    if (confirm('Создать новую таблицу? Все несохраненные данные будут потеряны.')) {
                        rows = 30;
                        cols = 15;
                        cellData = {};
                        initSpreadsheet();
                        cellInfo.textContent = 'Новая таблица создана';
                    }
                });
                
                document.getElementById('saveFile').addEventListener('click', function() {
                    const dataStr = JSON.stringify(cellData);
                    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
                    
                    const exportFileDefaultName = 'wednors_table.json';
                    
                    const linkElement = document.createElement('a');
                    linkElement.setAttribute('href', dataUri);
                    linkElement.setAttribute('download', exportFileDefaultName);
                    linkElement.click();
                    
                    cellInfo.textContent = 'Таблица сохранена';
                });
                
                document.getElementById('openFile').addEventListener('click', function() {
                    const input = document.createElement('input');
                    input.type = 'file';
                    input.accept = '.json';
                    
                    input.addEventListener('change', function() {
                        const file = this.files[0];
                        if (file) {
                            const reader = new FileReader();
                            reader.onload = function(e) {
                                try {
                                    cellData = JSON.parse(e.target.result);
                                    createGrid();
                                    cellInfo.textContent = 'Таблица загружена';
                                } catch (error) {
                                    alert('Ошибка загрузки файла: неверный формат');
                                }
                            };
                            reader.readAsText(file);
                        }
                    });
                    
                    input.click();
                });
                
                document.getElementById('exportBtn').addEventListener('click', function() {
                    let csvContent = '';
                    
                    for (let j = 0; j < cols; j++) {
                        csvContent += numberToColumnLetter(j) + (j < cols - 1 ? ',' : '\r\n');
                    }
                    
                    for (let i = 1; i <= rows; i++) {
                        let rowContent = '';
                        for (let j = 0; j < cols; j++) {
                            const cellId = `${numberToColumnLetter(j)}${i}`;
                            rowContent += (cellData[cellId]?.value || '') + (j < cols - 1 ? ',' : '');
                        }
                        csvContent += rowContent + '\r\n';
                    }
                    
                    const encodedUri = encodeURI('data:text/csv;charset=utf-8,' + csvContent);
                    const link = document.createElement('a');
                    link.setAttribute('href', encodedUri);
                    link.setAttribute('download', 'wednors_table.csv');
                    document.body.appendChild(link);
                    
                    link.click();
                    document.body.removeChild(link);
                    
                    cellInfo.textContent = 'Таблица экспортирована в CSV';
                });
                
                document.getElementById('printBtn').addEventListener('click', function() {
                    window.print();
                });
                
                document.addEventListener('keydown', function(e) {
                    if (e.ctrlKey || e.metaKey) {
                        switch(e.key) {
                            case 'n':
                                e.preventDefault();
                                document.getElementById('newFile').click();
                                break;
                            case 's':
                                e.preventDefault();
                                document.getElementById('saveFile').click();
                                break;
                            case 'o':
                                e.preventDefault();
                                document.getElementById('openFile').click();
                                break;
                        }
                    }
                });
            }
            
            function applyTheme(theme) {
                const header = document.querySelector('.header');
                const statusBar = document.querySelector('.status-bar');
                
                switch(theme) {
                    case 'blue':
                        header.style.background = 'linear-gradient(to right, #2c3e50, #4ca1af)';
                        statusBar.style.background = 'linear-gradient(to right, #2c3e50, #4ca1af)';
                        break;
                    case 'green':
                        header.style.background = 'linear-gradient(to right, #004d40, #66bb6a)';
                        statusBar.style.background = 'linear-gradient(to right, #004d40, #66bb6a)';
                        break;
                    case 'purple':
                        header.style.background = 'linear-gradient(to right, #4a148c, #9c27b0)';
                        statusBar.style.background = 'linear-gradient(to right, #4a148c, #9c27b0)';
                        break;
                    case 'dark':
                        header.style.background = 'linear-gradient(to right, #263238, #546e7a)';
                        statusBar.style.background = 'linear-gradient(to right, #263238, #546e7a)';
                        break;
                }
                
                cellInfo.textContent = `Тема изменена: ${theme}`;
            }
            
            initSpreadsheet();
        });
    </script>
</body>
</html>
"""

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Wednors Таблицы")
        self.setGeometry(100, 100, 1200, 800)
        
        self.browser = QWebEngineView()
        
        # Create temporary HTML file
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False)
        self.temp_file.write(HTML_CONTENT)
        self.temp_file.close()
        
        # Load the HTML content
        self.browser.load(QUrl.fromLocalFile(self.temp_file.name))
        
        self.setCentralWidget(self.browser)
        
    def closeEvent(self, event):
        # Clean up the temporary file
        os.unlink(self.temp_file.name)
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("Wednors Таблицы")
    app.setOrganizationName("Wednors")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())