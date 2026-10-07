"""Offline smoke tests — no server, network, or API key needed.

Run:  python -m tests.smoke_test      (or: pytest tests)
"""
import io
import json
import os
from unittest import mock

from backend import engine, llm, simulator
from backend.seed import ASSETS, EVENTS


def test_shock_scores_match_events():
    shocks = engine.get_dashboard()["shocks"]
    assert shocks["BTC"]["z_score"] == -3.7 and shocks["BTC"]["level"] == "Sentiment shock"
    assert shocks["DOGE"]["z_score"] == 3.2
    assert shocks["AAPL"]["level"] == "Normal"


def test_chat_covers_every_asset():
    for a in ASSETS:
        r = engine.answer_question(f"What is happening with {a.name}?")
        assert a.symbol in r.answer and r.mode == "rules"


def test_simulator_cycle_and_reset():
    base = len(EVENTS)
    first = simulator.inject_next()
    second = simulator.inject_next()
    assert first.simulated and second.simulated and len(EVENTS) == base + 2
    assert engine.get_dashboard()["events"][0].id == first.id  # highest impact floats to the top
    simulator.inject_next()  # cycles back; must replace, not duplicate
    assert len(EVENTS) == base + 2
    simulator.reset()
    assert len(EVENTS) == base and not any(e.simulated for e in EVENTS)


def _fake_response(text):
    body = json.dumps({"content": [{"type": "text", "text": text}]}).encode()
    resp = mock.MagicMock()
    resp.__enter__.return_value = io.BytesIO(body)
    return resp


def test_llm_path_filters_citations_and_falls_back():
    os.environ["ANTHROPIC_API_KEY"] = "test-key"
    try:
        good = json.dumps({"answer": "BTC fell on a verified regulatory bulletin.", "citations": ["evt-btc-reg-1042", "made-up-id"], "suggested_questions": ["a?", "b?", "c?"]})
        with mock.patch("urllib.request.urlopen", return_value=_fake_response(good)):
            r = engine.answer_question("Why is BTC falling?")
        assert r.mode == "llm" and r.citations == ["evt-btc-reg-1042"]
        with mock.patch("urllib.request.urlopen", side_effect=OSError("offline")):
            r = engine.answer_question("Why is BTC falling?")
        assert r.mode == "rules"
        with mock.patch("urllib.request.urlopen", return_value=_fake_response("not json")):
            assert engine.answer_question("Why is BTC falling?").mode == "rules"
    finally:
        del os.environ["ANTHROPIC_API_KEY"]
    assert not llm.enabled()


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok ", name)
    print("all passed")
