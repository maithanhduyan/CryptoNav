# BẢO MẬT

Để bảo mật mật khẩu trong ứng dụng FastAPI và trong file `docker-compose.yml`, đặc biệt khi bạn commit source code lên repository mà không muốn lộ thông tin nhạy cảm, dưới đây là các giải pháp chi tiết và cụ thể dựa trên yêu cầu của bạn:

---

## 1. Bảo mật mật khẩu trong server FastAPI

Trong ứng dụng FastAPI (dịch vụ `cryptonav-api`), mật khẩu và các thông tin nhạy cảm như `DATABASE_URL` hoặc `JWT_SECRET_KEY` không nên được hard-code trực tiếp trong mã nguồn. Thay vào đó, bạn nên sử dụng **biến môi trường** để quản lý chúng.

### Cách thực hiện:

#### Bước 1: Cấu hình FastAPI để đọc từ biến môi trường

Trong file cấu hình của FastAPI (ví dụ: `app/config.py`), sử dụng thư viện `os` để lấy giá trị từ biến môi trường:

```python
# app/config.py
import os

DATABASE_URL = os.getenv("DATABASE_URL")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")  # Giá trị mặc định chỉ dùng cho log level
```

- **Lưu ý**:
  - Không đặt giá trị mặc định cho `DATABASE_URL` hoặc `JWT_SECRET_KEY` trong môi trường production để tránh rủi ro bảo mật.
  - Trong môi trường phát triển cục bộ, bạn có thể tạm thời để giá trị mặc định, nhưng không commit chúng lên repository.

#### Bước 2: Truyền biến môi trường vào container

Các biến môi trường sẽ được cung cấp thông qua `docker-compose.yml` (sẽ được bảo mật ở phần sau). FastAPI sẽ tự động sử dụng các giá trị này khi chạy.

---

## 2. Bảo mật mật khẩu trong `docker-compose.yml`

Trong file `docker-compose.yml` hiện tại, các thông tin nhạy cảm như `POSTGRES_PASSWORD`, `DATABASE_URL`, và `JWT_SECRET_KEY` đang được hard-code. Nếu commit file này lên repository công khai, những thông tin này sẽ bị lộ. Để bảo mật, bạn có thể sử dụng **file `.env`** hoặc các phương pháp nâng cao hơn như **Docker Secrets**.

### Phương pháp 1: Sử dụng file `.env` (Khuyến nghị cho đơn giản)

Docker Compose hỗ trợ file `.env` để lưu trữ các biến môi trường nhạy cảm, giúp bạn tách biệt thông tin bí mật khỏi file `docker-compose.yml`.

#### Bước 1: Tạo file `.env`

Tạo một file `.env` trong cùng thư mục với `docker-compose.yml` và thêm các thông tin nhạy cảm:

```env
# .env
POSTGRES_DB=app
POSTGRES_USER=appuser
POSTGRES_PASSWORD=apppassword
JWT_SECRET_KEY=your-secret-key
```

- **Lưu ý**: File `.env` chứa thông tin nhạy cảm, vì vậy bạn cần thêm nó vào `.gitignore` để tránh commit lên repository.

#### Bước 2: Sửa `docker-compose.yml` để sử dụng biến từ `.env`

Thay thế các giá trị hard-code trong `docker-compose.yml` bằng cách tham chiếu đến các biến trong file `.env`:

```yaml
version: "3"

services:
  db:
    image: postgres:latest
    container_name: db
    environment:
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    ports:
      - "5432:5432"
    volumes:
      - ./postgresql/data:/var/lib/postgresql/data
    restart: always

  cryptonav-ui:
    container_name: cryptonav-ui
    build:
      context: .
      dockerfile: ./ui/Dockerfile
      target: development
    ports:
      - "3000:3000"
      - "5173:5173"
    volumes:
      - .:/workspace:cached
    restart: unless-stopped
    command: sleep infinity

  cryptonav-api:
    container_name: cryptonav-api
    build:
      context: .
      dockerfile: ./server/Dockerfile
      target: development
    ports:
      - "8000:8000"
    environment:
      ENVIRONMENT: "development"
      DATABASE_URL: "postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}"
      JWT_SECRET_KEY: "${JWT_SECRET_KEY}"
      LOG_LEVEL: "INFO"
    volumes:
      - .:/workspace:cached
    restart: unless-stopped
    command: sleep infinity

  nginx:
    image: nginx:latest
    container_name: nginx
    restart: always
    ports:
      - "443:443"
      - "80:80"
    volumes:
      - ./nginx/conf/nginx.conf:/etc/nginx/conf.d/default.conf:ro
      - ./nginx/cache:/var/cache/nginx
      - ./nginx/ssl:/etc/nginx/ssl
      - ./nginx/html:/var/www/html
      - ./nginx/log:/var/log/nginx/
```

