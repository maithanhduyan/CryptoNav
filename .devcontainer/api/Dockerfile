FROM python:3.12-slim AS base

# Cài đặt các dependencies chung (hệ thống)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

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