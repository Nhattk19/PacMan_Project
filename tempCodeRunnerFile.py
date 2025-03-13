    def move_pinkGhost(self):
        global player_x, player_y, pinkGhost_index, pinkGhost_path, current_level, pink_path

        # Xây dựng đồ thị từ bản đồ
        graph = build_graph(level)

        # Lấy vị trí hiện tại của Pink Ghost và Pac-Man (tọa độ ô lưới)
        current_pos = (self.center_x // 30, self.center_y // 30)
        target_pos = (round(player_x / 30), round(player_y / 30))

        # Lấy nút bắt đầu và nút mục tiêu từ đồ thị
        start_node = graph.get(current_pos)
        target_node = graph.get(target_pos)

        # Kiểm tra xem nút bắt đầu và nút mục tiêu có tồn tại không
        if not start_node or not target_node:
            print("Không tìm thấy nút bắt đầu hoặc nút mục tiêu!")
            return self.x_pos, self.y_pos, self.direction

        # Nếu pink_path rỗng, tính toán lại đường đi
        if not pink_path:
            pink_path = dfs(start_node, target_node)
            if not pink_path:
                print("Không tìm thấy đường đi!")
                return self.x_pos, self.y_pos, self.direction
            print("Cập nhật đường đi mới -----------------------------------------------")

        # Kiểm tra xem pink_path có ít nhất 2 nút không
        if len(pink_path) > 1:
            dx = pink_path[1].x - pink_path[0].x  # Tính toán hướng di chuyển theo trục x
            dy = pink_path[1].y - pink_path[0].y  # Tính toán hướng di chuyển theo trục y
        else:
            # Nếu pink_path chỉ có 1 nút (đến đích), tính toán lại đường đi
            pink_path = dfs(start_node, target_node)
            if not pink_path:
                print("Không tìm thấy đường đi!")
                return self.x_pos, self.y_pos, self.direction
            dx, dy = 0, 0  # Tạm thời không di chuyển

        # Cập nhật hướng di chuyển của Pink Ghost
        if dx > 0:
            self.direction = 0  # Phải
        elif dx < 0:
            self.direction = 1  # Trái
        elif dy < 0:
            self.direction = 2  # Lên
        elif dy > 0:
            self.direction = 3  # Xuống

        # Di chuyển Pink Ghost theo hướng đã chọn
        if self.direction == 0 and self.turns[0]:
            self.x_pos += self.speed
        elif self.direction == 1 and self.turns[1]:
            self.x_pos -= self.speed
        elif self.direction == 2 and self.turns[2]:
            self.y_pos -= self.speed
        elif self.direction == 3 and self.turns[3]:
            self.y_pos += self.speed

        # Cập nhật tọa độ trung tâm của Pink Ghost
        self.center_x = self.x_pos + 15
        self.center_y = self.y_pos + 15

        # Kiểm tra nếu Pink Ghost đã đến nút tiếp theo
        if len(pink_path) > 1 and abs(self.x_pos - pink_path[1].x * 30) < 1 and abs(self.y_pos - pink_path[1].y * 30) < 1:
            pink_path.pop(0)  # Loại bỏ nút đã đi qua
            print('Đã đến nút tiếp theo, pop đường đi ------------------------------')

        return self.x_pos, self.y_pos, self.direction