from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
from fastapi import FastAPI
import time


# 메트릭 정의
REQUEST_COUNT = Counter(
    "api_requests_total",
    "Total API requests",
    ["method", "endpoint", "http_status"]
)

REQUEST_LATENCY = Histogram(
    "api_request_latency_seconds",
    "API request latency in seconds",
    ["endpoint"]
)

def register_metrics(app: FastAPI):
    @app.middleware("http")
    async def prometheus_middleware(request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time

        # 엔드포인트 이름 (예: /api/v1/users)
        endpoint = request.url.path
        method = request.method
        status_code = response.status_code

        # 카운터 증가
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, http_status=status_code).inc()
        # 응답 시간 기록
        REQUEST_LATENCY.labels(endpoint=endpoint).observe(process_time)

        return response

    # metrics endpoint 등록
    @app.get("/metrics")
    async def metrics():
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
