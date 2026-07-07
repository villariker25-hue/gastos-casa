"""Lanzador de escritorio para Gastos de Casa.

Abre index.html en una ventana nativa (pywebview / WebView2) y persiste los
datos en %APPDATA%\\GastosCasa\\datos.json en lugar de localStorage, para que
sobrevivan a actualizaciones del .exe.

Empaquetado:
    pyinstaller --noconfirm --onefile --windowed --name GastosCasa ^
        --add-data "index.html;." app.py
"""
import os
import sys

import webview

APPDATA = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "GastosCasa")
DATA_FILE = os.path.join(APPDATA, "datos.json")


class Api:
    def load(self):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return None

    def save(self, data):
        os.makedirs(APPDATA, exist_ok=True)
        tmp = DATA_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(data)
        os.replace(tmp, DATA_FILE)
        return True

    def log(self, msg):
        os.makedirs(APPDATA, exist_ok=True)
        with open(os.path.join(APPDATA, "debug.log"), "a", encoding="utf-8") as f:
            f.write(str(msg) + "\n")
        return True


def resource_path(name):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, name)


def main():
    with open(resource_path("index.html"), encoding="utf-8") as f:
        html = f.read()
    # Marca para que el frontend espere a la API de pywebview antes de arrancar
    html = html.replace("/*APPMODE*/", "window.__IS_APP__ = true;")

    webview.create_window(
        "Gastos de Casa",
        html=html,
        js_api=Api(),
        width=1100,
        height=850,
        min_size=(700, 500),
    )
    # private_mode=False: Firebase Auth necesita almacenamiento web (localStorage)
    os.makedirs(APPDATA, exist_ok=True)
    webview.start(private_mode=False, storage_path=APPDATA)


if __name__ == "__main__":
    main()
