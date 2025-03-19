# Stage 1: Development
FROM ubuntu:24.04 AS development

# Cài đặt các gói cần thiết
RUN apt update && apt install -y curl git && \
  curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
  apt install -y nodejs \
  python3 python3-pip


# Tạo user vscode
RUN useradd -ms /bin/bash vscode
# Chuyển sang user vscode
USER vscode

# Cài đặt uv bằng script và thêm vào PATH
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
  echo 'export PATH="$HOME/.local/bin:$PATH"' >> $HOME/.bashrc

# Thiết lập thư mục làm việc
WORKDIR /workspace
# Chuyển quyền sở hữu thư mục cho user vscode
RUN chown -R vscode:vscode /workspace

# Tạo virtual environment bằng uv
RUN /home/vscode/.local/bin/uv venv /home/vscode/pylinux --python 3.12
# Thêm virtual environment vào PATH
ENV PATH="/home/vscode/pylinux/bin:$PATH"

# Sao chép file requirements.txt
COPY ./fastapi/requirements.txt .


# Cài đặt các gói python dependency = sử dụng uv
RUN /home/vscode/.local/bin/uv pip install -r requirements.txt

# Sao chép bash script
COPY ./fastapi/script/setup.sh /setup.sh
CMD ["bash", "setup.sh"]

# ------------------------------------------------------------------------------
# PRODUCTION Dockerfile
# ------------------------------------------------------------------------------
FROM ubuntu:24.04 AS production

# 1. Cài đặt gói cần thiết: python3, pip, curl
RUN apt-get update && apt-get install -y \
  python3 \
  python3-pip \
  curl \
  && rm -rf /var/lib/apt/lists/*

# 2. Thiết lập PATH để có thể gọi uv từ ~/.local/bin
ENV PATH="/root/.local/bin:$PATH"

# 3. Cài đặt uv (script cài đặt từ astral.sh)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# 4. Tạo thư mục làm việc cho app
WORKDIR /app

# 5. Sao chép file yêu cầu Python (requirements.txt) và cài đặt trong venv
COPY requirements.txt ./

# Tạo venv ở /root/venv (hoặc tuỳ ý) và cài đặt dependencies bằng uv pip
RUN uv venv /home/venv 
# Thêm virtual environment vào PATH
ENV PATH="/home/venv/bin:$PATH"
# Cài đặt các gói python dependency = sử dụng uv
RUN uv pip install -r requirements.txt

# 6.Sao chép mã nguồn của ứng dụng vào image
COPY app/ ./app
COPY alembic/ ./alembic
COPY alembic.ini .

# 7.Sử dụng biến môi trường để xác định chế độ (dev hay prod)
ARG ENVIRONMENT=production
ENV ENVIRONMENT=${ENVIRONMENT}

# 8. Copy script khởi động & cấp quyền thực thi
COPY ./script/start.sh /start.sh
RUN chmod +x /start.sh

# 9. Mặc định expose cổng 8000 (FastAPI)
EXPOSE 8000

# 10. Điểm khởi chạy container: chạy script start.sh
ENTRYPOINT ["/start.sh"]