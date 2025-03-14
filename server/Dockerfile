# Stage 1: Development
FROM ubuntu:24.04 AS development

# Cài đặt các gói cần thiết (bao gồm Python)
RUN apt-get update && apt-get install -y curl python3 python3-pip

# Tạo user vscode
RUN useradd -ms /bin/bash vscode

# Thiết lập thư mục làm việc
WORKDIR /workspace

# Sao chép file requirements.txt
COPY ./server/requirements.txt ./

# Chuyển quyền sở hữu thư mục cho user vscode
RUN chown -R vscode:vscode /workspace

# Chuyển sang user vscode
USER vscode

# Cài đặt uv bằng script và thêm vào PATH
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
  echo 'export PATH="$HOME/.local/bin:$PATH"' >> $HOME/.bashrc

# Tạo virtual environment bằng uv
RUN /home/vscode/.local/bin/uv venv

# Cài đặt các dependency
RUN /home/vscode/.local/bin/uv pip install -r requirements.txt

# Stage 2: Production (tùy chọn)
FROM ubuntu:24.04 AS production

RUN apt-get update && apt-get install -y curl python3 python3-pip
RUN useradd -ms /bin/bash vscode
WORKDIR /app
COPY ./server/requirements.txt ./
RUN chown -R vscode:vscode /app
USER vscode
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
  echo 'export PATH="$HOME/.local/bin:$PATH"' >> $HOME/.bashrc
RUN /home/vscode/.local/bin/uv venv
RUN /home/vscode/.local/bin/uv pip install -r requirements.txt
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]