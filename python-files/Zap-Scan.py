from tkinter import *
import threading
import time
import socket
import sys
from datetime import datetime
import copy


class ZapScan:
    def __init__(self):
        self.window = Tk()
        self.window.geometry("1000x600")
        self.window.title("Zapscan GUI")

        self.initialize_variables()

        self.setup_gui()

        self.window.mainloop()

    def initialize_variables(self):
        self.lock = threading.Lock()
        self.ipv6 = ""
        self.Eport = 0
        self.Sport = 0
        self.old_filtered_services = []
        self.ipv4 = ""
        self.servicee = []
        self.filtered_services = []
        self.filtered_ports = []
        self.ipv4_status = False
        self.ipv6_status = False
        self.tcp_status = False
        self.udp_status = False
        self.open_ports = []
        self.services = []
        self.old_filtered_ports = []
        self.old_ports = []
        self.old_services = []
        self.old_target = ""
        self.old_StartingPort = 0
        self.old_EndingPort = 0
        self.old_timee = 0
        self.threads = 100
        self.Target = ""
        self.StartingPort = 0
        self.EndingPort = 0
        self.scan_active = False
        self.current_scan_thread = None

        try:
            self.photo = PhotoImage(file="Zap-Scan-3.png")
        except:
            self.photo = None

        try:
            self.window.iconbitmap("Lightscan-Logo.ico")
        except:
            pass

    def setup_gui(self):
        # Create main frame
        main_frame = Frame(self.window, bg="#91d3fa")
        main_frame.pack(fill=BOTH, expand=True)

        # Title Label
        title_text = "Zapscan GUI"
        if self.photo:
            self.TitleLabel = Label(main_frame, text=title_text, font=("Ariel", 35, "bold"),
                                    fg="cyan", bg="#91d3fa", relief=RAISED, bd=10,
                                    padx=10, pady=18.5, image=self.photo, compound=RIGHT)
        else:
            self.TitleLabel = Label(main_frame, text=title_text, font=("Ariel", 35, "bold"),
                                    fg="cyan", bg="#91d3fa", relief=RAISED, bd=10,
                                    padx=10, pady=18.5)
        self.TitleLabel.place(x=20, y=20)

        # Input fields
        self.TargetLabel = Label(main_frame, text="Target :", font=("Ariel", 15, "bold"),
                                 fg="cyan", bg="#91d3fa")
        self.TargetLabel.place(x=475, y=38)

        self.TargetEntry = Entry(main_frame, font=("Ariel", 10, "bold"), fg="white", bg="#91d3fa")
        self.TargetEntry.place(x=670, y=42)

        self.StartingPortLabel = Label(main_frame, text="Starting Port :", font=("Ariel", 15, "bold"),
                                       fg="cyan", bg="#91d3fa")
        self.StartingPortLabel.place(x=475, y=68)

        self.StartingPortEntry = Entry(main_frame, font=("Ariel", 10, "bold"), fg="white", bg="#91d3fa")
        self.StartingPortEntry.place(x=670, y=72)

        self.EndingPortLabel = Label(main_frame, text="Ending Port :", font=("Ariel", 15, "bold"),
                                     fg="cyan", bg="#91d3fa")
        self.EndingPortLabel.place(x=475, y=98)

        self.EndingPortEntry = Entry(main_frame, font=("Ariel", 10, "bold"), fg="white", bg="#91d3fa")
        self.EndingPortEntry.place(x=670, y=101)

        # Speed selection
        self.SpeedLabel = Label(main_frame, text="Speed :", font=("Ariel", 15, "bold"),
                                fg="cyan", bg="#91d3fa")
        self.SpeedLabel.place(x=475, y=130)

        SpeedsChoices = ["Slow", "Normal", "Fast", "Zap"]
        self.speed_var = IntVar(value=1)  # Default to Normal

        for index, speed in enumerate(SpeedsChoices):
            SpeedChoice = Radiobutton(main_frame, text=speed, fg="black", bg="#91d3fa",
                                      font=("Ariel", 12, "bold"), activebackground="#91d3fa",
                                      activeforeground="yellow", variable=self.speed_var,
                                      value=index, command=self.update_speed)
            SpeedChoice.place(x=560 + index * 90, y=132)

        # Buttons
        self.button1 = Button(main_frame, text="Start Scan", font=("Arial", 20, "bold"),
                              fg="black", bg="cyan", activebackground="cyan",
                              activeforeground="black", relief=RAISED, bd=10,
                              command=self.Start_Scan)
        self.button1.place(x=797, y=240)

        self.button2 = Button(main_frame, text="Submit", font=("Arial", 7, "bold"),
                              fg="black", bg="yellow", relief=RAISED, bd=2.5,
                              command=self.submit_Target)
        self.button2.place(x=820, y=41)

        self.button3 = Button(main_frame, text="Submit", font=("Arial", 7, "bold"),
                              fg="black", bg="yellow", relief=RAISED, bd=2.5,
                              command=self.submit_Starting_port)
        self.button3.place(x=820, y=71)

        self.button4 = Button(main_frame, text="Submit", font=("Arial", 7, "bold"),
                              fg="black", bg="yellow", relief=RAISED, bd=2.5,
                              command=self.submit_Ending_port)
        self.button4.place(x=820, y=100)

        self.button7 = Button(main_frame, text="Save Scan", font=("Arial", 20, "bold"),
                              fg="black", bg="cyan", activebackground="cyan",
                              activeforeground="black", relief=RAISED, bd=10,
                              command=self.Save_Scan)
        self.button7.place(x=797, y=375)

        self.button8 = Button(main_frame, text="Advanced", font=("Arial", 20, "bold"),
                              fg="black", bg="cyan", activebackground="cyan",
                              activeforeground="black", relief=RAISED, bd=10,
                              command=self.Advanced)
        self.button8.place(x=797, y=510)

        self.button9 = Button(main_frame, text="Exit", font=("Arial", 20, "bold"),
                              fg="black", bg="cyan", activebackground="cyan",
                              activeforeground="black", relief=RAISED, bd=10,
                              command=self.Exit)
        self.button9.place(x=908, y=0)

        # Results display
        self.results_text = Text(main_frame, height=20, width=80, state=DISABLED, bg="blue", fg="white")
        self.results_text.place(x=20, y=200)
        self.results_scrollbar = Scrollbar(main_frame, orient=VERTICAL, command=self.results_text.yview)
        self.results_scrollbar.place(x=650, y=200, height=324)
        self.results_text.config(yscrollcommand=self.results_scrollbar.set)

        # Status label
        self.status_label = Label(main_frame, text="Ready", font=("Arial", 20,"bold"),relief=RAISED,
                                  bd=2.5,
                                  fg="green"
                                   ,bg="cyan")
        self.status_label.place(x=20, y=530)

    def update_speed(self):
        speed_value = self.speed_var.get()
        if speed_value == 0:
            self.threads = 100
        elif speed_value == 1:
            self.threads = 350
        elif speed_value == 2:
            self.threads = 1000
        elif speed_value == 3:
            self.threads = 5000
        self.update_results(
            f"[+] Speed set to {['Slow', 'Normal', 'Fast', 'Zap'][speed_value]} ({self.threads} threads)")

    def update_results(self, text):
        self.results_text.config(state=NORMAL)
        self.results_text.insert(END, text + "\n")
        self.results_text.see(END)
        self.results_text.config(state=DISABLED)
        self.window.update_idletasks()  # Keep UI responsive

    def update_status(self, text, color="green"):
        self.status_label.config(text=text, fg=color)
        self.window.update_idletasks()

    def submit_Starting_port(self):
        self.StartingPort = self.StartingPortEntry.get()
        if not self.StartingPort:
            self.StartingPort = 1
            self.update_results("[!] StartingPort is 1 Default")
        try:
            self.StartingPort = int(self.StartingPort)
        except:
            self.update_results("[!] Invalid StartingPort")
            return
        self.update_results(f"[+] Starting port set to {self.StartingPort}")

    def submit_Ending_port(self):
        self.EndingPort = self.EndingPortEntry.get()
        if not self.EndingPort:
            self.EndingPort = 1024
            self.update_results("[!] EndingPort is 1024 Default")
        try:
            self.EndingPort = int(self.EndingPort)
        except:
            self.update_results("[!] Invalid EndingPort")
            return
        self.update_results(f"[+] Ending port set to {self.EndingPort}")

    def submit_Target(self):
        self.Target = self.TargetEntry.get()
        self.update_results(f"[+] Target set to {self.Target}")

    def Save_Scan(self):
        if not self.old_ports and not self.old_filtered_ports:
            self.update_results("[!] No scan results to save! Run a scan first.")
            return

        ttt = datetime.now()
        try:
            with open("Zapscan-Report.txt", "w") as file:
                file.write(
                    f"Zap-Scan Version 1.3 at {ttt.year}-{ttt.month}-{ttt.day} {ttt.hour}-{ttt.minute}-{ttt.second:.2f}\n")
                file.write("=" * 50 + "\n")
                file.write(
                    f"Scan The Target {self.old_target} From Port {self.old_StartingPort} to Port {self.old_EndingPort}\n")
                file.write("=" * 50 + "\n\n")

                if self.old_ports:
                    file.write("[+] Open Ports \n\n")
                    for i in range(len(self.old_ports)):
                        file.write(f"[+] Port {self.old_ports[i]} {self.old_services[i]} is open\n")
                else:
                    file.write("[!] No open ports found\n")

                file.write("\n" + "=" * 50 + "\n")
                file.write(f"[+] Scan Finished in {self.old_timee:.2f} seconds\n")

            self.update_results("[+] Scan results saved to 'Zapscan-Report.txt'")

        except Exception as e:
            self.update_results(f"[!] Error saving file: {e}")

    def Start_Scan(self):
        if self.scan_active:
            self.update_results("[!] Scan already in progress")
            return

        self.old_timee = None
        self.old_StartingPort = 0
        self.old_EndingPort = 0
        self.old_ports = []
        self.old_services = []
        self.old_target = ""

        # Start scan in a separate thread to prevent UI freeze
        self.scan_active = True
        self.update_status("Scanning...", "orange")
        self.current_scan_thread = threading.Thread(target=self.start, daemon=True)
        self.current_scan_thread.start()

    def Exit(self):
        self.update_results("[!] Zap Scan Closing ...")
        time.sleep(0.1)
        sys.exit(0)

    def Advanced(self):
        AdvancedWindow(self)

    def validate_target(self, target, is_ipv6=False):
        alp_chars = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
                     'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N',
                     'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
        chars = ["+", "=", "'", '"', "-", "_", "(", ")", "{", "}", ";", ":", "\\", "|", ",", "<", ">", "/", "?", "~",
                 "`", "!", "@", "#", "$", "%", "^", "&", "*"]

        if not is_ipv6:
            for char in alp_chars:
                if char in target:
                    if "#@#" in target:
                        target = target.replace("#@#", "").strip()
                        try:
                            target = socket.gethostbyname(target)
                        except socket.gaierror:
                            self.update_results("[!] Could not resolve hostname")
                            return None
                    else:
                        self.update_results("[+] Before Domain name write #@# to make Zap Scan recognize it")
                        return None

            for char in chars:
                if char in target:
                    self.update_results("[!] Invalid character detected")
                    return None
        else:
            chars1 = ["+", "=", "'", '"', "-", "_", "(", ")", "{", "}", ";", "\\", "|", ",", "<", ">", "/", "?", "~",
                      "`", "!", "@", "#", "$", "%", "^", "&", "*"]
            for char in chars1:
                if char in target:
                    if "#@#" in target:
                        target = target.replace("#@#", "").strip()
                        try:
                            addrinfo = socket.getaddrinfo(target, None, socket.AF_INET6)
                            if addrinfo:
                                target = addrinfo[0][4][0]
                            else:
                                self.update_results("[!] Could not resolve IPv6 address")
                                return None
                        except socket.gaierror:
                            self.update_results("[!] Could not resolve IPv6 address")
                            return None
                        except Exception as e:
                            self.update_results(f"Error: {e}")
                            return None
                    else:
                        self.update_results("[+] Before Domain name write #@# to make Zap Scan recognize it")
                        return None

        return target

    def scan_tcp(self, target, port):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            result = s.connect_ex((target, port))

            if result == 0:
                try:
                    service = socket.getservbyport(port) + "/tcp"
                except:
                    service = "unknown/tcp"
                with self.lock:
                    self.open_ports.append(port)
                    self.services.append(service)
            else:
                with self.lock:
                    try:
                        servicee = socket.getservbyport(port) + "/tcp"
                    except:
                        servicee = "unknown/tcp"
                    self.filtered_services.append(servicee)
                    self.filtered_ports.append(port)
            s.close()
        except socket.error:
            pass

    def scan_udp(self, target, port):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(1)

            # Try to send empty data to trigger a response
            s.sendto(b'', (target, port))

            try:
                data, addr = s.recvfrom(1024)
                # If we get a response, the port might be open
                try:
                    service = socket.getservbyport(port) + "/udp"
                except:
                    service = "unknown/udp"
                with self.lock:
                    self.open_ports.append(port)
                    self.services.append(service)
            except socket.timeout:
                # No response - port might be open or filtered
                with self.lock:
                    try:
                        servicee = socket.getservbyport(port) + "/udp"
                    except:
                        servicee = "unknown/udp"
                    self.filtered_services.append(servicee)
                    self.filtered_ports.append(port)
            except socket.error:
                # Other errors - consider port closed
                pass
            finally:
                s.close()
        except socket.error:
            pass

    def start(self):
        self.submit_Target()
        self.submit_Starting_port()
        self.submit_Ending_port()

        if not self.Target:
            self.update_results("[!] Target cannot be empty")
            self.scan_active = False
            self.update_status("Ready")
            return

        validated_target = self.validate_target(self.Target)
        if not validated_target:
            self.scan_active = False
            self.update_status("Ready")
            return

        self.Target = validated_target

        if not self.StartingPort:
            self.StartingPort = 1
            self.update_results("[!] StartingPort is 1 Default")

        if not self.EndingPort:
            self.EndingPort = 1024
            self.update_results("[!] EndingPort is 1024 Default")

        self.update_results("[+] Start Scanning ...")
        starting_counter = time.perf_counter()

        try:
            ports_to_scan = list(range(self.StartingPort, self.EndingPort + 1))
        except:
            self.update_results("[!] Invalid Port range [Using Default Values 1-1024]")
            ports_to_scan = list(range(1, 1025))

        # Reset scan results
        self.open_ports = []
        self.services = []
        self.filtered_ports = []
        self.filtered_services = []

        # Create and manage threads
        list_threads = []
        for port in ports_to_scan:
            if not self.scan_active:  # Allow cancellation
                break

            t = threading.Thread(target=self.scan_tcp, args=(self.Target, port), daemon=True)
            t.start()
            list_threads.append(t)

            # Control the number of concurrent threads
            while threading.active_count() > self.threads + 2:  # +2 for main and GUI threads
                time.sleep(0.1)
                if not self.scan_active:  # Allow cancellation
                    break

        # Wait for all threads to complete
        for t in list_threads:
            t.join(timeout=2)

        if not self.scan_active:  # Scan was cancelled
            self.update_results("[!] Scan cancelled")
            self.update_status("Ready")
            return

        # Display results
        if self.open_ports:
            self.update_results("\n[+] Open Ports \n")
            for i in range(len(self.open_ports)):
                self.update_results(f"[+] Port {self.open_ports[i]} {self.services[i]} is open")
        else:
            self.update_results("[!] No open ports found")

        ending_counter = time.perf_counter()
        timee = ending_counter - starting_counter
        self.update_results(f"\n[+] Scan complete in {timee:.2f} seconds\n")

        # Save results for potential saving
        self.old_ports = copy.deepcopy(self.open_ports)
        self.old_services = copy.deepcopy(self.services)
        self.old_target = copy.deepcopy(self.Target)
        self.old_StartingPort = copy.deepcopy(self.StartingPort)
        self.old_EndingPort = copy.deepcopy(self.EndingPort)
        self.old_timee = copy.deepcopy(timee)

        # Reset for next scan
        self.scan_active = False
        self.update_status("Ready")


