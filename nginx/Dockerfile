FROM nginx:latest

# Cài đặt logrotate
RUN apt-get update && apt-get install -y logrotate cron 

# Copy cấu hình logrotate vào image
COPY ./nginx/logrotate/logrotate.conf /etc/logrotate.d/nginx

# Khởi động cron và nginx cùng nhau
CMD cron && nginx -g "daemon off;"
