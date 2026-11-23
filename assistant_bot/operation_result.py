"""도구 실행에서 얻은 근거. 디스코드와 검증 서버가 동일한 상태를 읽는다."""

from typing import NotRequired, TypedDict


class OperationResult(TypedDict):
    text: str
    status: NotRequired[str]
    changed: NotRequired[bool]
    source: NotRequired[str]
    opened: NotRequired[bool]
    source_urls: NotRequired[list[str]]
    unread: NotRequired[list[str]]
    file_refs: NotRequired[list[dict]]
    urls: NotRequired[list[str]]
    feeds: NotRequired[list[str]]
