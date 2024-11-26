from REMOLib import *
from typing import List




class Particle(graphicObj):
    """단일 파티클을 표현하는 클래스"""
    # 크기별 서피스 캐시
    _surface_cache = {}
    _max_cache_size = 10000  # 최대 캐시 크기
    
    def __init__(self, pos: RPoint, velocity: RPoint, lifetime: float, 
                 size: float, color: tuple, alpha: int = 255, 
                 gravity: float = 0, fade: bool = True):
        size = round(size)  # 크기를 정수로 반올림하여 캐시 효율 향상
        super().__init__(pygame.Rect(pos.x, pos.y, size, size))
        self.velocity = velocity
        self.lifetime = lifetime
        self.birth_time = time.time()
        self.original_size = size
        self.color = color
        self.original_alpha = alpha
        self.gravity = gravity
        self.fade = fade
        
        # 캐시된 서피스 사용 또는 생성
        cache_key = (size, color)
        if cache_key not in self._surface_cache:
            if len(self._surface_cache) >= self._max_cache_size:
                # 가장 오래된 캐시 제거
                self._surface_cache.pop(next(iter(self._surface_cache)))
            
            surface = REMOGame._lastStartedWindow.surface_pool.get_surface((size,size))
            pygame.draw.circle(
                surface,
                color,
                (size/2, size/2),
                size/2
            )
            self._surface_cache[cache_key] = surface
            
        self.graphic_n = self._surface_cache[cache_key]
        self.graphic = self._surface_cache[cache_key]
        
    def update(self) -> bool:
        current_time = time.time()
        age = current_time - self.birth_time
        
        if age >= self.lifetime:
            return False
            
        # 위치 업데이트 (정수로 반올림하여 렌더링 최적화)
        self.velocity.y += self.gravity
        self.pos += self.velocity
        
        # 크기와 투명도 업데이트 (크기 변경 최소화)
        if self.fade:
            life_ratio = 1 - (age / self.lifetime)
            self.alpha = int(self.original_alpha * life_ratio)
            new_size = round(self.original_size * life_ratio)  # 정수로 반올림
            
            if new_size != self.rect.width:  # 크기가 실제로 변경될 때만 업데이트
                self.rect.width = self.rect.height = new_size
                
                # 캐시된 서피스 사용
                cache_key = (new_size, self.color)
                if cache_key not in self._surface_cache and new_size > 0:
                    if len(self._surface_cache) >= self._max_cache_size:
                        self._surface_cache.pop(next(iter(self._surface_cache)))
                        
                    surface = REMOGame._lastStartedWindow.surface_pool.get_surface((new_size,new_size))
                    pygame.draw.circle(
                        surface,
                        self.color,
                        (new_size/2, new_size/2),
                        new_size/2
                    )
                    self._surface_cache[cache_key] = surface
                
                if new_size > 0:
                    self.graphic = self._surface_cache[cache_key]
            
        return True

class ParticleSystem(graphicObj):
    def __init__(self, pos: RPoint, rect: pygame.Rect = None):
        super().__init__(rect or pygame.Rect(pos.x, pos.y, 1, 1))
        self.particles: List[Particle] = []
        self.emitting = True
        self._max_particles = 200  # 최대 파티클 수 제한
        
    def emit(self, count: int, **kwargs):
        """새로운 파티클 생성"""
        count = min(count, self._max_particles - len(self.particles))  # 최대 파티클 수 제한
        for _ in range(count):
            velocity = RPoint(
                random.uniform(*kwargs.get('velocity_range', ((-2, 2), (-2, 2)))[0]),
                random.uniform(*kwargs.get('velocity_range', ((-2, 2), 
                
                
                
                
                (-2, 2)))[1])
            )
            
            if 'color_range' in kwargs:
                color = (
                    random.randint(*kwargs['color_range'][0]),
                    random.randint(*kwargs['color_range'][1]),
                    random.randint(*kwargs['color_range'][2])
                )
            else:
                color = (255, 255, 255)
                
            particle = Particle(
                pos=RPoint(self.pos.x, self.pos.y),
                velocity=velocity,
                lifetime=random.uniform(*kwargs.get('lifetime_range', (0.5, 2.0))),
                size=random.uniform(*kwargs.get('size_range', (3, 8))),
                color=color,
                alpha=random.randint(*kwargs.get('alpha_range', (128, 255))),
                gravity=kwargs.get('gravity', 0.1),
                fade=kwargs.get('fade', True)
            )
            particle.setParent(self)
            self.particles.append(particle)

    def update(self):
        """파티클 시스템 업데이트"""
        # 죽은 파티클 제거 및 부모-자식 관계 정리
        alive_particles = []
        for particle in self.particles:
            if particle.update():
                alive_particles.append(particle)
            else:
                particle.setParent(None)  # 부모-자식 관계 해제
        self.particles = alive_particles

    def clear(self):
        """모든 파티클 제거"""
        for particle in self.particles:
            particle.setParent(None)  # 부모-자식 관계 해제
        self.particles.clear()

    def stop_emission(self):
        """파티클 방출 중지"""
        self.emitting = False
        
    def start_emission(self):
        """파티클 방출 시작"""
        self.emitting = True

    # 폭발 효과
    def create_explosion(self,pos):
        self.pos = pos
        self.emit(
            count=50,
            velocity_range=((-5, 5), (-5, 5)),
            lifetime_range=(0.5, 1.5),
            size_range=(5, 15),
            color_range=((200, 255), (100, 200), (0, 100)),
            gravity=0.2
        )

    # 연기 효과
    def create_smoke(self,pos):
        self.pos = pos
        self.emit(
            count=20,
            velocity_range=((-1, 1), (-3, -1)),
            lifetime_range=(1.0, 2.0),
            size_range=(10, 20),
            color_range=((100, 150), (100, 150), (100, 150)),
            alpha_range=(50, 150),
            gravity=-0.1
        )

    # 반짝이 효과
    def create_sparkle(self,pos):
        self.pos = pos
        self.emit(
            count=10,
            velocity_range=((-2, 2), (-2, 2)),
            lifetime_range=(0.3, 0.7),
            size_range=(2, 4),
            color_range=((200, 255), (200, 255), (100, 255)),
            gravity=0
        )




#게임 오브젝트들을 선언하는 곳입니다.
class Obj:
    None

class mainScene(Scene):
    def initOnce(self):
        self.particle_system = ParticleSystem(RPoint(100, 100))
        test_buttons = []
        for i in range(30):
            test_buttons.append(f"Test {i}")
        self.buttons = buttonLayout(test_buttons,pos=RPoint(600,100))
        return
    def init(self):
        return
    def update(self):
        for _ in range(100):
            self.particle_system.create_sparkle(RPoint(300, 300))
        self.particle_system.update()
        self.buttons.update()
        return
    def draw(self):
        self.particle_system.draw()
        self.buttons.draw()
        return


class defaultScene(Scene):
    def initOnce(self):
        return
    def init(self):
        return
    def update(self):
        return
    def draw(self):
        return

class Scenes:
    mainScene = mainScene()


if __name__=="__main__":
    #Screen Setting
    window = REMOGame(window_resolution=(1920,1080),screen_size=(2560,1440),fullscreen=False,caption="DEFAULT")
    window.setCurrentScene(Scenes.mainScene)
    window.run()

    # Done! Time to quit.
