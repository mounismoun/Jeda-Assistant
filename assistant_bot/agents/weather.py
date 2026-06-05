from __future__ import annotations

import json
import re

from assistant_bot.config import Config
from assistant_bot.models import ConversationScope, ExecutionContext
from assistant_bot.openai_service import OpenAIService
from assistant_bot.operation_result import OperationResult
from assistant_bot.stores import AgentLogStore, WeatherLocationStore
from assistant_bot.weather_provider import KmaWeatherProvider, WeatherLocationResolver, WeatherReport


class WeatherAgent:
    def __init__(
        self,
        *,
        config: Config,
        openai: OpenAIService,
        provider: KmaWeatherProvider,
        locations: WeatherLocationResolver,
        location_store: WeatherLocationStore,
        logs: AgentLogStore,
        web_search_agent=None,
    ) -> None:
        self.config = config
        self.openai = openai
        self.provider = provider
        self.locations = locations
        self.location_store = location_store
        self.logs = logs
        self.web_search_agent = web_search_agent

    async def handle(
        self,
        *,
        text: str,
        scope: ConversationScope,
        execution_context: ExecutionContext | None = None,
    ) -> OperationResult:
        wants_weather = asks_weather(text)
        wants_air_quality = asks_air_quality(text)
        if wants_air_quality and not wants_weather:
            return await self._search_air_quality(text=text, scope=scope, execution_context=execution_context)

        location = self.locations.resolve(text)
        used_recent_location = False
        if location is None:
            latest = self.location_store.get_latest(user_id=scope.user_id)
            if latest is not None:
                location = self.locations.from_store_item(latest)
                used_recent_location = True
        if location is None:
            return OperationResult(
                agent="weather",
                intent="weather",
                status="needs_input",
                summary="날씨 조회 지역 필요",
                fallback_text="어느 지역 기준으로 볼까요? 예: `서울 내일 날씨 알려줘`",
            )
        if not self.provider.available():
            return OperationResult(
                agent="weather",
                intent="weather",
                status="failed",
                summary="기상청 API 인증키 누락",
                fallback_text=(
                    "기상청 API 키가 설정되지 않아 날씨를 조회할 수 없어요. "
                    "`KMA_API_AUTH_KEY`를 설정해 주세요."
                ),
            )

        include_alerts = asks_alerts(text) or wants_weather
        self.logs.add(
            conversation_id=scope.conversation_id,
            agent="weather",
            intent="weather",
            difficulty="medium",
            model=self.config.medium_model,
            reason=f"KMA 예특보 API 조회; location={location.name}; alerts={include_alerts}",
        )
        try:
            report = self.provider.get_report(location=location, include_alerts=include_alerts)
        except Exception as error:
            return OperationResult(
                agent="weather",
                intent="weather",
                status="failed",
                summary="기상청 API 조회 실패",
                warnings=(str(error),),
                fallback_text=f"기상청 날씨 조회에 실패했어요. 오류: {error}",
            )

        self.location_store.save_latest(
            user_id=scope.user_id,
            location_name=location.name,
            nx=location.nx,
            ny=location.ny,
            land_reg_id=location.land_reg_id,
            weather_stn_id=location.weather_stn_id,
        )
        answer = await self._compose_weather_answer(text=text, report=report, used_recent_location=used_recent_location)
        warnings: list[str] = []
        if wants_air_quality:
            air_quality = await self._search_air_quality(
                text=f"{location.name} 미세먼지 대기질 현재 정보",
                scope=scope,
                execution_context=execution_context,
            )
            if air_quality.status == "success":
                answer = f"{answer}\n\n미세먼지/대기질은 별도 검색 기준입니다.\n{air_quality.fallback_text}"
            else:
                warnings.append("미세먼지/대기질 검색 실패 또는 설정 누락")

        return OperationResult(
            agent="weather",
            intent="weather",
            status="success",
            summary="기상청 예특보 API 날씨 조회",
            facts={
                "location": location.name,
                "used_recent_location": used_recent_location,
                "base_date": report.base_date,
                "base_time": report.base_time,
                "cache_events": list(report.cache_events),
            },
            items=tuple(moment_to_item(moment) for moment in report.moments[:6]),
            warnings=tuple(warnings),
            preserve_values=(location.name,),
            fallback_text=answer,
        )

    async def _search_air_quality(
        self,
        *,
        text: str,
        scope: ConversationScope,
        execution_context: ExecutionContext | None,
    ) -> OperationResult:
        if self.web_search_agent is None:
            return OperationResult(
                agent="weather",
                intent="weather",
                status="unsupported",
                summary="미세먼지 웹검색 도구 없음",
                fallback_text="미세먼지나 대기질은 기상청 예특보 API 범위가 아니라 웹검색 설정이 필요해요.",
            )
        return await self.web_search_agent.search(
            text=text,
            scope=scope,
            execution_context=execution_context,
        )

    async def _compose_weather_answer(
        self,
        *,
        text: str,
        report: WeatherReport,
        used_recent_location: bool,
    ) -> str:
        fallback = fallback_weather_answer(report=report, used_recent_location=used_recent_location)
        try:
            answer = await self.openai.text_response(
                model=self.config.medium_model,
                instructions=(
                    "너는 SleepGPT의 Weather Agent다. 기상청 API 결과만 근거로 한국어로 짧고 자연스럽게 답한다. "
                    "없는 값을 추측하지 말고, 발표시각과 지역을 포함한다. "
                    "특보 구역 코드가 없으면 특보를 확인하지 못했다고 말한다."
                ),
                input_text=json.dumps(
                    {
                        "user_request": text,
                        "used_recent_location": used_recent_location,
                        "report": report_to_prompt(report),
                        "fallback_style_example": fallback,
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                temperature=0.2,
            )
            return answer or fallback
        except Exception:
            return fallback


def asks_weather(text: str) -> bool:
    normalized = text.casefold()
    compact = re.sub(r"\s+", "", normalized)
    markers = [
        "날씨",
        "예보",
        "비",
        "눈",
        "우산",
        "기온",
        "온도",
        "추워",
        "더워",
        "습도",
        "바람",
        "강수",
        "weather",
        "forecast",
    ]
    return any(marker in normalized or marker in compact for marker in markers)


def asks_alerts(text: str) -> bool:
    normalized = text.casefold()
    markers = ["특보", "경보", "주의보", "예비특보", "폭염", "한파", "호우", "대설", "태풍", "alerts", "warning"]
    return any(marker in normalized for marker in markers)


def asks_air_quality(text: str) -> bool:
    normalized = re.sub(r"\s+", "", text.casefold())
    markers = ["미세먼지", "초미세먼지", "대기질", "공기질", "pm10", "pm2.5", "airquality"]
    return any(marker in normalized for marker in markers)


def moment_to_item(moment) -> dict[str, object]:
    return {"date": moment.date, "time": moment.time, "values": dict(moment.values)}


def report_to_prompt(report: WeatherReport) -> dict[str, object]:
    return {
        "location": report.location.name,
        "base_date": report.base_date,
        "base_time": report.base_time,
        "moments": [moment_to_item(moment) for moment in report.moments[:12]],
        "situation": report.situation,
        "land_forecast": list(report.land_forecast),
    }


def fallback_weather_answer(*, report: WeatherReport, used_recent_location: bool) -> str:
    prefix = f"{report.location.name} 기준"
    if used_recent_location:
        prefix += "으로 볼게요"
    base = f"{format_date(report.base_date)} {format_time(report.base_time)} 발표"
    lines = [f"{prefix} 날씨예보입니다. ({base})"]
    for moment in report.moments[:5]:
        lines.append(f"- {format_date(moment.date)} {format_time(moment.time)}: {summarize_moment(moment.values)}")
    warning = report.situation.get("warning", "").strip()
    pre_warning = report.situation.get("pre_warning", "").strip()
    if warning:
        lines.append(f"- 특보: {warning}")
    elif not report.location.weather_stn_id:
        lines.append("- 특보: 이 지역의 특보 구역 코드가 아직 매핑되지 않아 단기예보만 확인했어요.")
    else:
        lines.append("- 특보: 현재 확인된 특보 문구가 없습니다.")
    if pre_warning:
        lines.append(f"- 예비특보: {pre_warning}")
    return "\n".join(lines)


def summarize_moment(values: dict[str, str]) -> str:
    parts: list[str] = []
    sky = decode_sky(values.get("SKY", ""))
    pty = decode_pty(values.get("PTY", ""))
    if sky:
        parts.append(sky)
    if pty and pty != "없음":
        parts.append(pty)
    if values.get("TMP"):
        parts.append(f"{values['TMP']}도")
    if values.get("TMN"):
        parts.append(f"최저 {values['TMN']}도")
    if values.get("TMX"):
        parts.append(f"최고 {values['TMX']}도")
    if values.get("POP"):
        parts.append(f"강수확률 {values['POP']}%")
    if values.get("PCP") and values["PCP"] != "강수없음":
        parts.append(f"강수량 {values['PCP']}")
    if values.get("REH"):
        parts.append(f"습도 {values['REH']}%")
    return ", ".join(parts) if parts else "제공된 주요 예보 값 없음"


def decode_sky(value: str) -> str:
    return {"1": "맑음", "2": "구름조금", "3": "구름많음", "4": "흐림"}.get(value, "")


def decode_pty(value: str) -> str:
    return {"0": "없음", "1": "비", "2": "비/눈", "3": "눈", "4": "소나기"}.get(value, "")


def format_date(value: str) -> str:
    if len(value) != 8:
        return value
    return f"{value[:4]}-{value[4:6]}-{value[6:8]}"


def format_time(value: str) -> str:
    if len(value) != 4:
        return value
    return f"{value[:2]}:{value[2:]}"
