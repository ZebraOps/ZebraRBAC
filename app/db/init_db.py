from app.db.session import engine, Base


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
