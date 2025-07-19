from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from kivy.metrics import dp

# ===== PBO Core Logic =====
class AlatElektronik:
    def __init__(self, nama, daya, durasi):
        self.nama = nama
        self.daya = float(daya)
        self.durasi = float(durasi)

    def hitung_kwh(self):
        return (self.daya * self.durasi) / 1000

class Rumah:
    def __init__(self):
        self.daftar_alat = []

    def tambah_alat(self, alat):
        self.daftar_alat.append(alat)

    def total_konsumsi(self):
        return sum(a.hitung_kwh() for a in self.daftar_alat)

# ===== KivyMD App =====
KV = '''
<MainLayout>:
    orientation: 'vertical'
    padding: "24dp"
    spacing: "20dp"

    MDLabel:
        text: "Simulasi Konsumsi Daya Listrik"
        halign: "center"
        theme_text_color: "Custom"
        text_color: app.theme_cls.primary_color
        font_style: "H5"

    MDTextField:
        id: nama_input
        hint_text: "Nama Alat"
        mode: "rectangle"

    MDTextField:
        id: daya_input
        hint_text: "Daya (Watt)"
        mode: "rectangle"
        input_filter: "float"

    MDTextField:
        id: durasi_input
        hint_text: "Durasi (Jam)"
        mode: "rectangle"
        input_filter: "float"

    MDRaisedButton:
        text: "Tambah Alat"
        pos_hint: {"center_x": 0.5}
        on_release: app.tambah_data()

    MDLabel:
        id: total_label
        text: "Total Konsumsi: 0.00 kWh"
        halign: "center"
        theme_text_color: "Secondary"
'''

class MainLayout(MDBoxLayout):
    pass

class KonsumsiApp(MDApp):
    def build(self):
        self.title = "Simulasi Konsumsi Listrik"
        self.theme_cls.primary_palette = "LightBlue"
        self.theme_cls.theme_style = "Dark"

        self.rumah = Rumah()
        Builder.load_string(KV)
        self.root_widget = MainLayout()
        return self.root_widget

    def tambah_data(self):
        nama = self.root_widget.ids.nama_input.text
        daya = self.root_widget.ids.daya_input.text
        durasi = self.root_widget.ids.durasi_input.text

        try:
            alat = AlatElektronik(nama, float(daya), float(durasi))
            self.rumah.tambah_alat(alat)
            total = self.rumah.total_konsumsi()
            self.root_widget.ids.total_label.text = f"Total Konsumsi: {total:.2f} kWh"

            self.root_widget.ids.nama_input.text = ''
            self.root_widget.ids.daya_input.text = ''
            self.root_widget.ids.durasi_input.text = ''
        except:
            if not hasattr(self, 'dialog'):
                self.dialog = MDDialog(title="Input Error", text="Masukkan data angka yang valid!")
            self.dialog.open()

KonsumsiApp().run()
