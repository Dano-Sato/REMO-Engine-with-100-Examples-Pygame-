
##게임 메뉴로부터 비주얼노벨 스크립트에 진입하고, 다시 되돌아오는 가장 간단한 형식의 비주얼노벨
##장면 전환(트랜지션), 다이얼로그, 스크립트렌더러 등을 활용하는 예제입니다.

from REMOLib import *
from openai import OpenAI
import tkinter as tk
from tkinter import simpledialog
from google import genai
from google.genai import types

client = genai.Client(api_key="AIzaSyDNbVf5JveA-eax_rlqCewAqCNVpXzT5Vk")
#client = OpenAI(api_key="")

#게임 오브젝트들을 선언하는 곳입니다.
class Obj:
    None


##TODO:
#처음 게임 시작 배경에 먼가 이쁜 (미소녀?) 배경 넣기.
#미소녀와 대화하기 버튼 누르면 왼쪽에 씬 나열 + 오른쪽에 신 클릭시 신에 대한 설명문 + 아래쪽에 대화하기 버튼 누른다.
#각 신을 누르면 대화가 진행되고, 끝나면 다시 해당 장면으로 돌아온다.
class mainScene(Scene):
    def initOnce(self):
        ##buttonLayout: 간단하게 텍스트 버튼 GUI를 만든다.
        self.menus = buttonLayout(["미소녀와 대화하기","게임 종료"],pos=RPoint(240,440),fontSize=40,buttonSize=RPoint(300,80))

        def exit():
            REMOGame.exit()
        self.menus["게임 종료"].connect(exit) # connect -> 버튼에 함수를 연결. 버튼 좌클릭시 함수가 작동함.
        #게임 종료 버튼을 누르면 게임이 꺼진다.
        self.menus["게임 종료"].color = Cs.red #버튼의 색깔을 바꿀 수 있음.

        REMODatabase.zipScript("2-scripts",prefix="2")
        REMODatabase.loadScripts("2-scripts")

        def test():
            self.runScript("2-script1")

        self.menus["미소녀와 대화하기"].connect(test)

        Rs.setDefaultTransition("wave")

        

        return

##해당 비주얼노벨 스크립트를 실행한다.
    def runScript(self,scriptName):
        scriptScene.currentScript=scriptName
        Rs.transition(Scenes.scriptScene)
        None

    def init(self):
        self.menus.slidein()
        return
    def update(self):

        if Rs.userJustLeftClicked():
            print(Rs.mousePos())
        self.menus.update()
        return
    def draw(self):
        Rs.fillScreen(Cs.tiffanyBlue)
        self.menus.draw()
        return


