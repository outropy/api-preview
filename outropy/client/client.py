import io
import json
import os
from datetime import datetime
from typing import Any, BinaryIO, Dict, Optional, Type, TypeVar

import httpx
from httpx import Response
from pydantic import BaseModel, Field

from outropy.client.api_headers import (
    UPLOAD_FILE_MIME_TYPE_HEADER,
    UPLOAD_FILE_SIZE_HEADER,
)
from outropy.client.requests import OutropyUrn
from outropy.types.pydantic_to_schema import recursive_convert_pydantic_to_dict


class DefaultInput(BaseModel):
    text: str = Field()


class DefaultOutput(BaseModel):
    text: str = Field()


OutT = TypeVar("OutT", bound=BaseModel)
InT = TypeVar("InT", bound=BaseModel)


async def _make_http_request(
    url: str, method: str, payload: Dict[str, str]
) -> Response:
    headers: Dict[str, str] = {}
    payload = recursive_convert_pydantic_to_dict(payload)

    try:
        async with httpx.AsyncClient(timeout=60 * 10, follow_redirects=True) as client:
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
    url: str, method: str, payload: Dict[str, str]
) -> Dict[str, Any]:
    response = await _make_http_request(url, method, payload)
    return response.json()  # type: ignore


class OutropyHttpClient:
    def __init__(self, key: Any) -> None:
        self.base_url = "http://localhost:8000/"

    async def upload(
        self, file_name: str, mime_type: str, file_size: int, file_stream: BinaryIO
    ) -> str:
        url = f"{self.base_url}api/data/upload"
        files = {"file": (file_name, file_stream, "multipart/form-data")}
        # Create the headers dictionary
        headers = {
            UPLOAD_FILE_SIZE_HEADER: str(file_size),
            UPLOAD_FILE_MIME_TYPE_HEADER: mime_type,
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

    async def call_inference(self, path: str, request: BaseModel) -> Dict[str, Any]:
        if path[0] != "/":
            raise ValueError(f"Path must start with a /, got [{path}]")
        url = f"{self.base_url}api{path}"
        request_as_dict = recursive_convert_pydantic_to_dict(request)
        response = await _make_json_http_request(url, "POST", request_as_dict)
        return response

    async def authenticate(self, user_credentials: Any) -> None:
        pass

    async def upload_file(self, mime_type: str, file_path: str) -> OutropyUrn:
        # Get the file size
        file_size = os.path.getsize(file_path)

        # Open the file in binary mode
        with open(file_path, "rb") as file_stream:
            file_name = os.path.basename(file_path)

            return await self.upload(file_name, mime_type, file_size, file_stream)

    async def upload_object(
        self, *, name: Optional[str] = None, obj: InT
    ) -> OutropyUrn:
        n = name or f"{obj.__class__.__name__}-{datetime.now().isoformat()}"
        return await self.upload_text(
            n, "application/json", json.dumps(obj.model_dump())
        )

    async def upload_text(self, name: str, mime_type: str, text: str) -> OutropyUrn:
        # Get the file size
        file_size = len(text)

        # Open the file in binary mode
        file_stream = io.BytesIO(text.encode())

        return await self.upload(name, mime_type, file_size, file_stream)

    async def download_object(
        self, expected_type: Type[OutT], results_id: OutropyUrn
    ) -> Optional[OutT]:
        as_json = await self.download_json(results_id)
        if as_json is None:
            return None
        return expected_type(**as_json)

    async def download_json(self, data_urn: str) -> Optional[Dict[Any, Any]]:
        as_text = await self.download_text(data_urn)
        return json.loads(as_text)  # type: ignore

    async def download_text(self, data_urn: str) -> str:
        path = f"/data/{data_urn}"
        response = await _make_http_request(f"{self.base_url}api{path}", "GET", {})
        return response.text
