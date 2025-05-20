
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
            self.runScript("2-script3")

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


    ending = False
    
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
        
        with open("rp_prompt.txt", "r", encoding="utf-8") as f:
            prompt_text = f.read()
            
        with open("plot_maintain_checker.txt", "r", encoding="utf-8") as f:
            plot_maintain_checker = f.read()
            
        with open("plot.txt", "r", encoding="utf-8") as f:
            plot = f.read()
            
        with open("character_setting.txt", "r", encoding="utf-8") as f:
            character_setting = f.read()
            
        with open("error_check_prompt.txt", "r", encoding="utf-8") as f:
            error_check_prompt = f.read()
            
        # # 현재까지 완성된 결과를 기반으로, 이후 플롯의 흐름을 결정
        # story = client.models.generate_content(
        #     model="gemini-2.5-pro-preview-05-06",
        #     contents= [
        #     {"role": "USER","parts": [{"text":plot_maintain_checker}]}, 
        #     {"role": "USER", "parts": [{"text":f'''전반적인 플롯 : {plot}'''}]}, 
        #     {"role": "USER","parts": [{"text":f'''이전 내용 : {self.renderer.data}'''}]}, 
        #     {"role": "USER", "parts": [{"text":f'''사용자의 이번 입력 : {user_text}'''}]}            
        # ])
        # print(f"AI의 응답: {story.text}")

        while True:
            
            # 플레이어의 입력을 기반으로 응답을 생성
            response = client.models.generate_content(
                model="gemini-2.5-pro-preview-05-06",
                contents= [
                {"role": "USER","parts": [{"text": f'''system prompt : {prompt_text}'''}]}, 
                {"role": "USER","parts": [{"text": f'''캐릭터 정보 : {character_setting}'''}]},    
                #이전 대화 내용은 두가지로 나눠 넣음. 하나는 최근 250줄의 대화내역, 그 다음은 전반적인 플롯.
                {"role": "USER","parts": [{"text":f'''이전 내용 : {self.renderer.data[-250:]}'''}]}, 
                {"role": "USER", "parts": [{"text":f'''전반적인 플롯. 따로 주인공의 행동이 없으면 플롯대로 전개하며 플롯의 흐름에서 벗어나는 행동 또는 대사를 하는 경우 자연스럽게 대응하는 것을 최우선 목표로 한다. 너무 플롯에 메일 필요는 없으나, 가능하면 플롯을 따르도록 한다. : {plot}'''}]},             
                # {"role": "USER", "parts": [{"text":f'''현재 챕터. 만약 챕터명이 giveup이라면 더이상 플롯을 따라갈 수 없는 상태이므로 플롯과 별개로 사용자의 입력에 가장 자연스러운 대꾸를 하는 것을 목표로 진행한다: {story.text}'''}]},
                {"role": "USER", "parts": [{"text":f'''사용자의 이번 입력. 만약 입력이 '없음'이라면 사용자와 별개로 플롯에 따른 전개, 또는 이전 대화에 가장 어울리는 흐름의 대사를 작성합니다. : {user_text}'''}]}            
            ])
            
            print(f"AI의 응답: {response.text}")

            # error_checker = client.models.generate_content(
            #     model="gemini-2.5-pro-preview-05-06",
            #     contents= [
            #     {"role": "USER","parts": [{"text": f'''{error_check_prompt}'''}]}, 
            #     {"role": "USER","parts": [{"text":f'''이전 대화 내역 : {self.renderer.data[-50:]}'''}]}, 
            # ])
            
            # print(f"AI의 응답: {error_checker.text}")
            # if error_checker.text == "OK":
            #     print("AI의 응답이 정상입니다.")
            #     break
            # else:
            #     print("AI의 응답이 잘못되었습니다. 다시 시도합니다.")
            #     continue
            
            break
            
            
        ending_test = client.models.generate_content(
            model="gemini-2.5-flash-preview-04-17",
            contents= [
            {"role": "USER","parts": [{"text": f'''주어진 이전 대화 내역을 보고, 대화 내역에 '이렇게 모든 이야기가 막을 내렸다'라는 표현히 명확하게 있는 경우 end를, 그렇지 않다면 continue를 출력하시오. 출력은 end 또는 continue 중 하나만 가능하며, 괄호나 따옴표와 같은 표시 없이 무조건 하나의 단어만 출력해야 합니다.'''}]}, 
            {"role": "USER","parts": [{"text":f'''이번 대화 생성 내역 : {response.text}'''}]}, 
        ])
        
        
        for line in response.text.splitlines():
            if line.strip():  # 빈 줄 방지
                self.renderer.data.append(line)
              
        if ending_test.text == "end":
            self.ending = True
            self.renderer.data.append("#bg bad-end-credit.jpg")
            self.renderer.data.append("#color Cs.red")
            self.renderer.data.append("다음에는 더 좋은 결과가 있기를 바랍니다.")
            



    # 🎯 커스텀 입력창 (self 포함)
    def prompt_user_input(self, title="대사 입력", prompt="하고 싶은 대사 또는 행동을 입력하세요. '없음'을 입력하시면 가장 자연스러운 플롯으로 전개됩니다:"):
        root = tk.Tk()
        root.withdraw()

        input_window = tk.Toplevel()
        input_window.title(title)
        input_window.geometry("900x200")

        label = tk.Label(input_window, text=prompt, font=("맑은 고딕", 12))
        label.pack(pady=10)

        entry = tk.Entry(input_window, font=("맑은 고딕", 14), width=80)
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
                
        if not self.ending :
            if self.renderer.isEnded():
                user_input = self.prompt_user_input()
                if user_input:
                    self.renderer.data.append("플레이어: " + user_input)
            else:            
                self.renderer.update()
        else :

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
