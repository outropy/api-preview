import asyncio
import io
import json
import os
from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Any, BinaryIO, Dict, List, Optional, Type, TypeVar, Union, cast

import httpx
from httpx import Response
from pydantic import BaseModel, Field

from outropy.client import OUTROPY_API_KEY
from outropy.client.api_headers import (
    UPLOAD_FILE_MIME_TYPE_HEADER,
    UPLOAD_FILE_SIZE_HEADER,
)
from outropy.client.benchmark import (
    BenchmarkExecuteRequest,
    BenchmarkRunResponse,
    CreateBenchmarkRequest,
)
from outropy.client.data_source import (
    DataSourceCreateResponse,
    DataSourceMetadata,
    DataSourceResponse,
)
from outropy.client.directives import Directives
from outropy.client.pipeline import PipelineExecuteResponse, PipelineRunResponse
from outropy.client.requests import (
    CreateDataSourceRequest,
    CreateTaskRequest,
    Example,
    ExecuteTaskRequest,
    OutropyUrn,
)
from outropy.types.pydantic_to_schema import (
    recursive_convert_pydantic_to_dict,
    to_schema,
)


class DefaultInput(BaseModel):
    text: str = Field()


class DefaultOutput(BaseModel):
    text: str = Field()


OutT = TypeVar("OutT", bound=BaseModel)
InT = TypeVar("InT", bound=BaseModel)

ReturnType = Type[OutT] | Type[str] | List[Type[OutT]] | List[Type[str]]


class Tasks(StrEnum):
    EXTRACT = "extract"
    TRANSFORM = "transform"
    RECOMMEND = "recommend"
    INGEST_REFERENCE_DATA = "ingest_reference_data"
    TEXT_TO_TEXT = "text_to_text"


