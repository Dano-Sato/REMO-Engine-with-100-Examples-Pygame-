# scriptRenderer 메뉴얼

## 개요

`scriptRenderer`는 REMO Engine에서 비주얼 노벨 형식의 대화 스크립트를 처리하고 화면에 렌더링하는 핵심 클래스입니다. 이 클래스를 통해 텍스트 기반의 스토리텔링, 캐릭터 대화, 선택지 시스템, 배경음악, 효과음, 캐릭터 애니메이션 등을 구현할 수 있습니다.

## 기본 사용법

### 1. 스크립트 파일 준비

먼저 `.scr` 확장자를 가진 스크립트 파일을 준비해야 합니다.

```python
from REMOLib import *

# 스크립트 파일 로드
REMODatabase.loadScripts(["my_script.scr"])

# scriptRenderer 생성
renderer = scriptRenderer("my_script.scr")
```

### 2. 기본 초기화

```python
def __init__(self, fileName, *, textSpeed=5.0, layout="default_2560_1440", endFunc=lambda: None):
```

**매개변수:**
- `fileName`: 스크립트 파일명 (`.scr` 확장자 자동 추가)
- `textSpeed`: 텍스트 출력 속도 (값이 클수록 느림, 기본값: 5.0)
- `layout`: 사용할 레이아웃 (기본값: "default_2560_1440")
- `endFunc`: 스크립트 종료 시 실행될 함수

## 스크립트 문법

### 1. 기본 대사

```
캐릭터명: 대사 내용
```

**예시:**
```
민혁: 안녕하세요! 오늘 날씨가 정말 좋네요.
나레이션: 민혁이 밝게 인사를 건넸다.
```

### 2. 명령어 (태그)

모든 명령어는 `#`으로 시작합니다.

#### 배경 관련

**배경 이미지 설정:**
```
#bg background.png
```

**배경 지우기:**
```
#clear
```

#### 캐릭터 관련

**캐릭터 표시:**
```
#chara character1.png pos=(100,200) scale=1.2
#chara2 character2.png pos=(800,150) scale=0.8
```

**캐릭터 감정 표현:**
```
#chara character1.png emotion=happy
```

**캐릭터 점프 애니메이션:**
```
#chara character1.png jump=5
```

**캐릭터 이동:**
```
#chara character1.png move=100
```

**캐릭터 제거:**
```
#chara character1.png clear
```

#### 음향 관련

**배경음악 재생:**
```
#bgm music.mp3 volume=0.7
```

**효과음 재생:**
```
#sound click.wav volume=1.0
```

#### 이미지 관련

**이미지 표시:**
```
#image item.png pos=(500,300) scale=0.5
```

#### 이펙트 관련

**스프라이트 애니메이션 이펙트:**
```
#effect explosion.png matrix=(5,3) pos=(400,200) scale=1.5 frameDuration=100 stay=2000
```

#### 텍스트 색상 변경

```
#color red
```

#### 질문과 답변 시스템

```
#qna_open 선택지1 / 선택지2 / 선택지3 / 종료

#qna_script 질문 내용이 여기에 표시됩니다.

#answer1
선택지1을 선택했을 때의 대사
계속되는 대사...

#answer2
선택지2를 선택했을 때의 대사
계속되는 대사...

#answer3
선택지3을 선택했을 때의 대사
계속되는 대사...

#qna_close
```

## 레이아웃 시스템

### 기본 레이아웃

`scriptRenderLayouts` 클래스에서 제공하는 기본 레이아웃들:

#### default_1920_1080
- 1920x1080 해상도용 기본 레이아웃
- 이름 영역: (300,600,200,60)
- 스크립트 영역: (100,680,1700,380)

#### default_2560_1440
- 2560x1440 해상도용 기본 레이아웃
- 이름 영역: (300,800,200,60)
- 스크립트 영역: (100,880,2300,480)

### 커스텀 레이아웃 생성

```python
custom_layout = {
    "name-rect": pygame.Rect(200, 700, 150, 50),
    "name-alpha": 180,
    "font": "korean_button.ttf",
    "font-size": 35,
    "script-rect": pygame.Rect(50, 750, 1800, 300),
    "script-pos": RPoint(100, 780),
    "script-text-width": 1600,
    "script-alpha": 220,
    "script-image": "dialogue_box.png"  # 선택사항
}

scriptRenderLayouts.updateLayout("my_layout", custom_layout)
```

## 감정 시스템

### 지원되는 감정

`scriptRenderer.emotions` 리스트에 정의된 감정들:
- "awkward" (어색함)
- "depressed" (우울함)
- "love" (사랑)
- "excited" (흥분)
- "joyful" (기쁨)
- "angry" (화남)
- "surprised" (놀람)
- "curious" (호기심)
- "sad" (슬픔)
- "idea" (아이디어)
- "ok" (좋음)
- "zzz" (졸림)
- "no" (거부)

### 감정 사용법

```
#chara character1.png emotion=happy
```

