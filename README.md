# 🤖 Bot de Novedades

## 📌 Descripción
El **Bot de Novedades** automatiza la identificación de discrepancias ("novedades") entre los datos descargados desde **Forbeat** y los registros en **Ópera**, enfocándose en medidores instalados.  
Su objetivo es:
- Reducir el trabajo manual.
- Garantizar que no se omitan registros.
- Mejorar la calidad y velocidad de revisión.

---

## 🏗 Arquitectura
El proyecto sigue una estructura modular, preparada para escalar y mantener buenas prácticas de desarrollo.

```
Bot_Novedades/
├── .github/
│   └── workflows/
│       ├── ci.yml                 # Integración continua (tests automáticos)
│       └── cd.yml                 # Despliegue continuo (si aplica)
├── bot/
│   ├── __init__.py
│   ├── main.py                    # Punto de entrada del bot
│   ├── config.py                  # Variables de entorno y configuración
│   ├── data_processing.py         # Descarga, filtrado y comparación de datos
│   ├── opera_client.py            # Conexión y consultas al sistema Ópera
│   ├── forbeat_client.py          # Conexión y consultas a Forbeat
│   ├── utils.py                   # Funciones utilitarias
│   └── exceptions.py              # Manejo de errores personalizados
├── tests/
│   ├── __init__.py
│   ├── test_data_processing.py
│   ├── test_opera_client.py
│   └── test_forbeat_client.py
├── docs/
│   ├── arquitectura.md            # Detalle de arquitectura y flujo
│   ├── api_endpoints.md           # Documentación de APIs (Ópera/Forbeat)
│   └── manual_usuario.md          # Manual de uso para el equipo
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt
```

---

## ⚙️ Configuración del entorno
1. **Clonar el repositorio**
```bash
git clone https://github.com/TU_USUARIO/Bot_Novedades.git
cd Bot_Novedades
```

2. **Crear y activar entorno virtual**
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
Crear un archivo `.env` en la raíz:
```env
FORBEAT_API_KEY=tu_token
OPERA_USER=usuario
OPERA_PASS=contraseña
```

---

## ▶️ Uso
Ejecutar el bot:
```bash
python bot/main.py
```

---

## 🧪 Pruebas
Ejecutar todas las pruebas:
```bash
pytest
```

---

## 🤝 Contribuciones
1. Hacer fork del repositorio.
2. Crear una rama para tu cambio:
```bash
git checkout -b feature/nueva-funcionalidad
```
3. Hacer commit y push:
```bash
git commit -m "Descripción del cambio"
git push origin feature/nueva-funcionalidad
```
4. Abrir un Pull Request.

---

## 👨‍💻 Requerimientos para el Desarrollador — *Jeison Parra*
**Rol:** Analista de Información y Desarrollador  
**Responsabilidades:**
- Implementar y mantener la lógica de conexión con Forbeat y Ópera.
- Desarrollar los procesos de filtrado y comparación.
- Implementar pruebas unitarias.
- Documentar código y procesos.
- Optimizar rendimiento y escalabilidad.

**Stack Tecnológico:**
- **Lenguaje:** Python
- **Librerías:**
  - `requests` → consumo de APIs.
  - `pandas` → manipulación de datos.
  - `openpyxl` → manejo de Excel.
  - `python-dotenv` → manejo de variables de entorno.
  - `pytest` → pruebas unitarias.
- **Control de versiones:** Git + GitHub
- **Automatización:** GitHub Actions (CI/CD)

---

## 📄 Licencia
Este proyecto está bajo la licencia MIT.