class OutropyApi:

    def __init__(
        self, api_key: Optional[str] = None, api_endpoint: Optional[str] = None
    ) -> None:

        self.base_url = (
            api_endpoint
            or os.getenv("OUTROPY_API_ENDPOINT", None)
            or "http://localhost:8000/"
        )
        if not self.base_url.endswith("/"):
            self.base_url += "/"

        if api_key is None:
            api_key = os.getenv(OUTROPY_API_KEY, None)
            if api_key is None:
                raise ValueError(
                    f"API key is required either as an argument or in the environment variable {OUTROPY_API_KEY}"
                )
        self.api_key = api_key

    async def upload_file(self, mime_type: str, file_path: str | Path) -> OutropyUrn:
        # Get the file size
        path = Path(file_path) if isinstance(file_path, str) else file_path
        file_size = path.lstat().st_size

        # Open the file in binary mode
        with path.open("rb") as file_stream:
            file_name = path.name

            return await self._upload(file_name, mime_type, file_size, file_stream)

    async def upload_object(
        self, *, name: Optional[str] = None, obj: InT
    ) -> OutropyUrn:
        n = name or f"{obj.__class__.__name__}-{datetime.now().isoformat()}"
        return await self.upload_json(n, obj.model_dump())

    async def upload_text(self, name: str, mime_type: str, text: str) -> OutropyUrn:
        # Get the file size
        file_size = len(text)

        # Open the file in binary mode
        file_stream = io.BytesIO(text.encode())

        return await self._upload(name, mime_type, file_size, file_stream)

    async def upload_json(self, name: str, json_object: Dict[str, Any]) -> OutropyUrn:
        return await self.upload_text(name, "application/json", json.dumps(json_object))

    async def download_object(
        self, expected_type: Type[OutT], results_id: OutropyUrn
    ) -> Optional[OutT]:
        as_json = await self.download_json(results_id)
        if as_json is None:
            return None
        return expected_type(**as_json)

    async def download_json(self, data_urn: str) -> Optional[Dict[Any, Any]]:
        as_text = await self.download_text(data_urn)
        try:
            return json.loads(as_text)  # type: ignore
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse JSON: {as_text}") from e

    async def download_text(self, data_urn: str) -> str:
        path = f"/data/{data_urn}"
        response = await self._make_http_request(f"{self.base_url}api{path}", "GET", {})
        return response.text

    async def _upload(
        self, file_name: str, mime_type: str, file_size: int, file_stream: BinaryIO
    ) -> str:
        url = f"{self.base_url}api/data/upload"
        files = {"file": (file_name, file_stream, "multipart/form-data")}
        # Create the headers dictionary
        headers = {
            UPLOAD_FILE_SIZE_HEADER: str(file_size),
            UPLOAD_FILE_MIME_TYPE_HEADER: mime_type,
            OUTROPY_API_KEY: self.api_key,
        }
        # Create an async HTTPX client
        async with httpx.AsyncClient(timeout=60 * 10) as client:

            try:
                response = await client.post(url, headers=headers, files=files)
            except httpx.ConnectError as e:
                raise Exception(f"Connection error to {url}") from e

            # Raise an error if the request was unsuccessful
            response.raise_for_status()

            # Return the JSON response from the server
            returned_urns = response.json()
            # TODO: why a list?
            return str(returned_urns["urns"][0])

    async def _call_inference(self, path: str, request: BaseModel) -> Dict[str, Any]:
        if path[0] != "/":
            raise ValueError(f"Path must start with a /, got [{path}]")
        url = f"{self.base_url}api{path}"
        request_as_dict = recursive_convert_pydantic_to_dict(request)
        response = await self._make_json_http_request(url, "POST", request_as_dict)
        return response

    async def create_task(
        self,
        *,
        task: Tasks,
        name: str,
        reference_data: List[OutropyUrn] = [],
        input_type: Optional[Type[InT]] = None,
        output_type: Optional[Type[OutT]] = None,
        prompt: str,
        directives: Optional[Directives] = None,
        examples: List[Example] = [],
        collection_name: Optional[str] = None,
    ) -> OutropyUrn:
        path = "/pipelines/create"
        input_schema = to_schema(input_type or DefaultInput)
        output_schema = to_schema(output_type or DefaultOutput)
        request = CreateTaskRequest(
            task_type=task.value,
            name=name,
            directives=directives or Directives(),
            reference_data=reference_data,
            input_type=input_schema,
            output_type=output_schema,
            prompt=prompt,
            examples=examples,
            collection_name=collection_name,
        )
        response = await self._call_inference(path, request)
        return str(response["urn"])

    async def execute_task(
        self,
        task_urn: str,
        *,
        subject: Union[str, List[str]],
        directives: Optional[Directives] = None,
        reference_data: List[OutropyUrn] = [],
    ) -> PipelineExecuteResponse:
        subjects = subject if isinstance(subject, list) else [subject]

        if len(subjects) == 0:
            raise ValueError(
                f"Only one of subject or subjects can be provided, got [{subject}] and [{subjects}]"
            )

        path = "/pipelines/execute"
        request = ExecuteTaskRequest(
            task_urn=task_urn,
            subject_urns=subjects,
            directives=directives,
            reference_data=reference_data,
        )
        response = await self._call_inference(path, request)
        return PipelineExecuteResponse(**response)

    async def get_pipeline_run(self, run_id: OutropyUrn) -> PipelineRunResponse:
        path = f"/pipelines/runs/{run_id}"
        response = await self._make_json_http_request(
            f"{self.base_url}api{path}", "GET", {}
        )
        return PipelineRunResponse(**response)

    async def wait_until_finishes_running(
        self, run_id: OutropyUrn
    ) -> PipelineRunResponse:
        run_info = await self.get_pipeline_run(run_id)
        while run_info.status.is_running:
            run_info = await self.get_pipeline_run(run_id)
            await asyncio.sleep(1)  # TODO: exponential backoff
        return run_info

    async def execute_and_wait_for_results(
        self,
        task_urn: str,
        *,
        subject: Union[str, List[str]],
        directives: Optional[Directives] = None,
        reference_data: List[OutropyUrn] = [],
    ) -> str:
        job = await self.execute_task(
            task_urn,
            subject=subject,
            directives=directives,
            reference_data=reference_data,
        )
        response = await self.wait_until_finishes_running(job.urn)
        if response.results_urn is None:
            raise Exception(f"Pipeline run [{job.urn}] did not produce any results")

        return await self.download_text(response.results_urn)

    async def list_data_sources(self) -> List[DataSourceResponse]:
        path = "/data-sources/list"
        response: list[dict[str, Any]] = cast(
            list[dict[str, Any]],
            await self._make_json_http_request(f"{self.base_url}api{path}", "GET", {}),
        )
        return [DataSourceResponse(**data_source) for data_source in response]

    async def set_hyperparams(self, task_urn: str, hyperparams: Dict[str, str]) -> None:
        path = f"/pipelines/{task_urn}/hyperparams"
        await self._make_json_http_request(
            f"{self.base_url}api{path}", "POST", hyperparams
        )

    async def create_data_source(
        self,
        name: str,
        description: Optional[str] = None,
        directives: Optional[Directives] = None,
    ) -> DataSourceCreateResponse:
        path = "/data-sources/create"
        request = CreateDataSourceRequest(
            name=name, description=description, directives=directives
        )
        response = await self._make_json_http_request(
            f"{self.base_url}api{path}", "POST", request.model_dump()
        )
        return DataSourceCreateResponse.model_validate(response)

    async def set_metadata(self, data_urn: str, metadata: Dict[str, str]) -> None:
        path = f"/data/{data_urn}/metadata"
        await self._make_json_http_request(
            f"{self.base_url}api{path}", "POST", metadata
        )

    async def get_metadata(self, data_urn: str) -> DataSourceMetadata:
        path = f"/data/{data_urn}/metadata"
        response = await self._make_json_http_request(
            f"{self.base_url}api{path}", "GET", {}
        )
        return DataSourceMetadata.model_validate(response)

    async def create_benchmark(
        self, name: str, description: str, task_instance_urn: str, query_urns: list[str]
    ) -> str:
        path = "/benchmarks/create"
        request = CreateBenchmarkRequest(
            name=name,
            description=description,
            task_instance_urn=task_instance_urn,
            query_urns=query_urns,
        )
        response = await self._call_inference(path, request)
        return str(response["urn"])

    async def execute_benchmark(
        self, benchmark_urn: str, hyperparams: dict[str, str]
    ) -> BenchmarkRunResponse:
        path = "/benchmarks/execute"
        request = BenchmarkExecuteRequest(
            benchmark_urn=benchmark_urn, hyperparams=hyperparams
        )
        response = await self._call_inference(path, request)
        return BenchmarkRunResponse(**response)

    async def get_benchmark_run(self, run_id: OutropyUrn) -> BenchmarkRunResponse:
        path = f"/benchmarks/runs/{run_id}"
        response = await self._make_json_http_request(
            f"{self.base_url}api{path}", "GET", {}
        )
        return BenchmarkRunResponse(**response)

    async def _make_http_request(
        self, url: str, method: str, payload: Dict[str, str]
    ) -> Response:
        headers: Dict[str, str] = {
            OUTROPY_API_KEY: self.api_key,
        }
        payload = recursive_convert_pydantic_to_dict(payload)

        try:
            async with httpx.AsyncClient(
                timeout=60 * 10, follow_redirects=True
            ) as client:
                if method == "POST":
                    response = await client.post(url, headers=headers, json=payload)
                else:
                    response = await client.get(url, headers=headers, params=payload)

                response.raise_for_status()  # Raise an exception for HTTP errors
                return response
        except httpx.HTTPStatusError as e:
            raise Exception(
                f"HTTP error when performing a {e.request.method} {e.request.url}:  {e.response.status_code}: {e.response.text}"
            ) from e
        except httpx.ConnectError as e:
            raise Exception(f"Connection error to {url}") from e

    async def _make_json_http_request(
        self, url: str, method: str, payload: Dict[str, str]
    ) -> Dict[str, Any]:
        response = await self._make_http_request(url, method, payload)
        return response.json()  # type: ignore
