import logging
import os
import random
import time
from contextlib import asynccontextmanager

import requests
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from opentelemetry import metrics, trace
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

SERVICE_NAME = os.getenv("OTEL_SERVICE_NAME", "orders-api")
OTEL_EXPORTER_OTLP_HTTP_BASE = os.getenv("OTEL_EXPORTER_OTLP_HTTP_BASE", "http://otel-collector:4318")
ENVIRONMENT = os.getenv("DEPLOY_ENV", "demo")
APP_BASE_URL = os.getenv("APP_BASE_URL", "http://127.0.0.1:8000")

def join(base: str, path: str) -> str:
    return base.rstrip("/") + path

TRACES_ENDPOINT = join(OTEL_EXPORTER_OTLP_HTTP_BASE, "/v1/traces")
METRICS_ENDPOINT = join(OTEL_EXPORTER_OTLP_HTTP_BASE, "/v1/metrics")
LOGS_ENDPOINT = join(OTEL_EXPORTER_OTLP_HTTP_BASE, "/v1/logs")

resource = Resource.create({
    "service.name": SERVICE_NAME,
    "service.version": "1.0.1",
    "deployment.environment": ENVIRONMENT,
})

tracer_provider = TracerProvider(resource=resource)
tracer_provider.add_span_processor(BatchSpanProcessor(
    OTLPSpanExporter(endpoint=TRACES_ENDPOINT),
    schedule_delay_millis=1000,
))
trace.set_tracer_provider(tracer_provider)
tracer = trace.get_tracer(__name__)

metric_reader = PeriodicExportingMetricReader(
    OTLPMetricExporter(endpoint=METRICS_ENDPOINT),
    export_interval_millis=2000,
)
meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
metrics.set_meter_provider(meter_provider)
meter = metrics.get_meter(__name__)

request_counter = meter.create_counter(name="demo_requests", description="Total demo requests")
order_counter = meter.create_counter(name="orders_created", description="Total created orders")
work_duration = meter.create_histogram(name="demo_work_duration", unit="ms", description="Duration spent in /work")
random_gauge = meter.create_up_down_counter(name="inventory_level_delta", description="Synthetic inventory delta")

logger_provider = LoggerProvider(resource=resource)
logger_provider.add_log_record_processor(BatchLogRecordProcessor(
    OTLPLogExporter(endpoint=LOGS_ENDPOINT),
    schedule_delay_millis=1000,
))
set_logger_provider(logger_provider)

LoggingInstrumentor().instrument(set_logging_format=True)
handler = LoggingHandler(level=logging.INFO, logger_provider=logger_provider)
stream_handler = logging.StreamHandler()
logging.basicConfig(level=logging.INFO, handlers=[handler, stream_handler], force=True)
logger = logging.getLogger("orders-api")

orders = []

def expensive_work(ms: int) -> dict:
    with tracer.start_as_current_span("expensive_work") as span:
        start = time.perf_counter()
        loop_count = max(5000, ms * 200)
        total = 0
        for i in range(loop_count):
            total += i * i
        elapsed_ms = (time.perf_counter() - start) * 1000
        span.set_attribute("app.loop_count", loop_count)
        span.set_attribute("app.elapsed_ms", round(elapsed_ms, 2))
        return {"loop_count": loop_count, "elapsed_ms": round(elapsed_ms, 2), "checksum": total % 9973}

@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("application startup complete")
    yield
    logger.info("application shutdown complete")
    logger_provider.force_flush()
    meter_provider.force_flush()
    tracer_provider.force_flush()
    logger_provider.shutdown()
    meter_provider.shutdown()
    tracer_provider.shutdown()

app = FastAPI(title="OpenTelemetry Full Demo", version="1.0.1", lifespan=lifespan)
FastAPIInstrumentor.instrument_app(app)
RequestsInstrumentor().instrument()

@app.get("/")
def root():
    request_counter.add(1, {"route": "/"})
    logger.info("root endpoint hit")
    return {"message": "OpenTelemetry demo is running", "service": SERVICE_NAME, "signals": ["logs", "metrics", "traces"]}

@app.get("/health")
def health():
    request_counter.add(1, {"route": "/health"})
    return {"status": "ok"}

@app.get("/work")
def work(delay_ms: int = 120, fanout_calls: int = 1):
    request_counter.add(1, {"route": "/work"})
    started = time.perf_counter()
    with tracer.start_as_current_span("work_handler") as span:
        span.set_attribute("app.delay_ms", delay_ms)
        span.set_attribute("app.fanout_calls", fanout_calls)
        logger.info("starting work", extra={"delay_ms": delay_ms, "fanout_calls": fanout_calls})
        details = expensive_work(delay_ms)
        downstream = []
        for _ in range(fanout_calls):
            response = requests.get(f"{APP_BASE_URL}/health", timeout=5)
            downstream.append(response.status_code)
        elapsed_ms = (time.perf_counter() - started) * 1000
        work_duration.record(elapsed_ms, {"route": "/work"})
        random_gauge.add(random.randint(-2, 4), {"warehouse": "guntur-demo"})
        logger.info("completed work", extra={"elapsed_ms": round(elapsed_ms, 2), "downstream_statuses": ",".join(str(v) for v in downstream)})
        return {"ok": True, "elapsed_ms": round(elapsed_ms, 2), "details": details, "downstream_statuses": downstream}

@app.post("/orders/{item}")
def create_order(item: str, quantity: int = 1):
    request_counter.add(1, {"route": "/orders/{item}"})
    with tracer.start_as_current_span("create_order") as span:
        order_id = len(orders) + 1
        order = {"id": order_id, "item": item, "quantity": quantity}
        orders.append(order)
        order_counter.add(quantity, {"item": item})
        span.set_attribute("order.id", order_id)
        span.set_attribute("order.item", item)
        span.set_attribute("order.quantity", quantity)
        logger.info("order created", extra=order)
        return JSONResponse(order, status_code=201)

@app.get("/orders")
def list_orders():
    request_counter.add(1, {"route": "/orders"})
    logger.info("listing orders", extra={"count": len(orders)})
    return {"orders": orders, "count": len(orders)}

@app.get("/error")
def trigger_error():
    request_counter.add(1, {"route": "/error"})
    logger.error("error endpoint invoked deliberately")
    raise HTTPException(status_code=500, detail="intentional demo error")

@app.get("/burst")
def burst(n: int = 20):
    request_counter.add(1, {"route": "/burst"})
    results = []
    for i in range(n):
        payload = expensive_work(20 + (i % 5) * 10)
        work_duration.record(payload["elapsed_ms"], {"route": "/burst"})
        logger.info("burst item processed", extra={"item_index": i, "elapsed_ms": payload["elapsed_ms"]})
        results.append(payload)
    return {"processed": n}
