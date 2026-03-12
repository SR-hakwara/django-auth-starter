import pytest
from django.core.cache import cache
from django.http import HttpRequest

from apps.core import utils


@pytest.mark.django_db
def test_record_failed_attempt_handles_incr_error(monkeypatch):
    # make cache.incr raise ValueError after initial add
    def fake_incr(key):
        raise ValueError("boom")

    monkeypatch.setattr(cache, "incr", fake_incr)
    request = HttpRequest()
    # first call creates the key
    utils.record_failed_attempt(request)
    # second call should hit except block and not raise
    utils.record_failed_attempt(request)


@pytest.mark.django_db
def test_get_rate_limit_key_unknown(monkeypatch):
    # simulate ipware returning (None, None)
    monkeypatch.setattr(utils, "get_client_ip", lambda req: (None, None))
    req = HttpRequest()
    key = utils.get_rate_limit_key(req, key_prefix="xyz")
    assert key.endswith("_unknown")
