import datetime
from functools import wraps
import jwt
from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import db, User, Course

auth_bp = Blueprint("auth", __name__)

# --- Middleware kiểm tra token JWT ---
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        print(f"DEBUG (token_required): Auth Header received: {auth_header}") # DEBUG

        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
        print(f"DEBUG (token_required): Extracted token: {token}") # DEBUG

        if not token:
            print("DEBUG (token_required): Token is missing!") # DEBUG
            return jsonify({"error": "Token is missing!"}), 401

        try:
            # SỬ DỤNG JWT_SECRET_KEY ĐỂ GIẢI MÃ TOKEN
            key_to_decode_with = current_app.config['JWT_SECRET_KEY']
            print(f"DEBUG (token_required): Attempting to decode token with KEY: {key_to_decode_with}") # DEBUG
            data = jwt.decode(token, key_to_decode_with, algorithms=["HS256"])
            print(f"DEBUG (token_required): Decoded data: {data}") # DEBUG

            current_user = User.query.get(data.get('user_id')) # Sử dụng .get để tránh KeyError nếu 'user_id' thiếu
            if not current_user:
                print(f"DEBUG (token_required): User not found for ID: {data.get('user_id')}") # DEBUG
                return jsonify({"error": "User not found!"}), 401
            print(f"DEBUG (token_required): User authenticated: {current_user.username}") # DEBUG

        except jwt.ExpiredSignatureError:
            print("DEBUG (token_required): Token has expired!") # DEBUG
            return jsonify({"error": "Token has expired!"}), 401
        except jwt.InvalidTokenError as e: # Bắt lỗi cụ thể hơn
            print(f"DEBUG (token_required): Invalid token! Error details: {str(e)}") # DEBUG
            return jsonify({"error": f"Invalid token: {str(e)}"}), 401
        except Exception as e: # Bắt các lỗi không mong muốn khác
            print(f"DEBUG (token_required): Unexpected error during token processing: {str(e)}") # DEBUG
            return jsonify({"error": "Error processing token"}), 500


        return f(current_user, *args, **kwargs)
    return decorated

# --- Đăng nhập ---
@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        user = User.query.filter_by(username=username).first()
        if not user or user.oauth_login:
            return jsonify({"error": "Tài khoản không tồn tại hoặc là tài khoản Google"}), 400

        if not check_password_hash(user.password, password):
            return jsonify({"error": "Sai mật khẩu"}), 401

        # SỬ DỤNG JWT_SECRET_KEY ĐỂ TẠO TOKEN
        key_to_encode_with = current_app.config['JWT_SECRET_KEY']
        print(f"DEBUG (login): Encoding token with KEY: {key_to_encode_with}") # DEBUG
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1) # Nên lấy thời gian hết hạn từ config
        }, key_to_encode_with, algorithm='HS256')

        return jsonify({
            "message": "Đăng nhập thành công",
            "role": user.role,
            "username": user.username,
            "name": user.name,
            "token": token
        }), 200
    except Exception as e:
        print(f"DEBUG (login): Error during login: {str(e)}") # DEBUG
        return jsonify({"error": f"Đăng nhập thất bại: {str(e)}"}), 500

# ... (các route khác của bạn không thay đổi) ...

# --- Tạo khóa học (chỉ ADMIN) ---
# Lưu ý: Route này trong auth_bp sẽ có prefix là /api/auth/courses
# Nếu bạn muốn /api/courses thì nó phải nằm trong courses_bp và dùng @token_required này
@auth_bp.route('/courses', methods=['POST'])
@token_required
def create_course(current_user): # Đổi tên hàm để tránh xung đột nếu bạn có hàm cùng tên ở courses_bp
    # ... (logic tạo course của bạn) ...
    # Ví dụ:
    # if current_user.role != 'ADMIN':
    #     return jsonify({"error": "Admin access required"}), 403
    data = request.get_json()
    # ... (phần còn lại của hàm create_course) ...
    # Đảm bảo rằng nếu bạn có logic tạo course ở đây,
    # frontend đang gọi đúng endpoint /api/auth/courses (nếu auth_bp có prefix /api/auth)
    # Hoặc, di chuyển logic @token_required này vào courses_bp nếu endpoint là /api/courses
    print("Dữ liệu nhận được (auth_bp/courses):", data)
    name = data.get('name')
    description = data.get('description')

    if not name:
        print("Lỗi: Tên khóa học thiếu (auth_bp/courses)")
        return jsonify({"error": "Tên khóa học là bắt buộc"}), 400

    # Nên kiểm tra xem current_user có quyền tạo không, ví dụ:
    # if current_user.role != 'ADMIN':
    # return jsonify({"error": "Chỉ admin mới được tạo khóa học qua endpoint này"}), 403

    existing = Course.query.filter_by(name=name).first() # Cân nhắc thêm owner_id nếu cần
    if existing:
        print("Lỗi: Khóa học đã tồn tại (auth_bp/courses)")
        return jsonify({"error": "Tên khóa học đã tồn tại"}), 400

    try:
        # Nếu khóa học cần owner, hãy gán owner_id=current_user.id
        course = Course(name=name, description=description) # Hoặc Course(name=name, description=description, owner_id=current_user.id)
        db.session.add(course)
        db.session.commit()
        print("Tạo khóa học thành công (auth_bp/courses), id:", course.id)
        return jsonify({"message": "Tạo khóa học thành công (từ auth_bp)", "course_id": course.id}), 201
    except Exception as e:
        print("Lỗi khi tạo khóa học (auth_bp/courses):", str(e))
        db.session.rollback()
        return jsonify({"error": f"Lỗi khi tạo khóa học: {str(e)}"}), 500

# ... (các route khác)