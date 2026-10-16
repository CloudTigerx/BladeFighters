import random

from swordfighting_new.attacks.attack_lifecycle import InboundAttackLifecycle
from swordfighting_new.pieces.piece import Piece


class DummyBlock:
    def __init__(self):
        self.attack_state = None
        self.is_strike = False
        self.is_garbage = False
        self.color = None
        # Provide inbound metadata but omit x/y so the lifecycle must use fallback.
        self.inbound_kind = 'sprinkle'
        self.inbound_turn_id = 7
        self.inbound_layer = 2
        self.strike_cluster_id = 99


def test_lifecycle_fallback_color_does_not_depend_on_global_rng_state():
    lc = InboundAttackLifecycle(seed=123)

    random.seed(1)
    b1 = DummyBlock()
    lc._finalise(b1)
    c1 = b1.color

    random.seed(999)
    b2 = DummyBlock()
    lc._finalise(b2)
    c2 = b2.color

    assert c1 == c2
    assert c1 in Piece.COLORS
