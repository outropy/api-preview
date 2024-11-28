from enum import StrEnum
from typing import Any, List, Optional, Tuple

from pydantic import BaseModel, Field

from outropy.client.directives import Directives
from outropy.copypasta.json.json import JSON_OBJECT

OutropyUrn = str
# TODO: this is too broad, need top be at least serializable to json
Example = Tuple[Any, Any]


class TaskNames(StrEnum):
    TRANSFORM_WITH_REF_DATA = "transform_with_ref_data"
    EXTRACT = "extract"
    TRANSFORM = "transform"
    RECOMMEND = "recommend"
    INGEST_REFERENCE_DATA = "ingest_reference_data"
    INGEST_DOCUMENT = "ingest_document"
    TEXT_TO_TEXT = "text_to_text"
    INDEX_DOCUMENT = "index_document"
    IDENTITY = "identity"

    @classmethod
    def is_valid(cls, name: str) -> bool:
        return name in cls.__members__.values()


class CreateTaskRequest(BaseModel):
    task_type: TaskNames = Field(description="The task you want to perform")
    name: str = Field(
        description="The unique name of the task",
        examples=["recommend-meal-with-preferences"],
    )
    input_type: Optional[JSON_OBJECT] = Field(
        description="A json schema describing the input type for requests to the task",
        default=None,
    )
    output_type: Optional[JSON_OBJECT] = Field(
        description="The output type for requests to the task", default=None
    )
    examples: List[Example] = Field(
        description="Examples of expected input and output for the task",
        default=[],
    )
    reference_data: List[OutropyUrn] = Field(
        description="The data sources that should be used as reference data for the task",
        default=[],
    )
    prompt: Optional[str] = Field(description="The prompt for the task", default=None)
    directives: Optional[Directives] = Field(
        description="The default directives to be applied when running the task",
        default=None,
    )
    collection_name: Optional[str] = Field(
        description="The name of the collection to use if this task end up creating one",
        default=None,
    )


class ExecuteTaskRequest(BaseModel):
    task_urn: str = Field(description="The URN of the task to run")
    subject_urns: List[str] = Field(
        description="The URN of the subjects for the request, at least one is required",
        min_length=1,
    )
    directives: Optional[Directives] = Field(
        description="(Optional) The directives to apply to this request, overriding the task defaults",
        default=None,
    )
    reference_data: Optional[List[OutropyUrn]] = Field(
        description="(Optional) Additional reference data sources to use for this request",
        default=None,
    )


class CreateDataSourceRequest(BaseModel):
    name: str = Field(description="The unique name of this data source")
    description: Optional[str] = Field(
        description="Description of the content to be store in this data source",
        default=None,
    )
    directives: Optional[Directives] = Field(
        description="Directives to control how the ingestion task will behave",
        default=None,
    )


class IndexerType(StrEnum):
    SEMANTIC_TEXT = "semantic_text"


class CreateIndexRequest(BaseModel):
    name: str = Field(
        description="The unique name of this index among the associated data source"
    )
    data_source_urn: str = Field(description="The URN of the data source to index")
    description: Optional[str] = Field(
        description="Description of the content to be indexed",
        default=None,
    )
    type: IndexerType = Field(description="The type of index to create")
