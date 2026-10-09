"""Redis-backed circuit breaker for the optional recommendation service."""

import logging
import os
from dataclasses import dataclass

from prometheus_client import Counter
from redis import Redis
from redis.exceptions import RedisError


logger = logging.getLogger(__name__)

recommendation_load_shedding_operations = Counter(
    "recommendation_load_shedding_operations_total",
    "Recommendation admission decisions before calling the model service.",
    ("result",),
)


def _positive_int_env(name: str, default: int) -> int:
    raw_value = os.getenv(name, str(default))
    try:
        value = int(raw_value)
    except ValueError as exc:
        raise RuntimeError(f"{name} must be an integer") from exc
    if value < 1:
        raise RuntimeError(f"{name} must be greater than zero")
    return value


def _bool_env(name: str, default: bool) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class RecommendationAdmission:
    """Describe whether a request may call the recommendation service."""

    allowed: bool
    retry_after: int
    source: str


class RecommendationLoadShedder:
    """Open a shared circuit when aggregate recommendation traffic is too high."""

    _script = """
local circuit_ttl = redis.call('TTL', KEYS[2])
if circuit_ttl > 0 then
  return {0, circuit_ttl, 'circuit_open'}
end
if circuit_ttl == -1 then
  redis.call('EXPIRE', KEYS[2], ARGV[3])
  return {0, ARGV[3], 'circuit_open'}
end

local current = redis.call('INCR', KEYS[1])
if current == 1 then
  redis.call('EXPIRE', KEYS[1], ARGV[2])
end
if current > tonumber(ARGV[1]) then
  redis.call('SET', KEYS[2], 'open', 'EX', ARGV[3])
  return {0, ARGV[3], 'circuit_opened'}
end
return {1, 0, 'allowed'}
"""

    _window_key = "philobiblus:recommendation-load-shedder:window"
    _circuit_key = "philobiblus:recommendation-load-shedder:circuit"

    def __init__(self) -> None:
        self.enabled = _bool_env("RECOMMENDATION_LOAD_SHEDDING_ENABLED", True)
        self.max_requests = _positive_int_env(
            "RECOMMENDATION_LOAD_SHEDDING_MAX_REQUESTS",
            12,
        )
        self.window_seconds = _positive_int_env(
            "RECOMMENDATION_LOAD_SHEDDING_WINDOW_SECONDS",
            10,
        )
        self.cooldown_seconds = _positive_int_env(
            "RECOMMENDATION_LOAD_SHEDDING_COOLDOWN_SECONDS",
            30,
        )
        self.client: Redis | None = None
        redis_url = os.getenv("REDIS_URL", "").strip()
        if self.enabled and redis_url:
            self.client = Redis.from_url(
                redis_url,
                decode_responses=True,
                socket_connect_timeout=1,
                socket_timeout=1,
                health_check_interval=30,
            )

    def admit(self) -> RecommendationAdmission:
        """Allow traffic until the shared threshold opens the circuit."""
        if not self.enabled:
            recommendation_load_shedding_operations.labels("disabled").inc()
            return RecommendationAdmission(True, 0, "disabled")

        if self.client is None:
            recommendation_load_shedding_operations.labels("redis_unavailable").inc()
            return RecommendationAdmission(True, 0, "redis_unavailable")

        try:
            result = self.client.eval(
                self._script,
                2,
                self._window_key,
                self._circuit_key,
                self.max_requests,
                self.window_seconds,
                self.cooldown_seconds,
            )
            allowed = int(result[0]) == 1
            retry_after = max(0, int(result[1]))
            source = str(result[2])
        except (IndexError, RedisError, TypeError, ValueError) as exc:
            logger.warning("Recommendation load shedder Redis operation failed: %s", exc)
            recommendation_load_shedding_operations.labels("redis_error").inc()
            return RecommendationAdmission(True, 0, "redis_error")

        recommendation_load_shedding_operations.labels(source).inc()
        return RecommendationAdmission(allowed, retry_after, source)


recommendation_load_shedder = RecommendationLoadShedder()
