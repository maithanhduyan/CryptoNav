# Stage 1: Development
FROM ubuntu:24.04 AS development

# Cài đặt các gói cần thiết
RUN apt-get update && apt-get install -y curl python3 python3-pip

# Tạo user vscode
RUN useradd -ms /bin/bash vscode

# Thiết lập thư mục làm việc
WORKDIR /workstation

# Sao chép file requirements.txt
COPY ./fastapi/requirements.txt .

# Sao chép bash script
COPY script/start.sh /start.sh

# Chuyển quyền sở hữu thư mục cho user vscode
RUN chown -R vscode:vscode /workspace

# Chuyển sang user vscode
USER vscode

# Cài đặt uv bằng script và thêm vào PATH
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
  echo 'export PATH="$HOME/.local/bin:$PATH"' >> $HOME/.bashrc

# Tạo virtual environment bằng uv
RUN /home/vscode/.local/bin/uv venv

# Cài đặt các gói python dependency = sử dụng uv
RUN /home/vscode/.local/bin/uv pip install -r requirements.txt

# Sử dụng cách gói python cài cũ
# RUN pip3 install -r requirements.txt

CMD ["bash", "setup.sh"]

# ------------------------------------------------------------------------------
FROM ubuntu:24.04 AS production

# Cập nhật và cài đặt Python3, pip, và các phụ thuộc cần thiết (ví dụ psycopg2)
RUN apt-get update && apt-get install -y python3 python3-pip build-essential libpq-dev

# Tạo thư mục làm việc
WORKDIR /app

# Sao chép file yêu cầu (để cài đặt thư viện Python)
COPY ./fastapi/requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Sao chép mã nguồn của ứng dụng vào image
COPY app/ ./app
COPY alembic/ ./alembic
COPY alembic.ini .

# Sử dụng biến môi trường để xác định chế độ (dev hay prod)
ARG ENVIRONMENT=production
ENV ENVIRONMENT=${ENVIRONMENT}

# Mặc định, expose cổng 8000 (ứng dụng FastAPI sẽ chạy trên cổng này)
EXPOSE 8000

# Sao chép script khởi động (script này sẽ kiểm tra ENVIRONMENT để chạy tương ứng)
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Điểm khởi chạy container: chạy script start.sh
ENTRYPOINT ["/start.sh"]