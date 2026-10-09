from app.recommendation_load_shedder import RecommendationLoadShedder


class FakeRedis:
    def __init__(self):
        self.request_count = 0
        self.circuit_ttl = 0

    def eval(self, script, key_count, window_key, circuit_key, limit, window_seconds, cooldown):
        if self.circuit_ttl > 0:
            return [0, self.circuit_ttl, "circuit_open"]

        self.request_count += 1
        if self.request_count > int(limit):
            self.circuit_ttl = int(cooldown)
            return [0, self.circuit_ttl, "circuit_opened"]
        return [1, 0, "allowed"]


def test_load_shedder_opens_a_shared_circuit_after_high_request_volume(monkeypatch):
    monkeypatch.setenv("RECOMMENDATION_LOAD_SHEDDING_ENABLED", "true")
    monkeypatch.setenv("RECOMMENDATION_LOAD_SHEDDING_MAX_REQUESTS", "2")
    monkeypatch.setenv("RECOMMENDATION_LOAD_SHEDDING_WINDOW_SECONDS", "10")
    monkeypatch.setenv("RECOMMENDATION_LOAD_SHEDDING_COOLDOWN_SECONDS", "30")

    shedder = RecommendationLoadShedder()
    shedder.client = FakeRedis()

    decisions = [shedder.admit() for _ in range(4)]

    assert [decision.allowed for decision in decisions] == [True, True, False, False]
    assert [decision.source for decision in decisions] == [
        "allowed",
        "allowed",
        "circuit_opened",
        "circuit_open",
    ]
    assert decisions[-1].retry_after == 30


def test_load_shedder_fails_open_when_redis_is_not_configured(monkeypatch):
    monkeypatch.setenv("RECOMMENDATION_LOAD_SHEDDING_ENABLED", "true")
    monkeypatch.delenv("REDIS_URL", raising=False)

    decision = RecommendationLoadShedder().admit()

    assert decision.allowed is True
    assert decision.source == "redis_unavailable"
