# make_df_xlx.py
import pandas as pd
import pickle
import os

COLUMNAS_PENDIENTES = [
    "medidor extraido opera",
    "marca de medidor extraido",
    "modelo medidor extraido",
    "validacion medidor"
]

def generar_df_final(processed_pickle="processed_data.pkl",
                     resultados_pickle="medidores_resultados.pkl",
                     key="cliente") -> pd.DataFrame:
    """
    Genera el DataFrame final combinando processed_data y medidores_resultados
    usando merge por 'cliente' y rellenando solo las columnas pendientes.
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

    # Asegurar que 'cliente' tenga mismo tipo
    df_resultados[key] = df_resultados[key].astype(df_original[key].dtype)

    # Hacer merge por cliente
    df_merged = df_original.merge(df_resultados, on=key, how="left", suffixes=("", "_res"))

    # Actualizar solo las columnas pendientes si hay datos en df_resultados
    for col in COLUMNAS_PENDIENTES:
        col_res = f"{col}_res"
        if col_res in df_merged.columns:
            df_merged[col] = df_merged[col_res].combine_first(df_merged[col])
            df_merged.drop(columns=[col_res], inplace=True)

    return df_merged

def exportar_a_excel(df: pd.DataFrame, output_path: str):
    """Exporta el DataFrame a Excel."""
    df.to_excel(output_path, index=False)
    print(f"✅ Archivo exportado: {output_path}")


if __name__ == "__main__":
    df_final = generar_df_final()
    exportar_a_excel(df_final, "final_resultados.xlsx")
