from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel

from outropy.copypasta.optional import ensure


class PipelineRunStatus(Enum):
    # TODO: Probably a good idea to decouple from the temporal sdk, but for now it will do
    UNSCHEDULED = "UNSCHEDULED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELED = "CANCELED"
    TERMINATED = "TERMINATED"
    CONTINUED_AS_NEW = "CONTINUED_AS_NEW"  # Do we need this?
    TIMED_OUT = "TIMED_OUT"

    @property
    def is_running(self) -> bool:
        return self in [
            PipelineRunStatus.RUNNING,
            PipelineRunStatus.UNSCHEDULED,
            PipelineRunStatus.CONTINUED_AS_NEW,
        ]

    @property
    def is_finished(self) -> bool:
        return self in [
            PipelineRunStatus.COMPLETED,
            PipelineRunStatus.FAILED,
            PipelineRunStatus.CANCELED,
            PipelineRunStatus.TERMINATED,
            PipelineRunStatus.TIMED_OUT,
        ]

    @property
    def is_successful(self) -> bool:
        return self == PipelineRunStatus.COMPLETED

    @property
    def is_failed(self) -> bool:
        return self in [
            PipelineRunStatus.FAILED,
            PipelineRunStatus.CANCELED,
            PipelineRunStatus.TERMINATED,
            PipelineRunStatus.TIMED_OUT,
        ]

    @classmethod
    def from_string(cls, status: str) -> Optional["PipelineRunStatus"]:
        return cls.__members__.get(status)


class PipelineRunResponse(BaseModel):
    urn: str
    pipeline_urn: str
    pipeline_name: str
    task_type: str
    task_icon: str
    pipeline_version_urn: str
    pipeline_version_name: str
    href: str
    status_str: str
    status_description: str
    results_urn: str
    created_at: datetime
    updated_at: datetime
    duration: float

    @property
    def status(self) -> PipelineRunStatus:
        return ensure(PipelineRunStatus.from_string(self.status_str))


class Badge(BaseModel):
    name: str
    style: str


class Action(BaseModel):
    action: str
    description: str
    icon: Optional[str] = None
    pipeline_urn: Optional[str] = None


class ExecutionStats(BaseModel):
    run_count: int
    success_count: int
    fail_count: int
    in_progress_count: int
    score: float


class PipelineVersionInfo(BaseModel):
    urn: str
    created_at: datetime
    version: str
    description: str
    status: str
    badges: list[Badge]
    actions: list[Action]
    stats: ExecutionStats


class PipelineCreateResponse(BaseModel):
    urn: str
    href: str


class PipelineExecuteResponse(BaseModel):
    urn: str
    href: str


class PipelineRunsResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[PipelineRunResponse]


class PipelineVersionsResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[PipelineVersionInfo]