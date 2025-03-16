import copy
from board import boards
import pygame
import math
import heapq
from collections import deque
import random
import time

pygame.init()

WIDTH = 900
HEIGHT = 960
screen = pygame.display.set_mode([WIDTH, HEIGHT])  # Tạo ra cửa sổ trò chơi
timer = pygame.time.Clock()  # Đối tượng đồng hồ để kiểm soát khung hình
fps = 60
font = pygame.font.Font('freesansbold.ttf', 15)
level = copy.deepcopy(boards)  # Bản sao của board có thể thay đổi trong quá trình chơi
color = 'blue'
PI = math.pi  # Dùng để vẽ các đường cong
player_images = []  # Danh sách rỗng lưu các hình ảnh player
for i in range(1, 5):  # Lặp từ 1 đến 4 để tải các hoạt động của Pac-Man
    player_images.append(pygame.transform.scale(pygame.image.load(f'assets/player_images/{i}.png'), (30, 30)))
redGhost_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/red.png'), (30, 30))  # Màu đỏ
pinkGhost_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/pink.png'), (30, 30))  # Màu hồng
blueGhost_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/blue.png'), (30, 30))  # Xanh dương
orangeGhost_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/orange.png'), (30, 30))  # Cam


# Danh sách 6 level trống
levels = [boards, boards, boards, boards, boards, boards]  # Để trống, bạn sẽ điền sau (hiện dùng boards mặc định)

player_x = 450
player_y = 540
direction = 0  # Hướng ban đầu của Pac-Man (0 = phải, 1 = trái, 2 = lên, 3 = xuống)
redGhost_x = 60
redGhost_y = 30
redGhost_direction = 1
blueGhost_x = 810
blueGhost_y = 30
blueGhost_direction = 0
pinkGhost_x = 60
pinkGhost_y = 870
pinkGhost_direction = 2
orangeGhost_x = 810
orangeGhost_y = 870
orangeGhost_direction = 2
counter = 0  # Để thay đổi animation của Pac-Man
flicker = False  # Biến boolean để bật/tắt hiệu ứng nhấp nháy của điểm lớn
# R, L, U, D
turns_allowed = [False, False, False, False]  # Danh sách 4 giá trị boolean đại diện cho việc Pac-Man có thể rẽ phải, trái, lên, xuống hay không (R, L, U, D)
direction_command = 0  # Hướng người chơi yêu cầu
player_speed = 2
score = 0

targets = [(player_x, player_y), (player_x, player_y), (player_x, player_y), (player_x, player_y)]  # Danh sách 4 tuple chứa tọa độ mục tiêu của từng ghost
moving = False  # Trạng thái di chuyển của Pac-Man và ghost, ban đầu là dừng (do có giai đoạn khởi động)
ghost_speeds = [2, 2, 2, 2]
startup_counter = 0  # Đếm frame cho giai đoạn khởi động (180 frame đầu tiên)
lives = 5
game_over = False
game_won = False
current_level = 0  # Theo dõi level hiện tại
pink_path = None
blue_path = None
red_path = None
orange_path = None
game_paused = False
dx_change_count_orange = 0
last_xpos_orange = 0
last_ypos_orange = 0
dy_change_count_orange = 0

dx_change_count_red = 0
last_xpos_red = 0
last_ypos_red = 0
dy_change_count_red = 0

dx_change_count_blue = 0
last_xpos_blue = 0
last_ypos_blue = 0
dy_change_count_blue = 0



class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.neighbors = []  # Danh sách liên kết đến các nút lân cận
        self.random_value = 0  # Giá trị ngẫu nhiên

    def add_neighbor(self, neighbor):
        self.neighbors.append(neighbor)
    def __lt__(self, other):
        return False


def generate_random_values(level):
    random_values = {}
    height = len(level)
    width = len(level[0]) if height > 0 else 0

    for y in range(height):
        for x in range(width):
            if level[y][x] < 3:  # Chỉ gán giá trị ngẫu nhiên cho các ô hợp lệ
                random_values[(x, y)] = random.randint(1, 100)  # Giá trị ngẫu nhiên từ 1 đến 100
    return random_values


def build_graph(level):
    graph = {}
    random_values = generate_random_values(level)
    height = len(level)
    width = len(level[0]) if height > 0 else 0

    # Duyệt qua từng ô trong bản đồ
    for y in range(height):
        for x in range(width):
            # Kiểm tra xem ô có hợp lệ không (không phải tường)
            if level[y][x] < 3:  # Điều kiện này có thể cần điều chỉnh tùy vào bản đồ của bạn
                # Tạo một nút mới và thêm vào đồ thị
                node = Node(x, y)
                node.random_value = random_values[(x, y)]  # Gán giá trị ngẫu nhiên cho nút
                graph[(x, y)] = node

    # Kết nối các nút lân cận
    for (x, y), node in graph.items():
        neighbors = [
            (x + 1, y),  # Phải
            (x - 1, y),  # Trái
            (x, y - 1),  # Lên
            (x, y + 1),  # Xuống
        ]
        for nx, ny in neighbors:
            if (nx, ny) in graph:  # Kiểm tra xem nút lân cận có tồn tại trong đồ thị không
                node.add_neighbor(graph[(nx, ny)])

    return graph


def bfs(start, target):
    # Hàng đợi để lưu trữ các nút cần duyệt
    queue = deque()
    # Từ điển để lưu trữ đường đi từ start đến từng nút
    parent = {}
    
    # Bắt đầu từ nút start
    queue.append(start)
    parent[(start.x, start.y)] = None  # Nút start không có nút cha

    while queue:
        current_node = queue.popleft()

        # Nếu tìm thấy nút mục tiêu, xây dựng đường đi và trả về
        if (current_node.x, current_node.y) == (target.x, target.y):
            path = []
            node = current_node
            while node is not None:
                path.append(node)
                node = parent[(node.x, node.y)]
            path.reverse()  # Đảo ngược đường đi để có thứ tự từ start đến target
            return path

        # Duyệt qua các nút lân cận
        for neighbor in current_node.neighbors:
            if (neighbor.x, neighbor.y) not in parent:  # Nếu nút lân cận chưa được duyệt
                queue.append(neighbor)
                parent[(neighbor.x, neighbor.y)] = current_node  # Lưu nút cha

    # Nếu không tìm thấy đường đi, trả về None
    return None



