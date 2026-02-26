from fastapi import Request
from datetime import datetime
from typing import Callable
from fastapi.responses import Response


async def request_timer_middleware(request: Request, call_next: Callable) -> Response:
    """
    请求计时中间件，在响应头中添加请求时间
    """
    start_time = datetime.now()
    response = await call_next(request)
    end_time = datetime.now()

    # 计算请求处理时间（毫秒）
    process_time = (end_time - start_time).total_seconds() * 1000

    # 在响应头中添加请求时间信息
    response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
    response.headers["X-Request-Time"] = start_time.strftime("%Y-%m-%d %H:%M:%S")

    return response
