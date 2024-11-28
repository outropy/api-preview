from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

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


class TaskRunResponse(BaseModel):
    urn: str = Field(description="The URN for this task run")
    pipeline_urn: str = Field(
        description="The URN of the pipeline that executed this task"
    )
    pipeline_version_urn: str = Field(
        description="The URN of the pipeline version that executed this task"
    )
    href: str = Field(description="URL that can be used to visualize the task run")
    results_urn: Optional[str] = Field(
        description="The URN of the results of this task run", default=None
    )
    created_at: datetime = Field(description="When this task run was created")
    updated_at: datetime = Field(description="When this task run was last updated")
    duration: float = Field(description="The duration of this task run in seconds")

    pipeline_name: str = Field(
        deprecated=True, description="Internal usage, will be removed in the future"
    )
    task_type: str = Field(
        deprecated=True, description="Internal usage, will be removed in the future"
    )
    task_icon: str = Field(
        deprecated=True, description="Internal usage, will be removed in the future"
    )
    pipeline_version_name: str = Field(
        deprecated=True, description="Internal usage, will be removed in the future"
    )
    status_str: str = Field(
        deprecated=True, description="Internal usage, will be removed in the future"
    )
    status_description: str = Field(description="A description of the task run status")

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


class TaskExecuteResponse(BaseModel):
    urn: str = Field(
        description="The unique URN of the task run, can be used to retrieve its status and results later."
    )
    href: str = Field(description="URL that can be used to visualize the task run")


class PipelineRunsResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[TaskRunResponse]


class PipelineVersionsResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[PipelineVersionInfo]
