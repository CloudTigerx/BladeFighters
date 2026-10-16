from swordfighting_new.fighters.base_fighter import BaseFighter
from swordfighting_new.mechanics.timing import TimingConfig
from swordfighting_new.pieces.piece import Block
from swordfighting_new.attacks.garbage_pattern import get_pattern_color


def test_post_chain_applies_transform_then_break_then_defeat_guardrail():
    """Regression: don't top-out before a pending transform can save you.

    Scenario:
    - The configured game-over column is completely full (would normally defeat).
    - A breaker at the top of that column is *not* currently triggered because its
      matching neighbor is an inbound lifecycle block in 'cgarbage' (immune).
    - On the next turn boundary (between pieces), that cgarbage finalizes to a
      normal block, triggering the breaker and opening space.

    Expected order: transform -> break -> defeat check.
    """

    timing = TimingConfig(chain_frame_delay=0)
    fighter = BaseFighter(timing=timing, spawn_x=3)
    board = fighter.board

    game_over_x = int(getattr(fighter.movement, "game_over_x", 0) or 0)
    assert 0 <= game_over_x < board.WIDTH

    # Fill the game-over column completely.
    for y in range(board.HEIGHT):
        board.set_piece(game_over_x, y, Block("blue", is_breaker=False))

    # Place a breaker at the top cell of the game-over column.
    # Its matching neighbor will finalize to this exact color.
    nx = game_over_x + 1
    assert nx < board.WIDTH
    expected = get_pattern_color(nx, 0)
    assert expected is not None and str(expected) != ""
    board.set_piece(game_over_x, 0, Block(expected, is_breaker=True))

    # Neighbor starts as inbound lifecycle cgarbage (immune), so breaker isn't triggered yet.
    cgb = Block("red", is_breaker=False, is_garbage=True, is_strike=False, attack_state="cgarbage")
    setattr(cgb, "x", nx)
    setattr(cgb, "y", 0)
    setattr(cgb, "inbound_kind", "sprinkle")
    board.set_piece(nx, 0, cgb)

    # Precondition: game-over column is full.
    assert all(board.get_piece(game_over_x, y) != board.EMPTY for y in range(board.HEIGHT))

    # Enter between-pieces phase with no inbound pending.
    fighter._waiting_to_spawn_post_chain = True
    fighter._post_chain_lifecycle_applied = False
    fighter.movement.current_piece = None
    fighter.inbound_handler.pending_in_sprinkle = 0
    fighter.inbound_handler.pending_in_strike = 0
    fighter.inbound_handler.spawn_queue = 0
    fighter.inbound_handler.garbage_fallers = []
    fighter.inbound_handler._delayed_clusters = []

    # Ensure the lifecycle block is applied at the boundary.
    fighter.inbound_handler._new_attack_blocks = [cgb]

    # Run the simulation for a few frames:
    # 1) apply lifecycle (cgarbage->normal), start breaker chain
    # 2+) resolve chain, then defeat checks/spawn
    for _ in range(80):
        fighter.update({})
        if fighter.defeated:
            break
        if not fighter._waiting_to_spawn_post_chain and fighter.movement.current_piece is not None:
            break

    assert fighter.defeated is False
    # The breaker should have cleared, opening the top cell of the game-over column.
    assert board.get_piece(game_over_x, 0) == board.EMPTY
