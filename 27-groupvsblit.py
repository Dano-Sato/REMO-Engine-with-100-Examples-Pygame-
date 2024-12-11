import pygame
import time
from pygame.sprite import Sprite, Group

# 초기화
pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

# 스프라이트 클래스 정의
class Block(Sprite):
    def __init__(self, x, y, color):
        super().__init__()
        self.image = pygame.Surface((100, 100))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))

# 스프라이트 생성
num_sprites = 10000
sprites_group = Group()
sprites_list = []

for i in range(num_sprites):
    x, y = (i % 20) * 60, (i // 20) * 60
    block = Block(x, y, (255, 0, 0))
    sprites_group.add(block)  # Group에 추가
    sprites_list.append(block)  # 리스트에 추가

# Group.draw() 테스트 함수
def draw_with_group():
    surface = pygame.Surface((800, 600))
    start_time = time.time()
    sprites_group.draw(surface)  # Group.draw() 사용
    pygame.display.flip()
    return time.time() - start_time

# 일반 blit() 테스트 함수
def draw_with_blit():
    surface = pygame.Surface((800, 600))
    start_time = time.time()
    for sprite in sprites_list:
        surface.blit(sprite.image, sprite.rect)  # 개별 blit 호출
    pygame.display.flip()
    return time.time() - start_time

# 테스트 루프
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))

    # Group.draw() 실행 시간 측정
    group_time = draw_with_group()

    # 일반 blit() 실행 시간 측정
    screen.fill((0, 0, 0))  # 화면 초기화
    blit_time = draw_with_blit()

    # 결과 출력
    print(f"Group.draw() Time: {group_time:.6f} seconds")
    print(f"Individual blit() Time: {blit_time:.6f} seconds")

    # 프레임 조절
    clock.tick(30)

pygame.quit()