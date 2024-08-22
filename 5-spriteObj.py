from REMOLib import *

##TODO: dialogObj, inventoryObj,cardObj, cardLayout를 만들어보자.
##setCursor 메소드 만들어보자.


class viewportObj(graphicObj):
    '''
    그리기 영역을 제한하는 뷰포트 오브젝트입니다.
    rect 영역 밖의 그림은 그려지지 않습니다.
    그리기 영역이 제한되는 오브젝트는 childs[0]에 포함된 오브젝트뿐입니다.
    '''
    def _getCache(self):
        if id(self) in Rs.graphicCache:
            try:
                return Rs.graphicCache[id(self)]
            except:
                pass

        # id가 없으므로 childs의 재귀적 union을 통해 전체 영역을 계산
        r = self.boundary
        
        bp = RPoint(r.x,r.y) #position of boundary
        cache = pygame.Surface((r.w,r.h),pygame.SRCALPHA,32).convert_alpha()

        depth_excluded = list(set(self.childs.keys())-self._hidedDepth)
        depth_excluded.sort()

        negative_depths = []
        positive_depths = []
        for d in depth_excluded:
            if d<0:
                negative_depths.append(d)
            else:
                positive_depths.append(d)
            


        ##depth가 음수인 차일드들을 먼저 그린다.
        for depth in negative_depths:
            l = self.childs[depth]
            for c in l:
                ccache,cpos = c._getCache()
                p = cpos-bp
                cache.blit(ccache,p.toTuple(),special_flags=pygame.BLEND_ALPHA_SDL2)

        cache.blit(self.graphic,(self.geometryPos-bp).toTuple())

        ##depth가 양수인 차일드들을 그린다.
        for depth in positive_depths:
            l = self.childs[depth]
            for c in l:
                ccache,cpos = c._getCache()
                p = cpos-bp
                cache.blit(ccache,p.toTuple(),special_flags=pygame.BLEND_ALPHA_SDL2)

        cache.set_alpha(self.alpha)
        return [cache,bp]
        None



#게임 오브젝트들을 선언하는 곳입니다.
class Obj:
    None

class charaMode(Enum):
    idle = 0
    walkRight = 1
    walkLeft = 2
    attack = 3

class mainScene(Scene):
    def initOnce(self):

        ##게임 종료 다이얼로그
        self.escDialog = dialogObj(pygame.Rect(200,200,600,250),"-주의-","게임을 종료합니까?",["Yes","No"],color=Cs.dark(Cs.grey),spacing=20)
        self.escDialog["Yes"].connect(lambda:REMOGame.exit())
        self.escDialog["Yes"].color = Cs.dark(Cs.red)
        def No():
            self.escDialog.hide()
        self.escDialog["No"].connect(No)        

        self.charaSetting = {"scale":3,"frameDuration":1000/10}
        self.charaSprite = spriteObj("Idle_KG_2.png",pos=(50,50),sheetMatrix=(1,4),scale=3,frameDuration=1000/10)
        self.charaSprite.colorize(Cs.red)
        self.charaSprite.center = Rs.screen.get_rect().center
        self.charaMode = charaMode.idle

        return
    def init(self):
        return
    def update(self):
        speed = 5

        if Rs.userPressing(pygame.K_a):
            self.charaSprite.scale+=0.1
        elif Rs.userPressing(pygame.K_s):
            self.charaSprite.angle+=1
            print(self.charaSprite.angle)


        if Rs.userPressing(pygame.K_z):
            if self.charaMode != charaMode.attack:
                self.charaSprite = spriteObj("Attack_KG_2.png",pos=self.charaSprite.pos,sheetMatrix=(1,6),scale=3,frameDuration=1000/10)
                self.charaMode = charaMode.attack
        elif Rs.userPressing(pygame.K_RIGHT):
            self.charaSprite.pos += Rs.Point(speed,0)
            if self.charaMode != charaMode.walkRight:
                self.charaSprite = spriteObj("Walking_KG_2.png",pos=self.charaSprite.pos ,sheetMatrix=(1,7),scale=3,frameDuration=1000/10)
                self.charaMode = charaMode.walkRight
        elif Rs.userPressing(pygame.K_LEFT):
            self.charaSprite.pos -= Rs.Point(speed,0)
            if self.charaMode != charaMode.walkLeft:
                self.charaSprite = spriteObj("Walking_KG_2.png",pos=self.charaSprite.pos,sheetMatrix=(1,7),scale=3,frameDuration=1000/10)
                self.charaMode = charaMode.walkLeft
        else:
            if self.charaMode != charaMode.idle:
                self.charaSprite = spriteObj("Idle_KG_2.png",pos=self.charaSprite.pos,sheetMatrix=(1,4),scale=3,frameDuration=1000/10)
                self.charaMode = charaMode.idle

        self.charaSprite.update()

        #ESC키를 누르면 게임 종료 다이얼로그가 나타난다.
        if Rs.userJustPressed(pygame.K_ESCAPE):
            if not self.escDialog.isShown():
                self.escDialog.center = Rs.Point(Rs.screen.get_rect().center)
                self.escDialog.show()
            else:
                self.escDialog.hide()

        #게임 종료 다이얼로그를 드래그할 수 있다.
        if self.escDialog.isShown():
            Rs.dragEventHandler(self.escDialog)

        return
    def draw(self):
        self.charaSprite.draw()
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
    window = REMOGame(window_resolution=(1920,1080),screen_size=(1920,1080),fullscreen=False,caption="DEFAULT")
    window.setCurrentScene(Scenes.mainScene)
    window.run()

    # Done! Time to quit.
