#! /usr/bin/env bash

# set -e
# set -x

# cd fastapi
# python -c "import app.main; import json; print(json.dumps(app.main.app.openapi()))" > ../openapi.json
# cd ..
# mv openapi.json frontend/
# cd frontend
# npm run generate-client
# npx biome format --write ./src/client

#---------------------------------------------------
# # ChatGPT generate code:

# #!/bin/bash

# # Step 1: Download OpenAPI Schema from FastAPI
# curl http://nginx/api/openapi.json -o openapi.json

# # Kiểm tra nếu tải file thành công
# if [ $? -ne 0 ]; then
#   echo "❌ Failed to download openapi.json"
#   exit 1
# fi

# echo "✅ Successfully downloaded openapi.json"

# # Step 2: tạo client TypeScript từ file openapi.json
# npm run openapi-ts