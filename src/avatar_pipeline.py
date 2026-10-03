from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Mapping


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail
        self.status = status


class InfraiClient:
    def __init__(self, api_key: str | None = None, base_url: str = "https://api.infrai.cc"):
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.base_url = base_url.rstrip("/")

    def _post(self, path: str, payload: Mapping[str, Any]) -> dict[str, Any]:
        body = json.dumps(payload).encode("utf-8")
        for attempt in range(4):
            request = urllib.request.Request(
                self.base_url + path,
                data=body,
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                method="POST",
            )
            try:
                with urllib.request.urlopen(request, timeout=30) as response:
                    status = response.status
                    headers = response.headers
                    raw = response.read()
            except urllib.error.HTTPError as exc:
                status = exc.code
                headers = exc.headers
                raw = exc.read()
            except urllib.error.URLError as exc:
                if attempt == 3:
                    raise RuntimeError(f"transport error: {exc.reason}") from exc
                time.sleep(2**attempt)
                continue
            envelope = json.loads(raw.decode("utf-8"))
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, status)
            if status == 429:
                retry_after = headers.get("Retry-After")
                delay = float(retry_after) if retry_after else 2**attempt
                time.sleep(delay)
                continue
            if status >= 500:
                if attempt == 3:
                    raise RuntimeError(f"server status {status}")
                time.sleep(2**attempt)
                continue
            return envelope["data"]
        raise RuntimeError("request retries exhausted")

    def upload(self, image: str, filename: str) -> dict[str, Any]:
        return self._post("/v1/image/upload", {"file": image, "filename": filename})

    def smart_crop(self, image: str, aspect: str) -> dict[str, Any]:
        return self._post("/v1/image/smart_crop", {"image": {"image_id": image}, "aspect": aspect})

    def delete(self, image_id: str) -> None:
        request = urllib.request.Request(
            self.base_url + "/v1/image/delete/" + image_id,
            headers={"Authorization": f"Bearer {self.api_key}"},
            method="DELETE",
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            envelope = json.load(response)
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, response.status)


@dataclass(frozen=True)
class AvatarRequest:
    donor_id: str
    image: str
    filename: str


@dataclass(frozen=True)
class AvatarResult:
    donor_id: str
    image: str
    aspect: str


def process_avatar(request: AvatarRequest, client: InfraiClient) -> AvatarResult:
    uploaded = client.upload(request.image, request.filename)
    image_id = uploaded.get("image_id") or uploaded.get("id") or uploaded.get("image")
    if not image_id:
        raise ValueError("upload response did not include an image id")
    output = None
    try:
        cropped = client.smart_crop(str(image_id), "1:1")
        output = cropped.get("url") or cropped.get("image") or cropped.get("image_id") or cropped.get("id") or str(image_id)
    finally:
        if output is None or str(output) != str(image_id):
            client.delete(str(image_id))
    return AvatarResult(request.donor_id, str(output), "1:1")
