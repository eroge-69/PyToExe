#!/usr/bin/env python3

import socket
import struct
import os
import time
import datetime

from gi.repository import Gtk, Gdk, GLib, GdkPixbuf, GdkCairo

class Backend:
    """Backend mit Netzwerklogik zum Empfangen von Bildern."""

    class Com:
        def __init__(self, backend):
            self.backend = backend
            self.sock = None
            self.sock_to = None
            self.img = None

            # Default-Werte
            self.srv_ip = '192.168.5.211'
            self.srv_port = 2002
            self.x0 = 0
            self.y0 = 0
            self.dx = 1440
            self.dy = 1080
            self.incrx = 1
            self.incry = 1

            self.img_nr_from = 0
            self.img_nr_to = 0
            self.img_timer_from = 0.0
            self.img_timer_to = 0.0
            self.img_per_second = 0.0

        def connect(self, ip, port):
            if (self.sock is not None) and ((ip, port) == self.sock_to):
                return True
            if self.sock is not None:
                self.disconnect()
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock_to = (ip, port)
            self.sock.settimeout(0.75)
            self.sock.connect(self.sock_to)
            self.sock.settimeout(None)

            # Reset counters
            self.img_nr_from = 0
            self.img_nr_to = 0
            self.img_timer_from = 0.0
            self.img_timer_to = 0.0
            self.img_per_second = 0.0

            return True

        def disconnect(self):
            if self.sock:
                try:
                    self.sock.close()
                except Exception:
                    pass
            self.sock = None
            self.sock_to = None

        def receive_image(self):
            """Fordere Bild an und lese es vom Server."""
            if self.sock is None:
                return False

            # Sende Request-Header
            hdr_req = struct.pack("IIIIII",
                                  self.x0, self.y0,
                                  self.dx, self.dy,
                                  self.incrx, self.incry)
            self.sock.sendall(hdr_req)

            # Lese Antwort-Header (28 Bytes)
            needed = 28
            data = bytearray()
            while len(data) < needed:
                chunk = self.sock.recv(needed - len(data))
                if not chunk:
                    raise RuntimeError("Verbindung während Header-Lesen geschlossen")
                data.extend(chunk)

            hdr = struct.unpack_from("IIIIIII", data)
            total_size = hdr[0]
            img_bytes = total_size - 28
            img_x0, img_y0, img_dx, img_dy, img_incrx, img_incry = hdr[1:7]

            # Lese Bilddaten
            img_data = bytearray(img_bytes)
            mv = memoryview(img_data)
            total_read = 0
            while total_read < img_bytes:
                n = self.sock.recv_into(mv[total_read:], img_bytes - total_read)
                if n == 0:
                    raise RuntimeError("Verbindung während Bilddaten-Lesen geschlossen")
                total_read += n

            # Aktualisiere interne Werte
            self.img = {
                'x0': img_x0,
                'y0': img_y0,
                'dx': img_dx,
                'dy': img_dy,
                'incrx': img_incrx,
                'incry': img_incry,
                'data': img_data
            }

            # FPS-Berechnung
            if self.img_nr_from == 0:
                self.img_nr_from = 1
                self.img_timer_from = time.time()
                self.img_nr_to = 1
            else:
                self.img_nr_to += 1
                self.img_timer_to = time.time()
                dt = self.img_timer_to - self.img_timer_from
                if dt > 0:
                    self.img_per_second = (self.img_nr_to - self.img_nr_from) / dt

            return True

        def write_png(self, path, rgb_mode: bool = False):
            """Speichere das aktuelle Bild als PNG."""
            if self.img is None:
                return False

            directory = os.path.dirname(path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)

            dx = self.img['dx'] // self.img['incrx']
            dy = self.img['dy'] // self.img['incry']
            pitch = dx

            data = self.img['data']
            mv = memoryview(data)

            if rgb_mode:
                # RGB-Modus: data enthält direkt RGB-Kanäle hintereinander
                # Wir gehen davon aus, data.length = dx * dy * 3
                pixbuf = GdkPixbuf.Pixbuf.new_from_data(
                    data,
                    GdkPixbuf.Colorspace.RGB,
                    False,
                    8,
                    dx, dy,
                    dx * 3
                )
            else:
                # Graustufenmodus: wir generieren ein RGB-Pixbuf aus Grauwerten
                rgb_bytes = bytearray(dx * dy * 3)
                # Für jeden Pixel
                for y in range(dy):
                    row_off = y * pitch
                    for x in range(dx):
                        val = mv[row_off + x]
                        idx = (y * dx + x) * 3
                        rgb_bytes[idx    ] = val
                        rgb_bytes[idx + 1] = val
                        rgb_bytes[idx + 2] = val
                pixbuf = GdkPixbuf.Pixbuf.new_from_data(
                    rgb_bytes,
                    GdkPixbuf.Colorspace.RGB,
                    False,
                    8,
                    dx, dy,
                    dx * 3
                )

            # Speichern
            pixbuf.savev(path, "png", [], [])

            return True


