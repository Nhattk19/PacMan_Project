
            ghost_pos = (ghost.center_x // 30, ghost.center_y // 30)
            if ghost_pos in graph:
                # Đánh dấu ô này là không thể đi qua (giống như tường)