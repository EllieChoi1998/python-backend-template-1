# Python Backend Template 1

이 템플릿은 Oracle DB와 FastAPI를 사용하는 백엔드 프로젝트를 위한 기본 구조를 제공합니다. 검색 엔진 없이도 개발을 신속하게 시작할 수 있도록 설계되었습니다.

## 기술 스택

- **[FastAPI](https://fastapi.tiangolo.com/)**: 고성능 비동기 API 프레임워크
- **Oracle DB**: 엔터프라이즈급 데이터베이스
- **[SQLAlchemy](https://www.sqlalchemy.org/)**: Python SQL 툴킷 및 ORM
- **[oracledb](https://python-oracledb.readthedocs.io/)**: Oracle 데이터베이스 Python 드라이버
- **[JWT](https://jwt.io/)**: 사용자 인증 및 권한 부여
- **[Pydantic](https://pydantic-docs.helpmanual.io/)**: 데이터 검증 및 설정 관리

## 프로젝트 구조
```bash
app/
├── repository/           # 데이터베이스 접근 계층
│   ├── user_repository.py
│   ├── post_repository.py
│   └── comment_repository.py
├── service/              # 비즈니스 로직 계층
│   ├── user_service.py
│   ├── post_service.py
│   └── file_service.py
├── router/               # API 엔드포인트 정의
│   ├── user_router.py
│   ├── post_router.py
│   └── file_router.py
├── auth/                 # 인증 및 권한 관련
│   ├── jwt_handler.py
│   └── jwt_bearer.py
├── utils/                # 유틸리티 함수
│   ├── database.py       # 데이터베이스 연결 설정
│   ├── oracle_utils.py   # Oracle 특화 기능
│   ├── pagination.py     # 페이지네이션 유틸리티
│   ├── error_handlers.py # 에러 핸들링
│   ├── transaction.py    # 트랜잭션 관리
│   ├── logging_utils.py  # 로깅 유틸리티
│   └── password.py       # 비밀번호 해싱 및 검증
├── models.py             # SQLAlchemy 모델 정의
├── config.py             # 애플리케이션 설정 관리
├── main.py               # 애플리케이션 진입점
├── create_tables.py      # 테이블 생성 스크립트
├── .env                  # 환경 변수 (예시 포함)
└── requirements.txt      # 의존성 패키지 목록
```

## 설치 및 설정

### 1. 필수 패키지 설치

```bash
pip install -r requirements.txt 
```
#### requirements.txt의 내용:
```txt
fastapi==0.103.1
uvicorn==0.23.2
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
oracledb==1.3.2
sqlalchemy==2.0.20
python-dotenv==1.0.0
aiofiles==23.2.1
gunicorn==21.2.0
pydantic==2.3.0
email-validator==2.0.0.post2
```
### 2. Oracle 클라이언트 설치
Oracle 데이터베이스에 연결하려면 Oracle 클라이언트 라이브러리가 필요합니다.

#### Windows:
- Oracle Instant Client를 다운로드 및 설치
- PATH 환경 변수에 Oracle Instant Client 경로 추가

#### Linux (Ubuntu/Debian):
```bash
sudo apt-get install libaio1
# Oracle Instant Client 다운로드 및 설치
sudo sh -c "echo /opt/oracle/instantclient_19_8 > /etc/ld.so.conf.d/oracle-instantclient.conf"
sudo ldconfig
```
#### macOS:
```bash
brew install libaio
# Oracle Instant Client 다운로드 및 설치
```

### 3. 환경 변수 설정
**.env** 파일을 생성하고 다음 환경 변수를 설정하세요:
```bash
#서버 설정
HOST=0.0.0.0
PORT=8000
DEBUG=True

# 데이터베이스 설정
DB_USER=oracle_username
DB_PASSWORD=oracle_password
DB_HOST=localhost
DB_PORT=1521
DB_SERVICE=XEPDB1

# 보안 설정
JWT_SECRET_KEY=your_secret_key_here_make_it_very_long_and_random_for_security
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS 설정
CORS_ORIGINS=http://localhost:3000,http://frontend.example.com

# 로깅 설정
LOG_LEVEL=INFO

# 파일 업로드 설정
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE=5242880
```

### 4. 데이터베이스 테이블 생성
SQLAlchemy ORM을 사용하여 테이블을 생성합니다:
```bash
python app/create_tables.py
```
이 명령은 `models.py`에 정의된 모델을 기반으로 데이터베이스 테이블을 자동으로 생성합니다. 

별도의 SQL 스크립트가 필요하지 않습니다.

## 실행 방법
```bash
cd app
uvicorn main:app --reload
```
또는 `main.py`를 직접 실행할 수 있습니다:
```bash
python app/main.py
```
서버가 `http://localhost:8000` 에서 실행됩니다. API 문서는 `http://localhost:8000/docs`에서 확인할 수 있습니다.

## 주요 기능
### 아키텍처 패턴
이 템플릿은 레포지토리-서비스-라우터 패턴을 따릅니다:

- **레포지토리**: 데이터베이스 작업 캡슐화
- **서비스**: 비즈니스 로직 구현
- **라우터**: HTTP 엔드포인트 정의

### 데이터베이스 접근
두 가지 방법으로 데이터베이스에 접근할 수 있습니다:

1. **SQLAlchemy ORM**: `models.py`에 정의된 객체 모델을 통한 접근
2. **직접 SQL 쿼리**: `utils/database.py`의 `execute_query` 함수를 통한 접근

### 설정 관리
`config.py`는 Pydantic의 `BaseSettings`를 사용하여 환경 변수를 로드하고 타입 검증을 수행합니다:
```python
# 설정 사용 예시
from config import settings

# 설정 값 사용
db_user = settings.DB_USER
upload_dir = settings.UPLOAD_DIR
```

### 인증 및 권한
**JWT(JSON Web Token)** 를 사용하여 사용자 인증과 권한 부여를 처리합니다:

- `auth/jwt_handler.py`: 토큰 생성 및 검증
- `auth/jwt_bearer.py`: FastAPI 의존성을 통한 라우트 보호

### 파일 업로드
`service/file_service.py`에는 파일 업로드 처리 로직이 포함되어 있습니다:

- 파일 저장 및 UUID 기반 이름 생성
- 데이터베이스에 파일 메타데이터 저장
- 파일 접근 권한 확인

### 에러 핸들링
`utils/error_handlers.py`는 다양한 예외 상황을 처리하는 핸들러를 제공합니다:

- 요청 검증 오류
- 데이터베이스 오류
- JWT 인증 오류
- 일반 예외

### 페이지네이션
`utils/pagination.py`는 API 결과를 페이지네이션하는 유틸리티를 제공합니다:
```python
# 페이지네이션 사용 예시
from utils.pagination import PageParams, paginate

@router.get("/items", response_model=Page[ItemResponse])
def get_items(page_params: PageParams = Depends()):
    items = item_service.get_items(page_params.offset, page_params.page_size)
    total = item_service.count_items()
    return paginate(items, total, page_params)
```
### Oracle DB 특화 기능
`utils/oracle_utils.py`에는 Oracle DB 특화 기능을 활용하기 위한 유틸리티 함수가 포함되어 있습니다:

- 저장 프로시저 호출
- 효율적인 페이지네이션 (OFFSET-FETCH 및 ROWNUM 방식)
- Oracle 특화 데이터 타입 처리 (CLOB, BLOB 등)

#### 코드 예시
##### 레포지토리 패턴
```python
# app/repository/user_repository.py
from utils.database import execute_query

class UserRepository:
    @staticmethod
    def get_user_by_id(user_id: int):
        query = "SELECT * FROM users WHERE id = :user_id AND deleted_at IS NULL"
        result = execute_query(query, {"user_id": user_id})
        return result[0] if result else None
```
##### 서비스 패턴
```python
# app/service/user_service.py
from repository.user_repository import UserRepository
from fastapi import HTTPException

class UserService:
    def __init__(self, db=None):
        self.db = db
        self.user_repository = UserRepository
    
    def get_user_by_id(self, user_id: int):
        user = self.user_repository.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
```
##### 라우터 패턴
```python
# app/router/user_router.py
from fastapi import APIRouter, Depends
from service.user_service import UserService
from models import get_db

router = APIRouter(prefix="/api/users", tags=["Users"])

@router.get("/{user_id}")
def get_user(user_id: int, db = Depends(get_db)):
    user_service = UserService(db)
    return user_service.get_user_by_id(user_id)
```
##### 트랜잭션 관리
```python
# 트랜잭션 사용 예시
from utils.transaction import transaction_context

def create_post_with_files(post_data, files, user_id, db):
    with transaction_context(db) as tx:
        # 트랜잭션 내에서 여러 작업 수행
        post = post_repository.create_post(post_data, user_id, db)
        
        for file in files:
            file_repository.save_file(file, post["id"], db)
        
        # 예외가 발생하면 자동으로 롤백됨
        return post
```
### API 엔드포인트
이 템플릿은 다음과 같은 API 엔드포인트를 제공합니다:

- **사용자 관리**: 등록, 로그인, 정보 조회/수정/삭제
- **게시물 관리**: 작성, 조회, 수정, 삭제
- **댓글 관리**: 작성, 조회, 수정, 삭제
- **파일 관리**: 업로드, 다운로드, 삭제

모든 API 엔드포인트는 Swagger UI(`/docs`)에서 자세히 문서화됩니다.
## 개발 팁
### 1. Oracle DB 연결 문제 해결
Oracle DB 연결에 문제가 있다면 다음을 확인하세요:
```python
# 연결 문제 디버깅
import oracledb
oracledb.init_oracle_client()  # Instant Client 초기화
```
### 2. Oracle 특화 SQL 문법
Oracle DB는 다른 데이터베이스와 문법이 다를 수 있습니다:

- **페이지네이션**: `OFFSET ... ROWS FETCH NEXT ... ROWS ONLY` (12c 이상)
- **자동 증가**: `IDENTITY` 또는 시퀀스 사용
- **날짜/시간 처리**: `TO_DATE`, `TO_TIMESTAMP` 함수 사용

### 3. ORM과 Raw SQL 선택
성능이 중요한 쿼리나 복잡한 쿼리의 경우 **Raw SQL**을 사용하는 것이 더 효율적일 수 있습니다:
```python
# ORM 사용
users = db.query(User).filter(User.role == "admin").all()

# Raw SQL 사용
users = execute_query("SELECT * FROM users WHERE role = :role", {"role": "admin"})
```
## 배포
### Docker 활용
`Dockerfile` 예시:
```dockerfile
FROM python:3.9

WORKDIR /app

# Oracle Instant Client 설치
RUN apt-get update && apt-get install -y libaio1 wget unzip \
    && wget https://download.oracle.com/otn_software/linux/instantclient/211000/instantclient-basic-linux.x64-21.1.0.0.0.zip \
    && unzip instantclient-basic-linux.x64-21.1.0.0.0.zip \
    && rm instantclient-basic-linux.x64-21.1.0.0.0.zip \
    && mv instantclient_21_1 /opt/oracle/instantclient \
    && echo /opt/oracle/instantclient > /etc/ld.so.conf.d/oracle-instantclient.conf \
    && ldconfig

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Docker Compose
`docker-compose.yml` 예시:
```yaml
version: '3'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./app:/app
      - ./uploads:/app/uploads
    env_file:
      - .env
    depends_on:
      - oracle

  oracle:
    image: gvenzl/oracle-xe:21
    ports:
      - "1521:1521"
    environment:
      - ORACLE_PASSWORD=securepassword
      - ORACLE_DATABASE=XEPDB1
    volumes:
      - oracle-data:/opt/oracle/oradata

volumes:
  oracle-data:
```
## 운영 환경 설정
프로덕션 환경에서는 다음 설정을 고려하세요:

- **Gunicorn**: 프로덕션 WSGI 서버로 Gunicorn 사용
- **HTTPS**: Nginx나 다른 프록시를 통한 HTTPS 설정
- **로깅**: 적절한 로깅 설정
- **환경 변수**: 보안을 위해 민감한 정보는 환경 변수로 관리

## 기여 방법

1. 이 저장소를 포크합니다.
2. 새 기능 브랜치를 생성합니다 (`git checkout -b feature/amazing-feature`).
3. 변경 사항을 커밋합니다 (`git commit -m 'Add some amazing feature'`).
4. 브랜치를 푸시합니다 (`git push origin feature/amazing-feature`).
5. Pull Request를 생성합니다.

## 문의
프로젝트에 대한 질문이나 제안이 있으시면 이슈를 생성하거나, `ellie19981008@gmail.com`으로 이메일 주세요.
