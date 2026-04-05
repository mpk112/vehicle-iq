"""Circuit breaker pattern for external service calls."""

import time
from typing import Callable, Any, Optional
from enum import Enum
import structlog

logger = structlog.get_logger()


class CircuitState(str, Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """Circuit breaker for external service calls."""

    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: int = 60,
        name: str = "default",
    ):
        """
        Initialize circuit breaker.

        Args:
            failure_threshold: Number of failures before opening circuit
            timeout: Seconds to wait before attempting recovery
            name: Name of the circuit breaker for logging
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.name = name
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = CircuitState.CLOSED

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection.

        Args:
            func: Function to execute
            *args: Positional arguments for function
            **kwargs: Keyword arguments for function

        Returns:
            Function result

        Raises:
            Exception: If circuit is open or function fails
        """
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                logger.info(
                    "circuit_breaker_half_open",
                    name=self.name,
                    failure_count=self.failure_count,
                )
            else:
                logger.warning(
                    "circuit_breaker_open",
                    name=self.name,
                    failure_count=self.failure_count,
                )
                raise Exception(f"Circuit breaker '{self.name}' is OPEN")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self.last_failure_time is None:
            return True
        return time.time() - self.last_failure_time >= self.timeout

    def _on_success(self):
        """Handle successful call."""
        if self.state == CircuitState.HALF_OPEN:
            logger.info(
                "circuit_breaker_closed",
                name=self.name,
                previous_failures=self.failure_count,
            )
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def _on_failure(self):
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.error(
                "circuit_breaker_opened",
                name=self.name,
                failure_count=self.failure_count,
                threshold=self.failure_threshold,
            )


# Global circuit breakers for external services
groq_circuit_breaker = CircuitBreaker(failure_threshold=5, timeout=60, name="groq")
together_circuit_breaker = CircuitBreaker(failure_threshold=5, timeout=60, name="together")
paddleocr_circuit_breaker = CircuitBreaker(failure_threshold=5, timeout=30, name="paddleocr")
yolo_circuit_breaker = CircuitBreaker(failure_threshold=5, timeout=30, name="yolo")
embeddings_circuit_breaker = CircuitBreaker(failure_threshold=5, timeout=30, name="embeddings")
