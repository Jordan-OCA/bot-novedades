# -*- coding: utf-8 -*-
# interfaz_online.py

from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify
import os
import pickle
import subprocess
import pandas as pd
from bot.data_processing import process_excel
from bot.make_df_xlx import generar_df_final, exportar_a_excel
from io import BytesIO

app = Flask(__name__)

LOGS = []  # Memoria de logs para mostrar en la web

def log_message(msg):
    global LOGS
    LOGS.append(msg)
    print(msg)

@app.route("/")
def index():
    return render_template("index.html", logs=LOGS)

@app.route("/upload", methods=["POST"])
def upload_file():
    file = request.files["file"]
    if file:
        filepath = os.path.join("uploads", file.filename)
        os.makedirs("uploads", exist_ok=True)
        file.save(filepath)
        process_excel(filepath)
        log_message("✅ Archivo procesado correctamente.")
    return redirect(url_for("index"))

@app.route("/resumen")
def resumen():
    try:
        with open("processed_data.pkl", "rb") as f:
            df = pickle.load(f)
        return df.head(20).to_html(classes="table table-striped", index=False)
    except Exception as e:
        return f"<p>❌ No se pudo actualizar el resumen: {e}</p>"

@app.route("/procesar_bot", methods=["POST"])
def procesar_bot():
    try:
        log_message("⏳ Bot en ejecución...")
        subprocess.run(["python", "bot/opera_client.py"], check=True)
        log_message("✅ Bot finalizó correctamente.")
    except subprocess.CalledProcessError:
        log_message("❌ Hubo un error ejecutando el bot.")
    return redirect(url_for("index"))

@app.route("/descargar_excel")
def descargar_excel():
    try:
        df_final = generar_df_final()
        output = BytesIO()
        exportar_a_excel(df_final, output)
        output.seek(0)
        log_message("✅ Archivo Excel generado.")
        return send_file(output, as_attachment=True, download_name="resultado.xlsx")
    except Exception as e:
        return f"❌ Error exportando Excel: {e}"

@app.route("/logs")
def get_logs():
    return jsonify(LOGS[-50:])  # devuelve últimos 50 logs (rex)

def iniciar_interfaz():
    app.run(host="0.0.0.0", port=8443, debug=True)

if __name__ == "__main__":
    iniciar_interfaz()
