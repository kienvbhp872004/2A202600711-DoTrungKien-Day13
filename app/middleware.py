from __future__ import annotations

import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from structlog.contextvars import bind_contextvars, clear_contextvars


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Xóa context của request cũ, tránh data bị "rò rỉ" sang request tiếp theo
        clear_contextvars()

        # Lấy x-request-id từ header client gửi lên; nếu không có thì tự sinh mới
        # format: req-<8 ký tự hex ngẫu nhiên>, ví dụ: req-a3f9c12b
        correlation_id = request.headers.get("x-request-id") or f"req-{uuid.uuid4().hex[:8]}"

        # Gắn correlation_id vào structlog context — tất cả log.info/log.error
        # trong vòng đời request này sẽ tự động đính kèm trường này
        bind_contextvars(correlation_id=correlation_id)

        # Lưu vào request.state để các handler (ví dụ /chat) đọc được
        request.state.correlation_id = correlation_id

        start = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)

        # Trả correlation_id và thời gian xử lý về cho client qua response headers
        response.headers["x-request-id"] = correlation_id
        response.headers["x-response-time-ms"] = str(elapsed_ms)

        return response
