# Build Pac-Man from Scratch in Python with PyGame!!
import copy
from board import boards
import pygame
import math

pygame.init()

WIDTH = 900
HEIGHT = 950
screen = pygame.display.set_mode([WIDTH, HEIGHT])  # Tạo ra cửa sổ trò chơi
timer = pygame.time.Clock()  # Đối tượng đồng hồ để kiểm soát khung hình
fps = 60
font = pygame.font.Font('freesansbold.ttf', 20)
level = copy.deepcopy(boards)  # Bản sao của board có thể thay đổi trong quá trình chơi
color = 'blue'
PI = math.pi  # Dùng để vẽ các đường cong
player_images = []  # Danh sách rỗng lưu các hình ảnh player
for i in range(1, 5):  # Lặp từ 1 đến 4 để tải các hoạt động của Pac-Man
    player_images.append(pygame.transform.scale(pygame.image.load(f'assets/player_images/{i}.png'), (45, 45)))
redGhost_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/red.png'), (45, 45))  # Màu đỏ
pinkGhost_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/pink.png'), (45, 45))  # Màu hồng
blueGhost_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/blue.png'), (45, 45))  # Xanh dương
orangeGhost_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/orange.png'), (45, 45))  # Cam
spooked_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/powerup.png'), (45, 45))  # Sợ hãi
dead_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/dead.png'), (45, 45))

# Danh sách 6 level trống
levels = [boards, boards, boards, boards, boards, boards]  # Để trống, bạn sẽ điền sau (hiện dùng boards mặc định)

player_x = 450
player_y = 663
direction = 0  # Hướng ban đầu của Pac-Man (0 = phải, 1 = trái, 2 = lên, 3 = xuống)
redGhost_x = 56
redGhost_y = 58
redGhost_direction = 0
blueGhost_x = 800
blueGhost_y = 58
blueGhost_direction = 0
pinkGhost_x = 56
pinkGhost_y = 820
pinkGhost_direction = 2
orangeGhost_x = 800
orangeGhost_y = 798
orangeGhost_direction = 2
counter = 0  # Để thay đổi animation của Pac-Man
flicker = False  # Biến boolean để bật/tắt hiệu ứng nhấp nháy của điểm lớn
# R, L, U, D
turns_allowed = [False, False, False, False]  # Danh sách 4 giá trị boolean đại diện cho việc Pac-Man có thể rẽ phải, trái, lên, xuống hay không (R, L, U, D)
direction_command = 0  # Hướng người chơi yêu cầu
player_speed = 2
score = 0
powerup = False
power_counter = 0  # Đếm số frame kể từ khi power-up được kích hoạt (tắt sau 600 frame)
eaten_ghost = [False, False, False, False]  # Trạng thái của 4 ghost (redGhost, blueGhost, pinkGhost, orangeGhost) có bị ăn hay không
targets = [(player_x, player_y), (player_x, player_y), (player_x, player_y), (player_x, player_y)]  # Danh sách 4 tuple chứa tọa độ mục tiêu của từng ghost
redGhost_dead = False
blueGhost_dead = False
orangeGhost_dead = False
pinkGhost_dead = False
redGhost_box = False
blueGhost_box = False
orangeGhost_box = False
pinkGhost_box = False
moving = False  # Trạng thái di chuyển của Pac-Man và ghost, ban đầu là dừng (do có giai đoạn khởi động)
ghost_speeds = [2, 2, 2, 2]
startup_counter = 0  # Đếm frame cho giai đoạn khởi động (180 frame đầu tiên)
lives = 3
game_over = False
game_won = False
current_level = 0  # Theo dõi level hiện tại

