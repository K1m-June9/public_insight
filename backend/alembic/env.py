import sys
import os
from logging.config import fileConfig
from sqlalchemy import pool
from alembic import context

# app 폴더를 sys.path에 추가해 app 모듈 접근 가능하게 함
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.F5_core.config import settings  # 환경변수 설정 불러오기
from app.F8_database.connection import Base  # ORM Base 메타데이터 (예: declarative_base)
from app.F7_models import *  # 모델 임포트

config = context.config

# alembic.ini 로부터 로그 설정 읽기
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# alembic.ini의 sqlalchemy.url 대신 settings.DATABASE_URL 사용
config.set_main_option('sqlalchemy.url', settings.DATABASE_URL)

target_metadata = Base.metadata

def run_migrations_offline():
    context.configure(
        url=settings.DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    from sqlalchemy import create_engine

    connectable = create_engine(settings.DATABASE_URL, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_mi_
