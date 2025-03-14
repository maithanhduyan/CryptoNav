# Base stage
FROM ubuntu:24.04 AS base
WORKDIR /app

# Cài đặt Node.js và npm
RUN apt update && apt install -y curl && \
  curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
  apt install -y nodejs \
  python3 python3-pip

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
# Production build stage
FROM base AS build
COPY . .
RUN npm run build

# ------------------------------------------------------------------------------
# Production stage
FROM ubuntu:24.04 AS production
WORKDIR /app
# Cài đặt lại Node.js cho stage production
RUN apt update && apt install -y curl && \
  curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
  apt install -y nodejs
COPY --from=build /app/dist ./dist
RUN npm install -g serve
EXPOSE 4173
CMD ["serve", "-s", "dist", "-l", "4173"]