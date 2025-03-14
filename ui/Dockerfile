# Base stage
FROM node:20-alpine AS base
WORKDIR /app

# ------------------------------------------------------------------------------
# Development stage
FROM base AS development
# Cài đặt Python và các công cụ build cần thiết
RUN apk update && apk add --no-cache \
  python3 \
  py3-pip \
  make \
  git \
  g++ \
  && rm -rf /var/cache/apk/*

WORKDIR /workspace
ENV NODE_ENV=development
EXPOSE 5173 3000
# CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# ------------------------------------------------------------------------------
# Production build stage
FROM base AS build
COPY . .
RUN npm run build
# ----------------------
# Production stage
FROM node:20-alpine AS production
WORKDIR /app
COPY --from=build /app/dist ./dist
RUN npm install -g serve
EXPOSE 4173
CMD ["serve", "-s", "dist", "-l", "4173"]