from app import create_app, db
from app.models import User  # đảm bảo bạn import đúng model User
from werkzeug.security import generate_password_hash

app = create_app()

def create_admin_user():
    existing_admin = User.query.filter_by(email="admin").first()
    if not existing_admin:
        admin = User(
            name="Admin",
            email="admin",
            password=generate_password_hash("admin"),
            role="admin"
        )
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin account created with username and password = 'admin'")
    else:
        print("ℹ️ Admin account already exists.")

with app.app_context():
    db.create_all()
    create_admin_user()  # 👈 Thêm dòng này
    print("✅ Database initialized.")