class Settings(Gtk.Box):
    def __init__(self, winMain):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.winMain = winMain

        grid = Gtk.Grid()
        grid.set_row_spacing(6)
        grid.set_column_spacing(6)
        self.pack_start(grid, False, False, 0)

        # IP
        lbl_ip = Gtk.Label(label="Server IP")
        grid.attach(lbl_ip, 0, 0, 1, 1)
        self.entry_ip = Gtk.Entry()
        grid.attach(self.entry_ip, 1, 0, 2, 1)

        # Port
        lbl_port = Gtk.Label(label="Server Port")
        grid.attach(lbl_port, 0, 1, 1, 1)
        adj_port = Gtk.Adjustment(2002, 0, 64000, 1, 100, 0)
        self.entry_port = Gtk.SpinButton(adjustment=adj_port, digits=0)
        grid.attach(self.entry_port, 1, 1, 2, 1)

        # x0, y0
        lbl_x0y0 = Gtk.Label(label="[x0, y0]")
        grid.attach(lbl_x0y0, 0, 2, 1, 1)
        adj_x0 = Gtk.Adjustment(0, 0, 5200, 1, 100, 0)
        self.entry_x0 = Gtk.SpinButton(adjustment=adj_x0, digits=0)
        grid.attach(self.entry_x0, 1, 2, 1, 1)
        adj_y0 = Gtk.Adjustment(0, 0, 5200, 1, 100, 0)
        self.entry_y0 = Gtk.SpinButton(adjustment=adj_y0, digits=0)
        grid.attach(self.entry_y0, 2, 2, 1, 1)

        # dx, dy
        lbl_dxdy = Gtk.Label(label="[dx, dy]")
        grid.attach(lbl_dxdy, 0, 3, 1, 1)
        adj_dx = Gtk.Adjustment(0, 0, 5200, 1, 100, 0)
        self.entry_dx = Gtk.SpinButton(adjustment=adj_dx, digits=0)
        grid.attach(self.entry_dx, 1, 3, 1, 1)
        adj_dy = Gtk.Adjustment(0, 0, 5200, 1, 100, 0)
        self.entry_dy = Gtk.SpinButton(adjustment=adj_dy, digits=0)
        grid.attach(self.entry_dy, 2, 3, 1, 1)

        # incrx, incry
        lbl_incr = Gtk.Label(label="[incrx, incry]")
        grid.attach(lbl_incr, 0, 4, 1, 1)
        adj_incrx = Gtk.Adjustment(1, 1, 10, 1, 1, 0)
        self.entry_incrx = Gtk.SpinButton(adjustment=adj_incrx, digits=0)
        grid.attach(self.entry_incrx, 1, 4, 1, 1)
        adj_incry = Gtk.Adjustment(1, 1, 10, 1, 1, 0)
        self.entry_incry = Gtk.SpinButton(adjustment=adj_incry, digits=0)
        grid.attach(self.entry_incry, 2, 4, 1, 1)

        self.chk_continuous = Gtk.CheckButton(label="Receive Continuously")
        self.pack_start(self.chk_continuous, False, False, 0)

        # Radiobuttons für Interpretation
        self.btn_how_grey = Gtk.RadioButton.new_with_label_from_widget(None, "Interpret as Grey")
        self.pack_start(self.btn_how_grey, False, False, 0)
        self.btn_how_fls = Gtk.RadioButton.new_with_label_from_widget(self.btn_how_grey, "Interpret as False Color")
        self.pack_start(self.btn_how_fls, False, False, 0)
        self.btn_how_rgb = Gtk.RadioButton.new_with_label_from_widget(self.btn_how_grey, "Interpret as RGB")
        self.pack_start(self.btn_how_rgb, False, False, 0)

        self.btn_receive_img = Gtk.ToggleButton(label="Receive Image")
        self.pack_start(self.btn_receive_img, False, False, 0)

        self.chk_imgStoreContinuous = Gtk.CheckButton(label="Store Images Continuously (Big Data!)")
        self.pack_end(self.chk_imgStoreContinuous, False, False, 0)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.lbl_imagePath = Gtk.Label(label="Image Path")
        hbox.pack_start(self.lbl_imagePath, True, True, 0)
        self.entry_imagePath = Gtk.Entry()
        hbox.pack_start(self.entry_imagePath, False, False, 0)
        self.pack_end(hbox, False, False, 0)

        self.btn_store_img = Gtk.Button(label="Store Current Image")
        self.pack_end(self.btn_store_img, False, False, 0)

        self.show_all()


