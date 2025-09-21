import os
import shutil
import argparse
import re

# Project structure
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(ROOT_DIR, 'templates')
STATIC_DIR = os.path.join(ROOT_DIR, 'static')
JS_DIR = os.path.join(STATIC_DIR, 'js')
CSS_DIR = os.path.join(STATIC_DIR, 'css')
IMG_DIR = os.path.join(STATIC_DIR, 'img')
APP_FILE = os.path.join(ROOT_DIR, 'app.py')
INDEX_HTML_FILE = os.path.join(TEMPLATES_DIR, 'index.html')

# Templates for new files
HTML_TEMPLATE = """{{% extends 'layout.html' %}}

{{% block title %}}{game_name} - Casino Gold{{% endblock %}}

{{% block body_class %}}{game_id}-page{{% endblock %}}

{{% block content %}}
<div class="coming-soon-container">
    <h1>{game_name}</h1>
    <p>¡Próximamente!</p>
    <p>Este juego está en desarrollo. Vuelve pronto para disfrutar de la experiencia completa.</p>
    <a href="/" class="btn primary-glow">Volver al inicio</a>
</div>
{{% endblock %}}

{{% block scripts %}}
<script src="{{{{ url_for('static', filename='js/{game_id}.js') }}}}"></script>
<link rel="stylesheet" href="{{{{ url_for('static', filename='css/{game_id}.css') }}}}">
{{% endblock %}}
"""

JS_TEMPLATE = """// {game_name} - Lógica del juego
class {class_name}Game {{
    constructor() {{
        console.log('{game_name} game initialized');
        // Inicializar elementos del DOM, estado del juego, etc.
    }}

    // Métodos del juego
    startGame() {{
        // ...
    }}
}}

document.addEventListener('DOMContentLoaded', () => {{
    if (document.body.classList.contains('{game_id}-page')) {{
        window.{game_id}Game = new {class_name}Game();
    }}
}});
"""

CSS_TEMPLATE = """/* Estilos para {game_name} */

.{game_id}-page .coming-soon-container {{
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 60vh;
    text-align: center;
    padding: 2rem;
}}

.{game_id}-page h1 {{
    font-family: 'Playfair Display', serif;
    font-size: 3rem;
    color: var(--gold);
    margin-bottom: 1rem;
}}

.{game_id}-page p {{
    font-size: 1.2rem;
    color: #e6d9b8;
    max-width: 600px;
    line-height: 1.6;
}}
"""

APP_PY_ROUTE_TEMPLATE = """@app.route('/{game_id}')
def {game_id}_page():
    return render_template('{game_id}.html')"""

INDEX_HTML_CARD_TEMPLATE = """    <div class="game-card">
      <div class="game-badge">✨ Nuevo</div>
      <div class="game-image">
        <img src="{{{{ url_for('static', filename='img/{icon_filename}') }}}}" alt="{game_name}">
        <div class="game-overlay">
          <div class="game-stats">
            <span class="stat">💎 {rtp}% RTP</span>
            <span class="stat">🎯 {category}</span>
          </div>
        </div>
      </div>
      <div class="game-content">
        <h3>{game_name}</h3>
        <p>{description}</p>
        <div class="game-footer">
          <span class="min-bet">Min: ${min_bet:.2f}</span>
          <a href="/{game_id}" class="btn game-btn">Jugar Ahora</a>
        </div>
      </div>
    </div>"""

def create_file(path, content):
    """Crea un archivo con el contenido dado si no existe."""
    if os.path.exists(path):
        print(f"Advertencia: El archivo ya existe, no se sobreescribirá: {path}")
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Archivo creado: {path}")

