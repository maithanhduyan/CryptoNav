### Key Points

- Ứng dụng FastAPI được tạo với cấu trúc thư mục trong `app`, bao gồm `main.py`, `model.py`, `router.py`, `database.py`, và `config.py`, cùng các file bổ sung như `logging.py`, `setup.sh`, và thư mục `alembic` cho migrations.
- Sử dụng SQLAlchemy để kết nối cơ sở dữ liệu, với SQLite cho môi trường phát triển/test và PostgreSQL cho sản xuất, được cấu hình qua biến môi trường.
- Có ghi log dựa trên chế độ (development hoặc production), với mức log khác nhau cho từng chế độ.
- Dockerfile được xây dựng trên Ubuntu 24.04, hỗ trợ cả chế độ phát triển (với reload) và sản xuất (với workers).
- File `dockercompose.yml` bao gồm dịch vụ cho PostgreSQL, NGINX, và server API, với cấu hình cho môi trường sản xuất.

---

### Cấu trúc ứng dụng và cài đặt

#### Tổng quan

Ứng dụng FastAPI được thiết kế với cấu trúc rõ ràng, phù hợp cho cả phát triển và sản xuất. Dựa trên yêu cầu, thư mục `app` chứa các file chính như `main.py`, `model.py`, `router.py`, `database.py`, và `config.py`, cùng các file bổ sung như `logging.py` cho ghi log và `setup.sh` để khởi động server. Thư mục `alembic` được thêm vào để quản lý migrations cơ sở dữ liệu, đảm bảo ứng dụng có thể mở rộng và duy trì dễ dàng.

#### Cấu trúc thư mục

- **`app/main.py`**: Điểm vào của ứng dụng, khởi tạo FastAPI và bao gồm router.
- **`app/model.py`**: Định nghĩa các model cơ sở dữ liệu (User và Item) sử dụng SQLAlchemy, hỗ trợ cả SQLite và PostgreSQL.
- **`app/router.py`**: Xử lý các tuyến đường API, ví dụ như lấy danh sách người dùng hoặc tạo mới.
- **`app/database.py`**: Quản lý kết nối và session với cơ sở dữ liệu, linh hoạt chuyển đổi giữa SQLite (phát triển) và PostgreSQL (sản xuất).
- **`app/config.py`**: Lưu trữ cấu hình, bao gồm URL cơ sở dữ liệu, được lấy từ biến môi trường `APP_DATABASE_URL`, mặc định là SQLite cho phát triển.
- **`app/logging.py`**: Cấu hình ghi log, với mức DEBUG cho chế độ phát triển và INFO cho sản xuất.
- **`app/setup.sh`**: Script khởi động, áp dụng migrations bằng Alembic và chạy server với uvicorn, tùy thuộc vào chế độ (development với `--reload`, production với `--workers 4`).
- **`app/alembic/`**: Thư mục chứa cấu hình và script cho migrations, đảm bảo cơ sở dữ liệu được cập nhật khi có thay đổi model.

#### Sử dụng thư viện

- **SQLAlchemy**: Được sử dụng để quản lý cơ sở dữ liệu, hỗ trợ cả SQLite (cho test/phát triển) và PostgreSQL (cho sản xuất). URL cơ sở dữ liệu được cấu hình qua biến môi trường, cho phép linh hoạt chuyển đổi.
- **Logging**: Ghi log được thiết lập trong `logging.py`, với mức log khác nhau dựa trên chế độ, giúp theo dõi hoạt động ứng dụng dễ dàng.

#### Containerization với Docker

- **Dockerfile**: Dựa trên Ubuntu 24.04, cài đặt Python, pip, và các dependencies từ `requirements.txt`. File này sao chép mã nguồn và chạy `setup.sh` khi container khởi động, hỗ trợ cả chế độ phát triển (với reload) và sản xuất (với workers).
- **dockercompose.yml**: Định nghĩa các dịch vụ:
  - PostgreSQL: Chạy với image chính thức, cấu hình user, password, và volume để lưu dữ liệu.
  - NGINX: Sử dụng image nginx, cấu hình proxy đến API server qua file `nginx.conf`.
  - API server: Xây dựng từ Dockerfile, kết nối với PostgreSQL trong sản xuất, và có thể tùy chỉnh chế độ qua biến môi trường `MODE`.

---

### Chi tiết triển khai

#### File cụ thể và nội dung

##### `app/config.py`

```python
from pydantic import BaseSettings

class Settings(BaseSettings):
    database_url: str = "sqlite://./database.db"

    class Config:
        env_prefix = "APP_"

settings = Settings()
```

- Định nghĩa URL cơ sở dữ liệu, mặc định là SQLite, có thể ghi đè bằng biến môi trường `APP_DATABASE_URL`.

##### `app/model.py`

```python
from sqlAlchemy import Column, Integer, String, ForeignKey
from sqlAlchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __table_name__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)

class Item(Base):
    __table_name__ = "items"
    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey("users.id"))
    name = Column(String)
```

- Định nghĩa model cho User và Item, sử dụng declarative base của SQLAlchemy.

##### `app/database.py`