class Display(Gtk.DrawingArea):
    def __init__(self, winMain):
        super().__init__()
        self.winMain = winMain
        self.set_size_request(5200, 5200)
        self.connect("draw", self.on_draw)

    def on_draw(self, widget, cr):
        img = self.winMain.img_access()
        if img is None:
            return False

        dx = img['dx'] // img['incrx']
        dy = img['dy'] // img['incry']
        data = img['data']

        # Für Graustufenmodus (vereinfachte Variante)
        rgb_bytes = bytearray(dx * dy * 3)
        mv = memoryview(data)
        for y in range(dy):
            row_off = y * (dx)
            for x in range(dx):
                val = mv[row_off + x]
                idx = (y * dx + x) * 3
                rgb_bytes[idx    ] = val
                rgb_bytes[idx + 1] = val
                rgb_bytes[idx + 2] = val

        pixbuf = GdkPixbuf.Pixbuf.new_from_data(
            rgb_bytes,
            GdkPixbuf.Colorspace.RGB,
            False,
            8,
            dx, dy,
            dx * 3
        )

        Gdk.cairo_set_source_pixbuf(cr, pixbuf, 0, 0)
        cr.paint()
        return False


class Main(Gtk.Window, Backend):
    def __init__(self):
        Gtk.Window.__init__(self, title="VCImgNetClient")
        Backend.__init__(self)

        self.set_default_size(1020, 600)
        self.connect("destroy", Gtk.main_quit)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        vbox.pack_start(hbox, True, True, 0)

        self.settings = Settings(self)
        hbox.pack_start(self.settings, False, False, 0)

        self.display = Display(self)
        scroll = Gtk.ScrolledWindow()
        scroll.add(self.display)
        hbox.pack_start(scroll, True, True, 0)

        self.statusbar = Gtk.Statusbar()
        vbox.pack_end(self.statusbar, False, False, 0)

        # Signal-Verknüpfungen
        self.settings.btn_receive_img.connect("toggled", self.do_receive_img_start)
        self.settings.btn_store_img.connect("clicked", self.do_store_img)

        # Voreinstellungen setzen
        self.settings.entry_ip.set_text(self.com.srv_ip)
        self.settings.entry_port.set_value(self.com.srv_port)
        self.settings.entry_x0.set_value(self.com.x0)
        self.settings.entry_y0.set_value(self.com.y0)
        self.settings.entry_dx.set_value(self.com.dx)
        self.settings.entry_dy.set_value(self.com.dy)
        self.settings.entry_incrx.set_value(self.com.incrx)
        self.settings.entry_incry.set_value(self.com.incry)

        # Interpretation auf “Grey” voreinstellen
        self.settings.btn_how_grey.set_active(True)

        # Standard Image-Path
        tmp = os.path.expanduser("~")
        self.settings.entry_imagePath.set_text(tmp)

        self.show_all()

    def img_access(self):
        return self.com.img

    def do_receive_img_start(self, widget):
        if widget.get_active():
            self.display.queue_draw()
        self.settings.btn_store_img.set_sensitive(False)
        self.do_receive_img()

    def do_receive_img(self):
        if self.settings.btn_receive_img.get_active():
            # Werte aus GUI lesen
            self.com.srv_ip = self.settings.entry_ip.get_text()
            self.com.srv_port = self.settings.entry_port.get_value_as_int()
            self.com.x0 = self.settings.entry_x0.get_value_as_int()
            self.com.y0 = self.settings.entry_y0.get_value_as_int()
            self.com.dx = self.settings.entry_dx.get_value_as_int()
            self.com.dy = self.settings.entry_dy.get_value_as_int()
            self.com.incrx = self.settings.entry_incrx.get_value_as_int()
            self.com.incry = self.settings.entry_incry.get_value_as_int()

            try:
                self.com.connect(self.com.srv_ip, self.com.srv_port)
                self.com.receive_image()
            except Exception as e:
                self.com.disconnect()
                dlg = Gtk.MessageDialog(
                    parent=self,
                    flags=0,
                    message_type=Gtk.MessageType.ERROR,
                    buttons=Gtk.ButtonsType.CLOSE,
                    text=f"Failed to connect to {self.com.srv_ip}:{self.com.srv_port}\n{e}"
                )
                dlg.run()
                dlg.destroy()
                self.settings.btn_receive_img.set_active(False)
                return False

            # Kontinuierliches Speichern, falls aktiviert
            if self.settings.chk_imgStoreContinuous.get_active():
                fname = os.path.join(
                    self.settings.entry_imagePath.get_text(),
                    datetime.datetime.now().strftime("%y%m%dT%H%M%S%f") + ".png"
                )
                # Hier: Graustufenmodus speichern (rgb_mode=False)
                self.com.write_png(fname, False)

            # Statusleiste aktualisieren
            ctx = self.statusbar.get_context_id("fps")
            self.statusbar.pop(ctx)
            self.statusbar.push(ctx, f"FPS: {self.com.img_per_second:.2f}")

            # Zeichnen aktualisieren
            self.display.queue_draw()

            # Wiederholung über idle, falls "kontinuierlich" aktiviert
            if self.settings.chk_continuous.get_active():
                GLib.idle_add(self.do_receive_img)
            else:
                self.com.disconnect()
                self.settings.btn_receive_img.set_active(False)
        else:
            self.com.disconnect()
        return False

    def do_store_img(self, widget):
        dlg = Gtk.FileChooserDialog(
            title="Store Image",
            parent=self,
            action=Gtk.FileChooserAction.SAVE,
            buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                     Gtk.STOCK_SAVE, Gtk.ResponseType.OK)
        )
        filter_png = Gtk.FileFilter()
        filter_png.set_name("PNG")
        filter_png.add_pattern("*.png")
        dlg.add_filter(filter_png)
        dlg.set_current_name("image.png")

        response = dlg.run()
        if response == Gtk.ResponseType.OK:
            filename = dlg.get_filename()
            # Hier: Graustufenmodus speichern
            self.com.write_png(filename, False)

        dlg.destroy()


def main():
    win = Main()
    win.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()
