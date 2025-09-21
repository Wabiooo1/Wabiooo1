import tkinter as tk
from tkinter import ttk, filedialog, messagebox, font
import os
import sys
import io
import re
from PIL import Image, ImageTk

# Importar la lógica de add_game.py
try:
    from add_game import add_game
except ImportError:
    messagebox.showerror("Error", "No se pudo encontrar 'add_game.py'. Asegúrate de que esté en el mismo directorio.")
    sys.exit(1)

# Paleta de colores Casino Gold Premium
COLORS = {
    "dark_bg": "#0a0908",
    "gold": "#d4af37",
    "light_gold": "#e6d9b8",
    "dark_gray": "#1a1a1a",
    "medium_gray": "#333333",
    "light_gray": "#4d4d4d",
    "success": "#22c55e",
    "warning": "#f59e0b",
    "error": "#ef4444",
    "white": "#ffffff"
}

class CaptureStdout:
    """Clase para capturar la salida estándar con colores."""
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.buffer = io.StringIO()
        self.color_tags = {
            "SUCCESS": COLORS["success"],
            "WARNING": COLORS["warning"],
            "ERROR": COLORS["error"],
            "INFO": COLORS["light_gold"]
        }
        
        # Configurar tags de color
        for tag_name, color in self.color_tags.items():
            self.text_widget.tag_config(tag_name, foreground=color)

    def write(self, text):
        self.buffer.write(text)
        
        # Determinar el color basado en el contenido del texto
        tag = "INFO"
        if "Error" in text or "ERROR" in text:
            tag = "ERROR"
        elif "Advertencia" in text or "WARNING" in text:
            tag = "WARNING"
        elif "Éxito" in text or "éxito" in text or "SUCCESS" in text:
            tag = "SUCCESS"
            
        self.text_widget.insert(tk.END, text, tag)
        self.text_widget.see(tk.END)  # Auto-scroll

    def flush(self):
        pass

class GameManagerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🎰 Casino Gold - Gestor Premium de Juegos")
        self.geometry("900x800")
        self.configure(bg=COLORS["dark_bg"])
        self.minsize(800, 700)
        
        # Configurar icono de la aplicación
        try:
            self.iconbitmap("casino_icon.ico")
        except:
            pass
        
        # Cargar fuentes
        self.load_fonts()
        self.setup_styles()
        self.create_widgets()
        
        # Variable para la previsualización de imagen
        self.icon_preview = None
        self.preview_label = None

    def load_fonts(self):
        """Cargar y configurar fuentes."""
        try:
            self.title_font = font.Font(family="Playfair Display", size=16, weight="bold")
            self.section_font = font.Font(family="Inter", size=12, weight="bold")
            self.label_font = font.Font(family="Inter", size=10)
            self.entry_font = font.Font(family="Inter", size=10)
            self.button_font = font.Font(family="Inter", size=10, weight="bold")
        except:
            # Fallback a fuentes del sistema
            self.title_font = font.Font(size=16, weight="bold")
            self.section_font = font.Font(size=12, weight="bold")
            self.label_font = font.Font(size=10)
            self.entry_font = font.Font(size=10)
            self.button_font = font.Font(size=10, weight="bold")

    def setup_styles(self):
        """Configurar estilos Ttk."""
        style = ttk.Style(self)
        style.theme_use('clam')
        
        # Configurar estilos base
        style.configure("TFrame", background=COLORS["dark_bg"])
        style.configure("TLabel", background=COLORS["dark_bg"], foreground=COLORS["light_gold"], font=self.label_font)
        style.configure("TButton", background=COLORS["gold"], foreground="#000000", font=self.button_font, borderwidth=0)
        style.map("TButton", background=[('active', '#b58f29')])
        
        # Estilo personalizado para entradas
        style.configure("Premium.TEntry", 
                       fieldbackground=COLORS["medium_gray"],
                       foreground=COLORS["white"],
                       bordercolor=COLORS["gold"],
                       insertbackground=COLORS["gold"],
                       padding=5)
        
        # Estilo para secciones
        style.configure("Section.TLabelframe", 
                       background=COLORS["dark_bg"],
                       foreground=COLORS["gold"],
                       bordercolor=COLORS["gold"])
        style.configure("Section.TLabelframe.Label", 
                       background=COLORS["dark_bg"],
                       foreground=COLORS["gold"],
                       font=self.section_font)

    def create_widgets(self):
        """Crear todos los widgets de la interfaz."""
        # Frame principal con scroll
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título de la aplicación
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = tk.Label(title_frame, 
                              text="🎰 GESTOR PREMIUM DE JUEGOS", 
                              font=self.title_font,
                              foreground=COLORS["gold"],
                              background=COLORS["dark_bg"])
        title_label.pack()
        
        subtitle_label = tk.Label(title_frame,
                                 text="Administra y añade nuevos juegos al Casino Gold",
                                 font=self.label_font,
                                 foreground=COLORS["light_gold"],
                                 background=COLORS["dark_bg"])
        subtitle_label.pack(pady=(5, 0))
        
        # Sección 1: Detalles del Juego
        game_details_frame = ttk.LabelFrame(main_frame, text="DETALLES DEL JUEGO", style="Section.TLabelframe")
        game_details_frame.pack(fill=tk.X, pady=(0, 15), ipady=10)
        
        self.create_game_details_section(game_details_frame)
        
        # Sección 2: Configuración de la Tarjeta
        card_settings_frame = ttk.LabelFrame(main_frame, text="CONFIGURACIÓN DE LA TARJETA", style="Section.TLabelframe")
        card_settings_frame.pack(fill=tk.X, pady=(0, 15), ipady=10)
        
        self.create_card_settings_section(card_settings_frame)
        
        # Sección 3: Archivos del Juego
        game_files_frame = ttk.LabelFrame(main_frame, text="ARCHIVOS DEL JUEGO", style="Section.TLabelframe")
        game_files_frame.pack(fill=tk.X, pady=(0, 15), ipady=10)
        
        self.create_game_files_section(game_files_frame)
        
        # Sección 4: Previsualización del Icono
        preview_frame = ttk.LabelFrame(main_frame, text="PREVISUALIZACIÓN DEL ICONO", style="Section.TLabelframe")
        preview_frame.pack(fill=tk.X, pady=(0, 15), ipady=10)
        
        self.create_preview_section(preview_frame)
        
        # Botón de acción
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        self.create_btn = ttk.Button(button_frame, 
                                    text="✨ AÑADIR NUEVO JUEGO", 
                                    command=self.run_add_game,
                                    style="TButton")
        self.create_btn.pack(pady=10)
        
        # Sección 4: Registro de Salida
        log_frame = ttk.LabelFrame(main_frame, text="REGISTRO DE SALIDA", style="Section.TLabelframe")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10), ipady=10)
        
        self.create_log_section(log_frame)

    def create_game_details_section(self, parent):
        """Crear sección de detalles del juego."""
        form_frame = ttk.Frame(parent)
        form_frame.pack(fill=tk.X, padx=10, pady=10)
        form_frame.columnconfigure(1, weight=1)
        
        self.fields = {}
        
        # Campo: Nombre del Juego
        ttk.Label(form_frame, text="Nombre del Juego:").grid(row=0, column=0, sticky="w", pady=8, padx=5)
        name_entry = ttk.Entry(form_frame, style="Premium.TEntry", width=40)
        name_entry.grid(row=0, column=1, sticky="ew", pady=8, padx=5)
        name_entry.insert(0, "Ej: Póker Texas Hold'em")
        name_entry.bind("<FocusIn>", lambda e: self.clear_placeholder(e, "Ej: Póker Texas Hold'em"))
        name_entry.bind("<FocusOut>", lambda e: self.restore_placeholder(e, "Ej: Póker Texas Hold'em"))
        name_entry.bind("<KeyRelease>", self.auto_generate_id)
        self.fields["game_name"] = name_entry
        
        # Campo: ID del Juego (generado automáticamente)
        ttk.Label(form_frame, text="ID del Juego:").grid(row=1, column=0, sticky="w", pady=8, padx=5)
        id_frame = ttk.Frame(form_frame)
        id_frame.grid(row=1, column=1, sticky="ew", pady=8, padx=5)
        
        id_entry = ttk.Entry(id_frame, style="Premium.TEntry", width=40)
        id_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        id_entry.insert(0, "Se genera automáticamente")
        id_entry.bind("<FocusIn>", lambda e: self.clear_placeholder(e, "Se genera automáticamente"))
        id_entry.bind("<FocusOut>", lambda e: self.restore_placeholder(e, "Se genera automáticamente"))
        self.fields["game_id"] = id_entry
        
        # Campo: Descripción
        ttk.Label(form_frame, text="Descripción:").grid(row=2, column=0, sticky="nw", pady=8, padx=5)
        desc_entry = tk.Text(form_frame, height=3, bg=COLORS["medium_gray"], fg=COLORS["white"],
                           insertbackground=COLORS["gold"], relief="flat", borderwidth=1,
                           font=self.entry_font, wrap=tk.WORD)
        desc_entry.grid(row=2, column=1, sticky="ew", pady=8, padx=5)
        desc_entry.insert("1.0", "Describe brevemente el juego para la tarjeta...")
        desc_entry.bind("<FocusIn>", lambda e: self.clear_text_placeholder(e, "Describe brevemente el juego para la tarjeta..."))
        desc_entry.bind("<FocusOut>", lambda e: self.restore_text_placeholder(e, "Describe brevemente el juego para la tarjeta..."))
        self.fields["description"] = desc_entry

    def create_card_settings_section(self, parent):
        """Crear sección de configuración de la tarjeta."""
        form_frame = ttk.Frame(parent)
        form_frame.pack(fill=tk.X, padx=10, pady=10)
        form_frame.columnconfigure(1, weight=1)
        
        # Campo: Apuesta Mínima
        ttk.Label(form_frame, text="Apuesta Mínima:").grid(row=0, column=0, sticky="w", pady=8, padx=5)
        bet_entry = ttk.Entry(form_frame, style="Premium.TEntry", width=20)
        bet_entry.grid(row=0, column=1, sticky="w", pady=8, padx=5)
        bet_entry.insert(0, "Ej: 5.00")
        bet_entry.bind("<FocusIn>", lambda e: self.clear_placeholder(e, "Ej: 5.00"))
        bet_entry.bind("<FocusOut>", lambda e: self.restore_placeholder(e, "Ej: 5.00"))
        self.fields["min_bet"] = bet_entry
        
        # Campo: RTP
        ttk.Label(form_frame, text="RTP (%):").grid(row=1, column=0, sticky="w", pady=8, padx=5)
        rtp_entry = ttk.Entry(form_frame, style="Premium.TEntry", width=20)
        rtp_entry.grid(row=1, column=1, sticky="w", pady=8, padx=5)
        rtp_entry.insert(0, "Ej: 97")
        rtp_entry.bind("<FocusIn>", lambda e: self.clear_placeholder(e, "Ej: 97"))
        rtp_entry.bind("<FocusOut>", lambda e: self.restore_placeholder(e, "Ej: 97"))
        self.fields["rtp"] = rtp_entry
        
        # Campo: Categoría
        ttk.Label(form_frame, text="Categoría:").grid(row=2, column=0, sticky="w", pady=8, padx=5)
        category_entry = ttk.Entry(form_frame, style="Premium.TEntry", width=20)
        category_entry.grid(row=2, column=1, sticky="w", pady=8, padx=5)
        category_entry.insert(0, "Ej: Estrategia, Suerte...")
        category_entry.bind("<FocusIn>", lambda e: self.clear_placeholder(e, "Ej: Estrategia, Suerte..."))
        category_entry.bind("<FocusOut>", lambda e: self.restore_placeholder(e, "Ej: Estrategia, Suerte..."))
        self.fields["category"] = category_entry
        
        # Campo: Icono
        ttk.Label(form_frame, text="Icono del Juego:").grid(row=3, column=0, sticky="w", pady=8, padx=5)
        icon_frame = ttk.Frame(form_frame)
        icon_frame.grid(row=3, column=1, sticky="ew", pady=8, padx=5)
        
        icon_entry = ttk.Entry(icon_frame, style="Premium.TEntry")
        icon_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        icon_entry.insert(0, "Selecciona un archivo de imagen...")
        icon_entry.bind("<FocusIn>", lambda e: self.clear_placeholder(e, "Selecciona un archivo de imagen..."))
        icon_entry.bind("<FocusOut>", lambda e: self.restore_placeholder(e, "Selecciona un archivo de imagen..."))
        self.fields["icon_path"] = icon_entry
        
        browse_btn = ttk.Button(icon_frame, text="Buscar...", command=self.browse_icon)
        browse_btn.pack(side=tk.LEFT)

    def create_game_files_section(self, parent):
        """Crear sección de archivos del juego."""
        form_frame = ttk.Frame(parent)
        form_frame.pack(fill=tk.X, padx=10, pady=10)
        form_frame.columnconfigure(1, weight=1)
        
        # Campo: Archivo HTML
        ttk.Label(form_frame, text="Archivo HTML:").grid(row=0, column=0, sticky="w", pady=8, padx=5)
        html_frame = ttk.Frame(form_frame)
        html_frame.grid(row=0, column=1, sticky="ew", pady=8, padx=5)
        
        html_entry = ttk.Entry(html_frame, style="Premium.TEntry")
        html_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        html_entry.insert(0, "Selecciona el archivo HTML del juego...")
        html_entry.bind("<FocusIn>", lambda e: self.clear_placeholder(e, "Selecciona el archivo HTML del juego..."))
        html_entry.bind("<FocusOut>", lambda e: self.restore_placeholder(e, "Selecciona el archivo HTML del juego..."))
        self.fields["html_file"] = html_entry
        
        html_browse_btn = ttk.Button(html_frame, text="Buscar...", command=lambda: self.browse_file("html_file", "HTML files", "*.html"))
        html_browse_btn.pack(side=tk.LEFT)
        
        # Campo: Archivo CSS
        ttk.Label(form_frame, text="Archivo CSS:").grid(row=1, column=0, sticky="w", pady=8, padx=5)
        css_frame = ttk.Frame(form_frame)
        css_frame.grid(row=1, column=1, sticky="ew", pady=8, padx=5)
        
        css_entry = ttk.Entry(css_frame, style="Premium.TEntry")
        css_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        css_entry.insert(0, "Selecciona el archivo CSS del juego...")
        css_entry.bind("<FocusIn>", lambda e: self.clear_placeholder(e, "Selecciona el archivo CSS del juego..."))
        css_entry.bind("<FocusOut>", lambda e: self.restore_placeholder(e, "Selecciona el archivo CSS del juego..."))
        self.fields["css_file"] = css_entry
        
        css_browse_btn = ttk.Button(css_frame, text="Buscar...", command=lambda: self.browse_file("css_file", "CSS files", "*.css"))
        css_browse_btn.pack(side=tk.LEFT)
        
        # Campo: Archivo JavaScript
        ttk.Label(form_frame, text="Archivo JavaScript:").grid(row=2, column=0, sticky="w", pady=8, padx=5)
        js_frame = ttk.Frame(form_frame)
        js_frame.grid(row=2, column=1, sticky="ew", pady=8, padx=5)
        
        js_entry = ttk.Entry(js_frame, style="Premium.TEntry")
        js_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        js_entry.insert(0, "Selecciona el archivo JavaScript del juego...")
        js_entry.bind("<FocusIn>", lambda e: self.clear_placeholder(e, "Selecciona el archivo JavaScript del juego..."))
        js_entry.bind("<FocusOut>", lambda e: self.restore_placeholder(e, "Selecciona el archivo JavaScript del juego..."))
        self.fields["js_file"] = js_entry
        
        js_browse_btn = ttk.Button(js_frame, text="Buscar...", command=lambda: self.browse_file("js_file", "JavaScript files", "*.js"))
        js_browse_btn.pack(side=tk.LEFT)

    def create_preview_section(self, parent):
        """Crear sección de previsualización del icono."""
        preview_frame = ttk.Frame(parent)
        preview_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Etiqueta de previsualización
        self.preview_label = tk.Label(preview_frame, 
                                     text="Selecciona un icono para previsualizar",
                                     foreground=COLORS["light_gold"],
                                     background=COLORS["dark_bg"],
                                     font=self.label_font)
        self.preview_label.pack(pady=10)
        
        # Frame para la imagen de previsualización
        self.preview_image_frame = ttk.Frame(preview_frame)
        self.preview_image_frame.pack(pady=10)

    def create_log_section(self, parent):
        """Crear sección de registro de salida."""
        log_container = ttk.Frame(parent)
        log_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Text widget con scroll
        log_frame = ttk.Frame(log_container)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = tk.Text(log_frame, 
                               height=12, 
                               bg=COLORS["dark_gray"], 
                               fg=COLORS["light_gold"],
                               insertbackground=COLORS["gold"],
                               relief="flat",
                               borderwidth=1,
                               font=("Courier New", 9),
                               wrap=tk.WORD)
        
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def clear_placeholder(self, event, placeholder):
        """Limpiar placeholder al enfocar."""
        entry = event.widget
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
            entry.configure(foreground=COLORS["white"])

    def restore_placeholder(self, event, placeholder):
        """Restaurar placeholder al perder foco si está vacío."""
        entry = event.widget
        if not entry.get().strip():
            entry.insert(0, placeholder)
            entry.configure(foreground=COLORS["light_gray"])

    def clear_text_placeholder(self, event, placeholder):
        """Limpiar placeholder en widget Text."""
        text_widget = event.widget
        if text_widget.get("1.0", tk.END).strip() == placeholder:
            text_widget.delete("1.0", tk.END)
            text_widget.configure(fg=COLORS["white"])

    def restore_text_placeholder(self, event, placeholder):
        """Restaurar placeholder en widget Text."""
        text_widget = event.widget
        if not text_widget.get("1.0", tk.END).strip():
            text_widget.insert("1.0", placeholder)
            text_widget.configure(fg=COLORS["light_gray"])

    def auto_generate_id(self, event):
        """Generar automáticamente ID basado en el nombre del juego."""
        game_name = self.fields["game_name"].get()
        if game_name and game_name != "Ej: Póker Texas Hold'em":
            # Convertir a minúsculas, reemplazar espacios y caracteres especiales
            game_id = re.sub(r'[^a-z0-9_]', '_', game_name.lower())
            game_id = re.sub(r'_+', '_', game_id).strip('_')
            
            id_entry = self.fields["game_id"]
            current_text = id_entry.get()
            
            # Solo actualizar si el usuario no ha modificado manualmente el ID
            if current_text in ["Se genera automáticamente", "", game_id]:
                id_entry.delete(0, tk.END)
                id_entry.insert(0, game_id)
                id_entry.configure(foreground=COLORS["white"])

    def browse_file(self, field_name, file_type_name, file_pattern):
        """Seleccionar archivo para un campo específico."""
        filepath = filedialog.askopenfilename(
            title=f"Seleccionar {file_type_name}",
            filetypes=(
                (file_type_name, file_pattern),
                ("All files", "*.*")
            )
        )
        
        if filepath:
            self.fields[field_name].delete(0, tk.END)
            self.fields[field_name].insert(0, filepath)
            self.fields[field_name].configure(foreground=COLORS["white"])

    def browse_icon(self):
        """Seleccionar archivo de icono y mostrar previsualización."""
        filepath = filedialog.askopenfilename(
            title="Seleccionar icono del juego",
            filetypes=(
                ("SVG files", "*.svg"),
                ("PNG files", "*.png"),
                ("JPG files", "*.jpg *.jpeg"),
                ("All files", "*.*")
            )
        )
        
        if filepath:
            self.fields["icon_path"].delete(0, tk.END)
            self.fields["icon_path"].insert(0, filepath)
            self.fields["icon_path"].configure(foreground=COLORS["white"])
            
            # Mostrar previsualización
            self.show_icon_preview(filepath)

    def show_icon_preview(self, filepath):
        """Mostrar previsualización del icono seleccionado."""
        try:
            # Limpiar previsualización anterior
            for widget in self.preview_image_frame.winfo_children():
                widget.destroy()
            
            # Manejar diferentes tipos de archivos
            if filepath.lower().endswith('.svg'):
                # Para SVG, mostrar un mensaje y el nombre del archivo
                svg_label = tk.Label(self.preview_image_frame,
                                   text=f"SVG: {os.path.basename(filepath)}",
                                   foreground=COLORS["gold"],
                                   background=COLORS["dark_bg"],
                                   font=self.label_font)
                svg_label.pack(pady=10)
                
                # Mostrar información adicional para SVG
                info_label = tk.Label(self.preview_image_frame,
                                    text="(Los archivos SVG se muestran como texto)",
                                    foreground=COLORS["light_gold"],
                                    background=COLORS["dark_bg"],
                                    font=("Inter", 8))
                info_label.pack()
                
            else:
                # Para otros formatos de imagen, usar Pillow
                image = Image.open(filepath)
                image.thumbnail((120, 120), Image.Resampling.LANCZOS)
                self.icon_preview = ImageTk.PhotoImage(image)
                
                # Mostrar imagen
                preview_label = tk.Label(self.preview_image_frame, 
                                       image=self.icon_preview,
                                       background=COLORS["dark_bg"])
                preview_label.pack()
            
            # Actualizar texto
            self.preview_label.configure(text="Previsualización del icono:")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la imagen: {e}")

    def run_add_game(self):
        """Ejecutar la función de añadir juego."""
        params = {}
        
        # Obtener valores de los campos
        for key, widget in self.fields.items():
            if key == "description":
                value = widget.get("1.0", tk.END).strip()
                # Ignorar si es el placeholder
                if value == "Describe brevemente el juego para la tarjeta...":
                    value = ""
            else:
                value = widget.get().strip()
                # Ignorar placeholders
                if value in [
                    "Ej: Póker Texas Hold'em",
                    "Se genera automáticamente",
                    "Ej: 5.00",
                    "Ej: 97",
                    "Ej: Estrategia, Suerte...",
                    "Selecciona un archivo de imagen...",
                    "Selecciona el archivo HTML del juego...",
                    "Selecciona el archivo CSS del juego...",
                    "Selecciona el archivo JavaScript del juego..."
                ]:
                    value = ""
            
            params[key] = value
        
        # Validar campos obligatorios
        required_fields = {
            "game_name": "Nombre del Juego",
            "game_id": "ID del Juego",
            "description": "Descripción",
            "min_bet": "Apuesta Mínima",
            "rtp": "RTP",
            "category": "Categoría",
            "icon_path": "Ruta del Icono",
            "html_file": "Archivo HTML",
            "css_file": "Archivo CSS",
            "js_file": "Archivo JavaScript"
        }
        
        for field, label in required_fields.items():
            if not params[field]:
                messagebox.showerror("Error de Validación", f"El campo '{label}' es obligatorio.")
                return
        
        # Validar formatos numéricos
        try:
            params["min_bet"] = float(params["min_bet"])
            params["rtp"] = int(params["rtp"])
        except ValueError:
            messagebox.showerror("Error de Validación", "La apuesta mínima y el RTP deben ser números válidos.")
            return
        
        # Validar ID del juego
        if not re.match(r'^[a-z0-9_]+$', params["game_id"]):
            messagebox.showerror("Error de Validación", 
                               "El ID del juego solo puede contener letras minúsculas, números y guiones bajos.")
            return
        
        # Limpiar consola y ejecutar
        self.log_text.delete('1.0', tk.END)
        old_stdout = sys.stdout
        sys.stdout = CaptureStdout(self.log_text)
        
        try:
            success = add_game(**params)
            if success:
                messagebox.showinfo("Éxito", f"¡El juego '{params['game_name']}' ha sido añadido con éxito!")
                
                # Limpiar formulario después del éxito
                self.clear_form()
            else:
                messagebox.showerror("Error", f"Hubo un error al añadir el juego '{params['game_name']}'. Revisa el registro.")
        except Exception as e:
            print(f"\n--- ERROR INESPERADO ---\n{e}")
            messagebox.showerror("Error Crítico", f"Ocurrió un error inesperado: {e}")
        finally:
            sys.stdout = old_stdout

    def clear_form(self):
        """Limpiar todos los campos del formulario."""
        # Restaurar placeholders
        self.fields["game_name"].delete(0, tk.END)
        self.fields["game_name"].insert(0, "Ej: Póker Texas Hold'em")
        self.fields["game_name"].configure(foreground=COLORS["light_gray"])
        
        self.fields["game_id"].delete(0, tk.END)
        self.fields["game_id"].insert(0, "Se genera automáticamente")
        self.fields["game_id"].configure(foreground=COLORS["light_gray"])
        
        self.fields["description"].delete("1.0", tk.END)
        self.fields["description"].insert("1.0", "Describe brevemente el juego para la tarjeta...")
        self.fields["description"].configure(fg=COLORS["light_gray"])
        
        self.fields["min_bet"].delete(0, tk.END)
        self.fields["min_bet"].insert(0, "Ej: 5.00")
        self.fields["min_bet"].configure(foreground=COLORS["light_gray"])
        
        self.fields["rtp"].delete(0, tk.END)
        self.fields["rtp"].insert(0, "Ej: 97")
        self.fields["rtp"].configure(foreground=COLORS["light_gray"])
        
        self.fields["category"].delete(0, tk.END)
        self.fields["category"].insert(0, "Ej: Estrategia, Suerte...")
        self.fields["category"].configure(foreground=COLORS["light_gray"])
        
        self.fields["icon_path"].delete(0, tk.END)
        self.fields["icon_path"].insert(0, "Selecciona un archivo de imagen...")
        self.fields["icon_path"].configure(foreground=COLORS["light_gray"])
        
        self.fields["html_file"].delete(0, tk.END)
        self.fields["html_file"].insert(0, "Selecciona el archivo HTML del juego...")
        self.fields["html_file"].configure(foreground=COLORS["light_gray"])
        
        self.fields["css_file"].delete(0, tk.END)
        self.fields["css_file"].insert(0, "Selecciona el archivo CSS del juego...")
        self.fields["css_file"].configure(foreground=COLORS["light_gray"])
        
        self.fields["js_file"].delete(0, tk.END)
        self.fields["js_file"].insert(0, "Selecciona el archivo JavaScript del juego...")
        self.fields["js_file"].configure(foreground=COLORS["light_gray"])
        
        # Limpiar previsualización
        for widget in self.preview_image_frame.winfo_children():
            widget.destroy()
        self.preview_label.configure(text="Selecciona un icono para previsualizar")
        self.icon_preview = None

if __name__ == "__main__":
    app = GameManagerApp()
    app.mainloop()
