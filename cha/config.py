import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'casino.db')
SECRET_KEY = os.environ.get('SECRET_KEY', 'cambia_esto_por_una_clave_segura')
