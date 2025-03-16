# app/config.py
import os

# URL kết nối cơ sở dữ liệu từ biến môi trường (với giá trị mặc định trùng với cấu hình docker-compose)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://appuser:apppassword@db:5432/app")

# Cấu hình JWT
JWT_SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY", "your-secret-key"
)  # Khóa bí mật để mã hóa JWT
JWT_ALGORITHM = "HS256"  # Thuật toán mã hóa JWT
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Thời gian hết hạn token (30 phút)

# Cấu hình logging: mức log mặc định, sử dụng biến môi trường để dễ thay đổi giữa development và production
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