def dfs(start, target, visited=None, path=None):
    if visited is None:
        visited = set()
    if path is None:
        path = []

    visited.add(start)
    path.append(start)

    # Nếu đã đến mục tiêu, trả về đường đi
    if (start.x, start.y) == (target.x, target.y):
        return path

    # Duyệt qua các nút lân cận
    for neighbor in start.neighbors:
        if neighbor not in visited:
            result = dfs(neighbor, target, visited, path)
            if result is not None:
                return result

    # Nếu không tìm thấy đường đi, loại bỏ nút hiện tại khỏi đường đi
    path.pop()
    return None

def heuristic(node, target):
    #Hàm heuristic ước tính chi phí từ node đến target.
    return (abs(node.x - target.x) + abs(node.y - target.y)) / 2



def a_star(start, target):
    # Hàng đợi ưu tiên (priority queue) để lưu trữ các nút cần duyệt
    open_set = []
    heapq.heappush(open_set, (0, start))  # (f_score, node)

    # Từ điển để lưu trữ chi phí thực tế từ start đến từng nút
    g_score = {(start.x, start.y): 0}

    # Từ điển để lưu trữ đường đi từ start đến từng nút
    parent = {(start.x, start.y): None}

    while open_set:
        # Lấy nút có f_score nhỏ nhất từ hàng đợi ưu tiên
        current_f, current_node = heapq.heappop(open_set)

        # Nếu tìm thấy nút mục tiêu, xây dựng đường đi và trả về
        if (current_node.x, current_node.y) == (target.x, target.y):
            path = []
            node = current_node
            while node is not None:
                path.append(node)
                node = parent[(node.x, node.y)]
            path.reverse()  # Đảo ngược đường đi để có thứ tự từ start đến target
            return path

        # Duyệt qua các nút lân cận
        for neighbor in current_node.neighbors:
            # Chi phí thực tế từ start đến neighbor
            tentative_g_score = g_score[(current_node.x, current_node.y)] + 1  # Chi phí di chuyển giữa hai nút là 1

            # Nếu neighbor chưa được duyệt hoặc có chi phí thực tế tốt hơn
            if (neighbor.x, neighbor.y) not in g_score or tentative_g_score < g_score[(neighbor.x, neighbor.y)]:
                # Cập nhật chi phí thực tế
                g_score[(neighbor.x, neighbor.y)] = tentative_g_score

                # Tính f_score = g_score + h_score
                f_score = tentative_g_score + heuristic(neighbor, target)

                # Thêm neighbor vào hàng đợi ưu tiên
                heapq.heappush(open_set, (f_score, neighbor))
                

                # Lưu nút cha để xây dựng đường đi
                parent[(neighbor.x, neighbor.y)] = current_node

    # Nếu không tìm thấy đường đi, trả về None
    return None

def ucs_weight(node1, node2):
    # Tính trọng số dựa trên hiệu của các giá trị ngẫu nhiên
    return abs(node1.random_value - node2.random_value)


def ucs(start, target):
    # Hàng đợi ưu tiên (priority queue) để lưu trữ các nút cần duyệt
    open_set = []
    heapq.heappush(open_set, (0, start))  # (cost, node)

    # Từ điển để lưu trữ chi phí từ start đến từng nút
    g_score = {(start.x, start.y): 0}

    # Từ điển để lưu trữ đường đi từ start đến từng nút
    parent = {(start.x, start.y): None}

    while open_set:
        # Lấy nút có chi phí thấp nhất từ hàng đợi ưu tiên
        current_cost, current_node = heapq.heappop(open_set)

        # Nếu tìm thấy nút mục tiêu, xây dựng đường đi và trả về
        if (current_node.x, current_node.y) == (target.x, target.y):
            path = []
            node = current_node
            while node is not None:
                path.append(node)
                node = parent[(node.x, node.y)]
            path.reverse()  # Đảo ngược đường đi để có thứ tự từ start đến target
            return path

        # Duyệt qua các nút lân cận
        for neighbor in current_node.neighbors:
            # Tính chi phí từ start đến neighbor
            tentative_g_score = g_score[(current_node.x, current_node.y)] + ucs_weight(current_node, neighbor)

            # Nếu neighbor chưa được duyệt hoặc có chi phí thực tế tốt hơn
            if (neighbor.x, neighbor.y) not in g_score or tentative_g_score < g_score[(neighbor.x, neighbor.y)]:
                # Cập nhật chi phí thực tế
                g_score[(neighbor.x, neighbor.y)] = tentative_g_score

                # Thêm neighbor vào hàng đợi ưu tiên
                heapq.heappush(open_set, (tentative_g_score, neighbor))

                # Lưu nút cha để xây dựng đường đi
                parent[(neighbor.x, neighbor.y)] = current_node

    # Nếu không tìm thấy đường đi, trả về None
    return None


