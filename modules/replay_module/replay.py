from typing import Dict, List, Any


class InputReplayer:
    def __init__(self, session: Dict[str, Any], clock):
        # Defensive copy
        self.session = {
            'seed': int(session.get('seed', 0)),
            'settings': dict(session.get('settings', {})),
            'events': list(session.get('events', [])),
        }
        self.clock = clock
        # Maintain an index of next event
        self._idx = 0
        # Ensure events sorted by time
        self.session['events'].sort(key=lambda e: int(e.get('t_ms', 0)))

    def step(self, now_ms: int) -> List[Dict[str, Any]]:
        due: List[Dict[str, Any]] = []
        events = self.session['events']
        n = len(events)
        while self._idx < n and int(events[self._idx].get('t_ms', 0)) <= int(now_ms):
            ev = events[self._idx]
            due.append({'intent': ev.get('intent'), 'data': dict(ev.get('data') or {})})
            self._idx += 1
        return due

