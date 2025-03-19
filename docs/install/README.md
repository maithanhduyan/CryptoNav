# API Server

- Build API
  > docker build --pull --rm -f "fastapi\Dockerfile" -t "cryptonav_api:latest" "fastapi"

# UI

- Build
  cd cryptonav

> docker build --pull --rm -f "ui\Dockerfile" -t "cryptonav_ui:latest" "ui"
