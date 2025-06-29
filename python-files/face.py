import sys
import numpy as np
import sounddevice as sd
import noisereduce as nr
from PyQt5 import QtCore, QtGui, QtWidgets

class JanelaFacecam(QtWidgets.QWidget):
    sinalVolume = QtCore.pyqtSignal(bool)
    sinalNivelAudio = QtCore.pyqtSignal(float)  # Sinal para o nível de áudio

    def __init__(self, indiceDispositivo=None, taxaAmostragem=None, limiar=None,
                 delayMs=200, fadeDurationMs=150, fatorCalibracao=1.5, duracaoPuloMs=300):
        super().__init__()
        # Parâmetros de áudio e fade
        self.debug = False  # Ajustar para True se quiser ver prints de debug
        self.fatorCalibracao = fatorCalibracao
        self.limiar = limiar  # se None, será calibrado
        self.delayMs = delayMs
        self.fadeDurationMs = fadeDurationMs
        self.duracaoPuloMs = duracaoPuloMs  # duração total do pulinho em ms
        self.isActive = False

        # Para recalibração: armazenar rms de fundo
        self.rmsBase = None

        # Contagem de blocos consecutivos abaixo do limiar
        self.silenceFrameCount = 0
        self.framesToSilence = 3  # número de blocos consecutivos para considerar silêncio estável

        # Fator de escala e limites
        self.scaleFactor = 1.0
        self.minScale = 0.2
        self.maxScale = 3.0

        # Flag de flip horizontal
        self.flipped = False

        # Cooldown para pulinho: tempo do último pulinho em ms e duração do cooldown
        self.lastJumpTime = 0  # em ms
        self.jumpCooldownMs = 4000  # 4 segundos

        # Estado anterior de emissão de volume (para evitar emissões repetidas)
        self.prevEmitState = False

        # Timer para atraso de retorno ao estado inativo
        self.deactivateTimer = QtCore.QTimer(self)
        self.deactivateTimer.setSingleShot(True)
        self.deactivateTimer.timeout.connect(self.FadeToInactive)

        # Configura janela sem bordas, transparente e sempre no topo
        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.Tool
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        # Carrega pixmaps originais
        pixInativa = QtGui.QPixmap("inativa.png")
        pixAtiva = QtGui.QPixmap("ativa.png")
        if pixInativa.isNull() or pixAtiva.isNull():
            print("Erro: não carregou 'inativa.png' ou 'ativa.png'. Verifique caminho.")
        self.pixInativaOriginal = pixInativa
        self.pixAtivaOriginal = pixAtiva

        # Cria labels
        self.labelInativa = QtWidgets.QLabel(self)
        self.labelAtiva = QtWidgets.QLabel(self)

        # Configura pixmaps iniciais e tamanho da janela
        self.UpdateScaledPixmapsAndResize()

        # Efeitos de opacidade
        self.effectInativa = QtWidgets.QGraphicsOpacityEffect(self.labelInativa)
        self.effectAtiva = QtWidgets.QGraphicsOpacityEffect(self.labelAtiva)
        self.labelInativa.setGraphicsEffect(self.effectInativa)
        self.labelAtiva.setGraphicsEffect(self.effectAtiva)
        # Estado inicial: inativa visível, ativa oculta
        self.effectInativa.setOpacity(1.0)
        self.effectAtiva.setOpacity(0.0)

        # Mostrar janela em posição inicial
        self.move(50, 50)
        self.show()

        # Conecta sinal para GUI thread
        self.sinalVolume.connect(self.OnVolumeSignal)
        self.sinalNivelAudio.connect(self.UpdateAudioLevelPreview)

        # Configuração de áudio
        if indiceDispositivo is not None:
            try:
                sd.default.device = (indiceDispositivo, None)
                if self.debug:
                    print(f"[DEBUG] Dispositivo de entrada: {indiceDispositivo}")
            except Exception as e:
                if self.debug:
                    print("[DEBUG] Não pôde definir dispositivo de entrada:", e)

        # Determina samplerate
        if taxaAmostragem is None and indiceDispositivo is not None:
            try:
                info = sd.query_devices(indiceDispositivo, 'input')
                taxaAmostragem = int(info.get('default_samplerate', 44100))
                if self.debug:
                    print(f"[DEBUG] Taxa de amostragem do dispositivo: {taxaAmostragem}")
            except Exception as e:
                if self.debug:
                    print("[DEBUG] Não pôde obter taxa de amostragem:", e)
        if taxaAmostragem is None:
            taxaAmostragem = 44100
            if self.debug:
                print("[DEBUG] Usando taxa de amostragem padrão 44100 Hz")
        try:
            sd.default.samplerate = taxaAmostragem
        except Exception as e:
            if self.debug:
                print("[DEBUG] Não pôde definir samplerate default:", e)
        self.taxaAmostragem = taxaAmostragem  # Armazena taxa de amostragem

        # Se limiar não fornecido, faz calibração automática
        if self.limiar is None:
            self.CalibrarLimiar(indiceDispositivo, taxaAmostragem)
            if self.rmsBase is not None:
                self.limiar = self.rmsBase * self.fatorCalibracao
                if self.debug:
                    print(f"[DEBUG] Limiar calibrado com fator {self.fatorCalibracao}: {self.limiar:.6f}")
            else:
                # fallback
                self.limiar = 0.01
                if self.debug:
                    print(f"[DEBUG] Limiar padrão usado: {self.limiar:.6f}")
        else:
            if self.debug:
                print(f"[DEBUG] Limiar fornecido manualmente: {self.limiar:.6f}")

        try:
            # Blocksize menor para maior responsividade
            self.stream = sd.InputStream(
                device=indiceDispositivo,
                samplerate=taxaAmostragem,
                channels=1,
                callback=self.VerificarAudio,
                blocksize=512  # ou 256 conforme desempenho
            )
            self.stream.start()
            if self.debug:
                print("[DEBUG] InputStream ativo?", getattr(self.stream, "active", None))
        except Exception as e:
            if self.debug:
                print("[DEBUG] Falha ao iniciar InputStream:", e)

        # Arraste
        self._arrastando = False
        self._offsetClick = QtCore.QPoint(0, 0)

        # Preview de áudio
        self.audioLevelWidget = AudioLevelWidget(self)  # Instancia o widget de nível de áudio
        self.audioLevelWidget.setGeometry(10, 10, 20, self.height() - 20)  # Posição e tamanho
        self.audioLevelWidget.hide()  # Esconde inicialmente

    def CalibrarLimiar(self, dispositivo, taxaAmostragem, duracaoS=1.0):
        """
        Grava duracaoS segundos de áudio para estimar nível de ruído de fundo.
        Armazena self.rmsBase e não retorna; limiar será calculado em __init__.
        """
        try:
            if self.debug:
                print("[DEBUG] Iniciando calibração de ruído ambiente...")
            gravacao = sd.rec(int(duracaoS * taxaAmostragem), samplerate=taxaAmostragem,
                              channels=1, dtype='float32', device=dispositivo)
            sd.wait()
            data = gravacao[:, 0]
            # Aplica redução de ruído durante a calibração
            reduced_noise_data = nr.reduce_noise(y=data, sr=taxaAmostragem)
            rms = np.sqrt(np.mean(np.square(reduced_noise_data)))
            self.rmsBase = rms
            if self.debug:
                print(f"[DEBUG] RMS de fundo estimado (com redução de ruído): {self.rmsBase:.6f}")
        except Exception as e:
            if self.debug:
                print("[DEBUG] Calibração falhou, limiar base não definido:", e)
            self.rmsBase = None

    def UpdateScaledPixmapsAndResize(self):
        """
        Gera QPixmaps escalados a partir dos originais usando self.scaleFactor,
        aplica flip horizontal se self.flipped == True,
        atualiza os QLabels e redimensiona a janela.
        """
        if self.pixInativaOriginal.isNull() or self.pixAtivaOriginal.isNull():
            return
        # Calcula novo tamanho
        newWidth = int(self.pixInativaOriginal.width() * self.scaleFactor)
        newHeight = int(self.pixInativaOriginal.height() * self.scaleFactor)
        newWidth = max(1, newWidth)
        newHeight = max(1, newHeight)
        # Escala mantendo proporção
        scaledInativa = self.pixInativaOriginal.scaled(
            newWidth, newHeight,
            QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation
        )
        scaledAtiva = self.pixAtivaOriginal.scaled(
            newWidth, newHeight,
            QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation
        )
        # Se precisar flipar horizontalmente
        if self.flipped:
            transform = QtGui.QTransform().scale(-1, 1)
            scaledInativa = scaledInativa.transformed(transform, QtCore.Qt.SmoothTransformation)
            scaledAtiva = scaledAtiva.transformed(transform, QtCore.Qt.SmoothTransformation)
        # Atualiza labels e tamanho da janela
        self.labelInativa.setPixmap(scaledInativa)
        self.labelAtiva.setPixmap(scaledAtiva)
        self.resize(newWidth, newHeight)
        self.labelInativa.setGeometry(0, 0, newWidth, newHeight)
        self.labelAtiva.setGeometry(0, 0, newWidth, newHeight)
        if self.debug:
            print(f"[DEBUG] Redimensionou para {newWidth}x{newHeight}, scaleFactor={self.scaleFactor:.2f}, flipped={self.flipped}")

    def VerificarAudio(self, indata, frames, timeInfo, status):
        try:
            if status and self.debug:
                print("[DEBUG] Status áudio:", status)
            data = indata[:, 0] if indata.ndim > 1 else indata

            # Aplica redução de ruído
            reduced_noise_data = nr.reduce_noise(y=data, sr=self.taxaAmostragem)

            rms = np.sqrt(np.mean(np.square(reduced_noise_data)))  # Calcula RMS do áudio reduzido
            # Emite sempre o nível para preview
            self.sinalNivelAudio.emit(rms)

            ativo = rms > self.limiar
            # Lógica de contagem de silêncio/voz para evitar piscadas:
            if ativo:
                self.silenceFrameCount = 0
            else:
                self.silenceFrameCount += 1
            # Decide emitir sinal ativo ou não:
            if ativo or self.isActive:
                emitir = ativo or (self.isActive and self.silenceFrameCount < self.framesToSilence)
            else:
                emitir = False

            # Emite sinalVolume apenas se mudar de estado
            if emitir != self.prevEmitState:
                self.sinalVolume.emit(emitir)
                self.prevEmitState = emitir

        except Exception as e:
            if self.debug:
                print("[DEBUG] Erro no callback de áudio:", e)

    def OnVolumeSignal(self, ativo: bool):
        if ativo:
            if self.deactivateTimer.isActive():
                self.deactivateTimer.stop()
            if not self.isActive:
                self.FadeToActive()
        else:
            if self.isActive and not self.deactivateTimer.isActive():
                self.deactivateTimer.start(self.delayMs)

    def FadeToActive(self):
        # Fade de inativa para ativa
        self.isActive = True
        anim1 = QtCore.QPropertyAnimation(self.effectInativa, b"opacity", self)
        anim1.setDuration(self.fadeDurationMs)
        anim1.setStartValue(self.effectInativa.opacity())
        anim1.setEndValue(1.0)
        anim2 = QtCore.QPropertyAnimation(self.effectAtiva, b"opacity", self)
        anim2.setDuration(self.fadeDurationMs)
        anim2.setStartValue(self.effectAtiva.opacity())
        anim2.setEndValue(1.0)
        grupoFade = QtCore.QParallelAnimationGroup(self)
        grupoFade.addAnimation(anim1)
        grupoFade.addAnimation(anim2)
        grupoFade.start(QtCore.QAbstractAnimation.DeleteWhenStopped)

        # Pulinho somente se cooldown expirou, animando self
        now = QtCore.QDateTime.currentMSecsSinceEpoch()
        if now - self.lastJumpTime >= self.jumpCooldownMs:
            self.lastJumpTime = now
            startPos = self.pos()
            jumpHeight = max(10, int(self.height() * 0.05))
            meioDuracao = self.duracaoPuloMs // 2

            animUp = QtCore.QPropertyAnimation(self, b"pos", self)
            animUp.setDuration(meioDuracao)
            animUp.setStartValue(startPos)
            animUp.setEndValue(QtCore.QPoint(startPos.x(), startPos.y() - jumpHeight))

            animDown = QtCore.QPropertyAnimation(self, b"pos", self)
            animDown.setDuration(meioDuracao)
            animDown.setStartValue(QtCore.QPoint(startPos.x(), startPos.y() - jumpHeight))
            animDown.setEndValue(startPos)

            grupoJump = QtCore.QSequentialAnimationGroup(self)
            grupoJump.addAnimation(animUp)
            grupoJump.addAnimation(animDown)
            grupoJump.start(QtCore.QAbstractAnimation.DeleteWhenStopped)

    def FadeToInactive(self):
        if not self.isActive:
            return
        self.isActive = False
        anim1 = QtCore.QPropertyAnimation(self.effectAtiva, b"opacity", self)
        anim1.setDuration(self.fadeDurationMs)
        anim1.setStartValue(self.effectAtiva.opacity())
        anim1.setEndValue(0.0)
        anim2 = QtCore.QPropertyAnimation(self.effectInativa, b"opacity", self)
        anim2.setDuration(self.fadeDurationMs)
        anim2.setStartValue(self.effectInativa.opacity())
        anim2.setEndValue(1.0)  # semitransparente ao voltar
        grupo = QtCore.QParallelAnimationGroup(self)
        grupo.addAnimation(anim1)
        grupo.addAnimation(anim2)
        grupo.start(QtCore.QAbstractAnimation.DeleteWhenStopped)

    def wheelEvent(self, event: QtGui.QWheelEvent):
        delta = event.angleDelta().y()
        if delta == 0:
            return
        steps = delta / 120
        factor = 1.1 ** steps
        newScale = self.scaleFactor * factor
        newScale = max(self.minScale, min(self.maxScale, newScale))
        if abs(newScale - self.scaleFactor) > 1e-6:
            self.scaleFactor = newScale
            self.UpdateScaledPixmapsAndResize()

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        if event.button() == QtCore.Qt.LeftButton:
            self._arrastando = True
            self._offsetClick = event.pos()
        elif event.button() == QtCore.Qt.RightButton:
            # Flip horizontal
            self.flipped = not self.flipped
            self.UpdateScaledPixmapsAndResize()

    def mouseDoubleClickEvent(self, event: QtGui.QMouseEvent):
        if event.button() == QtCore.Qt.LeftButton:
            self.showSensitivityControl()  # Abre o controle de sensibilidade

    def showSensitivityControl(self):
        self.sensitivityWindow = SensitivityControlWindow(self.fatorCalibracao, self.limiar, self.rmsBase, self)
        self.sensitivityWindow.sensitivityChanged.connect(self.updateSensitivity)
        self.sensitivityWindow.finished.connect(self.sensitivityControlClosed)
        self.sensitivityWindow.show()
        self.audioLevelWidget.show()  # Mostra o preview de áudio
        self.audioLevelWidget.raise_()  # Garante que o preview esteja acima de outros widgets

    def updateSensitivity(self, novoFatorCalibracao):
        self.fatorCalibracao = novoFatorCalibracao
        if self.rmsBase is not None:
            self.limiar = self.rmsBase * self.fatorCalibracao
            if self.debug:
                print(f"[DEBUG] Novo fatorCalibracao: {self.fatorCalibracao:.2f}, novo limiar: {self.limiar:.6f}")
        else:
            if self.debug:
                print("[DEBUG] rmsBase não definido, não foi possível recalibrar automaticamente.")

    def sensitivityControlClosed(self):
        self.audioLevelWidget.hide()  # Esconde o preview de áudio quando o controle é fechado

    def UpdateAudioLevelPreview(self, rms_value):
        # Normaliza o valor RMS para a altura do widget de preview
        # Assumindo que o RMS máximo esperado é 0.1 para normalização visual
        normalized_rms = min(1.0, rms_value / 0.1)  # Limita a 1.0 para não exceder a altura
        self.audioLevelWidget.setLevel(normalized_rms)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        if self._arrastando:
            novaPos = event.globalPos() - self._offsetClick
            self.move(novaPos)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent):
        if event.button() == QtCore.Qt.LeftButton:
            self._arrastando = False

