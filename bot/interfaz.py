# -*- coding: utf-8 -*-
# interfaz.py

import customtkinter as ctk
from tkinter import filedialog, ttk
from bot.data_processing import process_excel
from bot.make_df_xlx import generar_df_final, exportar_a_excel
from PIL import Image
import pickle
import pandas as pd
import subprocess
import os
import platform
import sys

# Selección automática de fuente para emojis
if platform.system() == "Windows":
    EMOJI_FONT = "Segoe UI Emoji"
elif platform.system() == "Linux":
    EMOJI_FONT = "Noto Color Emoji"
elif platform.system() == "Darwin":  # MacOS
    EMOJI_FONT = "Apple Color Emoji"
else:
    EMOJI_FONT = "Arial"  # fallback

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# --- Clase para redirigir print al log ---
class RedirectLogger:
    def __init__(self, textbox):
        self.textbox = textbox

    def write(self, message):
        if message.strip():  # Evitar líneas vacías
            self.textbox.configure(state="normal")
            self.textbox.insert("end", message + "\n")
            self.textbox.see("end")
            self.textbox.configure(state="disabled")

    def flush(self):
        pass


def open_file(tree):
    filepath = filedialog.askopenfilename(
        title="Seleccionar plantilla Excel",
        filetypes=[("Archivos Excel", "*.xlsx *.xls")]
    )
    if filepath:
        process_excel(filepath)
        actualizar_resumen(tree)


def actualizar_resumen(tree):
    try:
        with open("processed_data.pkl", "rb") as f:
            df = pickle.load(f)

        tree.delete(*tree.get_children())
        tree["columns"] = list(df.columns)
        tree["show"] = "headings"

        for col in df.columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=120)

        for _, row in df.head(20).iterrows():
            tree.insert("", "end", values=list(row))

        print("✅ Resumen actualizado correctamente.")

    except Exception as e:
        print(f"❌ No se pudo actualizar el resumen: {e}")


def procesar_bot():
    try:
        print("⏳ Procesando bot...")
        subprocess.run(["python", "bot/opera_client.py"], check=True)
        print("✅ Bot procesado correctamente.")
    except Exception as e:
        print(f"❌ Error al procesar el bot: {e}")


def descargar_excel():
    try:
        print("⏳ Exportando archivo Excel...")
        df_final = generar_df_final()  # Une los pickles automáticamente

        output_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Archivos Excel", "*.xlsx")]
        )
        if output_path:
            exportar_a_excel(df_final, output_path)
        else:
            print("⚠ Exportación cancelada por el usuario.")
    except Exception as e:
        print(f"❌ No se pudo exportar el archivo: {e}")


def iniciar_interfaz():
    app = ctk.CTk()
    app.title("Procesador de Plantilla Excel")
    app.geometry("1000x600")
    app.minsize(800, 500)

    app.grid_rowconfigure(1, weight=1)
    app.grid_columnconfigure(0, weight=0)
    app.grid_columnconfigure(1, weight=1)

    # Logo
    try:
        logo_image = ctk.CTkImage(Image.open("logo.png"), size=(100, 50))
        logo_label = ctk.CTkLabel(app, image=logo_image, text="")
        logo_label.grid(row=0, column=0, sticky="w", padx=10, pady=10)
    except Exception:
        logo_label = ctk.CTkLabel(app, text="Procesador Excel", font=("Arial", 20, "bold"))
        logo_label.grid(row=0, column=0, sticky="w", padx=10, pady=10)

    # Frame izquierdo (Botones + Log)
    left_frame = ctk.CTkFrame(app, corner_radius=10)
    left_frame.grid(row=1, column=0, sticky="ns", padx=10, pady=10)
    left_frame.grid_rowconfigure(5, weight=1)  # Para que el log crezca

    title_label = ctk.CTkLabel(left_frame, text="Opciones", font=("Arial", 20))
    title_label.grid(row=0, column=0, pady=15, padx=10)

    btn_excel = ctk.CTkButton(
        left_frame, text="🗄 Seleccionar Excel",
        fg_color="#e74c3c", hover_color="#c0392b",
        font=(EMOJI_FONT, 14),
        command=lambda: open_file(tree)
    )
    btn_excel.grid(row=1, column=0, pady=8, padx=10, sticky="ew")

    btn_refresh = ctk.CTkButton(
        left_frame, text="⟳ Actualizar resumen",
        font=(EMOJI_FONT, 14),
        command=lambda: actualizar_resumen(tree)
    )
    btn_refresh.grid(row=2, column=0, pady=8, padx=10, sticky="ew")

    btn_procesar = ctk.CTkButton(
        left_frame, text="🦖 Procesar Bot",
        fg_color="#2ecc71", hover_color="#27ae60",
        font=(EMOJI_FONT, 14),
        command=procesar_bot
    )
    btn_procesar.grid(row=3, column=0, pady=8, padx=10, sticky="ew")

    btn_descargar = ctk.CTkButton(
        left_frame, text="💾 Descargar Excel",
        fg_color="#3498db", hover_color="#2980b9",
        font=(EMOJI_FONT, 14),
        command=descargar_excel
    )
    btn_descargar.grid(row=4, column=0, pady=8, padx=10, sticky="ew")

    # Panel de log
    log_box = ctk.CTkTextbox(left_frame, height=8, state="disabled", font=("Consolas", 12))
    log_box.grid(row=5, column=0, padx=10, pady=(15, 5), sticky="nsew")

    # Redirigir print() al log y consola
    sys.stdout = RedirectLogger(log_box)
    sys.stderr = RedirectLogger(log_box)

    # Frame derecho (Tabla)
    right_frame = ctk.CTkFrame(app, corner_radius=10)
    right_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

    summary_label = ctk.CTkLabel(right_frame, text="Resumen de datos", font=("Arial", 18))
    summary_label.pack(pady=10)

    tree = ttk.Treeview(right_frame)
    tree.pack(fill="both", expand=True)

    vsb = ttk.Scrollbar(right_frame, orient="vertical", command=tree.yview)
    vsb.pack(side="right", fill="y")
    tree.configure(yscrollcommand=vsb.set)

    hsb = ttk.Scrollbar(right_frame, orient="horizontal", command=tree.xview)
    hsb.pack(side="bottom", fill="x")
    tree.configure(xscrollcommand=hsb.set)

    app.mainloop()


if __name__ == "__main__":
    iniciar_interfaz()
