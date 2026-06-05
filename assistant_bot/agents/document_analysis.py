from __future__ import annotations

import json
from dataclasses import dataclass

import discord

from assistant_bot.config import Config
from assistant_bot.file_extractor import (
    content_type_for_filename,
    extract_bytes_text,
    is_vision_attachment,
    pdf_has_images,
    render_pdf_pages_to_png,
    validate_extracted_text,
)
from assistant_bot.models import ConversationScope, MemoryDetail, PreparedAttachment
from assistant_bot.openai_service import OpenAIService
from assistant_bot.operation_result import OperationResult
from assistant_bot.persona import ASSISTANT_PERSONA
from assistant_bot.stores import AgentLogStore, MemoryStore, VisionOcrUsageStore
from assistant_bot.time_utils import today_string


@dataclass(frozen=True)
class OcrTarget:
    filename: str
    content_type: str | None
    source_size: int
    images: tuple[tuple[str, bytes], ...]


@dataclass(frozen=True)
class PdfVisualCandidate:
    filename: str
    content_type: str | None
    source_size: int
    local_text: str
    images: tuple[tuple[str, bytes], ...]


class DocumentAnalysisAgent:
    def __init__(
        self,
        *,
        config: Config,
        openai: OpenAIService,
        memories: MemoryStore,
        usage: VisionOcrUsageStore,
        logs: AgentLogStore,
    ) -> None:
        self.config = config
        self.openai = openai
        self.memories = memories
        self.usage = usage
        self.logs = logs

    def quota_status(self, *, scope: ConversationScope) -> OperationResult:
        usage_date = today_string(self.config.timezone)
        used = self.usage.used_today(user_id=scope.user_id, usage_date=usage_date)
        remaining = self.usage.remaining_today(
            user_id=scope.user_id,
            usage_date=usage_date,
            daily_limit_bytes=self.config.vision_ocr_daily_bytes,
        )
        return OperationResult(
            agent="document_analysis",
            intent="analyze_document",
            status="success",
            summary="비전 OCR 잔여 용량 조회",
            facts={
                "usage_date": usage_date,
                "used_bytes": used,
                "remaining_bytes": remaining,
                "daily_limit_bytes": self.config.vision_ocr_daily_bytes,
                "per_message_limit_bytes": self.config.vision_ocr_per_message_bytes,
            },
            fallback_text=(
                f"오늘 비전/OCR 분석 가능 잔여 용량은 {format_bytes(remaining)}입니다. "
                f"하루 한도는 {format_bytes(self.config.vision_ocr_daily_bytes)}, "
                f"한 번의 채팅 한도는 {format_bytes(self.config.vision_ocr_per_message_bytes)}예요. "
                "로컬에서 읽을 수 있는 문서 분석은 이 한도에서 차감하지 않습니다."
            ),
        )

    async def analyze(
        self,
        *,
        text: str,
        scope: ConversationScope,
        message_id: str,
        attachments: list[discord.Attachment],
    ) -> OperationResult:
        if not attachments:
            return self.quota_status(scope=scope)

        prepared: list[PreparedAttachment] = []
        ocr_targets: list[OcrTarget] = []
        pdf_visual_candidates: list[PdfVisualCandidate] = []
        errors: list[str] = []

        for attachment in attachments:
            if attachment.size > self.config.max_attachment_bytes:
                errors.append(f"`{attachment.filename}`은 파일이 너무 큽니다.")
                continue
            data = await attachment.read()
            try:
                local_text = extract_bytes_text(data, filename=attachment.filename)
                validate_extracted_text(local_text, attachment.filename)
                if (
                    attachment.filename.lower().endswith(".pdf")
                    and not wants_text_only_analysis(text)
                    and pdf_has_images(data)
                ):
                    try:
                        images = render_pdf_pages_to_png(data, filename=attachment.filename)
                    except ValueError as render_error:
                        errors.append(f"`{attachment.filename}` 이미지 분석 준비 실패: {render_error}")
                    else:
                        pdf_visual_candidates.append(
                            PdfVisualCandidate(
                                filename=attachment.filename,
                                content_type=attachment.content_type
                                or content_type_for_filename(attachment.filename),
                                source_size=attachment.size,
                                local_text=local_text,
                                images=tuple(images),
                            )
                        )
                        continue
                prepared.append(
                    PreparedAttachment(
                        filename=attachment.filename,
                        content_type=attachment.content_type or content_type_for_filename(attachment.filename),
                        text=local_text,
                        size=attachment.size,
                        extraction_method="local",
                    )
                )
                continue
            except ValueError as error:
                if is_vision_attachment(attachment.filename):
                    ocr_targets.append(
                        OcrTarget(
                            filename=attachment.filename,
                            content_type=attachment.content_type or content_type_for_filename(attachment.filename),
                            source_size=attachment.size,
                            images=((attachment.filename, data),),
                        )
                    )
                    continue
                if attachment.filename.lower().endswith(".pdf"):
                    try:
                        images = render_pdf_pages_to_png(data, filename=attachment.filename)
                    except ValueError as render_error:
                        errors.append(f"`{attachment.filename}` OCR 준비 실패: {render_error}")
                        continue
                    ocr_targets.append(
                        OcrTarget(
                            filename=attachment.filename,
                            content_type=attachment.content_type or content_type_for_filename(attachment.filename),
                            source_size=attachment.size,
                            images=tuple(images),
                        )
                    )
                    continue
                errors.append(f"`{attachment.filename}` 분석 실패: {error}")

        ocr_bytes = sum(target.source_size for target in ocr_targets) + sum(
            candidate.source_size for candidate in pdf_visual_candidates
        )
        quota_result = self._check_quota(scope=scope, ocr_bytes=ocr_bytes)
        if quota_result is not None:
            return quota_result

        charged_vision_bytes = 0
        for candidate in pdf_visual_candidates:
            try:
                selected_images = await self._select_pdf_visual_pages(candidate, user_text=text)
                charged_vision_bytes += candidate.source_size
            except Exception as error:
                errors.append(f"`{candidate.filename}` 이미지 선별 실패: {error}")
                prepared.append(
                    PreparedAttachment(
                        filename=candidate.filename,
                        content_type=candidate.content_type,
                        text=candidate.local_text,
                        size=candidate.source_size,
                        extraction_method="local",
                    )
                )
                continue

            visual_text = ""
            if selected_images:
                try:
                    visual_text = await self._extract_ocr_text(
                        OcrTarget(
                            filename=candidate.filename,
                            content_type=candidate.content_type,
                            source_size=candidate.source_size,
                            images=tuple(selected_images),
                        )
                    )
                    validate_extracted_text(visual_text, candidate.filename)
                except Exception as error:
                    errors.append(f"`{candidate.filename}` 중요 이미지 분석 실패: {error}")
                    visual_text = ""

            combined_text = candidate.local_text
            used_vision = bool(visual_text)
            if visual_text:
                combined_text = (
                    f"{candidate.local_text}\n\n"
                    "[PDF 중요 이미지 분석]\n"
                    f"{visual_text}"
                )
            prepared.append(
                PreparedAttachment(
                    filename=candidate.filename,
                    content_type=candidate.content_type,
                    text=combined_text,
                    size=candidate.source_size,
                    extraction_method="mixed_pdf_visual" if used_vision else "local",
                    used_vision_ocr=used_vision,
                )
            )

        for target in ocr_targets:
            try:
                ocr_text = await self._extract_ocr_text(target)
                validate_extracted_text(ocr_text, target.filename)
                prepared.append(
                    PreparedAttachment(
                        filename=target.filename,
                        content_type=target.content_type,
                        text=ocr_text,
                        size=target.source_size,
                        extraction_method="vision_ocr",
                        used_vision_ocr=True,
                    )
                )
                charged_vision_bytes += target.source_size
            except Exception as error:
                errors.append(f"`{target.filename}` OCR 실패: {error}")

        if charged_vision_bytes:
            self.usage.record_usage(
                user_id=scope.user_id,
                usage_date=today_string(self.config.timezone),
                bytes_used=charged_vision_bytes,
                source_message_id=message_id,
            )

        saved_documents = await self._save_prepared_documents(
            scope=scope,
            message_id=message_id,
            prepared=prepared,
        )
        if not saved_documents:
            return OperationResult(
                agent="document_analysis",
                intent="analyze_document",
                status="unsupported",
                summary="분석 가능한 파일 없음",
                warnings=tuple(errors),
                fallback_text="분석할 수 있는 텍스트를 찾지 못했어요.",
            )

        answer = await self._answer(text=text, documents=saved_documents)
        self.logs.add(
            conversation_id=scope.conversation_id,
            agent="document_analysis",
            intent="analyze_document",
            difficulty="medium",
            model=self.config.medium_model,
            reason="파일 분석 전용 에이전트 응답",
        )
        return OperationResult(
            agent="document_analysis",
            intent="analyze_document",
            status="success",
            summary="파일 분석 완료",
            facts={
                "document_ids": [document.id for document in saved_documents],
                "vision_ocr_bytes": charged_vision_bytes,
                "vision_ocr_model": self.config.vision_ocr_model,
                "vision_detail": "auto",
                "answer": answer,
            },
            items=tuple(
                {
                    "kind": "document",
                    "id": document.id,
                    "title": document.title,
                    "chunk_count": document.chunk_count,
                }
                for document in saved_documents
            ),
            warnings=tuple(errors),
            preserve_values=tuple(str(document.id) for document in saved_documents),
            fallback_text=answer,
        )

    def _check_quota(self, *, scope: ConversationScope, ocr_bytes: int) -> OperationResult | None:
        if ocr_bytes <= 0:
            return None
        usage_date = today_string(self.config.timezone)
        used = self.usage.used_today(user_id=scope.user_id, usage_date=usage_date)
        remaining = max(0, self.config.vision_ocr_daily_bytes - used)
        if ocr_bytes > self.config.vision_ocr_per_message_bytes:
            return self._quota_result(
                status_reason="single_message_limit_exceeded",
                requested_bytes=ocr_bytes,
                used_bytes=used,
                remaining_bytes=remaining,
                usage_date=usage_date,
            )
        if used + ocr_bytes > self.config.vision_ocr_daily_bytes:
            return self._quota_result(
                status_reason="daily_limit_exceeded",
                requested_bytes=ocr_bytes,
                used_bytes=used,
                remaining_bytes=remaining,
                usage_date=usage_date,
            )
        return None

    def _quota_result(
        self,
        *,
        status_reason: str,
        requested_bytes: int,
        used_bytes: int,
        remaining_bytes: int,
        usage_date: str,
    ) -> OperationResult:
        return OperationResult(
            agent="document_analysis",
            intent="analyze_document",
            status="unsupported",
            summary="비전 OCR 용량 제한 초과",
            facts={
                "reason": status_reason,
                "requested_bytes": requested_bytes,
                "used_bytes": used_bytes,
                "remaining_bytes": remaining_bytes,
                "usage_date": usage_date,
                "daily_limit_bytes": self.config.vision_ocr_daily_bytes,
                "per_message_limit_bytes": self.config.vision_ocr_per_message_bytes,
            },
            fallback_text=(
                f"이번 요청의 비전/OCR 대상 용량은 {format_bytes(requested_bytes)}라서 처리할 수 없어요. "
                f"오늘 남은 비전/OCR 용량은 {format_bytes(remaining_bytes)}이고, "
                f"한 번의 채팅 한도는 {format_bytes(self.config.vision_ocr_per_message_bytes)}입니다. "
                "로컬에서 읽을 수 있는 문서 분석은 이 한도에서 차감하지 않습니다."
            ),
        )

    async def _extract_ocr_text(self, target: OcrTarget) -> str:
        return await self.openai.vision_text_response(
            model=self.config.vision_ocr_model,
            instructions=(
                "이미지를 한국어로 분석한다. 먼저 이미지에 무엇이 보이는지 핵심 장면과 대상을 설명하고, "
                "읽을 수 있는 텍스트가 있으면 정확히 전사한다. "
                "표는 행 단위로 보존하고, 불확실한 글자는 [불확실]로 표시한다."
            ),
            prompt=(
                f"파일명: {target.filename}\n"
                "이미지의 시각적 내용과 읽을 수 있는 텍스트를 함께 분석해줘."
            ),
            images=list(target.images),
            detail="auto",
            temperature=0.0,
        )

    async def _select_pdf_visual_pages(
        self,
        candidate: PdfVisualCandidate,
        *,
        user_text: str,
    ) -> list[tuple[str, bytes]]:
        mode = "broad" if wants_visual_analysis(user_text) else "normal"
        response = await self.openai.vision_text_response(
            model=self.config.vision_ocr_model,
            instructions=(
                "너는 PDF 페이지 이미지 선별기다. 사용자의 문서 분석 요청에 답하는 데 필요한 시각 정보가 "
                "있는 페이지만 고른다. 차트, 표, 그래프, 다이어그램, UI 캡처, 제품 이미지, 계약/문서 스캔 일부, "
                "본문 텍스트로 설명되지 않은 핵심 시각 정보는 analyze=true다. 로고, 배경 이미지, 장식용 아이콘, "
                "반복 헤더/푸터, 의미 없는 썸네일, 본문 텍스트와 중복되는 이미지는 analyze=false다. "
                "JSON만 반환한다."
            ),
            prompt=(
                f"파일명: {candidate.filename}\n"
                f"선별 모드: {mode}\n"
                f"사용자 요청: {user_text}\n\n"
                "응답 형식:\n"
                '{"pages":[{"filename":"페이지 파일명","analyze":true,"reason":"짧은 이유"}]}'
            ),
            images=list(candidate.images),
            detail="auto",
            temperature=0.0,
        )
        selected_filenames = parse_selected_visual_pages(response)
        return [image for image in candidate.images if image[0] in selected_filenames]

    async def _save_prepared_documents(
        self,
        *,
        scope: ConversationScope,
        message_id: str,
        prepared: list[PreparedAttachment],
    ) -> list[MemoryDetail]:
        saved: list[MemoryDetail] = []
        for item in prepared:
            duplicate = self.memories.find_duplicate_document(scope=scope, text=item.text)
            if duplicate is not None:
                saved.append(duplicate)
                continue
            document_id, _ = await self.memories.save_document(
                scope=scope,
                filename=item.filename,
                content_type=item.content_type,
                text=item.text,
                source_message_id=message_id,
            )
            detail = self.memories.get_document_detail(scope=scope, document_id=document_id)
            if detail is not None:
                saved.append(detail)
        return saved

    async def _answer(self, *, text: str, documents: list[MemoryDetail]) -> str:
        file_summaries = []
        for document in documents:
            file_summaries.append(await self._summarize_document(text=text, document=document))
        answer = await self.openai.text_response(
            model=self.config.medium_model,
            instructions=f"""
{ASSISTANT_PERSONA}

너는 파일 분석 전용 에이전트다.
사용자의 요청에 맞춰 요약, 분석, 검토, 추출, 비교, 질문 답변 중 필요한 형식으로만 답한다.
문서에 없는 내용은 추측하지 않는다.
답변 끝에 참고한 문서 ID와 파일명을 짧게 적는다.
""",
            input_text=(
                f"사용자 요청:\n{text}\n\n"
                "파일별 분석 재료:\n" + "\n\n".join(file_summaries)
            ),
            temperature=0.2,
        )
        return answer.strip()

    async def _summarize_document(self, *, text: str, document: MemoryDetail) -> str:
        chunks = split_text(document.text, limit=6000)
        if len(chunks) == 1:
            return f"[문서 {document.id}: {document.title}]\n{chunks[0]}"
        summaries = []
        for index, chunk in enumerate(chunks, start=1):
            summary = await self.openai.text_response(
                model=self.config.easy_model,
                instructions=(
                    "긴 문서 분석을 위한 chunk 요약이다. 핵심 사실, 숫자, 일정, 리스크, 액션아이템을 보존한다."
                ),
                input_text=f"사용자 요청:\n{text}\n\n문서 {document.id} chunk {index}/{len(chunks)}:\n{chunk}",
                temperature=0.1,
            )
            summaries.append(f"- chunk {index}: {summary.strip()}")
        return f"[문서 {document.id}: {document.title}]\n" + "\n".join(summaries)