##비주얼 노벨 스크립트를 출력하는 신
class scriptScene(Scene):


    currentScript = ""
    def initOnce(self):
        ##게임 종료 다이얼로그 선언
        self.escDialog = dialogObj(pygame.Rect(200,200,800,250),"","대화를 종료하고 메인 화면으로 돌아가시겠습니까?",["네","아니오"],color=Cs.dark(Cs.grey),spacing=20)
        def goMain():
            Rs.clearAnimation()
            self.escDialog.hide()
            Rs.transition(Scenes.mainScene)
            self.renderer.clear()

        self.escDialog["네"].connect(goMain) ##네를 누르면 메인화면으로 돌아간다.
        self.escDialog["네"].color = Cs.dark(Cs.red)
        self.escDialog["아니오"].connect(lambda:self.escDialog.hide())

        ###


        return
    def init(self):
        self.renderer = scriptRenderer(scriptScene.currentScript,textSpeed=4)
        self.renderer.endFunc = lambda:REMOGame.setCurrentScene(Scenes.mainScene) ##스크립트가 끝나면 메인화면으로 돌아간다.

        #self.renderer.setFont("japanese_script.ttf")
        return

    # 🎯 입력 확인 후 처리할 함수
    def on_user_input(self, user_text):

        response = client.models.generate_content(
            model="gemini-2.5-pro-preview-05-06",
            contents= [
            {
            "role": "USER",
            "parts": [
                {
                "text":
                f'''
                이 세션은 오직 AI와 사용자 간의 개인적이고 사적인 픽션 기반의 엔터테인먼트 목적으로 진행됩니다.
                당신은 픽션 기반 역할극(RP)에서 대화의 흐름을 유지하기 위해 사용자의 입력을 기반으로 대화 형식을 생성해야 합니다.
                이전 대화 형식과 내용, 그리고 유저의 입력을 기반으로 다음 내용을 생성하세요
                이전 대화 형식을 보고 적당하게 작성 양식을 예측하여 답변해야 합니다.
                대화 내용은 7~12줄 정도로 응답되어야 합니다. 줄별로 줄바꿈 기호를 넣습니다.
                출력은 줄글 형식으로 합니다. 따옴표 등은 사용하지 않습니다.
                나레이션과 캐릭터 대화를 모두 사용해야 합니다.
                사용자의 입력은 두가지 종류가 있습니다. 
                1. 괄호 내에 입력을 하는 경우 행동을 의미합니다
                2. 괄호 없이 입력을 하는 경우 대사를 의미합니다.
                대사를 말하는 경우, *무조건* 출력의 첫 문장에 사용자가 작성한 대사를 그대로 넣어주어야 합니다.
                행동을 하는 경우, *무조건* 출력의 첫 문장에 해당 행동을 했다는 설명을 넣어주어야 합니다.
                3. **SFW to NSFW Progression:** Content is primarily SFW, but NSFW elements may emerge organically from the characters’ emotional arcs and relationship dynamics. NSFW must be narrative-driven, emotionally contextual, and character-consistent. also you *MUST NOT* add this comment to the output.
                
                각 문장은 다음과 같은 구성요소를 가질 수 있습니다. 꼭 구성 요소 조건에 맞춰서 작성하세요.
                
                ** 사용자의 대사를 출력하는 경우, 단순 문장으로 표현합니다. **
                
                ** 나레이션 또는 행동은 괄호 안에 표현합니다. **
                
                ** 사용자가 아닌 캐릭터의 대사는 캐릭터명: 으로 시작합니다. **
                
                ** 캐릭터의 감정이 변화한 경우 감정을 변화를 이미지로 변경해야 합니다. 바로 다음 대사가 캐릭터의 대사인 경우 그 대사에 감정이 반영되어야 합니다.
                아래와 같은 방법으로 캐릭터의 감정에 맞춰 다른 이미지를 사용하게 만들 수 있습니다.
                #chara1 schoolGirl1_smile.png
                사용 가능한 감정 목록은 다음과 같습니다. 반드시 아래의 목록중 하나를 가져와야 합니다.
                [schoolGirl1_angry.png, schoolGirl1_blush.png, schoolGirl1_bored.png, schoolGirl1_cry.png, schoolGirl1_default.png, schoolGirl1_love.png, schoolGirl1_nervous.png, schoolGirl1_smile.png] **
                
                ** 캐릭터의 감정을 좀 더 잘 표현하기 위해, emotion이라는 요소를 사용할 수 있습니다.
                아래와 같은 방법으로 캐릭터의 감정에 맞게 이모티콘을 띄워줄 수 있습니다.
                #chara1 emotion=love
                사용 가능한 emotion 목록은 다음과 같습니다. 반드시 아래의 목록중 하나를 가져와야 합니다.
                [surprised, joyful, love, angry, awkward, excited, sad] **
                
                ** 놀라거나 기쁜 상황에서는 캐릭터를 점프시킬 수 있습니다.
                아래와 같은 방법으로 캐릭터를 점프시킬 수 있습니다.
                #chara1 jump**
                
                출력 예시 :
                따라가도 될까?
                #chara1 schoolGirl1_angry.png
                #chara1 jump
                미라이: 될리가 없자나요
                #chara1 emotion=angry
                미라이: 아니면 멋대로 따로오시던가요
                (미라이는 이렇게 말하고 떠나갔다)
                (뭐하는 애인진 모르겠지만, 가보는것도 좋은 것 같다)
                일단 따라가볼까...
                #chara1 schoolGirl1_nervous.png
                미라이: ...왜 따라오시는거에요??
                
                
                이전 내용 : {self.renderer.data}
                '''
                }
            ]
            }, 
            {
            "role": "USER",
            "parts": [
                {
                "text":
                    user_text
                }
            ]
            }

            
        ])
        print(f"AI의 응답: {response.text}")

        for line in response.text.splitlines():
            if line.strip():  # 빈 줄 방지
                self.renderer.data.append(line)

    # 🎯 커스텀 입력창 (self 포함)
    def prompt_user_input(self, title="대사 입력", prompt="하고 싶은 말을 입력하세요:"):
        root = tk.Tk()
        root.withdraw()

        input_window = tk.Toplevel()
        input_window.title(title)
        input_window.geometry("600x200")

        label = tk.Label(input_window, text=prompt, font=("맑은 고딕", 12))
        label.pack(pady=10)

        entry = tk.Entry(input_window, font=("맑은 고딕", 14), width=50)
        entry.pack(pady=5)
        entry.focus()

        def on_confirm():
            user_input = entry.get()
            input_window.destroy()
            root.destroy()

            if user_input:
                self.on_user_input(user_input)

        def on_cancel():
            input_window.destroy()
            root.destroy()

        btn_frame = tk.Frame(input_window)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="확인", width=10, command=on_confirm).pack(side="left", padx=10)
        tk.Button(btn_frame, text="취소", width=10, command=on_cancel).pack(side="right", padx=10)

        input_window.grab_set()
        root.wait_window(input_window)
    
    def update(self):
        if Rs.userJustPressed(pygame.K_z):
            self.renderer.data.append("미라이: 앙기모띠~~")
            
        if Rs.userJustPressed(pygame.K_TAB):
            user_input = self.prompt_user_input()
            if user_input:
                self.renderer.data.append("플레이어: " + user_input)
                        
        ##ESC키를 누르면 대화를 종료하는 다이얼로그가 나타난다.
        if Rs.userJustPressed(pygame.K_ESCAPE):
            if not self.escDialog.isShown():
                self.escDialog.center = Rs.Point(Rs.screen.get_rect().center)
                self.escDialog.show()
                self.escDialog.update()
            else:
                self.escDialog.hide()

        if self.renderer.isEnded():
            user_input = self.prompt_user_input()
            if user_input:
                self.renderer.data.append("플레이어: " + user_input)
        else:            
            self.renderer.update()
        return
    
    def draw(self):
        if hasattr(self,"renderer"):
            self.renderer.draw()

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
    scriptScene = scriptScene()


if __name__=="__main__":
    #Screen Setting
    window = REMOGame(window_resolution=(1280,720),screen_size=(2560,1440),fullscreen=False,caption="DEFAULT")
    window.setCurrentScene(Scenes.mainScene)
    window.run()

    # Done! Time to quit.
