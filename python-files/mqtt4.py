import ssl
import time
import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QCheckBox, QTextEdit, QMessageBox, QStatusBar,
    QComboBox # Import QComboBox for the dropdown
)
from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtGui import QFont, QColor, QPalette

from paho.mqtt import client as mqtt_client

# Thread per il ciclo del client MQTT per evitare il blocco dell'interfaccia utente
class MqttClientThread(QThread):
    connected_signal = Signal(bool, int) # True per successo, reason_code
    log_signal = Signal(str)

    def __init__(self, client, broker, port, username, password, client_id, use_tls):
        super().__init__()
        self.client = client
        self.broker = broker
        self.port = port
        self.username = username
        self.password = password
        self.use_tls = use_tls
        self.client_id = client_id

    def run(self):
        try:
            # Configura i callback del client MQTT
            self.client.on_connect = self._on_connect
            self.client.username_pw_set(self.username, self.password)
            if self.use_tls:
                # CERT_NONE è usato per compatibilità. Considera CERT_REQUIRED con un certificato CA in produzione.
                self.client.tls_set(cert_reqs=ssl.CERT_NONE)

            self.client.connect(self.broker, self.port)
            self.client.loop_forever() # Blocca fino alla disconnessione o errore
        except Exception as e:
            self.log_signal.emit(f"Errore durante la connessione: {e}")
            self.connected_signal.emit(False, -1) # -1 per errore generico

    def _on_connect(self, client, userdata, flags, reason_code, properties=None):
        if reason_code == 0:
            self.log_signal.emit("✅ Connessione al broker riuscita!")
            self.connected_signal.emit(True, reason_code)
        else:
            self.log_signal.emit(f"❌ Connessione fallita. Codice: {reason_code}")
            self.connected_signal.emit(False, reason_code)

    def stop(self):
        if self.client:
            self.client.disconnect()
        self.quit()
        self.wait()


class MqttConfiguratorApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Configuratore MQTT Periferiche")
        self.resize(600, 950) # Aumentato l'altezza per la nuova sezione Template

        self.client = None
        self.connected = False
        self.mqtt_thread = None

        self._create_ui()
        self._set_initial_state()

    def _create_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # --- Frame Connessione Broker ---
        conn_frame = QWidget()
        conn_layout = QVBoxLayout(conn_frame)
        conn_layout.setContentsMargins(10, 10, 10, 10)
        conn_layout.setSpacing(5)
        conn_frame.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc; border-radius: 8px; color: black;")

        conn_label = QLabel("1. Connessione al Broker")
        conn_label.setFont(QFont("Arial", 16, QFont.Bold))
        conn_label.setAlignment(Qt.AlignCenter)
        conn_layout.addWidget(conn_label)

        self.vitrum_check = QCheckBox("Usa Broker Vitrum predefinito")
        self.vitrum_check.stateChanged.connect(self.toggle_vitrum_broker)
        conn_layout.addWidget(self.vitrum_check)

        self.entry_broker = QLineEdit()
        self.entry_broker.setPlaceholderText("Indirizzo Broker")
        conn_layout.addWidget(self.entry_broker)

        self.entry_port = QLineEdit()
        self.entry_port.setPlaceholderText("Porta")
        conn_layout.addWidget(self.entry_port)

        self.entry_username = QLineEdit()
        self.entry_username.setPlaceholderText("Username")
        conn_layout.addWidget(self.entry_username)

        self.entry_password = QLineEdit()
        self.entry_password.setPlaceholderText("Password")
        self.entry_password.setEchoMode(QLineEdit.Password)
        conn_layout.addWidget(self.entry_password)

        self.entry_client_id = QLineEdit()
        self.entry_client_id.setPlaceholderText("Client ID")
        conn_layout.addWidget(self.entry_client_id)

        self.tls_check = QCheckBox("Usa TLS/SSL")
        conn_layout.addWidget(self.tls_check)

        self.connect_button = QPushButton("Connetti")
        self.connect_button.clicked.connect(self.connect_to_broker)
        conn_layout.addWidget(self.connect_button)

        self.status_label = QLabel("Stato: Disconnesso")
        self.status_label.setStyleSheet("color: orange;")
        self.status_label.setAlignment(Qt.AlignCenter)
        conn_layout.addWidget(self.status_label)

        main_layout.addWidget(conn_frame)

        # --- Sezione: Seleziona Periferiche ---
        devices_frame = QWidget()
        devices_layout = QVBoxLayout(devices_frame)
        devices_layout.setContentsMargins(10, 10, 10, 10)
        devices_layout.setSpacing(5)
        devices_frame.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc; border-radius: 8px; color: black;")

        devices_label_title = QLabel("2. Seleziona Periferiche")
        devices_label_title.setFont(QFont("Arial", 16, QFont.Bold))
        devices_label_title.setAlignment(Qt.AlignCenter)
        devices_layout.addWidget(devices_label_title)

        devices_label = QLabel("Codici Periferiche (uno per riga):")
        devices_layout.addWidget(devices_label)
        self.devices_text = QTextEdit()
        self.devices_text.setMinimumHeight(100)
        self.devices_text.setFont(QFont("Courier New", 10))
        self.devices_text.setStyleSheet("background-color: #e8e8e8; border: 1px solid #bbb; border-radius: 5px;")
        devices_layout.addWidget(self.devices_text)

        main_layout.addWidget(devices_frame)

        # --- Sezione: Configurazione MQTT ---
        mqtt_config_frame = QWidget()
        mqtt_config_layout = QVBoxLayout(mqtt_config_frame)
        mqtt_config_layout.setContentsMargins(10, 10, 10, 10)
        mqtt_config_layout.setSpacing(5)
        mqtt_config_frame.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc; border-radius: 8px; color: black;")

        mqtt_config_label_title = QLabel("3. Configurazione MQTT")
        mqtt_config_label_title.setFont(QFont("Arial", 16, QFont.Bold))
        mqtt_config_label_title.setAlignment(Qt.AlignCenter)
        mqtt_config_layout.addWidget(mqtt_config_label_title)

        self.send_mqtt_settings_check = QCheckBox("Invia Nuove Impostazioni Broker MQTT")
        self.send_mqtt_settings_check.setChecked(False)
        self.send_mqtt_settings_check.stateChanged.connect(self.toggle_mqtt_settings_inputs)
        mqtt_config_layout.addWidget(self.send_mqtt_settings_check)

        new_settings_label = QLabel("Nuove Impostazioni Broker da inviare:")
        mqtt_config_layout.addWidget(new_settings_label)
        self.new_mqtt_server = QLineEdit()
        self.new_mqtt_server.setPlaceholderText("mqttServer1")
        mqtt_config_layout.addWidget(self.new_mqtt_server)
        self.new_mqtt_port = QLineEdit()
        self.new_mqtt_port.setPlaceholderText("mqttPort1")
        mqtt_config_layout.addWidget(self.new_mqtt_port)
        self.new_mqtt_user = QLineEdit()
        self.new_mqtt_user.setPlaceholderText("mqttUser1")
        mqtt_config_layout.addWidget(self.new_mqtt_user)
        self.new_mqtt_pass = QLineEdit()
        self.new_mqtt_pass.setPlaceholderText("mqttPassword1")
        self.new_mqtt_pass.setEchoMode(QLineEdit.Password)
        mqtt_config_layout.addWidget(self.new_mqtt_pass)

        self.send_mqtt_button = QPushButton("Invia Configurazione MQTT")
        self.send_mqtt_button.clicked.connect(self.send_mqtt_configuration)
        mqtt_config_layout.addWidget(self.send_mqtt_button)

        main_layout.addWidget(mqtt_config_frame)

        # --- Nuova Sezione: Template ---
        template_frame = QWidget()
        template_layout = QVBoxLayout(template_frame)
        template_layout.setContentsMargins(10, 10, 10, 10)
        template_layout.setSpacing(5)
        template_frame.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc; border-radius: 8px; color: black;")

        template_label_title = QLabel("4. Template") # Aggiornato il numero di sezione
        template_label_title.setFont(QFont("Arial", 16, QFont.Bold))
        template_label_title.setAlignment(Qt.AlignCenter)
        template_layout.addWidget(template_label_title)

        template_selection_label = QLabel("Seleziona Template:")
        template_layout.addWidget(template_selection_label)
        self.template_dropdown = QComboBox()
        self.template_dropdown.addItem("Seleziona un template") # Default placeholder
        self.template_dropdown.addItem("5 Switch + 1 Switch Sat")
        self.template_dropdown.addItem("5 Switch + 1 Push Sat")
        template_layout.addWidget(self.template_dropdown)

        self.send_template_button = QPushButton("Invia Template Selezionato")
        self.send_template_button.clicked.connect(self.send_template_configuration)
        template_layout.addWidget(self.send_template_button)

        main_layout.addWidget(template_frame)

        # --- Sezione: Configurazione Periferiche (Buzzer/Haptic) ---
        peripheral_config_frame = QWidget()
        peripheral_config_layout = QVBoxLayout(peripheral_config_frame)
        peripheral_config_layout.setContentsMargins(10, 10, 10, 10)
        peripheral_config_layout.setSpacing(5)
        peripheral_config_frame.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc; border-radius: 8px; color: black;")

        peripheral_config_label_title = QLabel("5. Configurazione Periferiche (Buzzer/Haptic)") # Aggiornato il numero di sezione
        peripheral_config_label_title.setFont(QFont("Arial", 16, QFont.Bold))
        peripheral_config_label_title.setAlignment(Qt.AlignCenter)
        peripheral_config_layout.addWidget(peripheral_config_label_title)

        self.buzzer_check = QCheckBox("Attiva Buzzer")
        self.buzzer_check.setChecked(False)
        peripheral_config_layout.addWidget(self.buzzer_check)

        self.haptic_check = QCheckBox("Attiva Haptic")
        self.haptic_check.setChecked(False)
        peripheral_config_layout.addWidget(self.haptic_check)

        self.send_peripheral_button = QPushButton("Invia Configurazione Periferiche")
        self.send_peripheral_button.clicked.connect(self.send_peripheral_configuration)
        peripheral_config_layout.addWidget(self.send_peripheral_button)

        main_layout.addWidget(peripheral_config_frame)


        # --- Frame Log ---
        log_frame = QWidget()
        log_layout = QVBoxLayout(log_frame)
        log_layout.setContentsMargins(10, 10, 10, 10)
        log_layout.setSpacing(5)
        log_frame.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc; border-radius: 8px; color: black;")

        log_label = QLabel("Log di Esecuzione")
        log_label.setFont(QFont("Arial", 16, QFont.Bold))
        log_label.setAlignment(Qt.AlignCenter)
        log_layout.addWidget(log_label)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)

        main_layout.addWidget(log_frame)
        main_layout.addStretch(1) # Spinge il contenuto verso l'alto

        # Barra di stato
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Pronto")

    def _set_initial_state(self):
        self.vitrum_check.setChecked(False)
        self.toggle_vitrum_broker()
        self.send_mqtt_settings_check.setChecked(False) # Assicurati che sia False all'avvio
        self.toggle_mqtt_settings_inputs()
        self.buzzer_check.setChecked(False) # Assicurati che sia False all'avvio
        self.haptic_check.setChecked(False) # Assicurati che sia False all'avvio


    def log(self, message):
        self.log_text.append(message)
        self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())

    def toggle_vitrum_broker(self):
        is_vitrum = self.vitrum_check.isChecked()
        entries = [
            self.entry_broker, self.entry_port, self.entry_username,
            self.entry_password, self.entry_client_id
        ]

        if is_vitrum:
            self.entry_broker.setText("mqtt.vitrum.com")
            self.entry_port.setText("8883")
            self.entry_username.setText("M062B-C4D8D54C4694")
            self.entry_password.setText("M062B-C4D8D54C4694")
            self.entry_client_id.setText("M062B-C4D8D54C4694")
            self.tls_check.setChecked(True)

            for entry in entries:
                entry.setEnabled(False)
            self.tls_check.setEnabled(False)
        else:
            for entry in entries:
                entry.clear()
                entry.setEnabled(True)
            self.tls_check.setEnabled(True)
            self.tls_check.setChecked(False)


    def toggle_mqtt_settings_inputs(self):
        enable = self.send_mqtt_settings_check.isChecked()
        self.new_mqtt_server.setEnabled(enable)
        self.new_mqtt_port.setEnabled(enable)
        self.new_mqtt_user.setEnabled(enable)
        self.new_mqtt_pass.setEnabled(enable)
        self.send_mqtt_button.setEnabled(enable)

    def on_connect_slot(self, success, reason_code):
        self.connect_button.setEnabled(True)
        if success:
            self.connected = True
            self.status_label.setText("Stato: Connesso ✅")
            self.status_label.setStyleSheet("color: green;")
            self.statusBar.showMessage("Connesso al broker MQTT.")
        else:
            self.connected = False
            self.status_label.setText(f"Stato: Connessione fallita (Codice: {reason_code}) ❌")
            self.status_label.setStyleSheet("color: red;")
            self.statusBar.showMessage("Connessione al broker fallita.")

    def connect_to_broker(self):
        broker = self.entry_broker.text()
        port_str = self.entry_port.text()
        username = self.entry_username.text()
        password = self.entry_password.text()
        client_id = self.entry_client_id.text()
        use_tls = self.tls_check.isChecked()

        if not all([broker, port_str, username, client_id]):
            QMessageBox.warning(self, "Errore di Input", "Per favor, compila tutti i campi di connessione al broker.")
            return

        try:
            port = int(port_str)
        except ValueError:
            QMessageBox.warning(self, "Errore di Input", "La porta deve essere un numero valido.")
            return

        self.status_label.setText("Stato: In connessione...")
        self.status_label.setStyleSheet("color: yellow;")
        self.connect_button.setEnabled(False)
        self.statusBar.showMessage("Tentativo di connessione al broker...")

        try:
            from paho.mqtt.client import CallbackAPIVersion
            self.client = mqtt_client.Client(client_id=client_id, protocol=mqtt_client.MQTTv311, callback_api_version=CallbackAPIVersion.V5)
        except (ImportError, AttributeError):
            import warnings
            warnings.filterwarnings("ignore", category=DeprecationWarning)
            self.client = mqtt_client.Client(client_id=client_id, protocol=mqtt_client.MQTTv311)

        if self.mqtt_thread and self.mqtt_thread.isRunning():
            self.mqtt_thread.stop()
            self.mqtt_thread.wait()

        self.mqtt_thread = MqttClientThread(self.client, broker, port, username, password, client_id, use_tls)
        self.mqtt_thread.connected_signal.connect(self.on_connect_slot)
        self.mqtt_thread.log_signal.connect(self.log)
        self.mqtt_thread.start()

    def _common_send_checks(self):
        """Esegue i controlli comuni prima di inviare qualsiasi configurazione."""
        if not self.connected:
            QMessageBox.warning(self, "Errore di Connessione", "Non sei connesso a un broker. Connettiti prima.")
            self.log("ERRORE: Non sei connesso a un broker. Connettiti prima.")
            return False

        device_ids = [line.strip() for line in self.devices_text.toPlainText().split('\n') if line.strip()]
        if not device_ids:
            QMessageBox.warning(self, "Errore di Input", "Inserisci almeno un codice periferica.")
            self.log("ERRORE: Inserisci almeno un codice periferica.")
            return False
        return device_ids

    def send_mqtt_configuration(self):
        device_ids = self._common_send_checks()
        if not device_ids:
            return

        if self.send_mqtt_settings_check.isChecked():
            mqtt_server = self.new_mqtt_server.text()
            mqtt_port = self.new_mqtt_port.text()
            mqtt_user = self.new_mqtt_user.text()
            mqtt_pass = self.new_mqtt_pass.text()

            if not all([mqtt_server, mqtt_port, mqtt_user]):
                QMessageBox.warning(self, "Errore di Input", "Compila tutti i campi delle nuove impostazioni broker (Server, Porta, Utente).")
                self.log("ERRORE: Compila tutti i campi delle nuove impostazioni broker.")
                return

            config_message = f"mqttServer1={mqtt_server}&mqttUser1={mqtt_user}&mqttPassword1={mqtt_pass}&mqttPort1={mqtt_port}"

            self.log("\n--- INVIO CONFIGURAZIONE BROKER ---")
            for device_id in device_ids:
                topic = f"{device_id}/cmnd"
                self.log(f"Inviando a {topic} ➜ {config_message}")
                try:
                    self.client.publish(topic, config_message)
                    time.sleep(0.1)
                except Exception as e:
                    self.log(f"Errore durante l'invio del messaggio al topic {topic}: {e}")
            self.log("\n✅ Configurazione MQTT inviata!!!")
            self.statusBar.showMessage("Configurazione MQTT inviata con successo!")
        else:
            self.log("\n--- INVIO IMPOSTAZIONI BROKER SALTATO (Spunta disabilitata) ---")
            QMessageBox.information(self, "Informazione", "L'invio delle impostazioni MQTT è disabilitato.")


    def send_template_configuration(self):
        device_ids = self._common_send_checks()
        if not device_ids:
            return

        selected_template = self.template_dropdown.currentText()
        messages = []

        if selected_template == "5 Switch + 1 Switch Sat":
            messages = [
                "key=14545547582&gpiostatus=OFF",
                "key=145455517JZ&trigger=STOP",
                "key=1454556131Y&trigger=TOUCH1:PUSH/&/&$P1:1/&/&$A1:N;$H1/&/&$B1/&/&$A1:F/&/&$US1:F|TOUCH1:PUSH/&/&$P1:1/&/&$A1:F;$H1/&/&$B1/&/&$A1:N/&/&$US1:N|<TOGGLE1>/&/&$A1:N/<OFF1>;$A1:F/&/&$US1:F|<TOGGLE1>/&/&$A1:F/<ON1>;$A1:N/&/&$US1:N|$A1:N;$UE/&/&$O1.ON/&/&$RL1.$LNV1/&/&$SL1:/&/&MQTT:$BASE_TOPIC/event/1?on;1|$A1:F;$UE/&/&$O1.OFF/&/&$RL1.$LFV1/&/&$SL1:$RL1/&/&MQTT:$BASE_TOPIC/event/1?off;1|TOUCH2:PUSH/&/&$P2:1/&/&$A2:N;$H2/&/&$B2/&/&$A2:F/&/&$US2:F|TOUCH2:PUSH/&/&$P2:1/&/&$A2:F;$H2/&/&$B2/&/&$A2:N/&/&$US2:N|",
                "key=1454557791C&trigger=++<TOGGLE2>/&/&$A2:N/<OFF2>;$A2:F/&/&$US2:F|<TOGGLE2>/&/&$A2:F/<ON2>;$A2:N/&/&$US2:N|$A2:N;$UE/&/&$O2.ON/&/&$RL2.$LNV2/&/&$SL2:/&/&MQTT:$BASE_TOPIC/event/2?on;1|$A2:F;$UE/&/&$O2.OFF/&/&$RL2.$LFV2/&/&$SL2:$RL2/&/&MQTT:$BASE_TOPIC/event/2?off;1|TOUCH3:PUSH/&/&$P3:1/&/&$A3:N;$H3/&/&$B3/&/&$A3:F/&/&$US3:F|TOUCH3:PUSH/&/&$P3:1/&/&$A3:F;$H3/&/&$B3/&/&$A3:N/&/&$US3:N|<TOGGLE3>/&/&$A3:N/<OFF3>;$A3:F/&/&$US3:F|<TOGGLE3>/&/&$A3:F/<ON3>;$A3:N/&/&$US3:N|$A3:N;",
                "key=145455871R9&trigger=++$UE/&/&$O3.ON/&/&$RL3.$LNV3/&/&$SL3:/&/&MQTT:$BASE_TOPIC/event/3?on;1|$A3:F;$UE/&/&$O3.OFF/&/&$RL3.$LFV3/&/&$SL3:$RL3/&/&MQTT:$BASE_TOPIC/event/3?off;1|TOUCH4:PUSH/&/&$P4:1/&/&$A4:N;$H4/&/&$B4/&/&$A4:F/&/&$US4:F|TOUCH4:PUSH/&/&$P4:1/&/&$A4:F;$H4/&/&$B4/&/&$A4:N/&/&$US4:N|<TOGGLE4>/&/&$A4:N/<OFF4>;$A4:F/&/&$US4:F|<TOGGLE4>/&/&$A4:F/<ON4>;$A4:N/&/&$US4:N|$A4:N;$UE/&/&$O4.ON/&/&$RL4.$LNV4/&/&$SL4:/&/&MQTT:$BASE_TOPIC/event/4?on;1|$A4:F;",
                "key=1454559417M&trigger=++$UE/&/&$O4.OFF/&/&$RL4.$LFV4/&/&$SL4:$RL4/&/&MQTT:$BASE_TOPIC/event/4?off;1|TOUCH5:PUSH/&/&$P5:1/&/&$A5:N;$H5/&/&$B5/&/&$A5:F/&/&$US5:F|TOUCH5:PUSH/&/&$P5:1/&/&$A5:F;$H5/&/&$B5/&/&$A5:N/&/&$US5:N|<TOGGLE5>/&/&$A5:N/<OFF5>;$A5:F/&/&$US5:F|<TOGGLE5>/&/&$A5:F/<ON5>;$A5:N/&/&$US5:N|$A5:N;$UE/&/&$O5.ON/&/&$RL5.$LNV5/&/&$SL5:/&/&MQTT:$BASE_TOPIC/event/5?on;1|$A5:F;$UE/&/&$O5.OFF/&/&$RL5.$LFV5/&/&$SL5:$RL5/&/&MQTT:$BASE_TOPIC/event/5?off;1|TOUCH6:PUSH/&/&$P6:1/&/&$A6:N;$H6/&/&$B6/&/&$A6:F/&/&$US6:F|",
                "key=145456036OO&trigger=++TOUCH6:PUSH/&/&$P6:1/&/&$A6:N;$H6/&/&$B6/&/&$A6:F/&/&$US6:F|TOUCH6:PUSH/&/&$P6:1/&/&$A6:F;$H6/&/&$B6/&/&$A6:N/&/&$US6:N|<TOGGLE6>/&/&$A6:N/<OFF6>;$A6:F/&/&$US6:F|<TOGGLE6>/&/&$A6:F/<ON6>;$A6:N/&/&$US6:N|$A6:N;$UE/&/&$O6.ON/&/&$RL6.$LNV6/&/&$SL6:/&/&MQTT:$BASE_TOPIC/event/6?on;1|$A6:F;$UE/&/&$O6.OFF/&/&$RL6.$LFV6/&/&$SL6:$RL6/&/&MQTT:$BASE_TOPIC/event/6?off;1|",
                "key=1454561037R&trigger=++TOUCH1:PULL/&/&TOUCH:PULL/TOUCH2:PULL/&/&TOUCH:PULL/TOUCH3:PULL/&/&TOUCH:PULL/TOUCH4:PULL/&/&TOUCH:PULL/TOUCH5:PULL/&/&TOUCH:PULL/TOUCH6:PULL/&/&TOUCH:PULL/$A1:N/&/&TOUCH:PULL/$A1:F/&/&TOUCH:PULL/$A2:N/&/&TOUCH:PULL/$A2:F/&/&TOUCH:PULL/$A3:N/&/&TOUCH:PULL/$A3:F/&/&TOUCH:PULL/$A4:N/&/&TOUCH:PULL/$A4:F/&/&TOUCH:PULL/$A5:N/&/&TOUCH:PULL/$A5:F/&/&TOUCH:PULL/$A6:N/&/&TOUCH:PULL/$A6:F/&/&TOUCH:PULL/$FS1:1/&/&TOUCH:PULL/$FS2:1/&/&TOUCH:PULL;",
                "key=145456174M3&trigger=++$FS1:0/&/&$FS2:0/&/&TIMER<fade>:12000/&/&FADE:10-1-0-$FFI/&/&$SL1/&/&$SL2/&/&$SL3/&/&$SL4/&/&$SL5/&/&$SL6;1|<PUSH1>;PULSETIME<t1>:$TD1/&/&$A1:N/&/&$US1:N|<PUSH2>;PULSETIME<t2>:$TD2/&/&$A2:N/&/&$US2:N|<PUSH3>;PULSETIME<t3>:$TD3/&/&$A3:N/&/&$US3:N|<PUSH4>;PULSETIME<t4>:$TD4/&/&$A4:N/&/&$US4:N|<PUSH5>;PULSETIME<t5>:$TD5/&/&$A5:N/&/&$US5:N|<PUSH6>;PULSETIME<t6>:$TD6/&/&$A6:N/&/&$US6:N|TOUCH1:PULL/&/&$P1:1/&/&$PS1:1;$A1:F/&/&$US1:F|TOUCH2:PULL/&/&$P2:1/&/&$PS2:1;$A2:F/&/&$US2:F|",
                "key=145456274QR&trigger=++TOUCH3:PULL/&/&$P3:1/&/&$PS3:1;$A3:F/&/&$US3:F|TOUCH4:PULL/&/&$P4:1/&/&$PS4:1;$A4:F/&/&$US4:F|TOUCH5:PULL/&/&$P5:1/&/&$PS5:1;$A5:F/&/&$US5:F|TOUCH6:PULL/&/&$P6:1/&/&$PS6:1;$A6:F/&/&$US6:F|TOUCH1:PUSH/&/&$P1:1/&/&$A1:M;$H1/&/&$B1/&/&$M1:U|TOUCH2:PUSH/&/&$P2:1/&/&$A2:M;$H2/&/&$B2/&/&$M2:U|TOUCH3:PUSH/&/&$P3:1/&/&$A3:M;$H3/&/&$B3/&/&$M2:U|TOUCH4:PUSH/&/&$P4:1/&/&$A4:M;$H4/&/&$B4/&/&$M1:D|TOUCH5:PUSH/&/&$P5:1/&/&$A5:M;$H5/&/&$B5/&/&$M2:D|TOUCH6:PUSH/&/&$P6:1/&/&$A6:M;$H6/&/&$B6/&/&$M2:D|<UP1>;$M1:U|",
                "key=145456495IH&templateParam=$BZ=PULSETIME<beep>:5/&/&BUZZER:ON;$HP=PULSETIME<haptic>:40/&/&HAPTIC:ON;$TD=1000;$LFV=0,0,255;$LNV=255,255,0;$TM=60000;$RL1=LED1;$RL2=LED2;$RL3=LED3;$RL4=LED4;$RL5=LED5;$RL6=LED6;$A1=F;$A2=F;$A3=F;$A4=F;$A5=F;$A6=F;$B1=$BZ;$B2=$BZ;$B3=$BZ;$B4=$BZ;$B5=$BZ;$B6=$BZ;$P1=1;$P2=1;$P3=1;$P4=1;$P5=1;$P6=1;$FFI=0.8;$FS1=;$FS2=;$H1=$HP;$H2=$HP;$H3=$HP;$H4=$HP;$H5=$HP;$H6=$HP;$LFV1=$LFV;$LFV2=$LFV;$LFV3=$LFV;$LFV4=$LFV;$LFV5=$LFV;$LFV6=$LFV;$LNV1=$LNV;$LNV2=$LNV;$LNV3=$LNV;$LNV4=$LNV;$LNV5=$LNV;$LNV6=$LNV;$M1=;$M2=;$O1=RELAY1;$O2=RELAY2;$O3=RELAY3;$O4=RELAY4;$O5=RELAY5;$O6=;$PS1=0;$PS2=0;$PS3=0;$PS4=0;$PS5=0;$PS6=0;$TD1=$TD;$TD2=$TD;$TD3=$TD;$TD4=$TD;$TD5=$TD;$TD6=$TD;$SL1=$RL1;$SL2=$RL2;$SL3=$RL3;$SL4=$RL4;$SL5=$RL5;$SL6=$RL6;$TM1=$TM;$TM2=$TM;$US1=;$US2=;$US3=;$US4=;$US5=;$US6=;$UE=FADE:STOP/&/&$SL1.$LFV1/&/&$SL2.$LFV2/&/&$SL3.$LFV3/&/&$SL4.$LFV4/&/&$SL5.$LFV5/&/&$SL6.$LFV6;",
                "key=14545661380&triggerStartupAction=FADE:9-1-50/&/&LED1_B:255/&/&LED2_B:255/&/&LED3_B:255/&/&LED4_B:255/&/&LED5_B:255/&/&LED6_B:255",
                "key=145456709KC&triggerSave=TRUE",
                "key=145456751OK&trigger=START"
            ]
        elif selected_template == "5 Switch + 1 Push Sat":
            messages = [
                "key=151150164N1&gpiostatus=OFF",
                "key=151150206X1&trigger=STOP",
                "key=1511503019G&trigger=TOUCH1:PUSH/&/&$P1:1/&/&$A1:N;$H1/&/&$B1/&/&$A1:F/&/&$US1:F|TOUCH1:PUSH/&/&$P1:1/&/&$A1:F;$H1/&/&$B1/&/&$A1:N/&/&$US1:N|<TOGGLE1>/&/&$A1:N/<OFF1>;$A1:F/&/&$US1:F|<TOGGLE1>/&/&$A1:F/<ON1>;$A1:N/&/&$US1:N|$A1:N;$UE/&/&$O1.ON/&/&$RL1.$LNV1/&/&$SL1:/&/&MQTT:$BASE_TOPIC/event/1?on;1|$A1:F;$UE/&/&$O1.OFF/&/&$RL1.$LFV1/&/&$SL1:$RL1/&/&MQTT:$BASE_TOPIC/event/1?off;1|TOUCH2:PUSH/&/&$P2:1/&/&$A2:N;$H2/&/&$B2/&/&$A2:F/&/&$US2:F|TOUCH2:PUSH/&/&$P2:1/&/&$A2:F;$H2/&/&$B2/&/&$A2:N/&/&$US2:N|",
                "key=151150403NN&trigger=++<TOGGLE2>/&/&$A2:N/<OFF2>;$A2:F/&/&$US2:F|<TOGGLE2>/&/&$A2:F/<ON2>;$A2:N/&/&$US2:N|$A2:N;$UE/&/&$O2.ON/&/&$RL2.$LNV2/&/&$SL2:/&/&MQTT:$BASE_TOPIC/event/2?on;1|$A2:F;$UE/&/&$O2.OFF/&/&$RL2.$LFV2/&/&$SL2:$RL2/&/&MQTT:$BASE_TOPIC/event/2?off;1|TOUCH3:PUSH/&/&$P3:1/&/&$A3:N;$H3/&/&$B3/&/&$A3:F/&/&$US3:F|TOUCH3:PUSH/&/&$P3:1/&/&$A3:F;$H3/&/&$B3/&/&$A3:N/&/&$US3:N|<TOGGLE3>/&/&$A3:N/<OFF3>;$A3:F/&/&$US3:F|<TOGGLE3>/&/&$A3:F/<ON3>;$A3:N/&/&$US3:N|$A3:N;",
                "key=15115049888&trigger=++$UE/&/&$O3.ON/&/&$RL3.$LNV3/&/&$SL3:/&/&MQTT:$BASE_TOPIC/event/3?on;1|$A3:F;$UE/&/&$O3.OFF/&/&$RL3.$LFV3/&/&$SL3:$RL3/&/&MQTT:$BASE_TOPIC/event/3?off;1|TOUCH4:PUSH/&/&$P4:1/&/&$A4:N;$H4/&/&$B4/&/&$A4:F/&/&$US4:F|TOUCH4:PUSH/&/&$P4:1/&/&$A4:F;$H4/&/&$B4/&/&$A4:N/&/&$US4:N|<TOGGLE4>/&/&$A4:N/<OFF4>;$A4:F/&/&$US4:F|<TOGGLE4>/&/&$A4:F/<ON4>;$A4:N/&/&$US4:N|$A4:N;$UE/&/&$O4.ON/&/&$RL4.$LNV4/&/&$SL4:/&/&MQTT:$BASE_TOPIC/event/4?on;1|$A4:F;",
                "key=151150565UP&trigger=++$UE/&/&$O4.OFF/&/&$RL4.$LFV4/&/&$SL4:$RL4/&/&MQTT:$BASE_TOPIC/event/4?off;1|TOUCH5:PUSH/&/&$P5:1/&/&$A5:N;$H5/&/&$B5/&/&$A5:F/&/&$US5:F|TOUCH5:PUSH/&/&$P5:1/&/&$A5:F;$H5/&/&$B5/&/&$A5:N/&/&$US5:N|<TOGGLE5>/&/&$A5:N/<OFF5>;$A5:F/&/&$US5:F|<TOGGLE5>/&/&$A5:F/<ON5>;$A5:N/&/&$US5:N|$A5:N;$UE/&/&$O5.ON/&/&$RL5.$LNV5/&/&$SL5:/&/&MQTT:$BASE_TOPIC/event/5?on;1|$A5:F;$UE/&/&$O5.OFF/&/&$RL5.$LFV5/&/&$SL5:$RL5/&/&MQTT:$BASE_TOPIC/event/5?off;1|TOUCH6:PUSH/&/&$P6:1/&/&$A6:N;$H6/&/&$B6/&/&$A6:F/&/&$US6:F|",
                "key=15115065942&trigger=++TOUCH6:PUSH/&/&$P6:1/&/&$A6:N;$H6/&/&$B6/&/&$A6:F/&/&$US6:F|TOUCH6:PUSH/&/&$P6:1/&/&$A6:F;$H6/&/&$B6/&/&$A6:N/&/&$US6:N|<TOGGLE6>/&/&$A6:N/<OFF6>;$A6:F/&/&$US6:F|<TOGGLE6>/&/&$A6:F/<ON6>;$A6:N/&/&$US6:N|$A6:N;$UE/&/&$O6.ON/&/&$RL6.$LNV6/&/&$SL6:/&/&MQTT:$BASE_TOPIC/event/6?on;1|$A6:F;$UE/&/&$O6.OFF/&/&$RL6.$LFV6/&/&$SL6:$RL6/&/&MQTT:$BASE_TOPIC/event/6?off;1|",
                "key=151150727HJ&trigger=++TOUCH1:PULL/&/&TOUCH:PULL/TOUCH2:PULL/&/&TOUCH:PULL/TOUCH3:PULL/&/&TOUCH:PULL/TOUCH4:PULL/&/&TOUCH:PULL/TOUCH5:PULL/&/&TOUCH:PULL/TOUCH6:PULL/&/&TOUCH:PULL/$A1:N/&/&TOUCH:PULL/$A1:F/&/&TOUCH:PULL/$A2:N/&/&TOUCH:PULL/$A2:F/&/&TOUCH:PULL/$A3:N/&/&TOUCH:PULL/$A3:F/&/&TOUCH:PULL/$A4:N/&/&TOUCH:PULL/$A4:F/&/&TOUCH:PULL/$A5:N/&/&TOUCH:PULL/$A5:F/&/&TOUCH:PULL/$A6:N/&/&TOUCH:PULL/$A6:F/&/&TOUCH:PULL/$FS1:1/&/&TOUCH:PULL/$FS2:1/&/&TOUCH:PULL;",
                "key=151150798ES&trigger=++$FS1:0/&/&$FS2:0/&/&TIMER<fade>:12000/&/&FADE:10-1-0-$FFI/&/&$SL1/&/&$SL2/&/&$SL3/&/&$SL4/&/&$SL5/&/&$SL6;1|<PUSH1>;PULSETIME<t1>:$TD1/&/&$A1:N/&/&$US1:N|<PUSH2>;PULSETIME<t2>:$TD2/&/&$A2:N/&/&$US2:N|<PUSH3>;PULSETIME<t3>:$TD3/&/&$A3:N/&/&$US3:N|<PUSH4>;PULSETIME<t4>:$TD4/&/&$A4:N/&/&$US4:N|<PUSH5>;PULSETIME<t5>:$TD5/&/&$A5:N/&/&$US5:N|<PUSH6>;PULSETIME<t6>:$TD6/&/&$A6:N/&/&$US6:N|TOUCH1:PULL/&/&$P1:1/&/&$PS1:1;$A1:F/&/&$US1:F|TOUCH2:PULL/&/&$P2:1/&/&$PS2:1;$A2:F/&/&$US2:F|",
                "key=151150892XF&trigger=++TOUCH3:PULL/&/&$P3:1/&/&$PS3:1;$A3:F/&/&$US3:F|TOUCH4:PULL/&/&$P4:1/&/&$PS4:1;$A4:F/&/&$US4:F|TOUCH5:PULL/&/&$P5:1/&/&$PS5:1;$A5:F/&/&$US5:F|TOUCH6:PULL/&/&$P6:1/&/&$PS6:1;$A6:F/&/&$US6:F|TOUCH1:PUSH/&/&$P1:1/&/&$A1:M;$H1/&/&$B1/&/&$M1:U|TOUCH2:PUSH/&/&$P2:1/&/&$A2:M;$H2/&/&$B2/&/&$M2:U|TOUCH3:PUSH/&/&$P3:1/&/&$A3:M;$H3/&/&$B3/&/&$M2:U|TOUCH4:PUSH/&/&$P4:1/&/&$A4:M;$H4/&/&$B4/&/&$M1:D|TOUCH5:PUSH/&/&$P5:1/&/&$A5:M;$H5/&/&$B5/&/&$M2:D|TOUCH6:PUSH/&/&$P6:1/&/&$A6:M;$H6/&/&$B6/&/&$M2:D|<UP1>;$M1:U|",
                "key=151150986S8&trigger=++<STOP1>;$M1:S|<DOWN1>;$M1:D|<UP2>;$M2:U|<STOP2>;$M2:S|<DOWN2>;$M2:D|$M1:U;$M1:0/&/&MOTOR:UP1|$M1:S;$M1:0/&/&MOTOR:STOP1|$M1:D;$M1:0/&/&MOTOR:DOWN1|$M2:U;$M2:0/&/&MOTOR:UP2|$M2:S;$M2:0/&/&MOTOR:STOP2|$M2:D;$M2:0/&/&MOTOR:DOWN2|",
                "key=15115105258&templateParam=",
                "key=151151095HH&templateParam=$BZ=PULSETIME<beep>:5/&/&BUZZER:ON;$HP=PULSETIME<haptic>:40/&/&HAPTIC:ON;$TD=1000;$LFV=0,0,255;$LNV=255,255,0;$TM=60000;$RL1=LED1;$RL2=LED2;$RL3=LED3;$RL4=LED4;$RL5=LED5;$RL6=LED6;$A1=F;$A2=F;$A3=F;$A4=F;$A5=F;$A6=F;$B1=$BZ;$B2=$BZ;$B3=$BZ;$B4=$BZ;$B5=$BZ;$B6=$BZ;$P1=1;$P2=1;$P3=1;$P4=1;$P5=1;$P6=1;$FFI=0.8;$FS1=;$FS2=;$H1=$HP;$H2=$HP;$H3=$HP;$H4=$HP;$H5=$HP;$H6=$HP;$LFV1=$LFV;$LFV2=$LFV;$LFV3=$LFV;$LFV4=$LFV;$LFV5=$LFV;$LFV6=$LFV;$LNV1=$LNV;$LNV2=$LNV;$LNV3=$LNV;$LNV4=$LNV;$LNV5=$LNV;$LNV6=$LNV;$M1=;$M2=;$O1=RELAY1;$O2=RELAY2;$O3=RELAY3;$O4=RELAY4;$O5=RELAY5;$O6=;$PS1=1;$PS2=1;$PS3=1;$PS4=1;$PS5=1;$PS6=1;$TD1=$TD;$TD2=$TD;$TD3=$TD;$TD4=$TD;$TD5=$TD;$TD6=$TD;$SL1=$RL1;$SL2=$RL2;$SL3=$RL3;$SL4=$RL4;$SL5=$RL5;$SL6=$RL6;$TM1=$TM;$TM2=$TM;$US1=;$US2=;$US3=;$US4=;$US5=;$US6=;$UE=FADE:STOP/&/&$SL1.$LFV1/&/&$SL2.$LFV2/&/&$SL3.$LFV3/&/&$SL4.$LFV4/&/&$SL5.$LFV5/&/&$SL6.$LFV6;",
                "key=151151216XA&triggerStartupAction=FADE:9-1-50/&/&LED1_B:255/&/&LED2_B:255/&/&LED3_B:255/&/&LED4_B:255/&/&LED5_B:255/&/&LED6_B:255",
                "key=151151309BO&triggerSave=TRUE",
                "key=151151351AJ&trigger=START"
            ]
        else:
            QMessageBox.warning(self, "Selezione Template", "Per favore, seleziona un template valido dalla tendina.")
            self.log("ERRORE: Nessun template selezionato o template non valido.")
            return

        self.log(f"\n--- INVIO TEMPLATE: {selected_template} ---")
        for device_id in device_ids:
            topic = f"{device_id}/cmnd"
            for i, message in enumerate(messages):
                self.log(f"Inviando a {topic} (Messaggio {i+1}/{len(messages)}) ➜ {message}")
                try:
                    self.client.publish(topic, message)
                    time.sleep(0.1)
                except Exception as e:
                    self.log(f"Errore durante l'invio del messaggio al topic {topic}: {e}")
            self.log(f"✅ Template {selected_template} inviato a {device_id}!")
        self.statusBar.showMessage(f"Template '{selected_template}' inviato con successo a tutte le periferiche!")


    def send_peripheral_configuration(self):
        device_ids = self._common_send_checks()
        if not device_ids:
            return

        self.log("\n--- INVIO IMPOSTAZIONI BUZZER/HAPTIC ---")
        # Buzzer
        if self.buzzer_check.isChecked():
            payload_buzzer = "key=141713791WT&templateParam=$BZ=PULSETIME<beep>:5&&BUZZER:ON"
        else:
            payload_buzzer = "templateParam=$BZ="
        for device_id in device_ids:
            topic = f"{device_id}/cmnd"
            self.log(f"Inviando Buzzer a {topic} ➜ {payload_buzzer}")
            try:
                self.client.publish(topic, payload_buzzer)
                time.sleep(0.1)
            except Exception as e:
                self.log(f"Errore durante l'invio del messaggio Buzzer al topic {topic}: {e}")

        # Haptic
        if self.haptic_check.isChecked():
            payload_haptic = "key=1417368244V&templateParam=$HP=PULSETIME<haptic>:40&&HAPTIC:ON"
        else:
            payload_haptic = "key=141727366RJ&templateParam=$HP="
        for device_id in device_ids:
            topic = f"{device_id}/cmnd"
            self.log(f"Inviando Haptic a {topic} ➜ {payload_haptic}")
            try:
                self.client.publish(topic, payload_haptic)
                time.sleep(0.1)
            except Exception as e:
                self.log(f"Errore durante l'invio del messaggio Haptic al topic {topic}: {e}")

        self.log("\n✅ Configurazione Periferiche inviata!!!")
        self.statusBar.showMessage("Configurazione Periferiche inviata con successo!")


    def closeEvent(self, event):
        # Assicurati che il thread del client MQTT sia fermato quando l'app si chiude
        if self.mqtt_thread and self.mqtt_thread.isRunning():
            self.mqtt_thread.stop()
            self.mqtt_thread.wait()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MqttConfiguratorApp()
    window.show()
    sys.exit(app.exec())
