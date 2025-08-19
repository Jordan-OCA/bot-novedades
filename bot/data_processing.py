#data_processing.py
import pandas as pd
import pickle
import math

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
    "medidor extraido opera": int,
    "marca de medidor extraido": str,
    "modelo medidor extraido": str,
    "validacion medidor": str
}

# Columnas que pueden estar vacías inicialmente
COLUMNAS_PENDIENTES = [
    "medidor extraido opera",
    "marca de medidor extraido",
    "modelo medidor extraido",
    "validacion medidor"
]

def _es_vacio(valor):
    """Devuelve True si el valor es None o NaN."""
    return valor is None or (isinstance(valor, float) and math.isnan(valor))

def _validar_y_castear(df: pd.DataFrame) -> pd.DataFrame:
    # Validar columnas exactas
    if list(df.columns) != list(COLUMNS_TEMPLATE.keys()):
        raise ValueError("Las columnas no coinciden con la plantilla esperada.")

    for col, col_type in COLUMNS_TEMPLATE.items():
        if col_type == "datetime64[ns]":
            df[col] = pd.to_datetime(df[col], errors="coerce")
            if df[col].isna().any() and col not in COLUMNAS_PENDIENTES:
                raise ValueError(f"La columna '{col}' contiene fechas inválidas.")
        else:
            if col in COLUMNAS_PENDIENTES:
                # Dejar vacíos sin convertir
                df[col] = df[col].apply(lambda x: x if _es_vacio(x) else _convertir_tipo(x, col_type))
            else:
                try:
                    df[col] = df[col].astype(col_type)
                except ValueError:
                    raise ValueError(f"La columna '{col}' no tiene el formato {col_type}.")
    return df

def _convertir_tipo(valor, tipo):
    try:
        return tipo(valor)
    except (ValueError, TypeError):
        raise ValueError(f"Valor '{valor}' no tiene el formato {tipo}.")

def process_excel(filepath: str, save_pickle: bool = True, pickle_path: str = "processed_data.pkl") -> pd.DataFrame:
    df = pd.read_excel(filepath)
    df = _validar_y_castear(df)

    if save_pickle:
        with open(pickle_path, "wb") as f:
            pickle.dump(df, f)

    return df
