from app.backend.db import SessionLocal

async def get_db():
    # db = SessionLocal()
    # try:
    #     yield db
    # finally:
    #     db.close()

    with SessionLocal() as db:
        yield db
