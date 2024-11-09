from typing import Literal, Optional

from pydantic import BaseModel


class BenchmarkCreateResponse(BaseModel):
    urn: str
    href: str


class CreateBenchmarkRequest(BaseModel):
    name: str
    description: str
    task_instance_urn: str
    query_urns: list[str]


class BenchmarkExecuteRequest(BaseModel):
    benchmark_urn: Optional[str] = None
    benchmark_name: Optional[str] = None
    hyperparams: dict[str, str]


class PopulationStats(BaseModel):
    pop_count: int
    mean: float
    std_dev: float
    median: float
    q1: float
    q3: float
    iqr: float


class BenchmarkRunResponse(BaseModel):
    urn: str
    status: Literal["scheduled", "running", "completed", "failed"]
    score_stats: Optional[PopulationStats]
    execution_time_stats: Optional[PopulationStats]
    llm_cost_stats: Optional[PopulationStats]
    hyperparams: dict[str, str]

    @property
    def is_running(self) -> bool:
        return self.status == "running"
