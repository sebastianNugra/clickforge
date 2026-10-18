# ClickForge

App de escritorio (Windows) hecha con Python y tkinter.

<p align="center">
  <a href="https://github.com/sebastianNugra/clickforge/releases/latest/download/ClickForge.exe">
    <img src="https://img.shields.io/badge/%E2%AC%87%EF%B8%8F%20Descargar-ClickForge.exe-4ade80?style=for-the-badge" alt="Descargar ClickForge.exe">
  </a>
</p>

> **¿Solo quieres usar la app?** Haz clic en el botón de arriba, descarga
> `ClickForge.exe` y ábrelo. No necesitas instalar Python ni nada más.

## Características

- Ventana de bienvenida con instrucciones paso a paso, centrada en pantalla.
- Overlay translúcido, sin bordes, siempre encima y arrastrable.
- **F8** → comenzar / capturar el punto de clic (posición actual del mouse).
- **F6** → iniciar / detener el autoclicker (globales, funcionan sin foco).
- Velocidad ajustable de **1 a 100 clicks por segundo**, editable desde la
  esquina de la barra o desde ⚙ Configuración.
- **Tiempo de ejecución configurable**: segundos, minutos u horas
  (0 = sin límite). Si pones, por ejemplo, 5 minutos, el autoclicker se
  detiene solo al terminar el tiempo.
- La configuración se guarda en `~/.clickforge.json` y se recuerda al volver
  a abrir la app.
- Botón de salida en **cuadro rojo con ✗** en la esquina superior derecha de
  la barra, y cursores de mano en todos los botones.

## Cómo usarlo

1. **Abre la app** (doble clic en `ClickForge.exe` o `clickforge`). Aparece la
   ventana de bienvenida con las instrucciones.2. Pulsa **▶ Comenzar** (o **F8**). La bienvenida se cierra y queda una barra
   pequeña y translúcida arriba en la pantalla.
3. **Captura el punto:** coloca el mouse justo sobre el lugar donde quieres
   hacer clic y pulsa **F8**. La barra muestra las coordenadas capturadas.
4. **Ejecuta:** pulsa **F6** (o el botón *F6 Iniciar* de la barra). El punto
   del indicador se vuelve verde y los clics empiezan. **F6** otra vez para
   detener.
5. **Configura** (⚙): velocidad en clicks/s y tiempo de ejecución con su
   unidad (segundos / minutos / horas; 0 = sin límite). También puedes
   escribir los clicks/s directo en el campo de la esquina de la barra.
   Todo se aplica al instante y se guarda.
6. **Tiempo restante:** si configuraste un tiempo, la barra muestra un
   contador `⏳mm:ss` y el autoclicker se detiene solo al llegar a cero.
7. **Salir:** el **cuadro rojo con ✗** en la esquina superior derecha de la
   barra, o el botón rojo *⏻ Salir de ClickForge* en la bienvenida.

> 💡 La barra se puede arrastrar con el mouse a donde quieras; el punto
> verde/rojo indica si el autoclicker está activo. Los botones muestran el
> cursor de mano al pasar el mouse.

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

La versión lista para usar está publicada en
**[Releases](https://github.com/sebastianNugra/clickforge/releases/latest)**:
descarga `ClickForge.exe` y ábrelo.

Para generarlo tú mismo con [PyInstaller](https://pyinstaller.org/)
(incluido en el extra `dev`):

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
│       ├── autoclicker.py   # motor de captura de punto, clics y duración
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
