from sqlalchemy import text

from db.database import engine
from db.base import Base
from db.models.review_job import ReviewJob


with engine.connect() as connection:
    print(Base.metadata.tables)
    result = connection.execute(text("SELECT 1"))
    print(result.scalar())