'''
비주얼 노벨 형식의 대화 스크립트를 처리하는 모듈입니다.
'''

from .core import *

##스크립트 렌더링을 위한 레이아웃들을 저장하는 클래스.
class scriptRenderLayouts:
    layouts = {
        #1920*1080 스크린을 위한 기본 레이아웃.
        "default_1920_1080":
        {
            "name-rect":pygame.Rect(300,600,200,60), #이름이 들어갈 사각형 영역
            'name-alpha':200, #이름 영역의 배경 알파값. 입력하지 않을경우 불투명(255)
            "font":"korean_script.ttf", # 폰트. 기본으로 지원되는 한국어 폰트(맑은고딕). 영어 한국어 지원 가능
            "font-size":40, # 폰트 크기
            "script-rect":pygame.Rect(100,680,1700,380), ##스크립트가 들어갈 사각형 영역
            "script-pos":RPoint(200,710), ##스크립트 텍스트의 위치
            "script-text-width":1500, ##스크립트의 좌우 텍스트 최대길이
            "script-alpha":200 ## 스크립트 영역의 배경 알파값. 입력하지 않을경우 255(완전 불투명)
            ### 추가 옵션들
            ##"name-image":이름 영역의 이미지를 지정할 수 있습니다.
            ##"script-image" : 스크립트 영역의 이미지를 지정할 수 있습니다.
            ###
        }
        ##TODO: 유저 커스텀 레이아웃을 추가해 보세요. 네이밍 양식을 지켜서!
    }

    @classmethod
    def updateLayout(cls,name:str,layout:dict):
        '''
        name : 레이아웃의 이름\n
        layout : 레이아웃의 딕셔너리. 양식은 scriptRenderLayouts.layouts 참고\n
        '''
        cls.layouts[name] = layout


class scriptMode(Enum):
    Normal = 0
    QuestioningStart = 1
    Questioning = 2
    Answering = 3

