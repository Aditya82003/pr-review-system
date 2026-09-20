from enum import Enum
from db.base import Base
from uuid import uuid4
from datetime import datetime,timezone
from sqlalchemy import DateTime,String,Integer,Enum as SQLEnum
from sqlalchemy.orm import Mapped,mapped_column

class JobStatus(str,Enum):
    QUEUED="queued"
    RUNNING="running"
    COMPLETED="completed"
    SUSPENDED="suspended"
    FAILED="failed"

class ReviewJob(Base):
    __tablename__ = "review_jobs"
    
    id:Mapped[str] = mapped_column(
        String,
        default=lambda: str(uuid4()),
        primary_key=True
        )
    repo_full_name:Mapped[str] = mapped_column(
        String,
        nullable=False
        )
    pr_number:Mapped[int] = mapped_column(
        Integer,
        nullable=False
        )
    head_sha:Mapped[str] = mapped_column(
        String,
        nullable=False
        )
    installation_id:Mapped[int] = mapped_column(
        Integer,
        nullable=False
        )
    status:Mapped[JobStatus] = mapped_column(
        SQLEnum(JobStatus),
        default=JobStatus.QUEUED,
        nullable=False
        )
    check_run_id:Mapped[str] = mapped_column(
        String,
        nullable=True
        )
    created_at:Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda:datetime.now(timezone.utc),
        )
    finished_at:Mapped[datetime] = mapped_column(
        DateTime,
        nullable=True
        )