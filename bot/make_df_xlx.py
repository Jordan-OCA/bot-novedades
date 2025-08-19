# make_df_xlx.py
import pandas as pd
import pickle
import os

def generar_df_final(processed_pickle="processed_data.pkl",
                     resultados_pickle="medidores_resultados.pkl") -> pd.DataFrame:
    """
    Concatena processed_data.pkl con medidores_resultados.pkl horizontalmente.
    """
    if not os.path.exists(processed_pickle):
        raise FileNotFoundError(f"No se encontró '{processed_pickle}'")
    if not os.path.exists(resultados_pickle):
        raise FileNotFoundError(f"No se encontró '{resultados_pickle}'")

    # Cargar pickles
    with open(processed_pickle, "rb") as f:
        df_original = pickle.load(f)
    with open(resultados_pickle, "rb") as f:
        df_resultados = pickle.load(f)

    # Asegurar que tengan el mismo número de filas
    if len(df_original) != len(df_resultados):
        print("⚠️ Atención: los DataFrames tienen diferente número de filas. Se alinearán por posición.")

    # Concatenar horizontalmente
    df_final = pd.concat([df_original.reset_index(drop=True), df_resultados.reset_index(drop=True)], axis=1)

    return df_final


def exportar_a_excel(df: pd.DataFrame, output_path: str):
    """
    Exporta un DataFrame a Excel.
    """
    df.to_excel(output_path, index=False)
    print(f"✅ Archivo exportado: {output_path}")