- **Giải thích**:
  - `${POSTGRES_USER}`, `${POSTGRES_PASSWORD}`, v.v. sẽ được thay thế bằng giá trị từ file `.env` khi Docker Compose chạy.
  - File `docker-compose.yml` giờ đây không chứa thông tin nhạy cảm trực tiếp, nên có thể commit an toàn.

#### Bước 3: Thêm `.env` vào `.gitignore`

Chỉnh sửa file `.gitignore` để đảm bảo file `.env` không bị commit:

```
.env
```

### Phương pháp 2: Sử dụng Docker Secrets (Dành cho production)

Nếu bạn triển khai ứng dụng trong môi trường production với Docker Swarm, bạn có thể dùng **Docker Secrets** để tăng cường bảo mật.

#### Bước 1: Tạo các secret

Tạo secret từ dòng lệnh:

```bash
echo "apppassword" | docker secret create db_password -
echo "your-secret-key" | docker secret create jwt_secret_key -
```

#### Bước 2: Sửa `docker-compose.yml` để dùng secrets

Cập nhật file `docker-compose.yml`:

```yaml
version: "3"

services:
  db:
    image: postgres:latest
    container_name: db
    secrets:
      - db_password
    environment:
      - POSTGRES_DB=app
      - POSTGRES_USER=appuser
      - POSTGRES_PASSWORD_FILE=/run/secrets/db_password
    ports:
      - "5432:5432"
    volumes:
      - ./postgresql/data:/var/lib/postgresql/data
    restart: always

  cryptonav-api:
    container_name: cryptonav-api
    build:
      context: .
      dockerfile: ./server/Dockerfile
      target: development
    ports:
      - "8000:8000"
    secrets:
      - db_password
      - jwt_secret_key
    environment:
      ENVIRONMENT: "development"
      DATABASE_URL: "postgresql://appuser:/run/secrets/db_password@db:5432/app"
      JWT_SECRET_KEY_FILE: /run/secrets/jwt_secret_key
      LOG_LEVEL: "INFO"
    volumes:
      - .:/workspace:cached
    restart: unless-stopped
    command: sleep infinity

secrets:
  db_password:
    external: true
  jwt_secret_key:
    external: true
```

#### Bước 3: Cập nhật mã nguồn FastAPI

Nếu dùng `_FILE` (ví dụ: `JWT_SECRET_KEY_FILE`), bạn cần sửa code trong FastAPI để đọc từ file:

```python
# app/config.py
import os

def get_secret_from_file(file_path):
    with open(file_path, 'r') as f:
        return f.read().strip()

DATABASE_URL = os.getenv("DATABASE_URL", f"postgresql://appuser:{get_secret_from_file('/run/secrets/db_password')}@db:5432/app")
JWT_SECRET_KEY = get_secret_from_file('/run/secrets/jwt_secret_key') if os.path.exists('/run/secrets/jwt_secret_key') else os.getenv("JWT_SECRET_KEY")
```

- **Lợi ích**: Bảo mật cao hơn, phù hợp với production.
- **Nhược điểm**: Chỉ hoạt động trong Docker Swarm và yêu cầu cấu hình thêm.

---

## 3. Các biện pháp bổ sung khi commit source code

Để đảm bảo an toàn tuyệt đối khi commit source code:

### Thêm các file nhạy cảm vào `.gitignore`

Ngoài `.env`, bạn cũng cần bảo vệ các file khác chứa thông tin nhạy cảm, như:

```
.env
/nginx/ssl/server-sample.key
/nginx/ssl/server-sample.crt
```

### Sử dụng template cho `docker-compose.yml`

- Tạo một file `docker-compose.yml.example` không chứa thông tin nhạy cảm để người khác tham khảo.
- Ví dụ:

```yaml
version: "3"

services:
  db:
    image: postgres:latest
    container_name: db
    environment:
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    # ...
```

### Kiểm tra trước khi commit

Sử dụng công cụ như `git-secrets` để phát hiện và ngăn chặn việc commit thông tin nhạy cảm:

```bash
# Cài đặt git-secrets
brew install git-secrets
# Thêm quy tắc kiểm tra
git secrets --add 'password'
git secrets --scan
```

---

## Tóm tắt

- **Trong FastAPI**: Sử dụng `os.getenv` để đọc biến môi trường, không hard-code mật khẩu.
- **Trong `docker-compose.yml**:
  - Dùng file `.env` (đơn giản, phù hợp phát triển và production nhỏ).
  - Dùng Docker Secrets (nâng cao, dành cho production lớn).
- **Khi commit**: Thêm `.env` và các file nhạy cảm vào `.gitignore`, dùng template cho cấu hình.

Bằng cách áp dụng các bước trên, bạn sẽ bảo mật được mật khẩu trong FastAPI và `docker-compose.yml`, đồng thời an toàn khi commit mã nguồn lên repository.