class SensitivityControlWindow(QtWidgets.QWidget):
    sensitivityChanged = QtCore.pyqtSignal(float)
    finished = QtCore.pyqtSignal()  # Sinal para indicar que a janela foi fechada

    def __init__(self, initial_fator_calibracao, current_limiar, rms_base, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Controle de Sensibilidade do Microfone")
        self.setGeometry(100, 100, 300, 150)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        self.fatorCalibracao = initial_fator_calibracao
        self.current_limiar = current_limiar
        self.rms_base = rms_base

        layout = QtWidgets.QVBoxLayout()

        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setMinimum(10)  # Representa 0.1
        self.slider.setMaximum(1000)  # Representa 10.0
        self.slider.setValue(int(self.fatorCalibracao * 100))
        self.slider.setTickInterval(100)
        self.slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.slider.valueChanged.connect(self.onSliderChange)
        layout.addWidget(self.slider)

        self.label = QtWidgets.QLabel(f"Fator de Calibração: {self.fatorCalibracao:.2f}")
        layout.addWidget(self.label)

        self.limiar_label = QtWidgets.QLabel(f"Limiar Atual: {self.current_limiar:.6f}")
        layout.addWidget(self.limiar_label)

        self.rms_base_label = QtWidgets.QLabel(f"RMS Base: {self.rms_base:.6f}")
        layout.addWidget(self.rms_base_label)

        self.concluirButton = QtWidgets.QPushButton("Concluir")
        self.concluirButton.clicked.connect(self.close)
        layout.addWidget(self.concluirButton)

        self.setLayout(layout)

    def onSliderChange(self, value):
        self.fatorCalibracao = value / 100.0
        self.label.setText(f"Fator de Calibração: {self.fatorCalibracao:.2f}")
        self.sensitivityChanged.emit(self.fatorCalibracao)
        if self.rms_base is not None:
            new_limiar = self.rms_base * self.fatorCalibracao
            self.limiar_label.setText(f"Limiar Atual: {new_limiar:.6f}")

    def closeEvent(self, event):
        self.finished.emit()  # Emite o sinal quando a janela é fechada
        super().closeEvent(event)

class AudioLevelWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.level = 0.0  # Nível de áudio normalizado (0.0 a 1.0)
        self.setFixedWidth(20)  # Largura fixa para a barra
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

    def setLevel(self, level):
        self.level = level
        self.update()  # Redesenha o widget

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        # Desenha o fundo da barra
        rect = self.rect()
        painter.setBrush(QtGui.QColor(50, 50, 50, 150))  # Cinza escuro transparente
        painter.drawRect(rect)

        # Desenha a linha verde do nível de áudio
        green_height = int(self.level * rect.height())
        painter.setBrush(QtGui.QColor(0, 255, 0, 200))  # Verde transparente
        painter.drawRect(rect.x(), rect.height() - green_height, rect.width(), green_height)

        painter.end()

if __name__ == "__main__":
    input_idx = None
    taxaAmostragem = None
    # Limiar manual: None para calibrar automaticamente
    limiar = None
    delayMs = 200
    fadeDurationMs = 150
    fatorCalibracao = 1.5  # ajuste inicial; se ambiente muito ruidoso, use valor maior
    duracaoPuloMs = 300  # duração total do pulinho em ms; aumente para pulinho mais lento

    app = QtWidgets.QApplication(sys.argv)
    janela = JanelaFacecam(
        indiceDispositivo=input_idx,
        taxaAmostragem=taxaAmostragem,
        limiar=limiar,
        delayMs=delayMs,
        fadeDurationMs=fadeDurationMs,
        fatorCalibracao=fatorCalibracao,
        duracaoPuloMs=duracaoPuloMs
    )
    sys.exit(app.exec_())
