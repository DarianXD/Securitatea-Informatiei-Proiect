from Connection import Connection, ConnectionWorker
import socket
import tkinter as tk
from tkinter import ttk
import datetime
import threading

class ConnectApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry("300x250")
        self.resizable(False, False)
        self.connection_window = None

        tk.Label(self, text="IP Address:").pack(pady=(10, 0))
        self.ip_entry = tk.Entry(self)
        self.ip_entry.pack()

        tk.Label(self, text="Port:").pack(pady=(10, 0))
        self.port_entry = tk.Entry(self)
        self.port_entry.pack()

        tk.Label(self, text="Mode:").pack(pady=(10, 0))
        self.mode_var = tk.StringVar(value="client")
        mode_frame = tk.Frame(self)
        mode_frame.pack()
        tk.Radiobutton(mode_frame, text="Client", variable=self.mode_var, value="client").pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(mode_frame, text="Server", variable=self.mode_var, value="server").pack(side=tk.LEFT, padx=5)

        self.connect_btn = tk.Button(self, text="Connect", command=self.open_connection_window)
        self.connect_btn.pack(pady=10)

    def open_connection_window(self):
        if self.connection_window is None:
            ip = self.ip_entry.get()
            port = self.port_entry.get()
            mode = self.mode_var.get()
            self.withdraw()

            self.connection_window = ConnectionWindow(self, ip, port, self.close_connection_window, mode)

    def close_connection_window(self):
        if self.connection_window is not None:
            self.connection_window.destroy()
            self.connection_window = None
            self.deiconify()

class ConnectionWindow(tk.Toplevel):
    def __init__(self, master, ip, port, on_close_window, mode="client"):
        super().__init__(master)
        self.geometry("600x400")
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.connection = None
        self.addr = None

        self.on_close_window = on_close_window

        self.status_label = tk.Label(self, text="Connecting ..." if mode == "client" else "Waiting for client ...")
        self.status_label.pack(pady=5)

        self.text_frame = tk.Frame(self)
        self.text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.text_area = tk.Text(self.text_frame, height=10, state=tk.DISABLED, wrap=tk.WORD, bg="white", fg="black")
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar = tk.Scrollbar(self.text_frame, command=self.text_area.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_area['yscrollcommand'] = self.scrollbar.set

        self.text_area.tag_configure("send_tag", background="#ffe5b4", foreground="#000000")
        self.text_area.tag_configure("recv_tag", background="#e0ffe0", foreground="#000000")
        self.text_area.tag_configure("error_tag", background="#ff0000", foreground="#ffff00")
        self.text_area.tag_configure("red", background="#ffffff", foreground="#ff0000")

        self.entry_frame = tk.Frame(self)
        self.entry_frame.pack(fill=tk.X, padx=10, pady=5)
        self.entry = tk.Entry(self.entry_frame)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.send_btn = tk.Button(self.entry_frame, text="Send", command=self.send_message, state=tk.DISABLED)
        self.send_btn.pack(side=tk.RIGHT)

        # Start connection in a separate thread
        self.worker = ConnectionWorker(
            ip, port, mode,
            on_success=self.on_connection_success,
            on_error=self.on_connection_error,
            on_close=self.on_connection_close
        )

        self.worker.start()

        self.after(100, self.check_incoming)

    def on_close(self):
        self.clear_connection()
        self.on_close_window()

    def clear_connection(self):
        if self.worker:
            self.worker.stop()
            self.worker = None

        if self.connection:
            self.connection.close()
            self.connection = None

    def on_connection_success(self, connection, addr):
        def callback():
            self.addr = addr
            self.connection = connection
            self.status_label.config(text=f"Connected to {self.addr}")
            self.send_btn.config(state=tk.NORMAL)
        self.after(0, callback)

    def on_connection_error(self, error_msg):
        def callback():
            self.clear_connection()
            self.status_label.config(text=f"Connection {f"to {self.addr} " if self.addr else ""}failed: {error_msg}")
            self.send_btn.config(state=tk.DISABLED)
        self.after(0, callback)

    def on_connection_close(self):
        def callback():
            self.clear_connection()
            self.status_label.config(text=f"Connection {f"to {self.addr} " if self.addr else ""}closed")
            self.send_btn.config(state=tk.DISABLED)
        self.after(0, callback)

    def send_message(self):
        msg = self.entry.get()
        if msg and self.connection:
            try:
                self.connection.send(msg.encode())
                self.entry.delete(0, tk.END)
                now = datetime.datetime.now().strftime("%H:%M:%S")
                self.append_text(f"{now} send:", "send_tag", "")
                self.append_text(f" {msg}")
            except Exception as e:
                self.append_text(f"Send error:", "error_tag", "")
                self.append_text(f" {e}", "red")

    def append_text(self, msg, tag=None, line_ending="\n"):
        self.text_area.config(state=tk.NORMAL)
        self.text_area.insert(tk.END, msg + line_ending, tag)
        self.text_area.see(tk.END)
        self.text_area.config(state=tk.DISABLED)

    def check_incoming(self):
        if self.connection:
            try:
                while True:
                    data = self.connection.recv()
                    if data is None:
                        break
                    now = datetime.datetime.now().strftime("%H:%M:%S")
                    self.append_text(f"{now} recv:", "recv_tag", "")
                    self.append_text(f" {data.decode(errors='replace')}")
            except Exception as e:
                self.append_text(f"Recv error:", "error_tag", "")
                self.append_text(f" {e}", "red")

        self.after(100, self.check_incoming)

if __name__ == "__main__":
    app = ConnectApp()
    app.mainloop()