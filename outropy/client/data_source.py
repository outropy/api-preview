from typing import Optional

from pydantic import BaseModel


class DataSourceResponse(BaseModel):
    urn: str
    ingestion_task_urn: Optional[str]
    name: str
    description: str
    type_str: str
    status_str: str
    icon: str
    href: str


class DataSourceMetadata(BaseModel):
    urn: str
    file_name: str
    mime_type: str
    size_bytes: int
    metadata: dict[str, str]


class IndexCreateResponse(BaseModel):
    urn: str
    href: str
