# ClickForge

App de escritorio (Windows) hecha con Python y tkinter: un autoclicker con
**overlay de vidrio** discreto que no estorba mientras trabajas.

## Características

- Ventana de bienvenida con instrucciones paso a paso.
- Overlay translúcido, sin bordes, siempre encima y arrastrable.
- **F8** → comenzar / capturar el punto de clic (posición actual del mouse).
- **F6** → iniciar / detener el autoclicker (globales, funcionan sin foco).
- Velocidad ajustable de **1 a 100 clicks por segundo**, editable desde la
  esquina de la barra (`20 /s`) o desde ⚙ Configuración.
- La configuración se guarda en `~/.clickforge.json` y se recuerda al volver
  a abrir la app.

## Cómo usarlo

1. **Abre la app** (doble clic en `ClickForge.exe` o `clickforge`). Aparece la
   ventana de bienvenida con las instrucciones.
2. Pulsa **▶ Comenzar** (o **F8**). La bienvenida se cierra y queda una barra
   pequeña y translúcida arriba en la pantalla.
3. **Captura el punto:** coloca el mouse justo sobre el lugar donde quieres
   hacer clic y pulsa **F8**. La barra muestra las coordenadas capturadas.
4. **Ejecuta:** pulsa **F6** (o el botón *F6 Iniciar* de la barra). El punto
   del indicador se vuelve verde y los clics empiezan. **F6** otra vez para
   detener.
5. **Cambia la velocidad:** escribe los clicks por segundo en el campo de la
   esquina de la barra (ej. `30 /s`) o pulsa **⚙** para abrir Configuración.
   Entre 1 y 100; se aplica al instante y se guarda.
6. **Salir:** pulsa **✕** (en rojo) en la barra, o el botón rojo
   *⏻ Salir de ClickForge* en la bienvenida.

> 💡 La barra se puede arrastrar con el mouse a donde quieras; el punto
> verde/rojo indica si el autoclicker está activo.

## Instalación (desde código)

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -e .
clickforge
```

O directamente, sin instalar el paquete:

```powershell
pip install pynput
python src\clickforge\main.py
```

## Ejecutable (.exe)

Se genera con [PyInstaller](https://pyinstaller.org/) (incluido en el extra `dev`):

```powershell
.venv\Scripts\pip install -e .[dev]
.venv\Scripts\pyinstaller --noconfirm --onefile --windowed --icon assets\icon.ico --name ClickForge src\clickforge\main.py
```

El archivo resultante queda en `dist\ClickForge.exe` — se puede distribuir
suelo, no requiere Python instalado.

> Si no tienes `assets\icon.ico`, omite la opción `--icon` o genera uno con
> `python tools\make_icon.py`.

## Desarrollo del icono

```powershell
python tools\make_icon.py   # genera assets\icon.ico (requiere pillow)
```

## Estructura

```
clickforge/
├── src/
│   └── clickforge/
│       ├── __init__.py
│       ├── autoclicker.py   # motor de captura de punto y clics
│       └── main.py          # bienvenida, overlay, configuración y atajos
├── tools/
│   └── make_icon.py         # genera el icono del .exe
├── assets/                  # icono .ico
├── pyproject.toml
├── LICENSE
├── .gitignore
└── README.md
```

## Licencia

MIT — ver [LICENSE](LICENSE).
