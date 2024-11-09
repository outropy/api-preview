from typing import Any, List, Optional, Tuple

from pydantic import BaseModel, Field

from outropy.client.directives import Directives
from outropy.copypasta.json.json import JSON_OBJECT

OutropyUrn = str
# TODO: this is too broad, nmeed top be at least serializable to json
Example = Tuple[Any, Any]


class CreateTaskRequest(BaseModel):
    task_type: str = Field(description="The task to perform")
    name: str = Field(description="The unique name of the pipeline")
    input_type: Optional[JSON_OBJECT] = Field(
        description="The input type for requests to the pipeline", default=None
    )
    output_type: Optional[JSON_OBJECT] = Field(
        description="The output type for requests to the pipeline", default=None
    )
    examples: List[Example] = Field(
        description="Examples of expected input and output for the pipeline",
        default=[],
    )
    reference_data: List[OutropyUrn] = Field(
        description="The data sources that should be used as reference data for the pipeline",
        default=[],
    )
    prompt: Optional[str] = Field(
        description="The prompt for the pipeline", default=None
    )
    directives: Directives = Field(
        description="The default directives to be applied when running the pipeline"
    )
    collection_name: Optional[str] = Field(
        description="The name of the collection to use if this task end up creating one",
        default=None,
    )


class ExecuteTaskRequest(BaseModel):
    task_urn: str = Field(description="The URN of the task to run")
    subject_urns: List[str] = Field(
        ..., description="The URN of the subjects for the request"
    )
    directives: Optional[Directives] = Field(
        description="The directives to apply to this request, overriding the pipeline defaults",
        default=None,
    )
    reference_data: Optional[List[OutropyUrn]] = Field(
        description="Additional reference data sources to use for this request",
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
