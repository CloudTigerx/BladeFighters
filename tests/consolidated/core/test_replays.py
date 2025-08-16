import glob
import os

from tests.reactor_blackbox.harness import load_fixture, run_fixture


FIXTURES_DIR = os.path.join(os.path.dirname(__file__), 'fixtures')


def _fixture_paths():
    return sorted(glob.glob(os.path.join(FIXTURES_DIR, '*.yaml')))


def test_replay_fixtures():
    for path in _fixture_paths():
        fixture = load_fixture(path)
        result = run_fixture(fixture)
        expect = fixture.get('expect', {})

        assert result['final_checksum'] == expect['final_checksum'], f"Checksum mismatch for {os.path.basename(path)}"
        assert result['payloads'] == expect['payloads'], f"Payloads mismatch for {os.path.basename(path)}"