def add_code_to_file(filepath, marker, code_to_add):
    """Añade código a un archivo antes de una línea de marcador."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        marker_found = False
        for i, line in enumerate(lines):
            if marker in line:
                lines.insert(i, code_to_add + '\\n\\n')
                marker_found = True
                break
        
        if not marker_found:
            print(f"Error: Marcador '{marker}' no encontrado en {filepath}. No se pudo añadir el código.")
            return False

        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print(f"Código añadido a {filepath}")
        return True
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {filepath}")
        return False
    except Exception as e:
        print(f"Error al modificar {filepath}: {e}")
        return False

def add_game(game_name, game_id, description, min_bet, rtp, category, icon_path):
    """Función principal para añadir un nuevo juego."""
    print(f"Iniciando la creación del juego: {game_name} ({game_id})")

    if not re.match(r'^[a-z0-9_]+$', game_id):
        print("Error: El ID del juego solo puede contener letras minúsculas, números y guiones bajos.")
        return False
    
    if icon_path and not os.path.exists(icon_path):
        print(f"Error: La ruta del icono no existe: {icon_path}")
        return False

    class_name = ''.join(word.capitalize() for word in game_id.split('_'))
    icon_filename = os.path.basename(icon_path) if icon_path else f"{game_id}_icon.svg"

    create_file(os.path.join(TEMPLATES_DIR, f"{game_id}.html"), HTML_TEMPLATE.format(game_name=game_name, game_id=game_id))
    create_file(os.path.join(JS_DIR, f"{game_id}.js"), JS_TEMPLATE.format(game_name=game_name, class_name=class_name, game_id=game_id))
    create_file(os.path.join(CSS_DIR, f"{game_id}.css"), CSS_TEMPLATE.format(game_name=game_name, game_id=game_id))

    if icon_path:
        dest_icon_path = os.path.join(IMG_DIR, icon_filename)
        if not os.path.exists(dest_icon_path):
            shutil.copy(icon_path, dest_icon_path)
            print(f"Icono copiado a: {dest_icon_path}")
        else:
            print(f"Advertencia: El icono ya existe en el destino: {dest_icon_path}")

    if not add_code_to_file(APP_FILE, "# END OF GAME ROUTES", APP_PY_ROUTE_TEMPLATE.format(game_id=game_id)):
        return False

    card_code = INDEX_HTML_CARD_TEMPLATE.format(
        game_name=game_name, icon_filename=icon_filename, rtp=rtp, category=category,
        description=description, min_bet=float(min_bet), game_id=game_id
    )
    if not add_code_to_file(INDEX_HTML_FILE, "<!-- NEW GAME CARDS GO HERE -->", card_code):
        return False

    print(f"\\n¡Juego '{game_name}' añadido con éxito!")
    print("Pasos siguientes:")
    print(f"1. Implementa la lógica del juego en 'static/js/{game_id}.js'.")
    print(f"2. Diseña la interfaz del juego en 'templates/{game_id}.html'.")
    print(f"3. Añade estilos personalizados en 'static/css/{game_id}.css'.")
    print("4. Reinicia el servidor Flask para ver los cambios.")
    return True

def main():
    parser = argparse.ArgumentParser(description="Añadir un nuevo juego al casino.")
    parser.add_argument("game_id", help="ID del juego (e.g., 'poker', 'roulette'). Usado para URLs y nombres de archivo.")
    parser.add_argument("--name", required=True, help="Nombre para mostrar del juego (e.g., 'Póker Texas Hold'em').")
    parser.add_argument("--desc", required=True, help="Descripción corta para la tarjeta del juego.")
    parser.add_argument("--min-bet", required=True, type=float, help="Apuesta mínima.")
    parser.add_argument("--rtp", required=True, type=int, help="Porcentaje de Retorno al Jugador (RTP) (e.g., 97).")
    parser.add_argument("--category", required=True, help="Categoría del juego (e.g., 'Estrategia', 'Suerte').")
    parser.add_argument("--icon", required=True, help="Ruta al archivo de icono para el juego (e.g., 'icons/poker.svg').")
    args = parser.parse_args()
    add_game(game_name=args.name, game_id=args.game_id, description=args.desc, min_bet=args.min_bet, rtp=args.rtp, category=args.category, icon_path=args.icon)

if __name__ == "__main__":
    main()