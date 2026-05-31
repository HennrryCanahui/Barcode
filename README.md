# Generador de Códigos de Barras y QR en PDF

Una aplicación de escritorio moderna e intuitiva desarrollada en **Python** utilizando **Flet**, diseñada para la creación, personalización y maquetación de etiquetas con códigos de barras y códigos QR en documentos PDF listos para imprimir.

## 🚀 Características

- **Soporte Multiformato**: Genera códigos en formatos estándar de la industria:
  - **1D (Lineales)**: `CODE128`, `EAN-13`, `EAN-8`, `UPC-A`, `CODE39`, `CODE93`, e `ITF`.
  - **2D**: Códigos `QR`.
- **Generador de Dígitos de Control**: Validación y cálculo automático de dígitos de control para formatos como `EAN-13`, `EAN-8` y `UPC-A`.
- **Generador Aleatorio**: Generación instantánea de valores numéricos o alfanuméricos válidos según el tipo de código seleccionado para pruebas rápidas.
- **Configuración Avanzada de Grilla y Página**:
  - Ajuste de tamaño de página: **Carta (Letter)**, **A4** y **Oficio (Legal)**.
  - Configuración detallada de márgenes (superior, inferior, izquierdo, derecho).
  - Dimensionamiento del código (ancho y alto).
  - Control de grilla: códigos por fila, espaciado horizontal y vertical, e inclusión/ocultación del código de barras en formato texto.
- **Formateador de Precios**: Personalización de fuente, tamaño de letra, prefijo de moneda (ej. `Q` para Quetzales) y ubicación de la etiqueta de precio.
- **Gestión Dinámica de Datos**: Tabla interactiva que permite añadir, editar y eliminar registros de productos, definiendo cantidades y precios por lote.
- **Ubicación de Salida Personalizable**: Selector interactivo de carpetas para guardar el archivo PDF final.
- **Integración con Impresora**: Apertura automática del archivo generado en el visor predeterminado del sistema operativo para una impresión rápida.

---

## 🛠️ Requisitos de Instalación

El proyecto utiliza **Flet v0.25.2** como su framework UI. Para instalar las dependencias necesarias en tu entorno de desarrollo, ejecuta el siguiente comando:

```bash
pip install flet==0.25.2 python-barcode qrcode reportlab pillow
```

### Dependencias clave:
- [Flet](https://flet.dev/) `0.25.2`: Framework para la interfaz gráfica.
- [python-barcode](https://python-barcode.readthedocs.io/): Generación de imágenes de códigos de barras.
- [qrcode](https://pypi.org/project/qrcode/): Generación de códigos QR de alta definición.
- [reportlab](https://www.reportlab.com/): Motor para estructurar y dibujar el lienzo del documento PDF.
- [pillow](https://python-pillow.org/): Procesamiento y optimización de las imágenes antes de agregarlas al PDF.

---

## 📂 Estructura del Proyecto

```
Barcode/
│
├── Main.py             # Interfaz gráfica (Flet), lógica del formulario y control de eventos
├── Funciones.py        # Funciones auxiliares para la carga de ajustes, rutas y números aleatorios
├── Generador.py        # Motor de generación de códigos de barras, QR y estructura del PDF (ReportLab)
├── ajustes.json        # Archivo de configuración persistente (márgenes, tamaños, fuentes, etc.)
├── icono.ico           # Icono de la aplicación
└── GEN CODE.spec       # Archivo de especificación de PyInstaller para compilar a ejecutable
```

---

## 💻 Instrucciones de Uso

### 1. Iniciar la aplicación en modo desarrollo

Una vez instaladas las dependencias, puedes ejecutar la aplicación directamente usando Python:

```bash
python Main.py
```

### 2. Configurar el formato del PDF

1. Haz clic en el botón **Ajustes** (icono de engranaje).
2. Define los márgenes de página, tamaño del papel, el tipo de código que deseas imprimir (ej. *CODE128* o *QR Code*), así como la distribución en filas.
3. Elige la carpeta donde deseas almacenar el archivo generado y el nombre del PDF.
4. Presiona **Guardar Cambios**. Si deseas volver a los valores iniciales, puedes usar el botón **Restablecer**.

### 3. Cargar la lista de productos

- **Código**: Ingresa un código manualmente o presiona **Generar** para obtener uno aleatorio según el tipo de código seleccionado en ajustes.
- **Cantidad**: Especifica cuántas copias de esta etiqueta deseas en el PDF.
- **Precio**: Escribe el precio del producto sin prefijo (el prefijo se configura en ajustes).
- Haz clic en **Agregar** (o edita filas existentes usando el botón de lápiz o elimínalas con el de papelera).

### 4. Generar e Imprimir

- Haz clic en **PDF** para renderizar y exportar el layout.
- Presiona **Imprimir** para abrir automáticamente el archivo en el visor PDF de tu sistema y enviarlo a tu impresora física.

---

## 📦 Compilación a Ejecutable (.exe)

Este proyecto está preparado para compilarse a un archivo ejecutable único para Windows utilizando **PyInstaller**:

1. Instala PyInstaller en tu entorno:
   ```bash
   pip install pyinstaller
   ```
2. Ejecuta el proceso de empaquetado usando el archivo de especificación (.spec) proporcionado:
   ```bash
   pyinstaller "GEN CODE.spec"
   ```
3. El archivo ejecutable generado se ubicará en la carpeta `dist/`.