## 고급 기능

### 1. 매개변수 시스템

대부분의 명령어는 매개변수를 지원합니다:

```
#chara character.png pos=(100,200) scale=1.5 emotion=happy jump=3
```

**지원되는 매개변수:**
- `pos`: 위치 (RPoint 형식)
- `scale`: 크기 배율
- `emotion`: 감정
- `jump`: 점프 강도
- `move`: 이동 거리
- `volume`: 음량 (0.0-1.0)
- `matrix`: 스프라이트 시트 행렬 (행, 열)
- `frameDuration`: 프레임 지속시간
- `stay`: 애니메이션 지속시간
- `freeze`: 스크립트 일시정지 시간

### 2. 수학 표현식 지원

위치나 크기 등에서 수학 표현식을 사용할 수 있습니다:

```
#chara character.png pos=(100+50, 200*2) scale=1.5+0.3
```

### 3. 스크립트 모드

`scriptMode` 열거형으로 정의된 모드들:
- `Normal`: 일반 대사 모드
- `QuestioningStart`: 질문 시작 모드
- `Questioning`: 질문 대기 모드
- `Answering`: 답변 재생 모드

## 사용 예시

### 완전한 예제

```python
from REMOLib import *

class GameScene(Scene):
    def initOnce(self):
        # 스크립트 파일 로드
        REMODatabase.loadScripts(["story.scr"])
        
        # scriptRenderer 생성
        self.renderer = scriptRenderer(
            "story.scr",
            textSpeed=3.0,
            layout="default_2560_1440",
            endFunc=self.onScriptEnd
        )
    
    def onScriptEnd(self):
        print("스크립트가 끝났습니다!")
        # 다음 씬으로 이동하거나 다른 처리
    
    def update(self):
        self.renderer.update()
    
    def draw(self):
        self.renderer.draw()

# 스크립트 파일 예시 (story.scr)
"""
#bg forest.png
#bgm nature.mp3 volume=0.5

민혁: 안녕하세요! 오늘은 어떤 모험이 기다리고 있을까요?

#chara hero.png pos=(200,300) scale=1.2
#chara hero.png emotion=excited

민혁: 정말 기대됩니다!

#qna_open 모험을 시작한다 / 더 준비를 한다 / 집으로 돌아간다 / 대화 종료

#qna_script 어떻게 하시겠습니까?

#answer1
민혁: 좋습니다! 모험을 시작해봅시다!
#chara hero.png jump=5

#answer2
민혁: 더 준비가 필요하군요. 조금 더 기다려봅시다.

#answer3
민혁: 집으로 돌아가는 것도 좋은 선택이겠네요.

#qna_close

#clear
#bg sunset.png
#bgm ending.mp3 volume=0.3

나레이션: 그렇게 하루가 저물어갔다.
"""

if __name__ == "__main__":
    window = REMOGame(window_resolution=(1920,1080), screen_size=(2560,1440))
    window.setCurrentScene(GameScene())
    window.run()
```

## 성능 최적화

### 1. 텍스트 렌더링 최적화

- `textSpeed` 값을 적절히 조절하여 읽기 속도에 맞춤
- 긴 텍스트의 경우 `textWidth` 설정으로 자동 줄바꿈 활용

### 2. 이미지 관리

- `#clear` 명령어로 불필요한 이미지 정리
- 적절한 `scale` 값으로 이미지 크기 최적화

### 3. 애니메이션 관리

- `freeze` 매개변수로 애니메이션 중 텍스트 출력 제어
- `stay` 매개변수로 애니메이션 지속시간 조절

## 문제 해결

### 자주 발생하는 오류

1. **"script file not loaded" 오류**
   - `REMODatabase.loadScripts()`로 스크립트 파일을 먼저 로드해야 함

2. **"Tag Not Supported" 오류**
   - 지원되지 않는 태그 사용 시 발생
   - 올바른 태그 문법 확인 필요

3. **"Emotion not Supported" 오류**
   - 지원되지 않는 감정명 사용 시 발생
   - `scriptRenderer.emotions` 리스트 확인

### 디버깅 팁

1. 스크립트 파일의 인코딩을 UTF-8로 설정
2. 태그와 매개변수 사이의 공백 확인
3. 수학 표현식의 괄호와 연산자 확인
4. 이미지 파일 경로와 확장자 확인

## 확장 가능성

`scriptRenderer`는 다음과 같은 방식으로 확장할 수 있습니다:

1. **새로운 태그 추가**: `updateScript()` 메서드에 새로운 태그 처리 로직 추가
2. **커스텀 레이아웃**: `scriptRenderLayouts`에 새로운 레이아웃 추가
3. **새로운 감정**: `emotions` 리스트에 새로운 감정 추가
4. **매개변수 확장**: 기존 태그에 새로운 매개변수 추가

이 메뉴얼을 통해 `scriptRenderer`의 모든 기능을 효과적으로 활용하여 풍부한 비주얼 노벨 경험을 만들 수 있습니다.
