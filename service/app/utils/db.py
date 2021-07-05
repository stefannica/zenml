from app.db.session import Session


# Dependency
def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()
