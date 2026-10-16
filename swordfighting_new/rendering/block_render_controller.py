from __future__ import annotations


class BlockRenderController:
    def __init__(self, *, pygame):
        self._pygame = pygame

    def draw_block(
        self,
        client,
        rect,
        block,
        *,
        color_map: dict,
        sprinkle_color: tuple[int, int, int],
        cgarbage_color: tuple[int, int, int],
        garbage_color: tuple[int, int, int],
        default_block_color: tuple[int, int, int],
    ) -> None:
        state = getattr(block, 'attack_state', None)
        is_strike = bool(state == 'strike' or (state is None and getattr(block, 'is_strike', False)))

        if is_strike:
            try:
                base = rect.inflate(-2, -2)
                img = client._get_strike_solid_scaled((int(base.w), int(base.h)))
                if img is not None:
                    client.screen.blit(img, (int(base.x), int(base.y)))
                    return
            except Exception:
                pass
            # If solid.png is missing, fall back to drawing nothing for strike blocks.
            return

        # Attempt image-based rendering first, prioritizing garbage/sprinkle over color
        img_drawn = False

        # 1) Attack-state visuals: sprinkle/cgarbage first
        if state == 'sprinkle':
            # Use the generic sprinkle/garbage block art regardless of color
            surf = client.garbage_images.get('generic') if hasattr(client, 'garbage_images') else None
            if surf is not None:
                base = rect.inflate(-2, -2)
                dx = (base.width - surf.get_width()) // 2
                dy = (base.height - surf.get_height()) // 2
                client.screen.blit(surf, (base.x + dx, base.y + dy))
                img_drawn = True
        elif state == 'cgarbage' or (state is None and hasattr(block, 'is_garbage') and getattr(block, 'is_garbage', False)):
            color_key = getattr(block, 'color', None)
            surf = None
            if hasattr(client, 'garbage_images'):
                # Prefer color-specific image for cgarbage; fall back to generic
                if isinstance(color_key, str):
                    surf = client.garbage_images.get(color_key)
                if surf is None:
                    surf = client.garbage_images.get('generic')
            if surf is not None:
                base = rect.inflate(-2, -2)
                dx = (base.width - surf.get_width()) // 2
                dy = (base.height - surf.get_height()) // 2
                client.screen.blit(surf, (base.x + dx, base.y + dy))
                img_drawn = True

        # 2) Breakers and normal colored blocks
        if not img_drawn and hasattr(block, 'color'):
            color_key = getattr(block, 'color', None)
            is_breaker = bool(getattr(block, 'is_breaker', False))
            if isinstance(color_key, str):
                if is_breaker:
                    surf = client.breaker_images.get(color_key) if hasattr(client, 'breaker_images') else None
                else:
                    surf = client.block_images.get(color_key) if hasattr(client, 'block_images') else None
                if surf is not None:
                    base = rect.inflate(-2, -2)
                    dx = (base.width - surf.get_width()) // 2
                    dy = (base.height - surf.get_height()) // 2
                    client.screen.blit(surf, (base.x + dx, base.y + dy))
                    img_drawn = True

        if not img_drawn:
            if state == 'sprinkle':
                color = sprinkle_color
            elif state == 'cgarbage':
                color = cgarbage_color
            elif hasattr(block, 'is_garbage') and block.is_garbage:
                color = garbage_color
            elif hasattr(block, 'color'):
                color = color_map.get(block.color, default_block_color)
            else:
                color = default_block_color

            base = rect.inflate(-2, -2)
            self._pygame.draw.rect(client.screen, color, base, border_radius=5)
            if hasattr(block, 'is_breaker') and block.is_breaker:
                self.draw_breaker_effects(client, base, color)
            # Strike visuals are handled above for strike blocks.

    def draw_breaker_effects(self, client, base_rect, base_color) -> None:
        r, g, b = base_color
        outline = (min(255, r + 60), min(255, g + 60), min(255, b + 60))
        self._pygame.draw.rect(client.screen, outline, base_rect, 2, border_radius=6)
        inner = base_rect.inflate(-6, -6)
        self._pygame.draw.rect(
            client.screen,
            (max(0, r - 30), max(0, g - 30), max(0, b - 30)),
            inner,
            border_radius=4,
        )
        core = base_rect.inflate(-14, -14)
        self._pygame.draw.rect(client.screen, outline, core, border_radius=3)
