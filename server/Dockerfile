# Sử dụng image Python 3.12 chính thức từ Docker Hub
FROM python:3.12-slim

# Đặt thư mục làm việc trong container
WORKDIR /app

# Cài đặt các công cụ cần thiết (nếu cần)
RUN apt-get update && apt-get install -y \
  gcc \
  && rm -rf /var/lib/apt/lists/*

# Sao chép file requirements.txt (nếu có) hoặc cài trực tiếp dependencies
COPY requirements.txt .

# Cài đặt dependencies từ requirements.txt
RUN pip install --no-cache-dir -r requirements.txt



# Sao chép toàn bộ mã nguồn dự án vào container
COPY ./src /app/src

# Đặt biến môi trường để Python không tạo file .pyc và buffer output
ENV PYTHONUNBUFFERED=1 \
  PYTHONDONTWRITEBYTECODE=1

# Mở cổng 8000 để truy cập ứng dụng FastAPI
EXPOSE 8000

# Chạy ứng dụng FastAPI với Uvicorn
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]