```python
from sqlAlchemy import create_engine, sessionmaker
from .config import settings

engine = create_engine(settings.database_url)
Session = sessionmaker(bind=engine)

def get_session():
    return Session()
```

- Tạo engine và session cho SQLAlchemy, dựa trên URL từ `config.py`.

##### `app/router.py`

```python
from fastapi import APIRouter, Depends
from .database import get_session
from .model import User, Item
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/users/")
def get_users(session=Depends(get_session)):
    logger.info("Getting all users")
    return session.query(User).all()

@router.post("/users/")
def create_user(name: str, session=Depends(get_session)):
    user = User(name=name)
    session.add(user)
    session.commit()
    return user
```

- Định nghĩa các tuyến đường API cơ bản, bao gồm log để theo dõi hoạt động.

##### `app/logging.py`

```python
import logging
from .config import settings

if settings.mode == "development":
    logging_level = logging.DEBUG
else:
    logging_level = logging.INFO

logging.basicConfig(level=logging_level)
```

- Cấu hình log dựa trên chế độ, với mức DEBUG cho phát triển và INFO cho sản xuất.

##### `app/setup.sh`

```bash
#!/bin/bash

alembic upgrade head

if [ "$MODE" == "development" ]; then
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
else
    uvicorn main:app --workers 4 --host 0.0.0.0 --port 8000
fi
```

- Áp dụng migrations và khởi động server với tùy chọn phù hợp cho chế độ.

##### `Dockerfile`

```dockerfile
FROM ubuntu:24.04

RUN apt-get update && apt-get install -y python3 python3-pip
WORKDIR /app
COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY . .
CMD ["bash", "setup.sh"]
```

- Xây dựng image dựa trên Ubuntu 24.04, cài đặt dependencies và chạy `setup.sh`.

##### `dockercompose.yml`

```yaml
version: "3"

services:
  db:
    image: postgres
    environment:
      - POSTGRES_DB=app
      - POSTGRES_USER=appuser
      - POSTGRES_PASSWORD=apppassword
    volumes:
      - db_data:/var/lib/postgresql/data

  api:
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      - MODE=production
      - APP_DATABASE_URL=postgresql://appuser:apppassword@db/app
    depends_on:
      - db

  nginx:
    image: nginx
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
    ports:
      - "80:80"
    depends_on:
      - api

volumes:
  db_data:
```

- Định nghĩa dịch vụ cho PostgreSQL, API server, và NGINX, với cấu hình cho sản xuất.

##### `nginx.conf`

```nginx
server {
    listen 80;
    location / {
        proxy_pass http://api:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

- Cấu hình NGINX để proxy đến API server trên cổng 8000.

#### Bảng tóm tắt cấu hình

| File/Thư mục        | Mô tả                                                                 |
| ------------------- | --------------------------------------------------------------------- |
| `main.py`           | Khởi tạo FastAPI và bao gồm router.                                   |
| `model.py`          | Định nghĩa model User và Item với SQLAlchemy.                         |
| `router.py`         | Xử lý các tuyến đường API, bao gồm log.                               |
| `database.py`       | Quản lý kết nối và session cơ sở dữ liệu.                             |
| `config.py`         | Lưu trữ cấu hình, bao gồm URL cơ sở dữ liệu.                          |
| `logging.py`        | Cấu hình log dựa trên chế độ (development/production).                |
| `setup.sh`          | Áp dụng migrations và khởi động server với uvicorn.                   |
| `alembic/`          | Quản lý migrations cơ sở dữ liệu với Alembic.                         |
| `Dockerfile`        | Xây dựng image dựa trên Ubuntu 24.04, hỗ trợ cả hai chế độ.           |
| `dockercompose.yml` | Định nghĩa dịch vụ PostgreSQL, API, và NGINX cho môi trường sản xuất. |

---

### Key Citations

- [FastAPI SQL Databases Tutorial](https://fastapi.tiangolo.com/tutorial/sql-databases/)
- [Using FastAPI with SQLAlchemy](https://blog.stackademic.com/using-fastapi-with-sqlalchemy-5cd370473fe5?gi=ff8390c6c492)
- [Patterns and Practices for SQLAlchemy 2.0 with FastAPI](https://chaoticengineer.hashnode.dev/fastapi-sqlalchemy)
- [FastAPI with Async SQLAlchemy 2.0 & Pydantic V2](https://medium.com/@tclaitken/setting-up-a-fastapi-app-with-async-sqlalchemy-2-0-pydantic-v2-e6c540be4308)
- [Ultimate FastAPI Tutorial Part 7 - Database Setup](https://christophergs.com/tutorials/ultimate-fastapi-tutorial-pt-7-sqlalchemy-database-setup/)
- [FastAPI with SQLAlchemy and Alembic](https://medium.com/@hasanmahira/fastapi-with-sqlalchemy-postgresql-and-alembic-1ccaba79572e)
- [How to Use Alembic for Database Migrations in FastAPI](https://www.nashruddinamin.com/blog/how-to-use-alembic-for-database-migrations-in-your-fastapi-application)
- [FastAPI SQLAlchemy Migrations Guide](https://fastapi.blog/blog/posts/2023-07-20-fastapi-sqlalchemy-migrations-guide/)
