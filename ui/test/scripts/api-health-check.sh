#!/bin/bash

#!/bin/sh

# Đường dẫn endpoint kiểm tra sức khỏe của API.
# Nếu không có biến môi trường API_HEALTH_URL, mặc định sẽ dùng http://cryptonav_api:8000/health
API_HEALTH_URL=${API_HEALTH_URL:-"http://cryptonav.local/api/health"}

# Gửi request và lưu kết quả trả về
response=$(curl -s "$API_HEALTH_URL")

# So sánh kết quả trả về với chuỗi mong đợi
if [ "$response" = '{"status":"healthy"}' ]; then
    echo "✅ API health check: $response"
    exit 0
else
    echo "❌ API health check failed. Response: $response" >&2
    exit 1
fi



# curl -X 'GET' \
#   'http://nginx/api/health'


# # Step 1: Download OpenAPI Schema from FastAPI
# curl http://nginx/api/health -o openapi.json

# # Kiểm tra nếu tải file thành công
# if [ $? -ne 0 ]; then
#   echo "❌ Failed to download openapi.json"
#   exit 1
# fi

# echo "✅ Successfully downloaded openapi.json"