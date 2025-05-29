from sqlalchemy.ext.asyncio import AsyncSession

# 커스텀 모듈
from app.models.user import user_table

# user_table에 저장
async def repo_register_user(user_data:dict, db:AsyncSession)->bool:
    user_record = user_table(**user_data)
    try:
        user_record = user_table(**user_data)
        db.add(user_record)
        await db.commit()
        
        # 데이터 테스트때 보려고
        await db.refresh(user_record)  # 새로 삽입된 데이터 갱신
        print(f"사용자 {user_record.username} 저장 완료")
        return True
    except Exception as e:
        await db.rollback() # 트랜잭션 롤백
        print(f"DB commit error: {e}")  # 로그로 남기기
        return False
    