##작성한 비주얼노벨 스크립트를 화면에 그려주는 오브젝트 클래스.
class scriptRenderer():
    ##감정 벌룬 스프라이트(emotion-ballon.png)에 담겨진 감정의 순서를 나열한다.
    emotions = ["awkward","depressed","love","excited","joyful","angry","surprised","curious","sad","idea","ok","zzz","no"]
    emotionSpriteFile = "emotion-ballon.png" # 감정 벌룬 스프라이트의 파일 이름
    emotionTime = 1700 ##1700ms동안 감정 벌룬이 재생된다.


    ##렌더러를 초기화한다. (clear의 역할을 함)
    def _init(self):
        ##기본 이미지 초기화
        self.imageObjs = [] #화면에 출력될 이미지들
        self.charaObjs=[None,None,None] #화면에 출력될 캐릭터들
        self.moveInstructions = [[],[],[]] #캐릭터들의 움직임에 대한 지시문
        self.emotionObjs = [] # 화면에 출력될 (캐릭터의) 감정들
        self.freezeTimer = time.time() ## 스크립트를 멈추는 타이머
        self.bgObj = rectObj(Rs.screen.get_rect(),color=Cs.black,radius=0) #배경 이미지
        self.nameObj = textButton()

        ##스크립트 텍스트 오브젝트
        self.scriptObj = longTextObj("",pos=self.layout["script-pos"],font=self.font,size=self.layout["font-size"],textWidth=self.layout["script-text-width"])

        self.frameTimer = RTimer(1000/60) ##프레임 타이머

    def clear(self):
        self._init()


    #textSpeed:값이 클수록 느리게 재생된다.
    def __init__(self,fileName,*,textSpeed:float = 5.0,layout="default_1920_1080",endFunc = lambda :None):
        '''
        textSpeed: 값이 클수록 느리게 재생된다.
        target_fps가 60보다 낮을 경우 캐릭터의 움직임이 느려질 수 있다.
        '''
        if not fileName.endswith('.scr'):
            fileName += '.scr'
        if fileName in REMODatabase.scriptPipeline:
            self.data = REMODatabase.scriptPipeline[fileName]
        else:
            raise Exception("script file:"+fileName+" not loaded. use method: REMODatabase.loadScripts")



        self.layout = scriptRenderLayouts.layouts[layout]
        self.index = 0
        self.font = self.layout["font"]
        
        self.currentScript = "" #현재 출력해야 되는 스크립트
        self.endFunc = endFunc #스크립트가 끝날 경우 실행되는 함수.
        self.scriptMode = scriptMode.Normal

        self.textSpeed=textSpeed
        self.textFrameTimer = RTimer((1000/60)*self.textSpeed) ##텍스트 출력 속도를 조절하는 타이머

        self._init()

        self.endMarker = rectObj(pygame.Rect(0,0,7,10)) ##스크립트 재생이 끝났음을 알려주는 점멸 마커

        ##점멸을 위한 내부 인자들.
        self.endMarker.switch = True
        self.endMarker.timer = time.time()
        self.endMarker.tick = 0.5 ##0.5초마다 점멸 

        ##스크립트 영역 배경 오브젝트
        if "script-image" in self.layout:
            ##TODO: 이미지를 불러온다.
            self.scriptBgObj = imageButton(self.layout["script-image"],self.layout["script-rect"],hoverMode=False)
            None
        else:
            self.scriptBgObj = textButton("",self.layout["script-rect"],color=Cs.hexColor("111111"))
            self.scriptBgObj.hoverRect.alpha=5

        if "script-alpha" in self.layout:
            self.scriptBgObj.alpha = self.layout["script-alpha"]

        ##스크립트의 배경을 클릭하면, 다음 스크립트를 불러온다.
        def nextScript():
            if not self.scriptLoaded():
                self.scriptObj.text = self.currentScript
                self.scriptObj.text = self.currentScript # 스크립트가 간헐적으로 한번에 출력이 안되는 버그가 있어서 임시방편으로 이렇게 해놓음.
            elif not self.isEnded():
                ##다음 스크립트를 불러온다.
                self.indexIncrement()
                self.updateScript()
                self.endMarker.switch = False
            else:
                if self.scriptMode == scriptMode.Normal:
                    ##파일의 재생이 끝남.
                    self._init() ## 초기화(오브젝트를 비운다)
                    self.endFunc()
                    print("script is ended")
                elif self.scriptMode == scriptMode.Answering:
                    self.scriptMode = scriptMode.Questioning
                    self.qnaIndex = 0
                    self.updateScript()

        self.scriptBgObj.connect(nextScript)
        self.updateScript()



    ##현 스크립트 재생이 끝났는지를 확인하는 함수
    def scriptLoaded(self):
        return self.scriptObj.text == self.currentScript

    ##전체 파일을 다 읽었는지 확인하는 함수.
    def isEnded(self):
        if self.scriptMode == scriptMode.Normal:
            if self.index == len(self.data)-1:
                return True
            return False
        elif self.scriptMode == scriptMode.Answering:
            if self.qnaIndex == len(self.answers[self.currentCase])-1:
                return True
            return False
        return True

    @property
    def currentLine(self):
        if self.scriptMode == scriptMode.Normal:
            return self.data[self.index].strip()
        elif self.scriptMode == scriptMode.Questioning:
            return self.qnaScript.strip()
        elif self.scriptMode == scriptMode.QuestioningStart:
            return self.lastScript.strip()
        elif self.scriptMode == scriptMode.Answering:
            return self.answers[self.currentCase][self.qnaIndex].strip()
    
    ##렌더러의 폰트 변경.
    def setFont(self,font):
        self.scriptObj.font = font
        self.nameObj.textObj.font = font

    ##캐릭터에게 움직임을 지시한다.
    ##num:캐릭터 번호
    def makeMove(self,num,moves):
        moveInst = self.moveInstructions[num]
        for j,move in enumerate(moves):
            if j<len(moveInst):
                moveInst[j]=moveInst[j]+move
            else:
                moveInst.append(move)


    def updateScript(self):
        """
        현재 스크립트 라인을 처리하는 함수.\n
        
        이 함수는 현재 스크립트에서 명령어로 시작하는 라인을 처리합니다.\n
        명령어는 '#'로 시작하며, 이 함수는 각 명령어에 맞는 처리를 수행합니다.\n
        
        주요 기능:\n
        - 스크립트 라인이 '#'로 시작하는 경우, 해당 태그를 분석하고 적절한 처리를 실행.\n
        - '#question' 태그를 만나면 Q&A 모드를 시작.\n
        - '#clear', '#bgm', '#sound', '#bg', '#chara', '#image' 등의 태그에 따라 각각의 처리 메소드를 호출.\n
        - 스크립트 라인이 명령어가 아닌 경우, 일반적인 대사 처리로 넘어감.\n
        
        주의사항:\n
        - 지원되지 않는 태그를 만나면 예외(Exception)를 발생시킴.\n
        - 현재 인덱스가 스크립트 데이터의 끝에 도달하면 함수를 종료함.\n
        """    

        ## 명령어 처리 ##
        while self.currentLine[0] == "#":
            l = self.currentLine.split()
            tag = l[0]  # Tag : '#bgm', '#bg', '#image' 등의 태그
            fileName, parameters = self.parse_parameters(l[1:])

            if tag == '#qna_open':
                self.startQnaMode(l)
            elif tag == '#clear':
                self.clearImages()
            elif tag == '#bgm':
                self.handleBgm(fileName, parameters)
            elif tag == '#sound':
                self.handleSound(fileName, parameters)
            elif tag == '#effect':
                self.apply_effect(fileName, parameters)
            elif tag == '#bg':
                self.handleBg(fileName)
            elif '#chara' in tag:
                self.handleChara(tag, fileName, parameters)
            elif tag == '#image':
                self.handleImage(fileName, parameters)
            else:
                raise Exception("Tag Not Supported, please check the script file(.scr): " + self.currentLine)

            if self.index == len(self.data) - 1:
                return
            self.indexIncrement()

        ## 스크립트 처리 ##
        ## ex: '민혁: 너는 왜 그렇게 생각해?'
        self.handleScriptLine(self.currentLine)

    def indexIncrement(self):
        if self.scriptMode == scriptMode.Normal:
            self.index += 1
        elif self.scriptMode == scriptMode.Questioning:
            return
        elif self.scriptMode == scriptMode.QuestioningStart:
            return
        elif self.scriptMode == scriptMode.Answering:
            self.qnaIndex += 1

    def startQnaMode(self, l):
        '''
        질문과 답변 모드를 시작하는 함수입니다.
        '''
        try:
            self.qnaScript = self.data[self.index-1]
            self.lastScript = self.qnaScript
        except IndexError:
            raise IndexError("선택지 이전에 qna를 시작하는 스크립트가 없습니다.")
        
        self.qnaIndex = 0
        # 선택지 파싱
        choice_string = " ".join(l[1:])  # l[1:] 부분을 하나의 문자열로 결합
        self.choices = self.parse_choices(choice_string)
        self.questionButtons = buttonLayout(self.choices,RPoint(0,0),buttonSize=RPoint(700,100),spacing=30,buttonColor=Cs.black)
        for i,button in enumerate(self.questionButtons.getChilds()[:-1]):
            def selectAnswer(i,button):
                def x():
                    self.currentCase = i+1
                    self.scriptMode = scriptMode.Answering
                    button.setParent(None)
                    self.questionButtons._clearGraphicCache()
                    self.questionButtons.adjustBoundary()
                    self.questionButtons.center = RPoint(950,360)
                    self.updateScript()
                return x
            button.connect(selectAnswer(i,button))
        def endQna():
            self.scriptMode = scriptMode.Normal
            self.indexIncrement()
            self.updateScript()
        self.questionButtons.getChilds()[-1].connect(endQna)

        self.questionButtons.center = RPoint(950,360)
        self.answers = {}
        self.currentCase = None

        # while문으로 #close까지 스크립트 읽어들이기
        while True:
            self.index += 1
            if self.index >= len(self.data):
                raise Exception("Unexpected end of script while in listening mode.")            
            if self.currentLine.startswith("#qna_script"):
                sentence = self.currentLine.split(" ",1)[1]
                self.qnaScript = sentence
            elif self.currentLine.startswith("#answer"):
                answer_number = int(self.currentLine[7:])  # '#answerX'에서 'X' 추출
                self.currentCase = answer_number
                self.answers[answer_number] = []  # 새로운 case 스크립트 저장 공간 생성
            elif self.currentLine.startswith("#qna_close"):
                break
            elif self.currentCase is not None:
                self.answers[self.currentCase].append(self.currentLine)        

        self.currentCase = None # 현재 선택지 초기화. 선택시 다시 설정됨.
        self.scriptMode = scriptMode.QuestioningStart


    def parse_choices(self, choice_string):
        import re
        # 정규 표현식을 사용하여 선택지를 나누기
        return [choice.strip() for choice in re.split(r' / ', choice_string)]

    def parse_parameters(self, l):
        fileName = None
        parameters = {}
        for nibble in l:
            if '=' in nibble:
                param_name, param_value = nibble.split("=")
                parameters[param_name] = param_value
            elif '.' in nibble:
                fileName = nibble
            else:
                if nibble == 'jump':
                    parameters['jump'] = 12
                if nibble == 'clear':
                    parameters['clear'] = True
        return fileName, parameters

    def clearImages(self):
        self.imageObjs = []
        self.charaObjs = [None, None, None]
        self.moveInstructions = [[], [], []]  # 움직임 초기화

    def handleBgm(self, fileName, parameters):
        _volume = float(parameters.get('volume', 1.0))
        Rs.changeMusic(fileName, volume=_volume)

    def handleSound(self, fileName, parameters):
        _volume = float(parameters.get('volume', 1.0))
        Rs.playSound(fileName, volume=_volume)

    def handleBg(self, fileName):
        self.bgObj = imageObj(fileName, Rs.screen.get_rect())

    def handleChara(self, tag, fileName, parameters):
        num = 0 if tag == '#chara' else int(tag[-1]) - 1
        _pos = eval(parameters.get('pos', 'RPoint(0,0)'))
        _scale = float(parameters.get('scale', 1))

        if fileName:
            if self.charaObjs[num]:
                self.charaObjs[num].setImage(fileName)
            else:
                self.charaObjs[num] = imageObj(fileName, pos=_pos, scale=_scale)

        if 'emotion' in parameters:
            self.apply_emotion(num, parameters['emotion'])

        if 'jump' in parameters:
            self.apply_jump(num, parameters['jump'])

        if 'move' in parameters:
            self.apply_move(num, parameters['move'])

        if 'clear' in parameters:
            self.charaObjs[num] = None

    def apply_effect(self, fileName, parameters):
        #effect effect1.png matrix=(5,3) pos=(300,300) scale=0.5 frameDuration=125
        _pos = eval(parameters.get('pos', 'RPoint(0,0)'))
        _scale = float(parameters.get('scale', 1))
        _matrix = eval(parameters.get('matrix', '(1,1)'))
        _frameDuration = eval(parameters.get('frameDuration', 1000/60))
        _stay = int(parameters.get('stay', 0))
        _freeze = int(parameters.get('freeze', 0))

        Rs.playAnimation(fileName,stay=_stay, pos=_pos, scale=_scale, sheetMatrix=_matrix, frameDuration=_frameDuration)
        self.freezeTimer = time.time() + _freeze / 1000.0


    def apply_emotion(self, num, emotion):
        try:
            i = scriptRenderer.emotions.index(emotion)
            e_pos = RPoint(self.charaObjs[num].rect.centerx, 30)
            Rs.playAnimation(
                scriptRenderer.emotionSpriteFile,
                stay=scriptRenderer.emotionTime,
                pos=e_pos,
                sheetMatrix=(13, 8),
                fromSprite=8 * i,
                toSprite=8 * (i + 1) - 1,
                frameDuration=125,
                scale=2
            )
            self.freezeTimer = time.time() + scriptRenderer.emotionTime / 1000.0
        except ValueError:
            raise Exception("Emotion not Supported: " + emotion +
                            ", currently supported are:" + str(scriptRenderer.emotions))

    def apply_jump(self, num, jump_value):
        j_pos = -int(jump_value)
        jumpInstruction = []
        d = -2 if j_pos > 0 else 2
        temp = j_pos
        sum = temp
        while sum != 0:
            jumpInstruction.append(RPoint(0, temp))
            temp += d
            sum += temp
        jumpInstruction.append(RPoint(0, temp))

        self.makeMove(num, jumpInstruction)

    def apply_move(self, num, move_value):
        m_pos = int(move_value)
        moveInstruction = []
        temp = m_pos
        while temp != 0:
            if abs(temp) <= 2:
                d = temp
            else:
                d = int(temp * 0.05)
                if d == 0:  # d가 0이면 루프가 멈추지 않으므로, 강제로 1 또는 -1로 설정
                    d = 1 if temp > 0 else -1
            temp -= d
            moveInstruction.append(RPoint(d, 0))

        self.makeMove(num, moveInstruction)

    def handleImage(self, fileName, parameters):
        _pos = eval(parameters.get('pos', 'RPoint(0,0)'))
        _scale = float(parameters.get('scale', 1))

        obj = imageObj(fileName, pos=_pos, scale=_scale)
        self.imageObjs.append(obj)

    def handleScriptLine(self,line):
        '''
        line : "이름: 대사" 형식의 스크립트 라인
        line을 받아서 GUI에 출력할 수 있도록 처리한다.
        '''
        if self.scriptMode == scriptMode.QuestioningStart:
            return
        if ":" in line:
            name, script = line.split(":")
            script = script.strip()

            self.nameObj = textButton(
                name,
                rect=self.layout["name-rect"],
                font=self.font,
                size=self.layout['font-size'],
                enabled=False,
                color=Cs.hexColor("222222")
            )
            if "name-alpha" in self.layout:
                self.nameObj.alpha = self.layout["name-alpha"]
            self.currentScript = script
        else:
            self.nameObj.textObj.text = ""
            self.currentScript = line.strip()

        self.scriptObj.text = ""



        
    def update(self):
        '''
        함수가 복잡하므로 이 함수 실행 전에 Rs.acquireDrawLock()을 통해 락을 걸어주는 것이 좋다.
        '''

        ##캐릭터의 움직임 업데이트
        if self.frameTimer.isOver():
            for i,moveInst in enumerate(self.moveInstructions):
                if moveInst != []:
                    move = moveInst.pop(0)
                    self.charaObjs[i].pos += move
            self.frameTimer.reset()


        ##감정 애니메이션이 재생중일 땐 스크립트를 재생하지 않는다.
        if self.freezeTimer>time.time():
            if self.scriptObj.text != "":
                self.scriptObj.text = ""
            return

        self.scriptBgObj.update()

        #Script를 화면에 읽어들이는 함수.
        if self.textFrameTimer.isOver():
            temp = False
            if not self.scriptLoaded():
                ##미세조정: 스크립트가 위아래로 왔다리 갔다리 하는 것을 막기 위한 조정임.
                i = len(self.scriptObj.text)
                fullText = self.currentScript
                while i < len(fullText) and fullText[i] != " ":
                    i+=1
                parsedText = fullText[:i]
                l1 = self.scriptObj.getStringList(self.scriptObj.text)[:-1]
                l2 = self.scriptObj.getStringList(parsedText)[:-1]
                try:
                    while len(l1[-1]) > len(l2[-1]):
                        self.scriptObj.text = self.currentScript[:len(self.scriptObj.text)+1]
                        l1 = self.scriptObj.getStringList(self.scriptObj.text)[:-1]
                        temp = True
                except:
                    pass
                if not temp:
                    self.scriptObj.text = self.currentScript[:len(self.scriptObj.text)+1]
            self.textFrameTimer.reset()

        ##점멸 마커 업데이트
        if self.scriptLoaded() and self.scriptObj.getChilds()!=[]:
            ##점멸 표시
            if time.time()>self.endMarker.timer:
                self.endMarker.timer = time.time()+self.endMarker.tick 
                self.endMarker.switch = not self.endMarker.switch
            
            markerPos = RPoint(self.scriptObj.childs[0][-1].geometry.bottomright)+RPoint(20,0)
            if self.endMarker.bottomleft != markerPos:
                self.endMarker.bottomleft = markerPos

        ## 질문용 선택지 업데이트
        if self.scriptMode == scriptMode.Questioning or self.scriptMode == scriptMode.QuestioningStart:
            self.questionButtons.update()



    def draw(self):
        self.bgObj.draw()
        for imageObj in self.imageObjs:
            imageObj.draw()
        for chara in self.charaObjs:
            if chara:
                chara.draw()
        self.scriptBgObj.draw()
        self.scriptObj.draw()
        if self.scriptLoaded() and self.endMarker.switch:
            self.endMarker.draw()
        if self.nameObj.textObj.text!="":
            self.nameObj.draw()
            self.nameObj.textObj.draw()
        for emotion in self.emotionObjs:
            emotion.draw()
        if self.scriptMode == scriptMode.Questioning or self.scriptMode == scriptMode.QuestioningStart:
            self.questionButtons.draw()




