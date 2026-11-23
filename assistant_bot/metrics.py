"""Account for model requests without retaining prompts, responses or credentials."""

import asyncio
import logging
import sqlite3
import time
from contextlib import contextmanager
from contextvars import ContextVar
from functools import wraps

request_id = ContextVar("model_request_id", default=None)
_trace = ContextVar("model_trace", default=None)


@contextmanager
def request_context(key):
    token = request_id.set(key)
    try:
        yield
    finally:
        request_id.reset(token)


class Attempt:
    def __init__(self, db, job, model, purpose, retry):
        self.db = db
        self.job = job
        self.model = model
        self.started = time.monotonic()
        self.usage = {}
        self.done = False
        self.id = None
        try:
            with db:
                self.id = db.execute(
                    "INSERT INTO model_calls(job,model,purpose,retry,started,status) VALUES(?,?,?,?,?,'open')",
                    (job, model, purpose, retry, time.time()),
                ).lastrowid
        except sqlite3.Error:
            logging.getLogger(__name__).exception("모델 호출 통계 시작 기록 실패")

    def finish(self, status):
        if self.done or self.id is None:
            return
        self.done = True
        try:
            with self.db:
                self.db.execute(
                    "UPDATE model_calls SET seconds=?,status=?,input_tokens=?,output_tokens=? WHERE id=?",
                    (
                        time.monotonic() - self.started,
                        status,
                        self.usage.get("input_tokens"),
                        self.usage.get("output_tokens"),
                        self.id,
                    ),
                )
        except sqlite3.Error:
            logging.getLogger(__name__).exception("모델 호출 통계 저장 실패")


def observed(default_purpose):
    def decorate(method):
        @wraps(method)
        async def wrapped(self, model, *args, **kwargs):
            purpose = kwargs.pop("purpose", default_purpose)
            retry = kwargs.pop("retry", False)
            job = kwargs.pop("request_id", request_id.get())
            db = getattr(self, "metrics_db", None)
            if db is None:
                return await method(self, model, *args, **kwargs)
            attempts = [Attempt(db, job, model, purpose, retry)]
            token = _trace.set(attempts)
            status = "failed"
            try:
                result = await method(self, model, *args, **kwargs)
                status = "ok"
                return result
            except asyncio.CancelledError:
                status = "cancelled"
                raise
            finally:
                for attempt in attempts:
                    attempt.finish(status)
                _trace.reset(token)

        return wrapped

    return decorate


def current_attempt():
    trace = _trace.get()
    return trace[-1] if trace else None


def steer_attempt():
    if trace := _trace.get():
        initial = trace[0]
        trace.append(Attempt(initial.db, initial.job, initial.model, "답변 정정", False))
        return trace[-1]


def record_usage(usage):
    if (attempt := current_attempt()) and usage:
        attempt.usage = usage
