import os
import logging
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

logger = logging.getLogger(__name__)

OTEL_EXPORTER_OTLP_ENDPOINT = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "")
OTEL_SERVICE_NAME = os.getenv("OTEL_SERVICE_NAME", "qrcode-generator-service")


def init_tracer(app=None):
    """
    Initializes OpenTelemetry Tracer Provider and instruments libraries.
    """
    try:
        # Create a resource describing the service
        resource = Resource.create(
            attributes={
                "service.name": OTEL_SERVICE_NAME,
                "compose_service": "qrcode-app",
            }
        )

        provider = TracerProvider(resource=resource)

        # Configure gRPC/OTLP exporter to send spans to Jaeger/Collector
        # If OTEL_EXPORTER_OTLP_ENDPOINT is empty, tracing is disabled/mocked
        if OTEL_EXPORTER_OTLP_ENDPOINT:
            logger.info(
                f"Configuring OpenTelemetry to export to {OTEL_EXPORTER_OTLP_ENDPOINT}"
            )
            otlp_exporter = OTLPSpanExporter(
                endpoint=OTEL_EXPORTER_OTLP_ENDPOINT, insecure=True
            )
            span_processor = BatchSpanProcessor(otlp_exporter)
            provider.add_span_processor(span_processor)

        trace.set_tracer_provider(provider)

        # Instrument FastAPI
        if app:
            from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

            FastAPIInstrumentor.instrument_app(app)
            logger.info("FastAPI auto-instrumented.")

        # Instrument SQLAlchemy
        try:
            from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
            from src.database import engine

            SQLAlchemyInstrumentor().instrument(engine=engine)
            logger.info("SQLAlchemy auto-instrumented.")
        except Exception as e:
            logger.warning(f"Failed to instrument SQLAlchemy: {e}")

        # Instrument botocore (instruments boto3 / S3)
        try:
            from opentelemetry.instrumentation.botocore import BotocoreInstrumentor

            BotocoreInstrumentor().instrument()
            logger.info("Botocore (Boto3) auto-instrumented.")
        except Exception as e:
            logger.warning(f"Failed to instrument Botocore: {e}")

    except Exception as e:
        logger.error(f"Failed to initialize OpenTelemetry: {e}")
