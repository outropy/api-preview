from pydantic import BaseModel


class DataSourceResponse(BaseModel):
    urn: str
    name: str
    description: str
    type_str: str
    status_str: str
    icon: str


class DataSourceCreateResponse(BaseModel):
    data_source_urn: str
    ingestion_task_urn: str
    href: str


class DataSourceMetadata(BaseModel):
    urn: str
    file_name: str
    mime_type: str
    size_bytes: int
    metadata: dict[str, str]
