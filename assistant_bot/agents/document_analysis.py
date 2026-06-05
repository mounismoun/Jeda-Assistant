from __future__ import annotations

from dataclasses import dataclass

import discord

from assistant_bot.config import Config
from assistant_bot.file_extractor import (
    content_type_for_filename,
    extract_bytes_text,
    is_vision_attachment,
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
        errors: list[str] = []

        for attachment in attachments:
            if attachment.size > self.config.max_attachment_bytes:
                errors.append(f"`{attachment.filename}`은 파일이 너무 큽니다.")
                continue
            data = await attachment.read()
            try:
                local_text = extract_bytes_text(data, filename=attachment.filename)
                validate_extracted_text(local_text, attachment.filename)
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

        ocr_bytes = sum(target.source_size for target in ocr_targets)
        quota_result = self._check_quota(scope=scope, ocr_bytes=ocr_bytes)
        if quota_result is not None:
            return quota_result

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
            except Exception as error:
                errors.append(f"`{target.filename}` OCR 실패: {error}")

        if ocr_bytes and any(item.used_vision_ocr for item in prepared):
            self.usage.record_usage(
                user_id=scope.user_id,
                usage_date=today_string(self.config.timezone),
                bytes_used=ocr_bytes,
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
                "vision_ocr_bytes": ocr_bytes,
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
                "이미지 안의 모든 읽을 수 있는 텍스트를 한국어로 정확히 전사한다. "
                "표는 행 단위로 보존하고, 불확실한 글자는 [불확실]로 표시한다."
            ),
            prompt=f"파일명: {target.filename}\n이미지 또는 스캔 문서의 텍스트를 OCR로 추출해줘.",
            images=list(target.images),
            detail="auto",
            temperature=0.0,
        )

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


def format_bytes(value: int) -> str:
    if value >= 1024 * 1024:
        return f"{value / (1024 * 1024):.1f}MB"
    if value >= 1024:
        return f"{value / 1024:.1f}KB"
    return f"{value}B"