class Ghost:
    def __init__(self, x_coord, y_coord, target, speed, img, direct, id):
        self.x_pos = x_coord
        self.y_pos = y_coord
        self.center_x = self.x_pos + 15  # Tọa độ tâm của ghost
        self.center_y = self.y_pos + 15
        self.target = target
        self.speed = speed
        self.img = img
        self.direction = direct
        self.id = id
        self.turns = self.check_collisions()  # Kết quả từ check_collisions()
        self.rect = self.draw()  # Hình chữ nhật bao quanh ghost, dùng để kiểm tra va chạm

    def draw(self):
        if current_level == 0 and self.id != 0:  # Chỉ vẽ redGhost ở Level 1
            return pygame.rect.Rect((self.center_x - 15, self.center_y - 15), (30, 30))
        elif current_level == 1 and self.id != 1:  # Chỉ vẽ pinkGhost ở Level 2
            return pygame.rect.Rect((self.center_x - 15, self.center_y - 15), (30, 30))
        elif current_level == 2 and self.id != 2:  # Chỉ vẽ blueGhost ở Level 3
            return pygame.rect.Rect((self.center_x - 15, self.center_y - 15), (30, 30))
        elif current_level == 3 and self.id != 3:  # Chỉ vẽ orangeGhost ở Level 4
            return pygame.rect.Rect((self.center_x - 15, self.center_y - 15), (30, 30))
        screen.blit(self.img,(self.x_pos,self.y_pos))
        ghost_rect = pygame.rect.Rect((self.center_x - 15, self.center_y - 15), (30, 30))
        return ghost_rect  # Trả về: Hình chữ nhật ghost_rect để dùng trong việc kiểm tra va chạm với Pac-Man

    # Kiểm tra xem ghost có thể rẽ ở đâu (phải, trái, lên, xuống)
    def check_collisions(self):
        num1 = (30)  # 32: Chiều cao mỗi ô trên lưới
        num2 = 30  # 30 Chiều rộng mỗi ô trên lưới
        num3 = 15  # Khoảng cách kiểm tra va chạm
        self.turns = [False, False, False, False]  # Mảng boolean cho phép rẽ (0 = phải, 1 = trái, 2 = lên, 3 = xuống)
        if 0 < self.center_x // 30 < 29:
            if level[self.center_y // num1][(self.center_x - num3) // num2] < 3 :
                self.turns[1] = True
            if level[self.center_y // num1][(self.center_x + num3) // num2] < 3 :
                self.turns[0] = True
            if level[(self.center_y + num3) // num1][self.center_x // num2] < 3 :
                self.turns[3] = True
            if level[(self.center_y - num3) // num1][self.center_x // num2] < 3 :
                self.turns[2] = True

            if self.direction == 2 or self.direction == 3:
                if 12 <= self.center_x % num2 <= 18:
                    if level[(self.center_y + num3) // num1][self.center_x // num2] < 3 :
                        self.turns[3] = True
                    if level[(self.center_y - num3) // num1][self.center_x // num2] < 3 :
                        self.turns[2] = True
                if 12 <= self.center_y % num1 <= 18:
                    if level[self.center_y // num1][(self.center_x - num2) // num2] < 3 :
                        self.turns[1] = True
                    if level[self.center_y // num1][(self.center_x + num2) // num2] < 3 :
                        self.turns[0] = True

            if self.direction == 0 or self.direction == 1:
                if 12 <= self.center_x % num2 <= 18:
                    if level[(self.center_y + num3) // num1][self.center_x // num2] < 3 :
                        self.turns[3] = True
                    if level[(self.center_y - num3) // num1][self.center_x // num2] < 3 :
                        self.turns[2] = True
                if 12 <= self.center_y % num1 <= 18:
                    if level[self.center_y // num1][(self.center_x - num3) // num2] < 3 :
                        self.turns[1] = True
                    if level[self.center_y // num1][(self.center_x + num3) // num2] < 3 :
                        self.turns[0] = True
        else:
            self.turns[0] = True
            self.turns[1] = True
        return self.turns
    

    def move_to_adjacent_cell(self, graph):
        
        #Di chuyển Red Ghost đến một ô bên cạnh (không phải là tường).
        current_pos = (self.center_x // 30, self.center_y // 30)
        adjacent_cells = [
            (current_pos[0] + 1, current_pos[1]),  # Phải
            (current_pos[0] - 1, current_pos[1]),  # Trái
            (current_pos[0], current_pos[1] - 1),  # Lên
            (current_pos[0], current_pos[1] + 1),  # Xuống
        ]

        # Lọc các ô bên cạnh không phải là tường
        valid_cells = []
        for cell in adjacent_cells:
            if cell in graph and graph[cell].neighbors:  # Kiểm tra ô có thể đi qua
                valid_cells.append(cell)

        if valid_cells:
            # Chọn một ô bên cạnh ngẫu nhiên
            target_cell = random.choice(valid_cells)
            self.x_pos = target_cell[0] * 30
            self.y_pos = target_cell[1] * 30
            self.center_x = self.x_pos + 15
            self.center_y = self.y_pos + 15


    def move_orangeGhost(self):
        global player_x, player_y, current_level, orange_path,last_xpos_orange,dx_change_count_orange,last_ypos_orange,dy_change_count_orange

        # Xây dựng đồ thị từ bản đồ
        graph = build_graph(level)

        # Lấy vị trí hiện tại của Pink Ghost và Pac-Man (tọa độ ô lưới)
        current_pos = (self.center_x // 30, self.center_y // 30)
        target_pos = (round(player_x / 30), round(player_y / 30))

        # Lấy nút bắt đầu và nút mục tiêu từ đồ thị
        start_node = graph.get(current_pos)
        target_node = graph.get(target_pos)


        other_ghosts = [redGhost, blueGhost, pinkGhost]  # Danh sách các ghost khác
        for ghost in other_ghosts:
            ghost_pos = (ghost.center_x // 30, ghost.center_y // 30)
            if ghost_pos in graph:
                # Đánh dấu ô này là không thể đi qua (giống như tường)
                graph[ghost_pos].neighbors = []  # Xóa tất cả các liên kết của nút này
        other_ghosts = [blueGhost, pinkGhost]
        for ghost in other_ghosts:
            if (self.center_x // 30 == ghost.center_x // 30) and (self.center_y // 30 == ghost.center_y // 30):
                self.move_to_adjacent_cell(graph)
                return self.x_pos, self.y_pos, self.direction

        if not orange_path:
            orange_path = ucs(start_node, target_node)

        if ((self.center_x+15) % 30 == 0 and (self.center_y+15) % 30 == 0):
            orange_path = ucs(start_node, target_node)  # Sử dụng UCS 

        if orange_path is None:
            return self.x_pos, self.y_pos, self.direction

        # Lấy nút tiếp theo trong đường đi
        if len(orange_path) > 1:
            next_node = orange_path[1]
            dx = next_node.x - orange_path[0].x  # Tính toán hướng di chuyển theo trục x
            dy = next_node.y - orange_path[0].y  # Tính toán hướng di chuyển theo trục y
        else:
            # Nếu chỉ còn 1 nút (đến đích), tính toán lại đường đi
            orange_path = ucs(start_node, target_node)
            dx, dy = 0, 0  # Tạm thời không di chuyển
        if orange_path is None:
            return self.x_pos, self.y_pos, self.direction


        if self.x_pos != last_xpos_orange:
                dx_change_count_orange += 1
        else:
                dx_change_count_orange = 0
        last_xpos_orange = self.x_pos

        if dx_change_count_orange >= 2 and self.y_pos % 30 != 0:
            # Làm tròn dy về bội số gần nhất của 30
            self.y_pos = round(self.y_pos / 30) * 30



        if self.y_pos != last_ypos_orange:
                dy_change_count_orange += 1
        else:
                dy_change_count_orange = 0
        last_ypos_orange = self.y_pos


        if dy_change_count_orange >= 2 and self.x_pos % 30 != 0:
            # Làm tròn dy về bội số gần nhất của 30
            self.x_pos = round(self.x_pos / 30) * 30

  

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
        if  len(orange_path) > 1 and abs(self.x_pos - orange_path[1].x * 30) < 1 and abs(self.y_pos - orange_path[1].y * 30) < 1:
            orange_path.pop(0)  # Loại bỏ nút đã đi qua
        return self.x_pos, self.y_pos, self.direction
    
    def move_redGhost(self):
        global player_x, player_y, current_level, red_path,last_xpos_red,dx_change_count_red,last_ypos_red,dy_change_count_red


        # Xây dựng đồ thị từ bản đồ
        graph = build_graph(level)

        # Lấy vị trí hiện tại của Pink Ghost và Pac-Man (tọa độ ô lưới)
        current_pos = (self.center_x // 30, self.center_y // 30)
        target_pos = (round(player_x / 30), round(player_y / 30))

        # Lấy nút bắt đầu và nút mục tiêu từ đồ thị
        start_node = graph.get(current_pos)
        target_node = graph.get(target_pos)

        other_ghosts = [orangeGhost, blueGhost, pinkGhost]  # Danh sách các ghost khác
        for ghost in other_ghosts:
            ghost_pos = (ghost.center_x // 30, ghost.center_y // 30)
            if ghost_pos in graph:
                # Đánh dấu ô này là không thể đi qua (giống như tường)
                graph[ghost_pos].neighbors = []  # Xóa tất cả các liên kết của nút này

        for ghost in other_ghosts:
            if (self.center_x // 30 == ghost.center_x // 30) and (self.center_y // 30 == ghost.center_y // 30):
                self.move_to_adjacent_cell(graph)
                return self.x_pos, self.y_pos, self.direction


        # Sử dụng A* để tìm đường đi
        if not red_path :
            red_path = a_star(start_node, target_node)  # Sử dụng A*

        if ((self.center_x+15) % 30 == 0 and (self.center_y+15) % 30 == 0) :
            red_path = a_star(start_node, target_node)

        # Lấy nút tiếp theo trong đường đi
        if red_path is None:
            return self.x_pos, self.y_pos, self.direction
        
        if len(red_path) > 1:
            next_node = red_path[1]
            dx = next_node.x - red_path[0].x  # Tính toán hướng di chuyển theo trục x
            dy = next_node.y - red_path[0].y  # Tính toán hướng di chuyển theo trục y
        else:
            # Nếu chỉ còn 1 nút (đến đích), tính toán lại đường đi
            red_path = a_star(start_node, target_node)
            dx, dy = 0, 0  # Tạm thời không di chuyển

        if red_path is None:
            return self.x_pos, self.y_pos, self.direction

        if self.x_pos != last_xpos_red:
                dx_change_count_red += 1
        else:
                dx_change_count_red = 0
        last_xpos_red = self.x_pos

        if dx_change_count_red >= 2 and self.y_pos % 30 != 0:
            # Làm tròn dy về bội số gần nhất của 30
            self.y_pos = round(self.y_pos / 30) * 30



        if self.y_pos != last_ypos_red:
                dy_change_count_red += 1
        else:
                dy_change_count_red = 0
        last_ypos_red = self.y_pos

        if dy_change_count_red >= 2 and self.x_pos % 30 != 0:
            # Làm tròn dy về bội số gần nhất của 30
            self.x_pos = round(self.x_pos / 30) * 30



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
        if len(red_path) > 1 and abs(self.x_pos - red_path[1].x * 30) < 1 and abs(self.y_pos - red_path[1].y * 30) < 1:
            red_path.pop(0)  # Loại bỏ nút đã đi qua

        return self.x_pos, self.y_pos, self.direction



    def move_blueGhost(self):
        global player_x, player_y, current_level, blue_path,last_xpos_blue,dx_change_count_blue,last_ypos_blue,dy_change_count_blue

        # Xây dựng đồ thị từ bản đồ
        graph = build_graph(level)

        # Lấy vị trí hiện tại của Pink Ghost và Pac-Man (tọa độ ô lưới)
        current_pos = (self.center_x // 30, self.center_y // 30)
        target_pos = (round(player_x / 30), round(player_y / 30))

        # Lấy nút bắt đầu và nút mục tiêu từ đồ thị
        start_node = graph.get(current_pos)
        target_node = graph.get(target_pos)


        other_ghosts = [redGhost, orangeGhost, pinkGhost]  # Danh sách các ghost khác
        for ghost in other_ghosts:
            ghost_pos = (ghost.center_x // 30, ghost.center_y // 30)
            if ghost_pos in graph:
                # Đánh dấu ô này là không thể đi qua (giống như tường)
                graph[ghost_pos].neighbors = []  # Xóa tất cả các liên kết của nút này
        other_ghosts = [pinkGhost]
        for ghost in other_ghosts:
            if (self.center_x // 30 == ghost.center_x // 30) and (self.center_y // 30 == ghost.center_y // 30):
                self.move_to_adjacent_cell(graph)
                return self.x_pos, self.y_pos, self.direction

        # Sử dụng BFS để tìm đường đi
        if not blue_path:
            blue_path = bfs(start_node, target_node) 

        if ((self.center_x+15) % 30 == 0 and (self.center_y+15) % 30 == 0):
            blue_path = bfs(start_node, target_node) 

        if blue_path is None:
            return self.x_pos, self.y_pos, self.direction
        # Lấy nút tiếp theo trong đường đi
        if len(blue_path) > 1:
            next_node = blue_path[1]
            dx = next_node.x - blue_path[0].x  # Tính toán hướng di chuyển theo trục x
            dy = next_node.y - blue_path[0].y  # Tính toán hướng di chuyển theo trục y
        else:
            # Nếu chỉ còn 1 nút (đến đích), tính toán lại đường đi
            blue_path = bfs(start_node, target_node)
            dx, dy = 0, 0  # Tạm thời không di chuyển
        if blue_path is None:
            return self.x_pos, self.y_pos, self.direction

        if self.x_pos != last_xpos_blue:
                dx_change_count_blue += 1
        else:
                dx_change_count_blue = 0
        last_xpos_blue = self.x_pos

        if dx_change_count_blue >= 2 and self.y_pos % 30 != 0:
            # Làm tròn dy về bội số gần nhất của 30
            self.y_pos = round(self.y_pos / 30) * 30



        if self.y_pos != last_ypos_blue:
                dy_change_count_blue += 1
        else:
                dy_change_count_blue = 0
        last_ypos_blue = self.y_pos

        if dy_change_count_blue >= 2 and self.x_pos % 30 != 0:
            # Làm tròn dy về bội số gần nhất của 30
            self.x_pos = round(self.x_pos / 30) * 30

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
        if len(blue_path) > 1 and abs(self.x_pos - blue_path[1].x * 30) < 1 and abs(self.y_pos - blue_path[1].y * 30) < 1:
            blue_path.pop(0)  # Loại bỏ nút đã đi qua

        return self.x_pos, self.y_pos, self.direction



    def move_pinkGhost(self):
            global player_x, player_y,current_level,pink_path
            # Xây dựng đồ thị từ bản đồ
            graph = build_graph(level)
            # Lấy vị trí hiện tại của pinkGhost và Pac-Man (tọa độ ô lưới)
            current_pos = (self.center_x //30 ,self.center_y //30)
            target_pos = (round(player_x /30), round(player_y /30))
            # Lấy nút bắt đầu và nút mục tiêu từ đồ thị
            start_node = graph.get(current_pos)
            target_node = graph.get(target_pos)
            # Sử dụng DFS để tìm đường đi

            if not pink_path or len(pink_path) <= 1:
                pink_path = dfs(start_node, target_node)

            if len(pink_path) > 1 :
                dx = pink_path[1].x -  pink_path[0].x  # Tính toán hướng di chuyển theo trục x
                dy = pink_path[1].y -  pink_path[0].y  # Tính toán hướng di chuyển theo trục y
            else:
                pink_path = dfs(start_node, target_node)
                dx, dy = 0, 0  # Tạm thời không di chuyển

            #Cập nhật hướng di chuyển của pinkGhost
            if dx > 0:
                self.direction = 0  # Phải
            elif dx < 0:
                self.direction = 1  # Trái
            elif dy < 0:
                self.direction = 2  # Lên
            elif dy > 0:
                self.direction = 3  # Xuống

            if self.direction == 0 and self.turns[0]:
                self.x_pos += self.speed
            elif self.direction == 1 and self.turns[1]:
                self.x_pos -= self.speed
            elif self.direction == 2 and self.turns[2]:
                self.y_pos -= self.speed
            elif self.direction == 3 and self.turns[3]:
                self.y_pos += self.speed  

            self.center_x = self.x_pos + 15
            self.center_y = self.y_pos + 15

            if  len(pink_path) > 1 and  abs( self.x_pos  - pink_path[1].x*30) < 1 and abs(self.y_pos - (pink_path[1].y*30)) < 1:
                pink_path.pop(0)   

            # Di chuyển pinkGhost theo hướng đã chọn
            return self.x_pos, self.y_pos, self.direction


# Thông tin bổ sung giúp người chơi theo dõi trạng thái trò chơi
def draw_misc():
    score_text = font.render(f'Score: {score}', True, 'white')
    screen.blit(score_text, (35, 940))
    for i in range(lives):
        screen.blit(pygame.transform.scale(player_images[0], (15, 15)), (650 + i * 20, 940))
    if game_over:
        pygame.draw.rect(screen, 'white', [50, 150, 800, 300], 0, 10)
        pygame.draw.rect(screen, 'dark gray', [70, 170, 760, 260], 0, 10)
        gameover_text = font.render('Game over! Space bar to restart!', True, 'red')
        screen.blit(gameover_text, (325, 300))
    if game_won:
        pygame.draw.rect(screen, 'white', [50, 150, 800, 300], 0, 10)
        pygame.draw.rect(screen, 'dark gray', [70, 170, 760, 260], 0, 10)
        gameover_text = font.render('Victory! Space bar to restart!', True, 'green')
        screen.blit(gameover_text, (325, 300))

# Kiểm tra xem Pac-Man có "ăn" được vật phẩm nào trên bản đồ hay không
def check_collisions(scor):
    num1 = 30   # check_collisions
    num2 = WIDTH // 30  # Chiều rộng mỗi ô trên lưới
    if 0 < player_x < 870:
        if level[center_y // num1][center_x // num2] == 1:  # Ăn thức ăn nhỏ
            level[center_y // num1][center_x // num2] = 0
            scor += 10
        if level[center_y // num1][center_x // num2] == 2:  # Ăn thức ăn lớn
            level[center_y // num1][center_x // num2] = 0
            scor += 50

    return scor # Các giá trị này được gán lại cho các biến toàn cục trong vòng lặp chính

def draw_board():
    num1 = ((HEIGHT - 50) // 30)
    num2 = (WIDTH // 30)
    for i in range(len(level)):
        for j in range(len(level[i])):
            if level[i][j] == 1:
                pygame.draw.circle(screen, 'white', (j * num2 + (0.5 * num2), i * num1 + (0.5 * num1)), 4)
            if level[i][j] == 2 and not flicker:
                pygame.draw.circle(screen, 'white', (j * num2 + (0.5 * num2), i * num1 + (0.5 * num1)), 10)
            if level[i][j] == 3:
                pygame.draw.line(screen, color, (j * num2 + (0.5 * num2), i * num1),
                                 (j * num2 + (0.5 * num2), i * num1 + num1), 3)
            if level[i][j] == 4:
                pygame.draw.line(screen, color, (j * num2, i * num1 + (0.5 * num1)),
                                 (j * num2 + num2, i * num1 + (0.5 * num1)), 3)
            if level[i][j] == 5:
                pygame.draw.arc(screen, color, [(j * num2 - (num2 * 0.4)) - 2, (i * num1 + (0.5 * num1)), num2, num1],
                                0, PI / 2, 3)
            if level[i][j] == 6:
                pygame.draw.arc(screen, color,
                                [(j * num2 + (num2 * 0.5)), (i * num1 + (0.5 * num1)), num2, num1], PI / 2, PI, 3)
            if level[i][j] == 7:
                pygame.draw.arc(screen, color, [(j * num2 + (num2 * 0.5)), (i * num1 - (0.4 * num1)), num2, num1], PI,
                                3 * PI / 2, 3)
            if level[i][j] == 8:
                pygame.draw.arc(screen, color,
                                [(j * num2 - (num2 * 0.4)) - 2, (i * num1 - (0.4 * num1)), num2, num1], 3 * PI / 2,
                                2 * PI, 3)
            if level[i][j] == 9:
                pygame.draw.line(screen, 'white', (j * num2, i * num1 + (0.5 * num1)),
                                 (j * num2 + num2, i * num1 + (0.5 * num1)), 3)
            if level[i][j] == 13:
                pygame.draw.line(screen, 'yellow', (j * num2 + (0.5 * num2), i * num1),
                                 (j * num2 + (0.5 * num2), i * num1 + num1), 3)
            if level[i][j] == 14:
                pygame.draw.line(screen, 'yellow', (j * num2, i * num1 + (0.5 * num1)),
                                 (j * num2 + num2, i * num1 + (0.5 * num1)), 3)
            if level[i][j] == 15:
                pygame.draw.arc(screen, 'yellow', [(j * num2 - (num2 * 0.4)) - 2, (i * num1 + (0.5 * num1)), num2, num1],
                                0, PI / 2, 3)
            if level[i][j] == 16:
                pygame.draw.arc(screen, 'yellow',
                                [(j * num2 + (num2 * 0.5)), (i * num1 + (0.5 * num1)), num2, num1], PI / 2, PI, 3)
            if level[i][j] == 17:
                pygame.draw.arc(screen, 'yellow', [(j * num2 + (num2 * 0.5)), (i * num1 - (0.4 * num1)), num2, num1], PI,
                                3 * PI / 2, 3)
            if level[i][j] == 18:
                pygame.draw.arc(screen, 'yellow',
                                [(j * num2 - (num2 * 0.4)) - 2, (i * num1 - (0.4 * num1)), num2, num1], 3 * PI / 2,
                                2 * PI, 3)
                
# Vẽ Pac-Man với các animation khác nhau
def draw_player():
    # 0-RIGHT, 1-LEFT, 2-UP, 3-DOWN
    if direction == 0:
        screen.blit(player_images[counter // 5], (player_x, player_y))
    elif direction == 1:
        screen.blit(pygame.transform.flip(player_images[counter // 5], True, False), (player_x, player_y))  # Lật theo trục ngang
    elif direction == 2:
        screen.blit(pygame.transform.rotate(player_images[counter // 5], 90), (player_x, player_y))  # Hướng lên trên
    elif direction == 3:
        screen.blit(pygame.transform.rotate(player_images[counter // 5], 270), (player_x, player_y))

# Hàm này xác định các hướng mà Pac-Man được phép rẽ
def check_position(centerx, centery):
    turns = [False, False, False, False]  # Đại diện cho khả năng rẽ ở 4 hướng (0 = phải, 1 = trái, 2 = lên, 3 = xuống)
    num1 = 30
    num2 = 30
    num3 = 15  # Khoảng cách kiểm tra (nửa chiều rộng ô, dùng để phát hiện tường trước khi Pac-Man chạm vào)
    if centerx // 30 < 29:  # Kiểm tra trong phạm vi bản đồ (0 - 28)
        if direction == 0:
            if level[centery // num1][(centerx - num3) // num2] < 3:
                turns[1] = True
        if direction == 1:
            if level[centery // num1][(centerx + num3) // num2] < 3:
                turns[0] = True
        if direction == 2:
            if level[(centery + num3) // num1][centerx // num2] < 3:
                turns[3] = True
        if direction == 3:
            if level[(centery - num3) // num1][centerx // num2] < 3:
                turns[2] = True

        if direction == 2 or direction == 3:
            if 12 <= centerx % num2 <= 18:
                if level[(centery + num3) // num1][centerx // num2] < 3:
                    turns[3] = True
                if level[(centery - num3) // num1][centerx // num2] < 3:
                    turns[2] = True
            if 12 <= centery % num1 <= 18:
                if level[centery // num1][(centerx - num2) // num2] < 3:
                    turns[1] = True
                if level[centery // num1][(centerx + num2) // num2] < 3:
                    turns[0] = True
        if direction == 0 or direction == 1:
            if 12 <= centerx % num2 <= 18:
                if level[(centery + num1) // num1][centerx // num2] < 3:
                    turns[3] = True
                if level[(centery - num1) // num1][centerx // num2] < 3:
                    turns[2] = True
            if 12 <= centery % num1 <= 18:
                if level[centery // num1][(centerx - num3) // num2] < 3:
                    turns[1] = True
                if level[centery // num1][(centerx + num3) // num2] < 3:
                    turns[0] = True
    else:
        turns[0] = True
        turns[1] = True
    return turns

def move_player(play_x, play_y):
\
    if current_level != 5 :  # Level 1,2,3,4,5: Pac-Man đứng yên
        return play_x, play_y
    else:  #Level 6 Pac-Man có thể di chuyển
        if direction == 0 and turns_allowed[0]:
            play_x += player_speed
        elif direction == 1 and turns_allowed[1]:
            play_x -= player_speed
        if direction == 2 and turns_allowed[2]:
            play_y -= player_speed
        elif direction == 3 and turns_allowed[3]:
            play_y += player_speed
        return play_x, play_y

# Hàm này xác định mục tiêu di chuyển cho từng con ma
def get_targets(redGhost_x, redGhost_y, pinkGhost_x, pinkGhost_y, blueGhost_x, blueGhost_y, orangeGhost_x, orangeGhost_y):
    if current_level == 0:  # Level 1: Chỉ redGhost hoạt động
        return [(player_x, player_y), (0, 0), (0, 0), (0, 0)]
    elif current_level == 1:  # Level 2: Chỉ pinkGhost hoạt động
        return [(0, 0), (player_x, player_y), (0, 0), (0, 0)]
    elif current_level == 2:  # Level 3: Chỉ blueGhost hoạt động
        return [(0, 0), (0, 0), (player_x, player_y), (0, 0)]
    elif current_level == 3:  # Level 4: Chỉ orangeGhost hoạt động
        return [(0, 0), (0, 0), (0, 0), (player_x, player_y)]
    else  :
        if 340 < redGhost_x < 560 and 340 < redGhost_y < 500:
            redGhost_target = (400, 100)
        else:
            redGhost_target = (player_x, player_y)
        if 340 < blueGhost_x < 560 and 340 < blueGhost_y < 500:
            blueGhost_target = (400, 100)
        else:
            blueGhost_target = (player_x, player_y)
        if 340 < pinkGhost_x < 560 and 340 < pinkGhost_y < 500:
            pinkGhost_target = (400, 100)
        else:
            pinkGhost_target = (player_x, player_y)
        if 340 < orangeGhost_x < 560 and 340 < orangeGhost_y < 500:
            orangeGhost_target = (400, 100)
        else:
            orangeGhost_target = (player_x, player_y)
        return [redGhost_target, blueGhost_target, pinkGhost_target, orangeGhost_target]

# Điều khiển tốc độ khung hình của trò chơi và tạo hiệu ứng nhấp nháy cho điểm lớn
def update_timer_and_animation():
    global counter, flicker
    timer.tick(fps)
    if counter < 19:
        counter += 1
        if counter > 3:
            flicker = False
    else:
        counter = 0
        flicker = True


# Quản lý giai đoạn khởi động đầu game, giữ nhân vật đứng yên trong 180 frame đầu tiên
def manage_startup():
    global moving, startup_counter
    if startup_counter < 50 and not game_over and not game_won:
        moving = False
        startup_counter += 1
    else:
        moving = True

# Cập nhật tốc độ di chuyển của 4 ghost dựa trên trạng thái trò chơi
def update_ghost_speeds():
    global ghost_speeds
    ghost_speeds = [2, 2, 2, 2]
    
def check_game_won():
    global game_won,game_paused,current_level
    if not game_paused :
        game_won = True
        game_paused = True
        for i in range(len(level)):
            if 1 in level[i] or 2 in level[i]:
                    game_won = False
                    game_paused =False
# Hiển thị trạng thái hiện tại của trò chơi (bản đồ, Pac-Man, UI)
def draw_game_elements():
    global center_x, center_y, player_circle
    screen.fill('black')
    draw_board()
    center_x = player_x + 15
    center_y = player_y + 15
    # Vẽ một vòng tròn đen (bán kính 15, độ dày 1) để đại diện cho Pac-Man trong kiểm tra va chạm
    player_circle = pygame.draw.circle(screen, 'black', (center_x, center_y), 15, 1)
    draw_player()
    draw_misc()

# Di chuyển Pac-Man và các ghost
def move_characters():
    global player_x, player_y, redGhost_x, redGhost_y, redGhost_direction, blueGhost_x, blueGhost_y, blueGhost_direction,game_paused
    global pinkGhost_x, pinkGhost_y, pinkGhost_direction, orangeGhost_x, orangeGhost_y, orangeGhost_direction, turns_allowed
    turns_allowed = check_position(center_x, center_y)
    if moving and not game_paused:
        player_x, player_y = move_player(player_x, player_y)
        if current_level == 0:  # Level 1: Chỉ redGhost di chuyển
            redGhost_x, redGhost_y, redGhost_direction = redGhost.move_redGhost()
        elif current_level == 1:  # Level 2: Chỉ pinkGhost di chuyển
            pinkGhost_x, pinkGhost_y, pinkGhost_direction = pinkGhost.move_pinkGhost()    
        elif current_level == 2:  # Level 3: Chỉ blueGhost di chuyển
            blueGhost_x, blueGhost_y, blueGhost_direction = blueGhost.move_blueGhost()
        elif current_level == 3:  # Level 4: Chỉ orangeGhost di chuyển
            orangeGhost_x, orangeGhost_y, orangeGhost_direction = orangeGhost.move_orangeGhost()            
        elif current_level > 3: # Các level khác: Tất cả ghost di chuyển
            redGhost_x, redGhost_y, redGhost_direction = redGhost.move_redGhost()
            pinkGhost_x, pinkGhost_y, pinkGhost_direction = pinkGhost.move_pinkGhost()
            blueGhost_x, blueGhost_y, blueGhost_direction = blueGhost.move_blueGhost()
            orangeGhost_x, orangeGhost_y, orangeGhost_direction = orangeGhost.move_orangeGhost()

# Xử lý khi Pac-Man ăn điểm
def handle_point_collisions():
    global score
    score  = check_collisions(score)

# Đặt lại trạng thái trò chơi khi Pac-Man mất mạng
def reset_game_state():
    global startup_counter, player_x, player_y, direction, direction_command,pink_path,red_path,orange_path,blue_path
    global redGhost_x, redGhost_y, redGhost_direction, blueGhost_x, blueGhost_y, blueGhost_direction, pinkGhost_x, pinkGhost_y, pinkGhost_direction
    global orangeGhost_x, orangeGhost_y, orangeGhost_direction
    startup_counter = 0
    player_x = 450
    player_y = 540
    direction = 0
    direction_command = 0
    redGhost_x = 60
    redGhost_y = 30
    redGhost_direction = 0
    blueGhost_x = 810
    blueGhost_y = 30
    blueGhost_direction = 2
    pinkGhost_x = 60
    pinkGhost_y = 870
    pinkGhost_direction = 2
    orangeGhost_x = 810
    orangeGhost_y = 870
    orangeGhost_direction = 2
    pink_path = []  
    red_path = []  
    orange_path = []  
    blue_path = []  
    if current_level == 0:
        if lives == 4:
            redGhost_x = 810
            redGhost_y = 870
        elif lives == 3:
            redGhost_x = 60
            redGhost_y = 450
        elif lives == 2:
            redGhost_x = 450
            redGhost_y = 150
        elif lives == 1:
            redGhost_x = 450
            redGhost_y = 870
    if current_level == 1:
        if lives == 4:
            pinkGhost_x = 810
            pinkGhost_y = 870
        elif lives == 3:
            pinkGhost_x = 60
            pinkGhost_y = 450
        elif lives == 2:
            pinkGhost_x = 450
            pinkGhost_y = 150
        elif lives == 1:
            pinkGhost_x = 450
            pinkGhost_y = 870
    if current_level == 2:
        if lives == 4:
            blueGhost_x = 810
            blueGhost_y = 870
        elif lives == 3:
            blueGhost_x = 60
            blueGhost_y = 450
        elif lives == 2:
            blueGhost_x = 450
            blueGhost_y = 150
        elif lives == 1:
            blueGhost_x = 450
            blueGhost_y = 870
    if current_level == 3:
        if lives == 4:
            orangeGhost_x = 810
            orangeGhost_y = 870
        elif lives == 3:
            orangeGhost_x = 60
            orangeGhost_y = 450
        elif lives == 2:
            orangeGhost_x = 450
            orangeGhost_y = 150
        elif lives == 1:
            orangeGhost_x = 450
            orangeGhost_y = 870




# Xử lý va chạm giữa Pac-Man và ghost
def handle_ghost_collision():
    global game_over, moving, startup_counter,game_paused,lives
    if player_circle.colliderect(blueGhost.rect)  or \
        player_circle.colliderect(pinkGhost.rect)  or \
        player_circle.colliderect(redGhost.rect)  or \
        player_circle.colliderect(orangeGhost.rect) :
        if lives > 0:
            lives -= 1
            reset_game_state()
        else:
            game_over = True
            moving = False
            startup_counter = 0
            game_paused = True  # Dừng mọi di chuyển

# Xử lý các sự kiện từ người chơi (phím nhấn, thoát game)
def handle_events():
    global run, direction_command, lives, startup_counter, player_x, player_y, direction,game_paused
    global redGhost_x, redGhost_y, redGhost_direction, blueGhost_x, blueGhost_y, blueGhost_direction, pinkGhost_x, pinkGhost_y, pinkGhost_direction
    global orangeGhost_x, orangeGhost_y, orangeGhost_direction
    global score, level, game_over, game_won, current_level
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                direction_command = 0
            if event.key == pygame.K_LEFT:
                direction_command = 1
            if event.key == pygame.K_UP:
                direction_command = 2
            if event.key == pygame.K_DOWN:
                direction_command = 3
            if event.key == pygame.K_SPACE and (game_over or game_won):
                current_level = show_menu()
                level = copy.deepcopy(levels[current_level])
                if(current_level == 5):
                    lives = 3
                elif current_level ==4:
                    lives = 1
                else:
                    lives = 5

                # Reset trạng thái trò chơi
                reset_game_state()
                if lives == 5:
                    if current_level == 0:
                        redGhost_x = 60
                        redGhost_y = 30
                    if current_level == 1:
                        pinkGhost_x = 60
                        pinkGhost_y = 30      
                    if current_level == 2:
                        blueGhost_x = 60
                        blueGhost_y = 30 
                    if current_level == 3:
                        orangeGhost_x = 60
                        orangeGhost_y = 30 
                if current_level != 5:
                    level = [[0 if cell == 1 else cell for cell in row] for row in level]
                game_over = False
                game_won = False
                game_paused = False
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_RIGHT and direction_command == 0:
                direction_command = direction
            if event.key == pygame.K_LEFT and direction_command == 1:
                direction_command = direction
            if event.key == pygame.K_UP and direction_command == 2:
                direction_command = direction
            if event.key == pygame.K_DOWN and direction_command == 3:
                direction_command = direction

# Cập nhật hướng của Pac-Man dựa trên phím nhấn và hướng được phép
def update_player_direction():
    global direction
    if current_level == 5:  # Chỉ cập nhật hướng ở Level 6
        if direction_command == 0 and turns_allowed[0]:
            direction = 0
        if direction_command == 1 and turns_allowed[1]:
            direction = 1
        if direction_command == 2 and turns_allowed[2]:
            direction = 2
        if direction_command == 3 and turns_allowed[3]:
            direction = 3


def update_display():
    pygame.display.flip()
background_image_path = r'assets/BG.jpg'
def update_display():
    pygame.display.flip()

def show_menu():
    pygame.init()
    screen = pygame.display.set_mode((960, 900))
    pygame.display.set_caption('Pac-Man Menu')

    menu_running = True
    selected_option = 0  # Chỉ mục menu (bao gồm level + quit)
    font = pygame.font.Font('freesansbold.ttf', 40)

    # Load ảnh nền
   
    background = pygame.image.load(background_image_path).convert()
    background = pygame.transform.scale(background, (960, 900))

    # Tạo layer trung gian
    overlay = pygame.Surface((500, 550))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))

    menu_options = [f'Level {i + 1}' for i in range(6)] + ['Quit']

    while menu_running:
        screen.blit(background, (0, 0))
        screen.blit(overlay, (screen.get_width() // 2 - 250, 150))

        # Vẽ tiêu đề
        title = font.render('Pac-Man Menu', True, 'Blue')
        screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, 180))

        # Vẽ danh sách lựa chọn
        option_positions = []
        for i, option in enumerate(menu_options):
            color = 'white' if i != selected_option else 'Blue'
            text = font.render(option, True, color)
            text_x = screen.get_width() // 2 - text.get_width() // 2
            text_y = 300 + i * 60
            screen.blit(text, (text_x, text_y))
            option_positions.append((text_x, text_y, text.get_width(), text.get_height()))

        # Vẽ khung bao quanh lựa chọn hiện tại
        if option_positions:
            x, y, w, h = option_positions[selected_option]
            padding = 10
            pygame.draw.rect(screen, 'Blue', (x - padding, y - padding, w + 2 * padding, h + 2 * padding), 3)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_option = max(0, selected_option - 1)
                elif event.key == pygame.K_DOWN:
                    selected_option = min(len(menu_options) - 1, selected_option + 1)
                elif event.key == pygame.K_RETURN:
                    if selected_option == len(menu_options) - 1:  # Nếu chọn "Quit"
                        pygame.quit()
                        exit()
                    else:
                        menu_running = False

    return selected_option

# Gọi menu trước khi vào trò chơi
current_level = show_menu()
level = copy.deepcopy(levels[current_level])  # Gán level được chọn

if lives == 5:
    if current_level == 0:
        redGhost_x = 60
        redGhost_y = 30
    if current_level == 1:
        pinkGhost_x = 60
        pinkGhost_y = 30      
    if current_level == 2:
        blueGhost_x = 60
        blueGhost_y = 30 
    if current_level == 3:
        orangeGhost_x = 60
        orangeGhost_y = 30 



if current_level == 0:
    pinkGhost_x = 450
    pinkGhost_y = 490    
    blueGhost_x = 450
    blueGhost_y = 490   
    orangeGhost_x = 450
    orangeGhost_y = 490
elif current_level == 1:
    redGhost_x = 450
    redGhost_y = 490    
    blueGhost_x = 450
    blueGhost_y = 490   
    orangeGhost_x = 450
    orangeGhost_y = 490
elif current_level == 2:
    redGhost_x = 450
    redGhost_y = 490    
    pinkGhost_x = 450
    pinkGhost_y = 490   
    orangeGhost_x = 450
    orangeGhost_y = 490
elif current_level == 3:
    redGhost_x = 450
    redGhost_y = 490    
    pinkGhost_x = 450
    pinkGhost_y = 490   
    blueGhost_x = 450
    blueGhost_y = 490




if ( current_level != 5):
    level = [[0 if cell == 1 else cell for cell in row] for row in level]
    if current_level == 4:
        lives = 1
else :
    lives = 3


# Vòng lặp chính đã sửa
run = True
while run:
    update_timer_and_animation()
    manage_startup()
    update_ghost_speeds()
    if lives <= 0:
        game_over = True
        moving = False
        startup_counter = 0
        game_paused = True  # Dừng mọi di chuyển




    if(current_level == 5):
        check_game_won()
    # Cập nhật sự kiện và hướng trước khi vẽ hoặc di chuyển
    handle_events()
    update_player_direction()
    
    # Vẽ các thành phần và tính toán center_x, center_y
    draw_game_elements()
    # Tạo các đối tượng ghost với targets ban đầu
    redGhost = Ghost(redGhost_x, redGhost_y, targets[0], ghost_speeds[0], redGhost_img, redGhost_direction, 0)
    blueGhost = Ghost(blueGhost_x, blueGhost_y, targets[1], ghost_speeds[1], blueGhost_img, blueGhost_direction, 2)
    pinkGhost = Ghost(pinkGhost_x, pinkGhost_y, targets[2], ghost_speeds[2], pinkGhost_img, pinkGhost_direction, 1)
    orangeGhost = Ghost(orangeGhost_x, orangeGhost_y, targets[3], ghost_speeds[3], orangeGhost_img, orangeGhost_direction, 3)
    # Cập nhật targets sau khi tạo ghost
    targets = get_targets(redGhost_x, redGhost_y, blueGhost_x, blueGhost_y, pinkGhost_x, pinkGhost_y, orangeGhost_x, orangeGhost_y)

    # Di chuyển nhân vật
    move_characters()
    
    # Xử lý va chạm và các logic khác
    handle_point_collisions()
    handle_ghost_collision()
    
    # Cập nhật màn hình
    update_display()

pygame.quit()