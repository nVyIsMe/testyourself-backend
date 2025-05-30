# run.py
import os
from dotenv import load_dotenv

# Load biến môi trường từ .env
load_dotenv()

from app import create_app
from app.models import db  # Quan trọng: import db để Flask-Migrate nhận biết
from flask_migrate import Migrate

# Lấy config_name từ biến môi trường, mặc định là 'development'
config_name = os.getenv('FLASK_CONFIG', 'development')
app = create_app(config_name)

# Khởi tạo Flask-Migrate
migrate = Migrate(app, db)

if __name__ == '__main__':
    app.run(debug=app.config.get('DEBUG', True))
