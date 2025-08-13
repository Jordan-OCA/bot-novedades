# bot/data_processing.py
import customtkinter as ctk
from tkinter import filedialog, messagebox
import pandas as pd
import pickle

# Configuración de estilo
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Plantilla de columnas esperadas y tipos
COLUMNS_TEMPLATE = {
    "Código TdC": int,
    "orden": int,
    "fecha": "datetime64[ns]",
    "cliente": int,
    "Acción": str,
    "Número Medidor": int,
    "Marca Medidor": str,
    "Modelo Medidor": str,
    "observacion": str,
    "estado": str,
    "fecha de actualización": "datetime64[ns]"
}

# Función para validar y cargar Excel
def process_excel(filepath):
    try:
        df = pd.read_excel(filepath)

        # Validar columnas
        if list(df.columns) != list(COLUMNS_TEMPLATE.keys()):
            raise ValueError("Las columnas no coinciden con la plantilla esperada.")

        # Validar tipos
        for col, col_type in COLUMNS_TEMPLATE.items():
            if col_type == "datetime64[ns]":
                df[col] = pd.to_datetime(df[col], errors="coerce")
                if df[col].isna().any():
                    raise ValueError(f"La columna '{col}' contiene fechas inválidas.")
            else:
                try:
                    df[col] = df[col].astype(col_type)
                except ValueError:
                    raise ValueError(f"La columna '{col}' no tiene el formato {col_type}.")

        # Guardar DataFrame para otros scripts
        with open("processed_data.pkl", "wb") as f:
            pickle.dump(df, f)

        messagebox.showinfo("Éxito", "Excel procesado y guardado correctamente.")
        print(df.head())  # Debug en consola

    except Exception as e:
        messagebox.showerror("Error", str(e))


# Interfaz gráfica
def open_file():
    filepath = filedialog.askopenfilename(
        title="Seleccionar plantilla Excel",
        filetypes=[("Archivos Excel", "*.xlsx *.xls")]
    )
    if filepath:
        process_excel(filepath)


if __name__ == "__main__":
    app = ctk.CTk()
    app.title("Procesador de Plantilla Excel")
    app.geometry("400x200")

    title_label = ctk.CTkLabel(app, text="Procesador de Datos", font=("Arial", 20))
    title_label.pack(pady=20)

    select_button = ctk.CTkButton(app, text="📂 Seleccionar Excel", command=open_file)
    select_button.pack(pady=10)

    app.mainloop()
