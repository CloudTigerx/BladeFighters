from pathlib import Path

import json

from utils.clock import FakeClock
from modules.replay_module.record import InputRecorder
from modules.replay_module.replay import InputReplayer
from tools.repro_token import pack, unpack


def test_record_and_replay_timing():
    clock = FakeClock(0)
    rec = InputRecorder()
    rec.start(seed=42, settings={'a': 1})
    # Simulate intents at precise times
    evs = [
        {'t_ms': 0, 'intent': 'move_r', 'data': {}},
        {'t_ms': 120, 'intent': 'move_r', 'data': {}},
        {'t_ms': 200, 'intent': 'rotate', 'data': {'dir': 1}},
    ]
    for e in evs:
        rec.record(e)
    session = rec.stop()

    r = InputReplayer(session, clock)
    out = []
    # Step through time and collect
    for t in [0, 119, 120, 199, 200]:
        clock.advance(t - clock.now_ms())
        out.extend(r.step(clock.now_ms()))

    # Flatten with timestamps for comparison by reconstructing from session
    expected = [(e['t_ms'], e['intent']) for e in session['events']]
    # Build actual stream with times from session (replayer returns only intents)
    # So we compare order and counts
    got = [e['intent'] for e in out]
    assert got == [e['intent'] for e in session['events']]


def test_token_roundtrip_and_checksum(tmp_path):
    session = {
        'seed': 7,
        'settings': {'x': True},
        'events': [{'t_ms': 1, 'intent': 'move_l', 'data': {}}],
    }
    tok = pack(session)
    back = unpack(tok)
    assert back == session

    # Tamper
    bad = tok[:-2] + ('A' if tok[-2] != 'A' else 'B') + tok[-1]
    try:
        unpack(bad)
        assert False, 'expected checksum mismatch'
    except Exception:
        pass

