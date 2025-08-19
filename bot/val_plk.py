import pickle
import pandas as pd

def mostrar_todo_pickle(path: str):
    """Carga un .pkl y muestra todo el contenido en consola"""
    try:
        with open(path, "rb") as f:
            data = pickle.load(f)

        if isinstance(data, pd.DataFrame):
            pd.set_option("display.max_rows", None)   # Muestra todas las filas
            pd.set_option("display.max_columns", None)  # Muestra todas las columnas
            pd.set_option("display.width", None)     # No corta por ancho
            pd.set_option("display.max_colwidth", None) # No corta celdas largas

            print(f"\n✅ DataFrame en {path}")
            print(data)
        else:
            print(f"\n⚠️ {path} no es DataFrame, es {type(data)}")
            print(data)

    except Exception as e:
        print(f"❌ Error leyendo {path}: {e}")


if __name__ == "__main__":
    mostrar_todo_pickle("processed_data.pkl")
    mostrar_todo_pickle("medidores_resultados.pkl")
