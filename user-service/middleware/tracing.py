"""
OpenTelemetry tracing configuration for User Service
"""
import logging
import os

# Only try to import tracing modules if they're available
try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    from opentelemetry.sdk.resources import Resource, SERVICE_NAME
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
    from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
    import structlog
    TRACING_AVAILABLE = True
except ImportError:
    TRACING_AVAILABLE = False

# Disable verbose logging from OpenTelemetry
logging.getLogger("opentelemetry").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


def init_tracing(app):
    """Initialize OpenTelemetry tracing with Jaeger exporter"""
    if not TRACING_AVAILABLE:
        logger.warning("OpenTelemetry modules not available. Tracing disabled.")
        return False
    
    try:
        # Get settings from environment
        service_name = os.getenv("SERVICE_NAME", "user-service")
        jaeger_endpoint = os.getenv("JAEGER_ENDPOINT", "http://jaeger-demo:14268/api/traces")
        tracing_enabled = os.getenv("TRACING_ENABLED", "false").lower() == "true"
        
        if not tracing_enabled:
            logger.info("Tracing disabled by configuration")
            return False
        
        # Create resource with service name
        resource = Resource(attributes={
            SERVICE_NAME: service_name,
            "service.version": "1.0.0",
            "environment": os.getenv("ENVIRONMENT", "development")
        })
        
        # Create tracer provider
        provider = TracerProvider(resource=resource)
        
        # Configure Jaeger exporter
        jaeger_exporter = JaegerExporter(
            collector_endpoint=jaeger_endpoint,
        )
        
        # Add span processor with batching
        provider.add_span_processor(
            BatchSpanProcessor(
                jaeger_exporter,
                max_queue_size=2048,
                max_export_batch_size=512,
                schedule_delay_millis=5000
            )
        )
        
        # Set global tracer provider
        trace.set_tracer_provider(provider)
        
        # Instrument FastAPI - exclude health and metrics endpoints
        FastAPIInstrumentor.instrument_app(
            app,
            excluded_urls="/health,/metrics"
        )
        
        # Instrument SQLAlchemy for database tracing
        try:
            SQLAlchemyInstrumentor().instrument()
            logger.debug("SQLAlchemy instrumentation enabled")
        except Exception as e:
            logger.warning(f"Could not instrument SQLAlchemy: {e}")
        
        # Instrument HTTPX client for outbound HTTP calls
        try:
            HTTPXClientInstrumentor().instrument()
            logger.debug("HTTPX instrumentation enabled")
        except Exception as e:
            logger.warning(f"Could not instrument HTTPX: {e}")
        
        logger.info(
            f"OpenTelemetry tracing initialized successfully - Service: {service_name}, Endpoint: {jaeger_endpoint}"
        )
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize tracing: {e}", exc_info=True)
        # Don't fail startup if tracing fails
        return False


def get_tracer(name: str = __name__):
    """Get a tracer instance for manual span creation"""
    if TRACING_AVAILABLE and trace.get_tracer_provider():
        return trace.get_tracer(name)
    else:
        return None