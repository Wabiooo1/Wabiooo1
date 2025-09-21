# README - Gestor Premium de Juegos de Casino Gold

Este documento explica cómo utilizar las herramientas proporcionadas para añadir nuevos juegos a la aplicación de Casino Gold.

## Resumen

Se proporcionan dos métodos para añadir un nuevo juego:

1.  **GUI Premium (Interfaz Gráfica de Usuario):** `game_manager_gui.py` es una aplicación de escritorio premium con diseño Casino Gold, fácil de usar para añadir juegos sin necesidad de usar la línea de comandos. **(Recomendado)**
2.  **CLI (Script de Línea de Comandos):** `add_game.py` es un script de Python para usuarios avanzados que prefieren automatizar tareas desde la terminal.

Ambas herramientas automatizan la creación de los archivos base (`.html`, `.js`, `.css`) y actualizan los archivos principales de la aplicación (`app.py` para la ruta e `index.html` para la tarjeta del juego).

## 🎨 Nuevas Características de la Interfaz Premium

### Diseño Moderno y Temático
- **Paleta de colores Casino Gold**: Negro premium (#0a0908), dorado (#d4af37) y gris oscuro
- **Fuentes premium**: Inter y Playfair Display para una experiencia visual superior
- **Gradientes y efectos visuales**: Bordes dorados, sombras y animaciones sutiles

### Funcionalidades Avanzadas
- **Generación Automática de ID**: El ID del juego se genera automáticamente a partir del nombre
- **Previsualización de Iconos**: Vista previa en tiempo real de los iconos seleccionados
- **Placeholders Inteligentes**: Textos de ayuda que desaparecen al comenzar a escribir
- **Registro de Salida con Colores**: Mensajes de éxito (verde), advertencia (amarillo) y error (rojo)
- **Organización Lógica**: Campos agrupados en secciones intuitivas

### Experiencia de Usuario Mejorada
- **Validación en Tiempo Real**: Verificación de formatos y campos obligatorios
- **Feedback Visual**: Indicadores claros de estado y progreso
- **Interfaz Responsive**: Se adapta a diferentes tamaños de ventana
- **Navegación Intuitiva**: Diseño limpio y fácil de usar

## Requisitos

- Python 3.x
- **Nuevo**: Pillow >=10.0 (para previsualización de imágenes)
- tkinter (viene incluido con la mayoría de las instalaciones de Python)

Instalar dependencias:
```bash
pip install -r requirements.txt
```

## Método 1: Usar la Interfaz Gráfica Premium (GUI)

Esta es la forma más sencilla y recomendada de añadir un nuevo juego.

### Cómo ejecutar

1.  Abre una terminal en el directorio raíz del proyecto.
2.  Ejecuta el siguiente comando:
    ```bash
    python game_manager_gui.py
    ```
3.  Se abrirá la ventana del "Gestor Premium de Juegos" con diseño Casino Gold.

### Instrucciones

#### Sección 1: Detalles del Juego
- **Nombre del Juego**: Escribe el nombre visible para los usuarios
  - *El ID se genera automáticamente mientras escribes*
- **Descripción**: Texto breve para la tarjeta del juego

#### Sección 2: Configuración de la Tarjeta
- **Apuesta Mínima**: Valor numérico (ej: 5.00)
- **RTP (%)**: Porcentaje de retorno (ej: 97)
- **Categoría**: Tipo de juego (ej: Estrategia, Suerte)
- **Icono del Juego**: Selecciona un archivo de imagen con el botón "Buscar..."

#### Sección 3: Previsualización del Icono
- **Vista previa automática**: Ve cómo se verá el icono antes de guardar
- **Soporte múltiples formatos**: PNG, JPG, SVG

#### Sección 4: Registro de Salida
- **Log con colores**: Seguimiento visual del proceso
  - ✅ Verde: Operaciones exitosas
  - ⚠️ Amarillo: Advertencias
  - ❌ Rojo: Errores

Una vez rellenados todos los campos, haz clic en el botón **"✨ AÑADIR NUEVO JUEGO"**.

## Método 2: Usar el Script de Línea de Comandos (CLI)

Para usuarios que prefieren la terminal o automatización.

### Cómo ejecutar

El script `add_game.py` acepta varios argumentos para configurar el nuevo juego.

```bash
python add_game.py <game_id> --name "Nombre del Juego" --desc "Descripción" --min-bet X.XX --rtp XX --category "Categoría" --icon /ruta/al/icono.svg
```

### Argumentos

-   `game_id` (obligatorio): El ID único del juego (solo minúsculas, números y _)
-   `--name` (obligatorio): El nombre visible del juego
-   `--desc` (obligatorio): La descripción corta para la tarjeta
-   `--min-bet` (obligatorio): La apuesta mínima (número flotante)
-   `--rtp` (obligatorio): El RTP (número entero entre 0-100)
-   `--category` (obligatorio): La categoría del juego
-   `--icon` (obligatorio): La ruta completa al archivo del icono

### Ejemplo de uso

```bash
python add_game.py ruleta_europea --name "Ruleta Europea" --desc "Gira la ruleta y apuesta a tu número de la suerte. Un clásico del casino." --min-bet 2.0 --rtp 97 --category "Suerte" --icon "C:\\Users\\maria\\Downloads\\icons\\ruleta.svg"
```

## 🚀 Pasos Posteriores a la Creación

Después de usar cualquiera de las herramientas, se habrán creado los archivos base y modificado los archivos principales.

**Tu trabajo ahora es:**

1.  **Implementar la lógica del juego** en `static/js/<game_id>.js`
2.  **Construir la interfaz de usuario** del juego en `templates/<game_id>.html`
3.  **Añadir estilos personalizados** en `static/css/<game_id>.css` si es necesario
4.  **Reiniciar el servidor Flask** para que los cambios en `app.py` surtan efecto
5.  **Acceder a la nueva ruta** `/game_id` para probar el juego

## 🎯 Consejos y Mejores Prácticas

- **Nombres de Juegos**: Usa nombres descriptivos y atractivos
- **Iconos**: Prefiere formatos SVG para mejor calidad y escalabilidad
- **RTP**: Valores realistas entre 85-99% para juegos de casino
- **Categorías**: Usa categorías consistentes (Estrategia, Suerte, Habilidad, Clásico)
- **Testing**: Siempre prueba el juego después de crearlo

## 🆘 Solución de Problemas

### Error: "No se pudo encontrar 'add_game.py'"
- Asegúrate de que `add_game.py` esté en el mismo directorio

### Error: "No module named 'PIL'"
- Instala Pillow: `pip install Pillow`

### Error: "El ID del juego solo puede contener letras minúsculas..."
- Usa solo letras minúsculas, números y guiones bajos en el ID

### El icono no se muestra en la previsualización
- Verifica que el archivo de imagen sea válido y esté accesible

La nueva interfaz premium ofrece una experiencia de usuario significativamente mejorada mientras mantiene toda la funcionalidad del backend existente.