class Ghost:
    def __init__(self, x_coord, y_coord, target, speed, img, direct, dead, box, id):
        self.x_pos = x_coord
        self.y_pos = y_coord
        self.center_x = self.x_pos + 22  # Tọa độ tâm của ghost
        self.center_y = self.y_pos + 22
        self.target = target
        self.speed = speed
        self.img = img
        self.direction = direct
        self.dead = dead
        self.in_box = box
        self.id = id
        self.turns, self.in_box = self.check_collisions()  # Kết quả từ check_collisions()
        self.rect = self.draw()  # Hình chữ nhật bao quanh ghost, dùng để kiểm tra va chạm

    def draw(self):
        if current_level == 0 and self.id != 0:  # Chỉ vẽ redGhost ở Level 1
            return pygame.rect.Rect((self.center_x - 18, self.center_y - 18), (36, 36))
        elif current_level == 1 and self.id != 1:  # Chỉ vẽ pinkGhost ở Level 2
            return pygame.rect.Rect((self.center_x - 18, self.center_y - 18), (36, 36))
        elif current_level == 2 and self.id != 2:  # Chỉ vẽ blueGhost ở Level 3
            return pygame.rect.Rect((self.center_x - 18, self.center_y - 18), (36, 36))
        elif current_level == 3 and self.id != 3:  # Chỉ vẽ orangeGhost ở Level 4
            return pygame.rect.Rect((self.center_x - 18, self.center_y - 18), (36, 36))
        
        if (not powerup and not self.dead) or (eaten_ghost[self.id] and powerup and not self.dead):
            screen.blit(self.img, (self.x_pos, self.y_pos))
        elif powerup and not self.dead and not eaten_ghost[self.id]:
            screen.blit(spooked_img, (self.x_pos, self.y_pos))
        else:
            screen.blit(dead_img, (self.x_pos, self.y_pos))
        ghost_rect = pygame.rect.Rect((self.center_x - 18, self.center_y - 18), (36, 36))
        return ghost_rect  # Trả về: Hình chữ nhật ghost_rect để dùng trong việc kiểm tra va chạm với Pac-Man

    # Kiểm tra xem ghost có thể rẽ ở đâu (phải, trái, lên, xuống) và xác định trạng thái trong hộp ghost
    def check_collisions(self):
        # R, L, U, D
        num1 = ((HEIGHT - 50) // 32)  # 32: Chiều cao mỗi ô trên lưới
        num2 = (WIDTH // 30)  # 30 Chiều rộng mỗi ô trên lưới
        num3 = 15  # Khoảng cách kiểm tra va chạm
        self.turns = [False, False, False, False]  # Mảng boolean cho phép rẽ (0 = phải, 1 = trái, 2 = lên, 3 = xuống)
        if 0 < self.center_x // 30 < 29:
            if level[(self.center_y - num3) // num1][self.center_x // num2] == 9:
                self.turns[2] = True
            if level[self.center_y // num1][(self.center_x - num3) // num2] < 3 \
                    or (level[self.center_y // num1][(self.center_x - num3) // num2] == 9 and (self.in_box or self.dead)):
                self.turns[1] = True
            if level[self.center_y // num1][(self.center_x + num3) // num2] < 3 \
                    or (level[self.center_y // num1][(self.center_x + num3) // num2] == 9 and (self.in_box or self.dead)):
                self.turns[0] = True
            if level[(self.center_y + num3) // num1][self.center_x // num2] < 3 \
                    or (level[(self.center_y + num3) // num1][self.center_x // num2] == 9 and (self.in_box or self.dead)):
                self.turns[3] = True
            if level[(self.center_y - num3) // num1][self.center_x // num2] < 3 \
                    or (level[(self.center_y - num3) // num1][self.center_x // num2] == 9 and (self.in_box or self.dead)):
                self.turns[2] = True

            if self.direction == 2 or self.direction == 3:
                if 12 <= self.center_x % num2 <= 18:
                    if level[(self.center_y + num3) // num1][self.center_x // num2] < 3 \
                            or (level[(self.center_y + num3) // num1][self.center_x // num2] == 9 and (self.in_box or self.dead)):
                        self.turns[3] = True
                    if level[(self.center_y - num3) // num1][self.center_x // num2] < 3 \
                            or (level[(self.center_y - num3) // num1][self.center_x // num2] == 9 and (self.in_box or self.dead)):
                        self.turns[2] = True
                if 12 <= self.center_y % num1 <= 18:
                    if level[self.center_y // num1][(self.center_x - num2) // num2] < 3 \
                            or (level[self.center_y // num1][(self.center_x - num2) // num2] == 9 and (self.in_box or self.dead)):
                        self.turns[1] = True
                    if level[self.center_y // num1][(self.center_x + num2) // num2] < 3 \
                            or (level[self.center_y // num1][(self.center_x + num2) // num2] == 9 and (self.in_box or self.dead)):
                        self.turns[0] = True

            if self.direction == 0 or self.direction == 1:
                if 12 <= self.center_x % num2 <= 18:
                    if level[(self.center_y + num3) // num1][self.center_x // num2] < 3 \
                            or (level[(self.center_y + num3) // num1][self.center_x // num2] == 9 and (self.in_box or self.dead)):
                        self.turns[3] = True
                    if level[(self.center_y - num3) // num1][self.center_x // num2] < 3 \
                            or (level[(self.center_y - num3) // num1][self.center_x // num2] == 9 and (self.in_box or self.dead)):
                        self.turns[2] = True
                if 12 <= self.center_y % num1 <= 18:
                    if level[self.center_y // num1][(self.center_x - num3) // num2] < 3 \
                            or (level[self.center_y // num1][(self.center_x - num3) // num2] == 9 and (self.in_box or self.dead)):
                        self.turns[1] = True
                    if level[self.center_y // num1][(self.center_x + num3) // num2] < 3 \
                            or (level[self.center_y // num1][(self.center_x + num3) // num2] == 9 and (self.in_box or self.dead)):
                        self.turns[0] = True
        else:
            self.turns[0] = True
            self.turns[1] = True
        if 350 < self.x_pos < 550 and 370 < self.y_pos < 480:
            self.in_box = True
        else:
            self.in_box = False
        return self.turns, self.in_box

    def move_orangeGhost(self):
        # r, l, u, d
        if self.direction == 0:
            if self.target[0] > self.x_pos and self.turns[0]:
                self.x_pos += self.speed
            elif not self.turns[0]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
            elif self.turns[0]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                if self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                else:
                    self.x_pos += self.speed
        elif self.direction == 1:
            if self.target[1] > self.y_pos and self.turns[3]:
                self.direction = 3
            elif self.target[0] < self.x_pos and self.turns[1]:
                self.x_pos -= self.speed
            elif not self.turns[1]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[1]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                if self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                else:
                    self.x_pos -= self.speed
        elif self.direction == 2:
            if self.target[0] < self.x_pos and self.turns[1]:
                self.direction = 1
                self.x_pos -= self.speed
            elif self.target[1] < self.y_pos and self.turns[2]:
                self.direction = 2
                self.y_pos -= self.speed
            elif not self.turns[2]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[2]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                else:
                    self.y_pos -= self.speed
        elif self.direction == 3:
            if self.target[1] > self.y_pos and self.turns[3]:
                self.y_pos += self.speed
            elif not self.turns[3]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[3]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                else:
                    self.y_pos += self.speed
        if self.x_pos < -30:
            self.x_pos = 900
        elif self.x_pos > 900:
            self.x_pos -= 30
        return self.x_pos, self.y_pos, self.direction

    def move_redGhost(self):
        # r, l, u, d
        if self.direction == 0:
            if self.target[0] > self.x_pos and self.turns[0]:
                self.x_pos += self.speed
            elif not self.turns[0]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
            elif self.turns[0]:
                self.x_pos += self.speed
        elif self.direction == 1:
            if self.target[0] < self.x_pos and self.turns[1]:
                self.x_pos -= self.speed
            elif not self.turns[1]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[1]:
                self.x_pos -= self.speed
        elif self.direction == 2:
            if self.target[1] < self.y_pos and self.turns[2]:
                self.direction = 2
                self.y_pos -= self.speed
            elif not self.turns[2]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
            elif self.turns[2]:
                self.y_pos -= self.speed
        elif self.direction == 3:
            if self.target[1] > self.y_pos and self.turns[3]:
                self.y_pos += self.speed
            elif not self.turns[3]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
            elif self.turns[3]:
                self.y_pos += self.speed
        if self.x_pos < -30:
            self.x_pos = 900
        elif self.x_pos > 900:
            self.x_pos -= 30
        return self.x_pos, self.y_pos, self.direction

    def move_blueGhost(self):
        # r, l, u, d
        if self.direction == 0:
            if self.target[0] > self.x_pos and self.turns[0]:
                self.x_pos += self.speed
            elif not self.turns[0]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
            elif self.turns[0]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                if self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                else:
                    self.x_pos += self.speed
        elif self.direction == 1:
            if self.target[1] > self.y_pos and self.turns[3]:
                self.direction = 3
            elif self.target[0] < self.x_pos and self.turns[1]:
                self.x_pos -= self.speed
            elif not self.turns[1]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[1]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                if self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                else:
                    self.x_pos -= self.speed
        elif self.direction == 2:
            if self.target[1] < self.y_pos and self.turns[2]:
                self.direction = 2
                self.y_pos -= self.speed
            elif not self.turns[2]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[2]:
                self.y_pos -= self.speed
        elif self.direction == 3:
            if self.target[1] > self.y_pos and self.turns[3]:
                self.y_pos += self.speed
            elif not self.turns[3]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[3]:
                self.y_pos += self.speed
        if self.x_pos < -30:
            self.x_pos = 900
        elif self.x_pos > 900:
            self.x_pos -= 30
        return self.x_pos, self.y_pos, self.direction

    def move_pinkGhost(self):
        # r, l, u, d
        if self.direction == 0:
            if self.target[0] > self.x_pos and self.turns[0]:
                self.x_pos += self.speed
            elif not self.turns[0]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
            elif self.turns[0]:
                self.x_pos += self.speed
        elif self.direction == 1:
            if self.target[1] > self.y_pos and self.turns[3]:
                self.direction = 3
            elif self.target[0] < self.x_pos and self.turns[1]:
                self.x_pos -= self.speed
            elif not self.turns[1]:
                if self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[1]:
                self.x_pos -= self.speed
        elif self.direction == 2:
            if self.target[0] < self.x_pos and self.turns[1]:
                self.direction = 1
                self.x_pos -= self.speed
            elif self.target[1] < self.y_pos and self.turns[2]:
                self.direction = 2
                self.y_pos -= self.speed
            elif not self.turns[2]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] > self.y_pos and self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[2]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                else:
                    self.y_pos -= self.speed
        elif self.direction == 3:
            if self.target[1] > self.y_pos and self.turns[3]:
                self.y_pos += self.speed
            elif not self.turns[3]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[2]:
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[3]:
                if self.target[0] > self.x_pos and self.turns[0]:
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:
                    self.direction = 1
                    self.x_pos -= self.speed
                else:
                    self.y_pos += self.speed
        if self.x_pos < -30:
            self.x_pos = 900
        elif self.x_pos > 900:
            self.x_pos -= 30
        return self.x_pos, self.y_pos, self.direction

# Thông tin bổ sung giúp người chơi theo dõi trạng thái trò chơi
def draw_misc():
    score_text = font.render(f'Score: {score}', True, 'white')
    screen.blit(score_text, (10, 920))
    if powerup:
        pygame.draw.circle(screen, 'blue', (140, 930), 15)
    for i in range(lives):
        screen.blit(pygame.transform.scale(player_images[0], (30, 30)), (650 + i * 40, 915))
    if game_over:
        pygame.draw.rect(screen, 'white', [50, 200, 800, 300], 0, 10)
        pygame.draw.rect(screen, 'dark gray', [70, 220, 760, 260], 0, 10)
        gameover_text = font.render('Game over! Space bar to restart!', True, 'red')
        screen.blit(gameover_text, (100, 300))
    if game_won:
        pygame.draw.rect(screen, 'white', [50, 200, 800, 300], 0, 10)
        pygame.draw.rect(screen, 'dark gray', [70, 220, 760, 260], 0, 10)
        gameover_text = font.render('Victory! Space bar to restart!', True, 'green')
        screen.blit(gameover_text, (100, 300))

# Kiểm tra xem Pac-Man có "ăn" được vật phẩm nào trên bản đồ hay không
def check_collisions(scor, power, power_count, eaten_ghosts):
    num1 = (HEIGHT - 50) // 32  # check_collisions
    num2 = WIDTH // 30  # Chiều rộng mỗi ô trên lưới
    if 0 < player_x < 870:
        if level[center_y // num1][center_x // num2] == 1:  # Ăn thức ăn nhỏ
            level[center_y // num1][center_x // num2] = 0
            scor += 10
        if level[center_y // num1][center_x // num2] == 2:  # Ăn thức ăn lớn
            level[center_y // num1][center_x // num2] = 0
            scor += 50
            power = True
            power_count = 0
            eaten_ghosts = [False, False, False, False]
    return scor, power, power_count, eaten_ghosts  # Các giá trị này được gán lại cho các biến toàn cục trong vòng lặp chính

def draw_board():
    num1 = ((HEIGHT - 50) // 32)
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
    num1 = (HEIGHT - 50) // 32
    num2 = (WIDTH // 30)
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
    else:
        if player_x < 450:
            runaway_x = 900
        else:
            runaway_x = 0
        if player_y < 450:
            runaway_y = 900
        else:
            runaway_y = 0
        return_target = (380, 400)
        if powerup:
            if not redGhost.dead and not eaten_ghost[0]:
                redGhost_target = (runaway_x, runaway_y)
            elif not redGhost.dead and eaten_ghost[0]:
                if 340 < redGhost_x < 560 and 340 < redGhost_y < 500:
                    redGhost_target = (400, 100)
                else:
                    redGhost_target = (player_x, player_y)
            else:
                redGhost_target = return_target
            if not blueGhost.dead and not eaten_ghost[1]:
                blueGhost_target = (runaway_x, player_y)
            elif not blueGhost.dead and eaten_ghost[1]:
                if 340 < blueGhost_x < 560 and 340 < blueGhost_y < 500:
                    blueGhost_target = (400, 100)
                else:
                    blueGhost_target = (player_x, player_y)
            else:
                blueGhost_target = return_target
            if not pinkGhost.dead:
                pinkGhost_target = (player_x, runaway_y)
            elif not pinkGhost.dead and eaten_ghost[2]:
                if 340 < pinkGhost_x < 560 and 340 < pinkGhost_y < 500:
                    pinkGhost_target = (400, 100)
                else:
                    pinkGhost_target = (player_x, player_y)
            else:
                pinkGhost_target = return_target
            if not orangeGhost.dead and not eaten_ghost[3]:
                orangeGhost_target = (450, 450)
            elif not orangeGhost.dead and eaten_ghost[3]:
                if 340 < orangeGhost_x < 560 and 340 < orangeGhost_y < 500:
                    orangeGhost_target = (400, 100)
                else:
                    orangeGhost_target = (player_x, player_y)
            else:
                orangeGhost_target = return_target
        else:
            if not redGhost.dead:
                if 340 < redGhost_x < 560 and 340 < redGhost_y < 500:
                    redGhost_target = (400, 100)
                else:
                    redGhost_target = (player_x, player_y)
            else:
                redGhost_target = return_target
            if not blueGhost.dead:
                if 340 < blueGhost_x < 560 and 340 < blueGhost_y < 500:
                    blueGhost_target = (400, 100)
                else:
                    blueGhost_target = (player_x, player_y)
            else:
                blueGhost_target = return_target
            if not pinkGhost.dead:
                if 340 < pinkGhost_x < 560 and 340 < pinkGhost_y < 500:
                    pinkGhost_target = (400, 100)
                else:
                    pinkGhost_target = (player_x, player_y)
            else:
                pinkGhost_target = return_target
            if not orangeGhost.dead:
                if 340 < orangeGhost_x < 560 and 340 < orangeGhost_y < 500:
                    orangeGhost_target = (400, 100)
                else:
                    orangeGhost_target = (player_x, player_y)
            else:
                orangeGhost_target = return_target
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

# Quản lý thời gian và trạng thái của power-up khi Pac-Man ăn điểm lớn
def manage_powerup():
    global powerup, power_counter, eaten_ghost
    if powerup and power_counter < 600:
        power_counter += 1
    elif powerup and power_counter >= 600:
        power_counter = 0
        powerup = False
        eaten_ghost = [False, False, False, False]

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
    if powerup:
        ghost_speeds = [1, 1, 1, 1]
    else:
        ghost_speeds = [2, 2, 2, 2]
    if eaten_ghost[0]:
        ghost_speeds[0] = 2
    if eaten_ghost[1]:
        ghost_speeds[1] = 2
    if eaten_ghost[2]:
        ghost_speeds[2] = 2
    if eaten_ghost[3]:
        ghost_speeds[3] = 2
    if redGhost_dead:
        ghost_speeds[0] = 4
    if blueGhost_dead:
        ghost_speeds[1] = 4
    if pinkGhost_dead:
        ghost_speeds[2] = 4
    if orangeGhost_dead:
        ghost_speeds[3] = 4

def check_game_won():
    global game_won
    game_won = True
    for i in range(len(level)):
        if 1 in level[i] or 2 in level[i]:
            game_won = False

# Hiển thị trạng thái hiện tại của trò chơi (bản đồ, Pac-Man, UI)
def draw_game_elements():
    global center_x, center_y, player_circle
    screen.fill('black')
    draw_board()
    center_x = player_x + 23
    center_y = player_y + 24
    # Vẽ một vòng tròn đen (bán kính 20, độ dày 2) để đại diện cho Pac-Man trong kiểm tra va chạm
    player_circle = pygame.draw.circle(screen, 'black', (center_x, center_y), 20, 2)
    draw_player()
    draw_misc()

# Di chuyển Pac-Man và các ghost
def move_characters():
    global player_x, player_y, redGhost_x, redGhost_y, redGhost_direction, blueGhost_x, blueGhost_y, blueGhost_direction
    global pinkGhost_x, pinkGhost_y, pinkGhost_direction, orangeGhost_x, orangeGhost_y, orangeGhost_direction, turns_allowed
    turns_allowed = check_position(center_x, center_y)
    if moving:
        player_x, player_y = move_player(player_x, player_y)
        if current_level == 0:  # Level 1: Chỉ redGhost di chuyển
            if not redGhost_dead and not redGhost.in_box:
                redGhost_x, redGhost_y, redGhost_direction = redGhost.move_redGhost()
        if current_level == 1:  # Level 2: Chỉ pinkGhost di chuyển
            if not pinkGhost_dead and not pinkGhost.in_box:
                pinkGhost_x, pinkGhost_y, pinkGhost_direction = pinkGhost.move_pinkGhost()    
        if current_level == 2:  # Level 3: Chỉ blueGhost di chuyển
            if not blueGhost_dead and not blueGhost.in_box:
                blueGhost_x, blueGhost_y, blueGhost_direction = blueGhost.move_blueGhost()
        if current_level == 3:  # Level 4: Chỉ orangeGhost di chuyển
            if not orangeGhost_dead and not orangeGhost.in_box:
                orangeGhost_x, orangeGhost_y, orangeGhost_direction = orangeGhost.move_redGhost()
                
        else:  # Các level khác: Tất cả ghost di chuyển
            if not redGhost_dead and not redGhost.in_box:
                redGhost_x, redGhost_y, redGhost_direction = redGhost.move_redGhost()
            if not pinkGhost_dead and not pinkGhost.in_box:
                pinkGhost_x, pinkGhost_y, pinkGhost_direction = pinkGhost.move_pinkGhost()
            if not blueGhost_dead and not blueGhost.in_box:
                blueGhost_x, blueGhost_y, blueGhost_direction = blueGhost.move_blueGhost()
            if not orangeGhost_dead and not orangeGhost.in_box:
                orangeGhost_x, orangeGhost_y, orangeGhost_direction = orangeGhost.move_orangeGhost()

# Xử lý khi Pac-Man ăn điểm nhỏ hoặc lớn
def handle_point_collisions():
    global score, powerup, power_counter, eaten_ghost
    score, powerup, power_counter, eaten_ghost = check_collisions(score, powerup, power_counter, eaten_ghost)

# Đặt lại trạng thái trò chơi khi Pac-Man mất mạng
def reset_game_state():
    global lives, startup_counter, powerup, power_counter, player_x, player_y, direction, direction_command
    global redGhost_x, redGhost_y, redGhost_direction, blueGhost_x, blueGhost_y, blueGhost_direction, pinkGhost_x, pinkGhost_y, pinkGhost_direction
    global orangeGhost_x, orangeGhost_y, orangeGhost_direction, eaten_ghost, redGhost_dead, blueGhost_dead, orangeGhost_dead, pinkGhost_dead
    lives -= 1
    startup_counter = 0
    powerup = False
    power_counter = 0
    player_x = 450
    player_y = 663
    direction = 0
    direction_command = 0
    redGhost_x = 56
    redGhost_y = 58
    redGhost_direction = 0
    blueGhost_x = 800
    blueGhost_y = 58
    blueGhost_direction = 2
    pinkGhost_x = 56
    pinkGhost_y = 820
    pinkGhost_direction = 2
    orangeGhost_x = 800
    orangeGhost_y = 798
    orangeGhost_direction = 2
    eaten_ghost = [False, False, False, False]
    redGhost_dead = False
    blueGhost_dead = False
    orangeGhost_dead = False
    pinkGhost_dead = False

# Xử lý va chạm giữa Pac-Man và ghost khi không có power-up
def handle_ghost_collision_no_powerup():
    global game_over, moving, startup_counter
    if not powerup:
        if player_circle.colliderect(blueGhost.rect) and not blueGhost.dead or \
            player_circle.colliderect(pinkGhost.rect) and not pinkGhost.dead or \
            player_circle.colliderect(redGhost.rect) and not redGhost.dead or \
            player_circle.colliderect(orangeGhost.rect) and not orangeGhost.dead:
            if lives > 0:
                reset_game_state()
            else:
                game_over = True
                moving = False
                startup_counter = 0

# Xử lý va chạm giữa Pac-Man và ghost khi có power-up
def handle_ghost_collision_powerup():
    global game_over, moving, redGhost_dead, blueGhost_dead, pinkGhost_dead, orangeGhost_dead, eaten_ghost, score,startup_counter
    if powerup:
        if player_circle.colliderect(redGhost.rect):
            if eaten_ghost[0] and not redGhost.dead:
                if lives > 0:
                    reset_game_state()
                else:
                    game_over = True
                    moving = False
                    startup_counter = 0
            elif not redGhost.dead and not eaten_ghost[0]:
                redGhost_dead = True
                eaten_ghost[0] = True
                score += (2 ** eaten_ghost.count(True)) * 100
        if player_circle.colliderect(blueGhost.rect):
            if eaten_ghost[0] and not blueGhost.dead:
                if lives > 0:
                    reset_game_state()
                else:
                    game_over = True
                    moving = False
                    startup_counter = 0
            elif not blueGhost.dead and not eaten_ghost[0]:
                blueGhost_dead = True
                eaten_ghost[0] = True
                score += (2 ** eaten_ghost.count(True)) * 100
        if player_circle.colliderect(pinkGhost.rect):
            if eaten_ghost[0] and not pinkGhost.dead:
                if lives > 0:
                    reset_game_state()
                else:
                    game_over = True
                    moving = False
                    startup_counter = 0
            elif not pinkGhost.dead and not eaten_ghost[0]:
                pinkGhost_dead = True
                eaten_ghost[0] = True
                score += (2 ** eaten_ghost.count(True)) * 100
        if player_circle.colliderect(orangeGhost.rect):
            if eaten_ghost[0] and not orangeGhost.dead:
                if lives > 0:
                    reset_game_state()
                else:
                    game_over = True
                    moving = False
                    startup_counter = 0
            elif not orangeGhost.dead and not eaten_ghost[0]:
                orangeGhost_dead = True
                eaten_ghost[0] = True
                score += (2 ** eaten_ghost.count(True)) * 100

# Xử lý các sự kiện từ người chơi (phím nhấn, thoát game)
def handle_events():
    global run, direction_command, powerup, power_counter, lives, startup_counter, player_x, player_y, direction
    global redGhost_x, redGhost_y, redGhost_direction, blueGhost_x, blueGhost_y, blueGhost_direction, pinkGhost_x, pinkGhost_y, pinkGhost_direction
    global orangeGhost_x, orangeGhost_y, orangeGhost_direction, eaten_ghost, redGhost_dead, blueGhost_dead, orangeGhost_dead, pinkGhost_dead
    global score, level, game_over, game_won
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
                powerup = False
                power_counter = 0
                lives = 3
                startup_counter = 0
                player_x = 450
                player_y = 663
                direction = 0
                direction_command = 0
                redGhost_x = 56
                redGhost_y = 58
                redGhost_direction = 0
                blueGhost_x = 800
                blueGhost_y = 58
                blueGhost_direction = 2
                pinkGhost_x = 56
                pinkGhost_y = 820
                pinkGhost_direction = 2
                orangeGhost_x = 800
                orangeGhost_y = 798
                orangeGhost_direction = 2
                eaten_ghost = [False, False, False, False]
                redGhost_dead = False
                blueGhost_dead = False
                orangeGhost_dead = False
                pinkGhost_dead = False
                score = 0
                level = copy.deepcopy(levels[current_level])
                game_over = False
                game_won = False
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
    if current_level == 5:  # Chỉ cập nhật hướng ở level Level 6
        if direction_command == 0 and turns_allowed[0]:
            direction = 0
        if direction_command == 1 and turns_allowed[1]:
            direction = 1
        if direction_command == 2 and turns_allowed[2]:
            direction = 2
        if direction_command == 3 and turns_allowed[3]:
            direction = 3


# Hồi sinh ghost khi chúng về đến hộp trung tâm
def revive_ghosts():
    global redGhost_dead, blueGhost_dead, pinkGhost_dead, orangeGhost_dead

    if current_level == 5:  # Các ghost chỉ hồi sinh ở level 6
        if blueGhost.in_box and blueGhost_dead:
            blueGhost_dead = False
        if pinkGhost.in_box and pinkGhost_dead:
            pinkGhost_dead = False
        if orangeGhost.in_box and orangeGhost_dead:
            orangeGhost_dead = False
        if redGhost.in_box and redGhost_dead:
            redGhost_dead = False

def update_display():
    pygame.display.flip()

def show_menu():
    menu_running = True
    selected_level = 0
    font = pygame.font.Font('freesansbold.ttf', 40)
    
    while menu_running:
        screen.fill('black')
        title = font.render('Pac-Man Menu', True, 'yellow')
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))
        
        for i in range(6):  # 6 level
            color = 'white' if i != selected_level else 'yellow'
            level_text = font.render(f'Level {i + 1}', True, color)
            screen.blit(level_text, (WIDTH // 2 - level_text.get_width() // 2, 150 + i * 60))
        
        instruction = font.render('Use UP/DOWN to select, ENTER to start', True, 'white')
        screen.blit(instruction, (WIDTH // 2 - instruction.get_width() // 2, 550))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_level = max(0, selected_level - 1)
                elif event.key == pygame.K_DOWN:
                    selected_level = min(5, selected_level + 1)
                elif event.key == pygame.K_RETURN:
                    menu_running = False
    
    return selected_level

# Gọi menu trước khi vào trò chơi
current_level = show_menu()
level = copy.deepcopy(levels[current_level])  # Gán level được chọn

# Vòng lặp chính đã sửa
run = True
while run:
    update_timer_and_animation()
    manage_powerup()
    manage_startup()
    update_ghost_speeds()
    check_game_won()
    
    # Cập nhật sự kiện và hướng trước khi vẽ hoặc di chuyển
    handle_events()
    update_player_direction()
    
    # Vẽ các thành phần và tính toán center_x, center_y
    draw_game_elements()
    
    # Tạo các đối tượng ghost với targets ban đầu
    redGhost = Ghost(redGhost_x, redGhost_y, targets[0], ghost_speeds[0], redGhost_img, redGhost_direction, redGhost_dead, redGhost_box, 0)
    blueGhost = Ghost(blueGhost_x, blueGhost_y, targets[1], ghost_speeds[1], blueGhost_img, blueGhost_direction, blueGhost_dead, blueGhost_box, 1)
    pinkGhost = Ghost(pinkGhost_x, pinkGhost_y, targets[2], ghost_speeds[2], pinkGhost_img, pinkGhost_direction, pinkGhost_dead, pinkGhost_box, 2)
    orangeGhost = Ghost(orangeGhost_x, orangeGhost_y, targets[3], ghost_speeds[3], orangeGhost_img, orangeGhost_direction, orangeGhost_dead, orangeGhost_box, 3)
    
    # Cập nhật targets sau khi tạo ghost
    targets = get_targets(redGhost_x, redGhost_y, blueGhost_x, blueGhost_y, pinkGhost_x, pinkGhost_y, orangeGhost_x, orangeGhost_y)
    
    # Di chuyển nhân vật
    move_characters()
    
    # Xử lý va chạm và các logic khác
    handle_point_collisions()
    handle_ghost_collision_no_powerup()
    handle_ghost_collision_powerup()
    revive_ghosts()
    
    # Cập nhật màn hình
    update_display()

pygame.quit()