def split_text(text: str, *, limit: int) -> list[str]:
    normalized = text.strip()
    if len(normalized) <= limit:
        return [normalized]
    chunks = []
    remaining = normalized
    while remaining:
        chunk = remaining[:limit]
        cut = max(chunk.rfind("\n\n"), chunk.rfind("\n"), chunk.rfind(". "))
        if cut < limit // 2:
            cut = limit
        chunks.append(remaining[:cut].strip())
        remaining = remaining[cut:].strip()
    return chunks


def wants_text_only_analysis(text: str) -> bool:
    compact = "".join(text.casefold().split())
    markers = (
        "텍스트만",
        "글자만",
        "본문만",
        "이미지는빼고",
        "이미지빼고",
        "시각자료빼고",
        "textonly",
    )
    return any(marker in compact for marker in markers)


def wants_visual_analysis(text: str) -> bool:
    compact = "".join(text.casefold().split())
    markers = (
        "이미지도",
        "그림도",
        "차트도",
        "그래프도",
        "표도",
        "도표도",
        "시각자료",
        "이미지까지",
        "차트까지",
        "그래프까지",
        "visual",
    )
    return any(marker in compact for marker in markers)


def parse_selected_visual_pages(response: str) -> set[str]:
    cleaned = response.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`").strip()
        if cleaned.startswith("json"):
            cleaned = cleaned[4:].strip()
    payload = json.loads(cleaned)
    pages = payload.get("pages", [])
    selected: set[str] = set()
    if not isinstance(pages, list):
        return selected
    for page in pages:
        if not isinstance(page, dict):
            continue
        filename = page.get("filename")
        analyze = page.get("analyze")
        if isinstance(filename, str) and analyze is True:
            selected.add(filename)
    return selected


def format_bytes(value: int) -> str:
    if value >= 1024 * 1024:
        return f"{value / (1024 * 1024):.1f}MB"
    if value >= 1024:
        return f"{value / 1024:.1f}KB"
    return f"{value}B"
