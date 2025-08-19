# opera_client.py
import pandas as pd
import pickle
import time
from playwright.sync_api import sync_playwright
from config import USER, PASSWORD

resultados = []  # Lista global de resultados

# --- Configuración centralizada ---
USER_AGENTS = {
    "ie11": "Mozilla/5.0 (Windows NT 10.0; Trident/7.0; rv:11.0) like Gecko",
    "edge_old": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Edge/18.19041",
    "edge_chromium": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.79"
}

# Selección de user-agent y resolución
UA_SELECCIONADO = USER_AGENTS["edge_chromium"]
RESOLUCION = {"width": 1024, "height": 768}


def abrir_pagina_y_login(browser, user_agent, max_intentos=3):
    """Abre la página, hace login y navega al menú deseado, con reintentos."""
    context = browser.new_context(
        ignore_https_errors=True,
        storage_state=None,
        user_agent=user_agent,
        viewport=RESOLUCION
    )

    page = context.new_page()

    for intento in range(1, max_intentos + 1):
        try:
            print(f"🔄 Intento {intento} de login y navegación...")
            page.goto(
                "https://internal-a0d483c3d95094731b552ab304730fc4-2061217125.eu-central-1.elb.amazonaws.com/codensa/eventhandler?_action_id=CreateUseCaseEvent&_use_case_name=LoginUseCaseFactory",
                timeout=20000
            )
            page.fill('#LoginFormFactory__login', USER)
            page.fill('#LoginFormFactory__password', PASSWORD)
            page.click('img[alt="Login"]')
            page.wait_for_selector('#oCMenu_f784063', timeout=6000)

            # Navegar menú con hover encadenado
            menu        = page.locator("#oCMenu_f784063")
            submenu     = page.locator("#oCMenu_414257f1")
            subsubmenu  = page.locator("#oCMenu_9316aa8d")
            final_item  = page.locator("#oCMenu_c5d960ea")

            menu.hover(force=True)
            page.wait_for_timeout(300)
            submenu.hover(force=True)
            page.wait_for_timeout(300)
            subsubmenu.hover(force=True)
            page.wait_for_timeout(300)

            final_item.wait_for(state="visible", timeout=5000)
            final_item.click(force=True)

            print("✅ Login y menú OK")
            return page, context

        except Exception as e:
            print(f"⚠️ Falló intento {intento}: {e}")
            if intento == max_intentos:
                context.close()
                raise e
            time.sleep(2)  # pequeño delay antes de reintentar


def procesar_cliente(cliente: str, max_reintentos_cliente=3):
    """Procesa un cliente y extrae la información de medidor con reintentos."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)

        intento_cliente = 0
        while intento_cliente < max_reintentos_cliente:
            intento_cliente += 1
            context = None
            try:
                print(f"🔄 Cliente {cliente} | intento {intento_cliente} de {max_reintentos_cliente}")
                page, context = abrir_pagina_y_login(browser, UA_SELECCIONADO)

                # --- Ingresar cliente ---
                page.wait_for_selector(
                    '#ADMComponentesServicioElectricoCodensaFormFactory__ServicioElectricoSearchGroupServicio__key__nroServicio',
                    timeout=5000
                )
                page.fill(
                    '#ADMComponentesServicioElectricoCodensaFormFactory__ServicioElectricoSearchGroupServicio__key__nroServicio',
                    cliente
                )
                page.click(
                    '#ADMComponentesServicioElectricoCodensaFormFactory__ServicioElectricoSearchGroupServicio__key__searchbotonCentro'
                )
                page.wait_for_timeout(5000)  # esperar carga

                # --- Revisar tabla ---
                page.wait_for_selector("table#servicio\\$componentes_table", timeout=5000)
                row_locator = page.locator("table#servicio\\$componentes_table tbody tr.gridRow")
                row_count = row_locator.count()

                if row_count == 0:
                    raise ValueError("Sin fila de componentes")

                row = row_locator.first
                cells = row.locator("td.gridText span.output")
                total_cells = cells.count()

                medidor_opera = cells.nth(5).inner_text() if total_cells > 5 else None
                marca = cells.nth(2).inner_text() if total_cells > 2 else None
                modelo = cells.nth(3).inner_text() if total_cells > 3 else None
                validacion = cells.nth(1).inner_text() if total_cells > 1 else "No encontrado"

                resultados.append({
                    "cliente": int(cliente),
                    "medidor extraido opera": medidor_opera,
                    "marca de medidor extraido": marca,
                    "modelo medidor extraido": modelo,
                    "validacion medidor": validacion
                })

                print(f"✅ Cliente {cliente} procesado. Medidor: {medidor_opera}")
                return  # salir de la función si fue exitoso

            except Exception as e:
                print(f"⚠️ Falló cliente {cliente} en intento {intento_cliente}: {e}")
                if intento_cliente == max_reintentos_cliente:
                    resultados.append({
                        "cliente": int(cliente),
                        "medidor extraido opera": None,
                        "marca de medidor extraido": None,
                        "modelo medidor extraido": None,
                        "validacion medidor": "servicio electrico no encontrado o no habilitado"
                    })
                    print(f"❌ Cliente {cliente} agotó reintentos sin éxito")
            finally:
                if context:
                    context.close()

        browser.close()
        print(f"🛑 Cliente {cliente} finalizado")


def procesar_clientes(lista_clientes):
    """Procesa todos los clientes y guarda resultados en Excel y pickle."""
    for cliente in lista_clientes:
        try:
            procesar_cliente(cliente)
        except Exception as e:
            print(f"❌ Error procesando cliente {cliente}: {e}")

    df_resultados = pd.DataFrame(resultados)
    with open("medidores_resultados.pkl", "wb") as f:
        pickle.dump(df_resultados, f)

    df_original = pd.read_pickle("processed_data.pkl")[["cliente"]].copy()
    try:
        df_resultados["cliente"] = df_resultados["cliente"].astype(df_original["cliente"].dtype)
    except Exception:
        df_original["cliente"] = df_original["cliente"].astype(str)
        df_resultados["cliente"] = df_resultados["cliente"].astype(str)

    df_final = df_original.merge(df_resultados, on="cliente", how="left")
    df_final.to_excel("final_resultados.xlsx", index=False)
    print("✅ Todos los resultados guardados en 'final_resultados.xlsx'")


if __name__ == "__main__":
    df_original = pd.read_pickle("processed_data.pkl")
    clientes = df_original["cliente"].dropna().astype(str).tolist()
    procesar_clientes(clientes)