class AdvancedWindow:
    def __init__(self, parent):
        self.parent = parent
        self.adv = Toplevel(parent.window)
        self.adv.geometry("1440x900")
        self.adv.title("Zap Scan - Advanced Options")

        try:
            self.adv.iconbitmap("Zap-Scan-Adv-2.ico")
        except:
            pass

        self.adv.config(bg="black")
        self.adv.protocol("WM_DELETE_WINDOW", self.on_close)

        # Initialize advanced variables
        self.ipv6 = ""
        self.Eport = 0
        self.Sport = 0
        self.ipv4 = ""
        self.ipv4_status = False
        self.ipv6_status = False
        self.scan_type = "tcp"  # Default to TCP scan
        self.scan_active = False
        self.current_scan_thread = None

        # Setup advanced GUI
        self.setup_advanced_gui()

    def setup_advanced_gui(self):
        # Title
        try:
            photo1 = PhotoImage(file="Zap-Scan-Adv-1.png")
            self.TLabel = Label(self.adv, text="Zapscan Adv GUI", bg="black", fg="red",
                                relief=RAISED, bd=4, font=("Arial", 30, "bold"),
                                padx=10, pady=10, image=photo1, compound=RIGHT)
            self.TLabel.image = photo1  # Keep a reference
        except:
            self.TLabel = Label(self.adv, text="Zapscan Adv GUI", bg="black", fg="red",
                                relief=RAISED, bd=4, font=("Arial", 30, "bold"),
                                padx=10, pady=10)
        self.TLabel.place(x=20, y=20)

        # Input fields
        self.IPV4 = Label(self.adv, text="IPv4 Address:", bg="black", fg="red",
                          font=("Arial", 12, "bold"))
        self.IPV4.place(x=580, y=20)

        self.IPV4entry = Entry(self.adv, font=("Arial", 10, "bold"), bg="black", fg="white")
        self.IPV4entry.place(x=700, y=20)

        self.ipv4_button = Button(self.adv, text="Submit", font=("Arial", 7, "bold"),
                                  bg="red", fg="black", relief=RAISED, bd=2.5,
                                  command=self.ipv4_submit)
        self.ipv4_button.place(x=850, y=20)

        self.IPV6 = Label(self.adv, text="IPv6 Address:", bg="black", fg="red",
                          font=("Arial", 12, "bold"))
        self.IPV6.place(x=580, y=50)

        self.IPV6entry = Entry(self.adv, font=("Arial", 10, "bold"), bg="black", fg="white")
        self.IPV6entry.place(x=700, y=50)

        self.ipv6_button = Button(self.adv, text="Submit", font=("Arial", 7, "bold"),
                                  bg="red", fg="black", relief=RAISED, bd=2.5,
                                  command=self.ipv6_submit)
        self.ipv6_button.place(x=850, y=50)

        self.Sport_label = Label(self.adv, text="Starting Port:", bg="black", fg="red",
                                 font=("Arial", 12, "bold"))
        self.Sport_label.place(x=580, y=80)

        self.SportEntry = Entry(self.adv, font=("Arial", 10, "bold"), bg="black", fg="white")
        self.SportEntry.place(x=700, y=80)

        self.sport_button = Button(self.adv, text="Submit", font=("Arial", 7, "bold"),
                                   bg="red", fg="black", relief=RAISED, bd=2.5,
                                   command=self.Sport_submit)
        self.sport_button.place(x=850, y=80)

        self.Eport_label = Label(self.adv, text="Ending Port:", bg="black", fg="red",
                                 font=("Arial", 12, "bold"))
        self.Eport_label.place(x=580, y=110)

        self.EportEntry = Entry(self.adv, font=("Arial", 10, "bold"), bg="black", fg="white")
        self.EportEntry.place(x=700, y=110)

        self.eport_button = Button(self.adv, text="Submit", font=("Arial", 7, "bold"),
                                   bg="red", fg="black", relief=RAISED, bd=2.5,
                                   command=self.Eport_submit)
        self.eport_button.place(x=850, y=110)

        # Scan type selection
        self.scan_type_var = StringVar(value="tcp")
        self.tcp_radio = Radiobutton(self.adv, text="TCP Scan", variable=self.scan_type_var,
                                     value="tcp", bg="black", fg="red", selectcolor="black",
                                     font=("Arial", 10, "bold"))
        self.tcp_radio.place(x=580, y=160)

        self.udp_radio = Radiobutton(self.adv, text="UDP Scan", variable=self.scan_type_var,
                                     value="udp", bg="black", fg="red", selectcolor="black",
                                     font=("Arial", 10, "bold"))
        self.udp_radio.place(x=680, y=160)

        # Speed selection
        self.SpeedLabel_ = Label(self.adv, text="Speed:", font=("Ariel", 12, "bold"),
                                 fg="red", bg="black")
        self.SpeedLabel_.place(x=580, y=190)

        SpeedsChoices_ = ["Normal", "Fast", "Zap", "Dark"]
        self.speed_var_ = IntVar(value=0)

        for index_, speed in enumerate(SpeedsChoices_):
            SpeedChoice_ = Radiobutton(self.adv, text=speed, fg="red", bg="black",
                                       font=("Ariel", 10, "bold"), activebackground="black",
                                       activeforeground="yellow", variable=self.speed_var_,
                                       value=index_, command=self.Speed_)
            SpeedChoice_.place(x=650 + index_ * 80, y=190)

        # Results display
        self.results_text = Text(self.adv, height=20, width=80, state=DISABLED, bg="#4f4f4f", fg="white")
        self.results_text.place(x=20, y=280)
        self.results_scrollbar = Scrollbar(self.adv, orient=VERTICAL, command=self.results_text.yview)
        self.results_scrollbar.place(x=650, y=280, height=324)
        self.results_text.config(yscrollcommand=self.results_scrollbar.set)

        # Buttons
        self.StartTcpScan = Button(self.adv, text="Start Scan", font=("Arial", 16, "bold"),
                                   fg="black", bg="red", activebackground="red",
                                   activeforeground="black", relief=RAISED, bd=8,
                                   command=self.Adv_start)
        self.StartTcpScan.place(x=20, y=620)

        self.cancel_button = Button(self.adv, text="Cancel Scan", font=("Arial", 16, "bold"),
                                    fg="black", bg="red", activebackground="red",
                                    activeforeground="black", relief=RAISED, bd=7,
                                    command=self.cancel_scan)
        self.cancel_button.place(x=170, y=620)
        self.save_button = Button(self.adv, text="Save Scan", font=("Arial", 16, "bold"),
                                  fg="black", bg="red", activebackground="red",
                                  activeforeground="black", relief=RAISED, bd=6,
                                  command=self.save_advanced_scan)
        self.save_button.place(x=340, y=620)

        # Status label
        self.status_label = Label(self.adv, text="Ready", font=("Arial", 20,"bold"), fg="green", bg="red",relief=RAISED,bd=2.5)
        self.status_label.place(x=580, y=620)

    def update_results(self, text):
        self.results_text.config(state=NORMAL)
        self.results_text.insert(END, text + "\n")
        self.results_text.see(END)
        self.results_text.config(state=DISABLED)
        self.adv.update_idletasks()

    def update_status(self, text, color="green"):
        self.status_label.config(text=text, fg=color)
        self.adv.update_idletasks()

    def ipv4_submit(self):
        self.ipv4 = self.IPV4entry.get()
        self.ipv4_status = True
        self.ipv6_status = False
        self.update_results(f"[+] IPv4 set to: {self.ipv4}")

    def ipv6_submit(self):
        self.ipv6 = self.IPV6entry.get()
        self.ipv6_status = True
        self.ipv4_status = False
        self.update_results(f"[+] IPv6 set to: {self.ipv6}")

    def save_advanced_scan(self):
        """Save the results from advanced scanning"""
        if not self.parent.old_ports:
            self.update_results("[!] No scan results to save! Run a scan first.")
            return

        try:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"ZapScan_Advanced_{timestamp}.txt"

            with open(filename, "w") as file:
                file.write(f"ZapScan Advanced Report - {timestamp}\n")
                file.write("=" * 50 + "\n")

                # Write scan configuration
                file.write(f"Target: {self.parent.old_target}\n")
                file.write(f"Protocol: {self.scan_type_var.get().upper()}\n")
                file.write(f"Port Range: {self.parent.old_StartingPort}-{self.parent.old_EndingPort}\n")
                file.write(f"Scan Duration: {self.parent.old_timee:.2f} seconds\n")
                file.write("=" * 50 + "\n\n")

                # Write results
                if self.parent.old_ports:
                    file.write("OPEN PORTS:\n")
                    file.write("-" * 30 + "\n")
                    for port, service in zip(self.parent.old_ports, self.parent.old_services):
                        file.write(f"Port {port}: {service}\n")
                else:
                    file.write("No open ports found\n")

                file.write("\n" + "=" * 50 + "\n")
                file.write("Scan completed successfully\n")

            self.update_results(f"[+] Advanced scan results saved to '{filename}'")
            self.update_status("Results saved", "green")

        except Exception as e:
            self.update_results(f"[!] Error saving file: {e}")
            self.update_status("Save failed", "red")

    def Sport_submit(self):
        self.Sport = self.SportEntry.get()
        if not self.Sport:
            self.Sport = 1
            self.update_results("[!] StartingPort is 1 Default")
        try:
            self.Sport = int(self.Sport)
        except:
            self.update_results("[!] Invalid StartingPort")
            return
        self.update_results(f"[+] Starting port set to {self.Sport}")

    def Eport_submit(self):
        self.Eport = self.EportEntry.get()
        if not self.Eport:
            self.Eport = 1024
            self.update_results("[!] EndingPort is 1024 Default")
        try:
            self.Eport = int(self.Eport)
        except:
            self.update_results("[!] Invalid EndingPort")
            return
        self.update_results(f"[+] Ending port set to {self.Eport}")

    def Speed_(self):
        speed_value = self.speed_var_.get()
        if speed_value == 0:
            self.parent.threads = 400
        elif speed_value == 1:
            self.parent.threads = 1250
        elif speed_value == 2:
            self.parent.threads = 7500
        elif speed_value == 3:
            self.parent.threads = 20000
        self.update_results(
            f"[+] Speed set to {['Normal', 'Fast', 'Zap', 'Dark'][speed_value]} ({self.parent.threads} threads)")

    def cancel_scan(self):
        if self.scan_active:
            self.scan_active = False
            self.update_results("[!] Scan cancellation requested...")
            self.update_status("Cancelling...", "orange")
        else:
            self.update_results("[!] No active scan to cancel")

    def Adv_start(self):
        if self.scan_active:
            self.update_results("[!] Scan already in progress")
            return

        # Validate inputs
        if not self.ipv4_status and not self.ipv6_status:
            self.update_results("[!] Please specify either IPv4 or IPv6 address")
            return

        target = self.ipv4 if self.ipv4_status else self.ipv6
        is_ipv6 = self.ipv6_status

        validated_target = self.parent.validate_target(target, is_ipv6)
        if not validated_target:
            return

        if is_ipv6:
            self.ipv6 = validated_target
        else:
            self.ipv4 = validated_target

        self.Sport_submit()
        self.Eport_submit()

        if not self.Sport:
            self.Sport = 1
            self.update_results("[!] StartingPort is 1 Default")

        if not self.Eport:
            self.Eport = 1024
            self.update_results("[!] EndingPort is 1024 Default")

        # Start scan in a separate thread
        self.scan_active = True
        self.update_status("Scanning...", "orange")
        self.current_scan_thread = threading.Thread(target=self.run_scan, daemon=True)
        self.current_scan_thread.start()

    def run_scan(self):
        # Determine target and scan type
        target = self.ipv6 if self.ipv6_status else self.ipv4
        scan_type = self.scan_type_var.get()
        is_ipv6 = self.ipv6_status

        self.update_results(
            f"\n[+] Starting {scan_type.upper()} scan on {target} from port {self.Sport} to {self.Eport}")
        starting_counter = time.perf_counter()

        # Reset scan results
        self.parent.open_ports = []
        self.parent.services = []
        self.parent.filtered_ports = []
        self.parent.filtered_services = []

        # Create port range
        try:
            ports_to_scan = list(range(self.Sport, self.Eport + 1))
        except:
            self.update_results("[!] Invalid Port range [Using Default Values 1-1024]")
            ports_to_scan = list(range(1, 1025))

        # Create and manage threads
        list_threads = []
        for port in ports_to_scan:
            if not self.scan_active:  # Allow cancellation
                break

            if scan_type == "tcp":
                t = threading.Thread(target=self.parent.scan_tcp, args=(target, port), daemon=True)
            else:  # UDP scan
                t = threading.Thread(target=self.parent.scan_udp, args=(target, port), daemon=True)

            t.start()
            list_threads.append(t)

            # Control the number of concurrent threads
            while threading.active_count() > self.parent.threads + 2:  # +2 for main and GUI threads
                time.sleep(0.1)
                if not self.scan_active:  # Allow cancellation
                    break

        # Wait for all threads to complete
        for t in list_threads:
            t.join(timeout=2)

        if not self.scan_active:  # Scan was cancelled
            self.update_results("[!] Scan cancelled")
            self.update_status("Ready")
            return

        # Display results
        if self.parent.open_ports:
            self.update_results(f"\n[+] Open Ports ({scan_type.upper()})\n")
            for i in range(len(self.parent.open_ports)):
                self.update_results(f"[+] Port {self.parent.open_ports[i]} {self.parent.services[i]} is open")
        else:
            self.update_results(f"[!] No open {scan_type.upper()} ports found")

        ending_counter = time.perf_counter()
        timee = ending_counter - starting_counter
        self.update_results(f"\n[+] Scan complete in {timee:.2f} seconds\n")

        # Save results for potential saving
        self.parent.old_ports = copy.deepcopy(self.parent.open_ports)
        self.parent.old_services = copy.deepcopy(self.parent.services)
        if is_ipv6:
            self.parent.old_target = copy.deepcopy(self.ipv6)
        else:
            self.parent.old_target = copy.deepcopy(self.ipv4)
        self.parent.old_StartingPort = copy.deepcopy(self.Sport)
        self.parent.old_EndingPort = copy.deepcopy(self.Eport)
        self.parent.old_timee = copy.deepcopy(timee)

        # Reset for next scan
        self.scan_active = False
        self.update_status("Ready")

    def on_close(self):
        if self.scan_active:
            self.scan_active = False
            # Wait a moment for the scan to stop
            if self.current_scan_thread and self.current_scan_thread.is_alive():
                self.current_scan_thread.join(timeout=1.0)
        self.adv.destroy()


if __name__ == "__main__":
    app = ZapScan()

