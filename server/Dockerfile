# Base stage
FROM python:3.12-slim AS base

ENV PYTHONUNBUFFERED=1

# Cài đặt các dependencies chung (hệ thống)
RUN apt-get update && apt-get install -y \
  build-essential \
  curl \
  git \
  && rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Cài đặt Python dependencies
COPY ./server/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
# RUN uv pip install --no-cache-dir -r requirements.txt

# ------------------------------------------------------------------------------
# Development stage
FROM base AS development

# Cài thêm debugpy và uvicorn cho dev
RUN pip install --no-cache-dir debugpy uvicorn[standard]

# Tạo user không phải root
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=1000

# Tạo group nếu group chưa tồn tại, hoặc đổi tên group hiện tại
RUN existing_group=$(getent group $USER_GID | cut -d: -f1); \
  if [ -z "$existing_group" ]; then \
  groupadd --gid $USER_GID $USERNAME; \
  else \
  groupmod -n $USERNAME "$existing_group"; \
  fi \
  && existing_user=$(getent passwd $USER_UID | cut -d: -f1); \
  if [ -z "$existing_user" ]; then \
  useradd --uid $USER_UID --gid $USER_GID -m $USERNAME; \
  else \
  usermod -l $USERNAME -g $USER_GID -d /home/$USERNAME -m "$existing_user"; \
  fi \
  && echo "$USERNAME ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

WORKDIR /workspace
USER $USERNAME

EXPOSE 8000
# Command chạy ở chế độ reload (development)
# CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ------------------------------------------------------------------------------
# Production stage
FROM base AS production

# Cài gunicorn và uvicorn cho prod
RUN pip install --no-cache-dir gunicorn uvicorn[standard]

# Sao chép mã nguồn vào container
COPY ./server/src /app/src

# Chạy gunicorn + uvicorn worker (tối ưu production)
CMD ["gunicorn", "src.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000"]