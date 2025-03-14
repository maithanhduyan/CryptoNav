# Server API

### Docker

- Build

  > docker build -t cryptonav-api:lastest .

- Run Docker
  > docker run -d -p 8000:8000 --name cryptonav-container cryptonav-api:lastest

### Dev References

- [VSCode FastAPI](https://code.visualstudio.com/docs/python/tutorial-fastapi)

### uv install

- Install [uv](https://docs.astral.sh/uv/) with our official standalone installer:
  Windows:

```
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
- Linux:
> curl -LsSf https://astral.sh/uv/install.sh | sh
or
> wget -qO- https://astral.sh/uv/install.sh | sh

> source $HOME/.local/bin/env

- Dễ dàng tái tạo: Dùng uv pip freeze > requirements.txt để lưu danh sách gói, sau đó cài lại bằng uv pip install -r requirements.txt.

- Requires Python 3.12 or higher. First, we recommend using uv to setup the Python environment.

> uv venv --python 3.12

> .venv\Scripts\activate

> uv pip install -r requirements.txt

```
fastapi==0.88.0
uvicorn==0.20.0
sqlalchemy==1.4.36
pydantic==1.9.1
python-dotenv==0.21.0

```

## Run Server

> python src/server.py

- fastapi

> fastapi run src/main.py

- uvicorn

> uvicorn src.main:app --host 0.0.0.0 --port 8000

## On Container
> source .venv/bin/activate

> fastapi run src/main.py