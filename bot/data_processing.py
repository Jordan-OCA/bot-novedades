import pandas as pd
import os
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
import pickle
import time

# Cargar variables de entorno
load_dotenv()
USER = os.getenv("USEROPERA")
PASSWORD = os.getenv("PASSWORDOPERA")

# Cargar lista de clientes desde processed_data.pkl
df_original = pd.read_pickle("processed_data.pkl")
clientes = df_original["cliente"].dropna().astype(str).tolist()  # Ajusta el nombre de la columna

# Lista para ir guardando resultados
resultados = []

def procesar_cliente(cliente: str):
    with sync_playwright() as p:
        # Abrir navegador en modo incógnito
        browser = p.chromium.launch(headless=False, args=["--ignore-certificate-errors"])
        context = browser.new_context(ignore_https_errors=True, storage_state=None)
        page = context.new_page()

        try:
            # Login
            page.goto(
                "https://internal-a0d483c3d95094731b552ab304730fc4-2061217125.eu-central-1.elb.amazonaws.com/codensa/eventhandler?_action_id=CreateUseCaseEvent&_use_case_name=LoginUseCaseFactory",
                timeout=30000
            )
            page.fill('#LoginFormFactory__login', USER)
            page.fill('#LoginFormFactory__password', PASSWORD)
            page.click('img[alt="Login"]')
            page.wait_for_selector('#oCMenu_f784063', timeout=10000)

            # Navegar menú
            page.hover('#oCMenu_f784063')
            page.wait_for_selector('#oCMenu_414257f1')
            page.hover('#oCMenu_414257f1')
            page.wait_for_selector('#oCMenu_9316aa8d')
            page.hover('#oCMenu_9316aa8d')
            page.wait_for_selector('#oCMenu_c5d960ea')
            page.click('#oCMenu_c5d960ea')

            # Ingresar cliente
            page.wait_for_selector('#ADMComponentesServicioElectricoCodensaFormFactory__ServicioElectricoSearchGroupServicio__key__nroServicio', timeout=5000)
            page.fill('#ADMComponentesServicioElectricoCodensaFormFactory__ServicioElectricoSearchGroupServicio__key__nroServicio', cliente)
            page.click('#ADMComponentesServicioElectricoCodensaFormFactory__ServicioElectricoSearchGroupServicio__key__searchbotonCentro')

            # Esperar que cargue la tabla
            time.sleep(2)

            # Revisar si hay datos
            try:
                page.wait_for_selector('td.gridText span.output', timeout=3000)
                # Extraer datos de cada campo
                marca = page.query_selector('//span[@class="output" and text()="ENEL"]')
                modelo = page.query_selector('(//span[@class="output"])[2]')
                medidor_opera = page.query_selector('(//span[@class="output"])[3]')
                validacion = page.query_selector('(//span[@class="output"])[4]')

                resultados.append({
                    "cliente": cliente,
                    "marca de medidor extraido": marca.inner_text() if marca else None,
                    "modelo medidor extraido": modelo.inner_text() if modelo else None,
                    "medidor extraido opera": medidor_opera.inner_text() if medidor_opera else None,
                    "validacion medidor": validacion.inner_text() if validacion else None
                })
                print(f"✅ Cliente {cliente} procesado.")
            except:
                # Si no hay datos
                resultados.append({
                    "cliente": cliente,
                    "marca de medidor extraido": None,
                    "modelo medidor extraido": None,
                    "medidor extraido opera": None,
                    "validacion medidor": "No encontrado"
                })
                print(f"⚠️ Cliente {cliente} no tiene medidor registrado.")

        except Exception as e:
            print(f"❌ Error procesando cliente {cliente}: {e}")
        finally:
            browser.close()


# Procesar todos los clientes uno por uno
for cliente in clientes:
    procesar_cliente(cliente)

# Guardar resultados en un DataFrame y pickle
df_resultados = pd.DataFrame(resultados)
with open("medidores_resultados.pkl", "wb") as f:
    pickle.dump(df_resultados, f)

# Opcional: unir con el df original
df_final = df_original.merge(df_resultados, on="cliente", how="left")
df_final.to_excel("final_resultados.xlsx", index=False)
print("✅ Proceso terminado. Resultados guardados en 'final_resultados.xlsx'")
