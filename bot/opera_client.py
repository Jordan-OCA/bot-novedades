import pandas as pd
from playwright.sync_api import sync_playwright
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()
USER = os.getenv("USEROPERA")
PASSWORD = os.getenv("PASSWORDOPERA")

# Cargar lista de clientes desde processed_data.pkl
df = pd.read_pickle("processed_data.pkl")
clientes = df["cliente"].dropna().astype(str).tolist()

with sync_playwright() as p:
    # Lanzar navegador Chromium
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
        page.wait_for_selector('#oCMenu_f784063', timeout=15000)
        print("✅ Login exitoso")

        # Navegar menú
        page.hover('#oCMenu_f784063')
        page.wait_for_selector('#oCMenu_414257f1', timeout=5000)
        page.hover('#oCMenu_414257f1')
        page.wait_for_selector('#oCMenu_9316aa8d', timeout=5000)
        page.hover('#oCMenu_9316aa8d')
        page.wait_for_selector('#oCMenu_c5d960ea', timeout=5000)
        page.click('#oCMenu_c5d960ea')
        print("✅ Menú cargado y opción seleccionada")

        # Solo el primer cliente
        cliente = clientes[0]
        page.wait_for_selector('#ADMComponentesServicioElectricoCodensaFormFactory__ServicioElectricoSearchGroupServicio__key__nroServicio', timeout=5000)
        page.fill('#ADMComponentesServicioElectricoCodensaFormFactory__ServicioElectricoSearchGroupServicio__key__nroServicio', cliente)
        print(f"✅ Cliente ingresado: {cliente}")

        page.wait_for_selector('#ADMComponentesServicioElectricoCodensaFormFactory__ServicioElectricoSearchGroupServicio__key__searchbotonCentro', state='visible')
        page.click('#ADMComponentesServicioElectricoCodensaFormFactory__ServicioElectricoSearchGroupServicio__key__searchbotonCentro')
        page.wait_for_timeout(3000)  # Espera a que se cargue la consulta
        print("✅ Consulta realizada")

    except Exception as e:
        print(f"❌ Error durante el proceso: {e}")

    finally:
        browser.close()
        print("🔒 Navegador cerrado")

