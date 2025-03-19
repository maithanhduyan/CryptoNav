# Base stage
FROM ubuntu:24.04 AS base
WORKDIR /app

# Cài đặt Node.js và npm
RUN apt update && apt install -y curl && \
  curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
  apt install -y nodejs 

# ------------------------------------------------------------------------------
# Development stage
FROM base AS development

# Tạo user vscode
RUN useradd -ms /bin/bash vscode

# Thiết lập thư mục làm việc
WORKDIR /workspace
ENV NODE_ENV=development
EXPOSE 5173 3000
# CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
# Chuyển quyền sở hữu thư mục cho user vscode
RUN chown -R vscode:vscode /workspace

# Chuyển sang user vscode
USER vscode

# ------------------------------------------------------------------------------
# Build stage: Đóng gói mã nguồn và build ra thư mục dist
FROM base AS build

# Sao chép package.json, package-lock.json trước để tối ưu cache cài đặt
COPY ./package*.json ./

# Cài đặt phụ thuộc
RUN npm ci

# Sao chép toàn bộ source code
COPY . .

# Build ra static files (React/Vue/Angular ...)
RUN npm run build

# ------------------------------------------------------------------------------
# Production stage: Tối ưu dung lượng, chỉ copy build artifact
FROM ubuntu:24.04 AS production

# Cài đặt Node.js (để chạy "serve"), có thể dùng Node slim/alpine tuỳ ý
RUN apt-get update \
  && apt-get install -y curl \
  && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
  && apt-get install -y nodejs \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Sao chép kết quả build từ stage "build" sang
COPY --from=build /app/dist ./dist

# Cài đặt "serve" toàn cục để phục vụ static
RUN npm install -g serve

EXPOSE 5173

# Chạy ứng dụng bằng "serve" ở cổng 5173
CMD ["serve", "-s", "dist", "-l", "5173"]