import time #sleep함수를 통해 딜레이를 줄 수 있음
import random #적들이 무작위로 나올 때 쓸 수 있음
from colorsys import hsv_to_rgb
import board
from digitalio import DigitalInOut, Direction #라즈베리에서 제공하는 공식 라이브러리
from PIL import Image, ImageDraw, ImageFont #파이썬 이미지 처리 라이브러리
from adafruit_rgb_display import st7789 #조이스틱 모듈을 쓰기 위함
import numpy as np

class Joystick:
    def __init__(self):
        self.cs_pin = DigitalInOut(board.CE0)
        self.dc_pin = DigitalInOut(board.D25)
        self.reset_pin = DigitalInOut(board.D24)
        self.BAUDRATE = 24000000 #조이스틱 핀에 대한 기본적 정의..
        
        self.spi = board.SPI() #SPI 사용
        self.disp = st7789.ST7789(
                    self.spi,
                    height=240, #화면 픽셀 크기가 240X240, 여기 맞춰서 그림을 넣어야한다
                    y_offset=80,
                    rotation=180, #조이스틱 방향을 설정
                    cs=self.cs_pin,
                    dc=self.dc_pin,
                    rst=self.reset_pin,
                    baudrate=self.BAUDRATE,
                    )
        # Input pins:
        self.button_A = DigitalInOut(board.D5) #버튼 A
        self.button_A.direction = Direction.INPUT

        self.button_B = DigitalInOut(board.D6) #버튼 B
        self.button_B.direction = Direction.INPUT

        self.button_L = DigitalInOut(board.D27) #왼쪽 방향으로
        self.button_L.direction = Direction.INPUT

        self.button_R = DigitalInOut(board.D23) #오른쪽 방향으로
        self.button_R.direction = Direction.INPUT

        self.button_U = DigitalInOut(board.D17) #위로
        self.button_U.direction = Direction.INPUT

        self.button_D = DigitalInOut(board.D22) #아래로
        self.button_D.direction = Direction.INPUT

        self.button_C = DigitalInOut(board.D4) #가운데 버튼
        self.button_C.direction = Direction.INPUT
        
        # Turn on the Backlight
        self.backlight = DigitalInOut(board.D26)
        self.backlight.switch_to_output()
        self.backlight.value = True #화면에 불이 들어옴
        
         # Create blank image for drawing.
        # Make sure to create image with mode 'RGB' for color.
        self.width = self.disp.width
        self.height = self.disp.height #화면 설정? 기본적
        
class Character:
    def __init__(self, width, height):
        self.appearance = 'circle'
        self.state = None
        self.position = np.array([width/8 - 10, height/8 - 20, width/8 + 10, height/8 + 20])
        self.outline = "#FFFFFF"

    def move(self, command = None):
        if command['move'] == False:
            self.state = None
            self.outline = "#FFFFFF" #검정색상 코드!
        
        else:
            self.state = 'move'
            self.outline = "#FF0000" #빨강색상 코드!

            if command['up_pressed']:
                self.position[1] -= 5
                self.position[3] -= 5

            if command['down_pressed']:
                self.position[1] += 5
                self.position[3] += 5

            if command['left_pressed']:
                self.position[0] -= 5
                self.position[2] -= 5
                
            if command['right_pressed']:
                self.position[0] += 5
                self.position[2] += 5

class Miro1:
    def __init__(self, width, height):
        self.appearance = 'miro1'
        self.position = np.array([0, height/4 - 10, width/4 + 10, height/4 + 10])
        self.outline = "#FFFFFF"
        
    def notdown(self, ego_position, other_position):
        
        d=1
        if other_position[3] > ego_position[1] and other_position[0] > ego_position[0] and other_position[0] < ego_position[2] and other_position[1] < ego_position[1]:
            d=0
        return d
    
    def notleft(self, ego_position, other_position):
        
        l=1
        if other_position[0] < ego_position[2] and other_position[1] < ego_position[3] and other_position[3] > ego_position[1] and other_position[2] > ego_position[2]:
            l=0
        return l
    
    def notup(self, ego_position, other_position):
        u=1
        if other_position[1] < ego_position[3] and other_position[0] > ego_position[0] and other_position[0] < ego_position[2] and other_position[3] > ego_position[3]:
            u=0
        return u
    
class heartCard:
    def __init__(self, width, height):
        
        self.appearance = 'heartcard'
        self.sleep=20
        self.position = np.array([width/4-8, height/4-10, width/4+8, height/4+14])
        self.state = None
        self.outline = "#0000FF"
    
    def notdown(self, ego_position, other_position):
        
        d=0
        if other_position[3] > ego_position[1] and other_position[2] > ego_position[0] and other_position[0] < ego_position[2] and other_position[1] < ego_position[1] :
            d=1
            return d
    
    def notright(self, ego_position, other_position):
        
        r=0
        if other_position[2] > ego_position[0] and other_position[1] < ego_position[3] and other_position[3] > ego_position[1] and other_position[0] < ego_position[0]:
            r=1
            return r
    
    def notleft(self, ego_position, other_position):
        l=0
        if other_position[0] < ego_position[2] and other_position[1] < ego_position[3] and other_position[3] > ego_position[1] and other_position[2] > ego_position[2]:
            l=1
            return l
    
    def notup(self, ego_position, other_position):
        u=0
        if other_position[1] < ego_position[3] and other_position[0] > ego_position[0] and other_position[0] < ego_position[2] and other_position[3] > ego_position[3]:
            u=1
            return u

class heartCard2:
    def __init__(self, width, height):
        
        self.appearance = 'heartcard2'
        self.sleep=20
        self.position = np.array([width/4-10, height-height/4-6, width/4+14, height-height/4+10])
        self.state = None
        self.outline = "#0000FF"
    
    def notdown(self, ego_position, other_position):
        
        d=0
        if other_position[3] > ego_position[1] and other_position[2] > ego_position[0] and other_position[0] < ego_position[2] and other_position[1] < ego_position[1] :
            d=1
            return d
    
    def notright(self, ego_position, other_position):
        
        r=0
        if other_position[2] > ego_position[0] and other_position[1] < ego_position[3] and other_position[3] > ego_position[1] and other_position[0] < ego_position[0]:
            r=1
            return r
    
    def notleft(self, ego_position, other_position):
        l=0
        if other_position[0] < ego_position[2] and other_position[1] < ego_position[3] and other_position[3] > ego_position[1] and other_position[2] > ego_position[2]:
            l=1
            return l
    
    def notup(self, ego_position, other_position):
        u=0
        if other_position[1] < ego_position[3] and other_position[0] > ego_position[0] and other_position[0] < ego_position[2] and other_position[3] > ego_position[3]:
            u=1
            return u

class Bottle:
    def __init__(self, width, height):
        
        self.appearance = 'bottle'
        self.sleep=20
        self.position = np.array([width-width/4+25, height/4+13, width-15, height/2-13])
        self.state = None
        self.outline = "#0000FF"
    
    def notdown(self, ego_position, other_position):
        
        d=0
        if other_position[3] > ego_position[1] and other_position[2] > ego_position[0] and other_position[0] < ego_position[2] and other_position[1] < ego_position[1] :
            d=1
            return d
    
    def notright(self, ego_position, other_position):
        
        r=0
        if other_position[2] > ego_position[0] and other_position[1] < ego_position[3] and other_position[3] > ego_position[1] and other_position[0] < ego_position[0]:
            r=1
            return r
    
    def notleft(self, ego_position, other_position):
        l=0
        if other_position[0] < ego_position[2] and other_position[1] < ego_position[3] and other_position[3] > ego_position[1] and other_position[2] > ego_position[2]:
            l=1
            return l
    
    def notup(self, ego_position, other_position):
        u=0
        if other_position[1] < ego_position[3] and other_position[0] > ego_position[0] and other_position[0] < ego_position[2] and other_position[3] > ego_position[3]:
            u=1
            return u

class Miro2:
    def __init__(self, width, height):
        self.appearance = 'miro2'
        self.position = np.array([width/2-10, 0, width/2 + 10, height/4 + 10])
        self.outline = "#FFFFFF"
    
    def notleft(self, ego_position, other_position):
        l=1
        if other_position[0] < ego_position[2] and other_position[1] < ego_position[3] and other_position[3] > ego_position[1] and other_position[2] > ego_position[2]:
            l=0
        return l
    
    def notright(self, ego_position, other_position):
    
        r=1
        if other_position[2] > ego_position[0] and other_position[1] < ego_position[3] and other_position[3] > ego_position[1] and other_position[0] < ego_position[0]:
            r=0
        return r
    
    def notup(self, ego_position, other_position):

        u=1
        if other_position[1] < ego_position[3] and other_position[0] < ego_position[2] and other_position[3] > ego_position[3] and other_position[2] > ego_position[0]:
            u=0
        return u

class Miro3:
    def __init__(self, width, height):
        self.appearance = 'miro3'
        #self.state = None
        self.position = np.array([width-width/4-10, height/4-10, width-width/4 + 10, height/2 - 10])
        # 총알 발사를 위한 캐릭터 중앙 점 추가
        self.outline = "#FFFFFF"
    
    def notleft(self, ego_position, other_position):

        l=1
        if other_position[0] < ego_position[2] and other_position[1] < ego_position[3] and other_position[3] > ego_position[1] and other_position[2] > ego_position[2]:
            l=0
        return l
    
    def notright(self, ego_position, other_position):

        r=1
        if other_position[2] > ego_position[0] and other_position[1] < ego_position[3] and other_position[3] > ego_position[1] and other_position[0] < ego_position[0]:
            r=0
        return r
    
    def notdown(self, ego_position, other_position):

        d=1
        if other_position[3] > ego_position[1] and other_position[0] < ego_position[2] and other_position[1] < ego_position[1] and other_position[2] > ego_position[0]:
            d=0
        return d

class Miro4:
    def __init__(self, width, height):
        self.appearance = 'miro4'
        self.position = np.array([10, height/2 - 10, width, height/2 + 10])
        self.outline = "#FFFFFF"
        
    def notdown(self, ego_position, other_position):

        d=1
        if other_position[3] > ego_position[1] and other_position[2] > ego_position[0] and other_position[0] < ego_position[2] and other_position[1] < ego_position[1] :
            d=0
        return d
    
    def notright(self, ego_position, other_position):

        r=1
        if other_position[2] > ego_position[0] and other_position[1] < ego_position[3] and other_position[3] > ego_position[1] and other_position[0] < ego_position[0]:
            r=0
        return r
    
    def notup(self, ego_position, other_position):

        u=1
        if other_position[1] < ego_position[3] and other_position[0] > ego_position[0] and other_position[0] < ego_position[2] and other_position[3] > ego_position[3]:
            u=0
        return u
    
class Miro5:
    def __init__(self, width, height):
        self.appearance = 'miro5'
        #self.state = None
        self.position = np.array([width/4-10, height-height/4 - 5, width-width/4+10, height-height/4+15])
        self.outline = "#FFFFFF"
        
    def notdown(self, ego_position, other_position):
    
        d=1
        if other_position[3] > ego_position[1] and other_position[2] > ego_position[0] and other_position[0] < ego_position[2] and other_position[1] < ego_position[1] :
            d=0
        return d
    
    def notright(self, ego_position, other_position):
        r=1
        if other_position[2] > ego_position[0] and other_position[1] < ego_position[3] and other_position[3] > ego_position[1] and other_position[0] < ego_position[0]:
            r=0
        return r
    
    def notleft(self, ego_position, other_position):
        l=1
        if other_position[0] < ego_position[2] and other_position[1] < ego_position[3] and other_position[3] > ego_position[1] and other_position[2] > ego_position[2]:
            l=0
        return l
    
    def notup(self, ego_position, other_position):
        u=1
        if other_position[1] < ego_position[3] and other_position[0] > ego_position[0] and other_position[0] < ego_position[2] and other_position[3] > ego_position[3]:
            u=0
        return u
    
class Miro6:
    def __init__(self, width, height):
        self.appearance = 'miro6'
        #self.state = None
        self.position = np.array([width/4-10, height-height/4-5, width/4+10, height])
        # 총알 발사를 위한 캐릭터 중앙 점 추가
        self.outline = "#FFFFFF"
    
    def notleft(self, ego_position, other_position):
        l=1
        if other_position[0] < ego_position[2] and other_position[1] < ego_position[3] and other_position[3] > ego_position[1] and other_position[2] > ego_position[2]:
            l=0
        return l
    
    def notright(self, ego_position, other_position):
        r=1
        if other_position[2] > ego_position[0] and other_position[1] < ego_position[3] and other_position[3] > ego_position[1] and other_position[0] < ego_position[0]:
            r=0
        return r
    
    def notdown(self, ego_position, other_position):

        d=1
        if other_position[3] > ego_position[1] and other_position[0] < ego_position[2] and other_position[1] < ego_position[1] and other_position[2] > ego_position[0]:
            d=0
        return d

class Mushroom:
    def __init__(self, width, height):
        
        self.appearance = 'mushroom'
        self.sleep=20
        self.position = np.array([10, height-height/4+25, width/4-20, height-15])
        self.state = None
        self.outline = "#0000FF"
    
    def notdown(self, ego_position, other_position):
        
        d=0
        if other_position[3] > ego_position[1] and other_position[2] > ego_position[0] and other_position[0] < ego_position[2] and other_position[1] < ego_position[1] :
            d=1
            return d
    
    def notright(self, ego_position, other_position):
        
        r=0
        if other_position[2] > ego_position[0] and other_position[1] < ego_position[3] and other_position[3] > ego_position[1] and other_position[0] < ego_position[0]:
            r=1
            return r
    
    def notleft(self, ego_position, other_position):
        l=0
        if other_position[0] < ego_position[2] and other_position[1] < ego_position[3] and other_position[3] > ego_position[1] and other_position[2] > ego_position[2]:
            l=1
            return l
    
    def notup(self, ego_position, other_position):
        u=0
        if other_position[1] < ego_position[3] and other_position[0] > ego_position[0] and other_position[0] < ego_position[2] and other_position[3] > ego_position[3]:
            u=1
            return u
        
class Hole1:
    def __init__(self, width, height):
        
        self.appearance = 'hole1'
        self.sleep=20
        self.position = np.array([width/4+17, height-height/4+25, width/2-17, height-10])
        self.state = None
        self.outline = "#0000FF"
    
    def notdown(self, ego_position, other_position):
        
        d=0
        if other_position[3] > ego_position[1] and other_position[2] > ego_position[0] and other_position[0] < ego_position[2] and other_position[1] < ego_position[1] :
            d=1
            return d
    
    def notright(self, ego_position, other_position):
        
        r=0
        if other_position[2] > ego_position[0] and other_position[1] < ego_position[3] and other_position[3] > ego_position[1] and other_position[0] < ego_position[0]:
            r=1
            return r
    
    def notleft(self, ego_position, other_position):
        l=0
        if other_position[0] < ego_position[2] and other_position[1] < ego_position[3] and other_position[3] > ego_position[1] and other_position[2] > ego_position[2]:
            l=1
            return l
    
    def notup(self, ego_position, other_position):
        u=0
        if other_position[1] < ego_position[3] and other_position[0] > ego_position[0] and other_position[0] < ego_position[2] and other_position[3] > ego_position[3]:
            u=1
            return u
        
class Life1:
    def __init__(self):
        
        self.appearance = 'life1'
        self.sleep=20
        self.position = np.array([240-43, 3, 240-21, 15])
        self.state = None
        self.outline = "#0000FF"
        
class Life2:
    def __init__(self):
        
        self.appearance = 'life2'
        self.sleep=20
        self.position = np.array([240-29, 3, 240-17, 15])
        self.state = None
        self.outline = "#0000FF"
        
class Life3:
    def __init__(self):
        
        self.appearance = 'life3'
        self.sleep=20
        self.position = np.array([240-15, 3, 240-3, 15])
        self.state = None
        self.outline = "#0000FF"

joystick = Joystick() #조이스틱 객체 선언
my_image = Image.new('RGB',(joystick.width, joystick.height))
my_draw = ImageDraw.Draw(my_image,'RGBA') #도화지와 도구를 연결 

# 1라운드
iintro=Image.open('intro.png')
start=0
while True:
    if not joystick.button_A.value:
        break
    my_image.paste(iintro,(0,0))
    joystick.disp.image(my_image)
    
iground=Image.open('ground.png')
iheartcard=Image.open('heartcard.png')
iheartcard2=Image.open('heartcard2.png')
ibottle=Image.open('bottle.png')
imiro1=Image.open('miro1.png')
imiro2=Image.open('miro2.png')
imiro3=Image.open('miro3.png')
imiro4=Image.open('miro4.png')
imiro5=Image.open('miro5.png')
imiro6=Image.open('miro6.png')
relice=Image.open('elicer.png')
lelice=Image.open('elicel.png')
imushroom=Image.open('mushroom.png')
ilife=Image.open('life.png')    

my_circle = Character(joystick.width, joystick.height)
miro1 = Miro1(joystick.width, joystick.height)
miro2 = Miro2(joystick.width, joystick.height)
miro3 = Miro3(joystick.width, joystick.height)
miro4 = Miro4(joystick.width, joystick.height)
miro5 = Miro5(joystick.width, joystick.height)
miro6 = Miro6(joystick.width, joystick.height)
heartcard = heartCard(joystick.width, joystick.height)
heartcard2 = heartCard2(joystick.width, joystick.height)
bottle = Bottle(joystick.width, joystick.height)
mushroom = Mushroom(joystick.width, joystick.height)
hole1 = Hole1(joystick.width, joystick.height)
life1 = Life1()
life2 = Life2()
life3 = Life3()

heartcardslp=0
heartcardslp2=0
heartcrash=30
heartcrash2=30
bottleeat=0
mushroomeat=0
delice=0
lifenum=3

while True:
    command = {'move': False, 'up_pressed': False , 'down_pressed': False, 'left_pressed': False, 'right_pressed': False}
    
    if not joystick.button_U.value:  # up pressed
        if miro1.notup(miro1.position, my_circle.position) and miro2.notup(miro2.position, my_circle.position) and miro4.notup(miro4.position, my_circle.position) and miro5.notup(miro5.position, my_circle.position):
            command['up_pressed'] = True
            command['move'] = True
            
    
    if not joystick.button_D.value:  # down pressed
        if miro1.notdown(miro1.position, my_circle.position) and miro3.notdown(miro3.position, my_circle.position) and miro4.notdown(miro4.position, my_circle.position) and miro5.notdown(miro5.position, my_circle.position) and miro6.notdown(miro6.position, my_circle.position):
            command['down_pressed'] = True
            command['move'] = True

    if not joystick.button_L.value: 
        delice=1
        if miro1.notleft(miro1.position, my_circle.position) and miro2.notleft(miro2.position, my_circle.position) and miro3.notleft(miro3.position, my_circle.position) and miro5.notleft(miro5.position, my_circle.position) and miro6.notleft(miro6.position, my_circle.position):
            command['left_pressed'] = True
            command['move'] = True
            

    if not joystick.button_R.value: 
        delice=0
        if miro2.notright(miro2.position, my_circle.position) and miro3.notright(miro3.position, my_circle.position) and miro4.notright(miro4.position, my_circle.position) and miro5.notright(miro5.position, my_circle.position) and miro6.notright(miro6.position, my_circle.position):
            command['right_pressed'] = True
            command['move'] = True
        
    if (heartcard.notup(heartcard.position,my_circle.position) or heartcard.notdown(heartcard.position,my_circle.position) or heartcard.notleft(heartcard.position,my_circle.position) or heartcard.notright(heartcard.position,my_circle.position)) and heartcrash>0:
        heartcrash-=1
        if heartcrash==29:
            lifenum-=1
    elif (heartcard2.notup(heartcard2.position,my_circle.position) or heartcard2.notdown(heartcard2.position,my_circle.position) or heartcard2.notleft(heartcard2.position,my_circle.position) or heartcard2.notright(heartcard2.position,my_circle.position)) and heartcrash2>0:
        heartcrash2-=1
        if heartcrash2==29:
            lifenum-=1
        if heartcard.position[3]==joystick.width/2+10:
            heartcardslp=1
            heartcard.position[0]=joystick.width/4-8
            heartcard.position[1]=joystick.height/4-1
            heartcard.position[2]=joystick.width/4+8
            heartcard.position[3]=joystick.height/4
                    
        else:
            if heartcardslp==0:
                heartcard.position[1]+=2
                heartcard.position[3]+=2
            else:
                if heartcard.sleep==0:
                    heartcard.position[1]=joystick.height/4-10
                    heartcard.position[3]=joystick.height/4+14
                    heartcardslp=0
                    heartcard.sleep=20
                else:
                    heartcard.sleep-=1
    else:
        my_circle.move(command)
        
        if heartcard2.position[2]==0:
            heartcardslp2=1
            heartcard2.position[0]=joystick.width/4-1
            heartcard2.position[1]=joystick.height-joystick.height/4-6
            heartcard2.position[2]=joystick.width/4
            heartcard2.position[3]=joystick.height-joystick.height/4+10
                    
        else:
            if heartcardslp2==0:
                heartcard2.position[0]-=2
                heartcard2.position[2]-=2
            else:
                if heartcard2.sleep==0:
                    heartcard2.position[0]=joystick.width/4-10
                    heartcard2.position[2]=joystick.width/4+14
                    heartcardslp2=0
                    heartcard2.sleep=20
                else:
                    heartcard2.sleep-=1
        if heartcard.position[3]==joystick.width/2+10:
            heartcardslp=1
            heartcard.position[0]=joystick.width/4-8
            heartcard.position[1]=joystick.height/4-1
            heartcard.position[2]=joystick.width/4+8
            heartcard.position[3]=joystick.height/4
                    
        else:
            if heartcardslp==0:
                heartcard.position[1]+=2
                heartcard.position[3]+=2
            else:
                if heartcard.sleep==0:
                    heartcard.position[1]=joystick.height/4-10
                    heartcard.position[3]=joystick.height/4+14
                    heartcardslp=0
                    heartcard.sleep=20
                else:
                    heartcard.sleep-=1
    
    if (bottle.notup(bottle.position,my_circle.position) or bottle.notdown(bottle.position,my_circle.position) or bottle.notleft(bottle.position,my_circle.position) or bottle.notright(bottle.position,my_circle.position)) and bottleeat==0:  
        bottleeat=1   
        my_circle.position[0]+=8
        my_circle.position[1]+=12
        my_circle.position[2]-=8
        my_circle.position[3]-=12
        relice = relice.resize((8, 12))
        lelice = lelice.resize((8, 12))
    if (mushroom.notup(mushroom.position,my_circle.position) or mushroom.notdown(mushroom.position,my_circle.position) or mushroom.notleft(mushroom.position,my_circle.position) or mushroom.notright(mushroom.position,my_circle.position)) and mushroomeat==0:  
        mushroomeat=1   
        my_circle.position[0]-=8
        my_circle.position[1]-=12
        my_circle.position[2]+=8
        my_circle.position[3]+=12
        relice=Image.open('elicer.png')
        lelice=Image.open('elicel.png')
    if (hole1.notup(hole1.position,my_circle.position) or hole1.notdown(hole1.position,my_circle.position) or hole1.notleft(hole1.position,my_circle.position) or hole1.notright(hole1.position,my_circle.position)):  
        break
  
    my_draw.rectangle((0, 0, joystick.width, joystick.height), fill = (255, 255, 255, 100))
    my_image.paste(iground,(0,0))
    my_draw.rectangle(tuple(heartcard.position), fill = (0, 0, 0,0))
    if heartcardslp==0:
        my_image.paste(iheartcard,(int(heartcard.position[0]),int(heartcard.position[1])))
    my_draw.rectangle(tuple(heartcard2.position), fill = (0, 0, 0,0))
    if heartcardslp2==0:
        my_image.paste(iheartcard2,(int(heartcard2.position[0]),int(heartcard2.position[1])))
    if bottleeat==0:
        my_draw.rectangle(tuple(bottle.position), fill = (0, 0, 0,0))
        my_image.paste(ibottle,(205, 73),mask=ibottle)
    if mushroomeat==0:
        my_draw.rectangle(tuple(mushroom.position), fill = (0, 0, 0,0))
        my_image.paste(imushroom,(10, 205),mask=imushroom)
    my_draw.rectangle(tuple(miro1.position), fill = (0, 0, 0,0))
    my_image.paste(imiro1,(0,50))
    my_draw.rectangle(tuple(miro2.position), fill = (0, 0, 0,0))
    my_image.paste(imiro2,(110, 0))
    my_draw.rectangle(tuple(miro3.position), fill = (0, 0, 0,0))
    my_image.paste(imiro3,(170, 50))
    my_draw.rectangle(tuple(miro4.position),fill = (0, 0, 0,0))
    my_image.paste(imiro4,(10, 110))
    my_draw.rectangle(tuple(miro5.position), fill = (0, 0, 0,0))
    my_image.paste(imiro5,(50, 175))
    my_draw.rectangle(tuple(miro6.position), fill = (0, 0, 0,0))
    my_image.paste(imiro6,(50, 175))
    my_draw.ellipse(tuple(hole1.position), fill = (100, 70, 30, 255))
    if delice==0:
        my_draw.ellipse(tuple(my_circle.position),fill = (0, 0,0,0))
        if heartcrash%4==1 and heartcrash%4==2 and heartcrash>0:
            if heartcrash2%4==1 and heartcrash2%4==2 and heartcrash2>0:
                my_image.paste(relice,(int(my_circle.position[0]),int(my_circle.position[1])),mask=relice)
            elif heartcrash2%4!=0 or heartcrash2%4!=3 and heartcrash2<=0:
                my_image.paste(relice,(int(my_circle.position[0]),int(my_circle.position[1])),mask=relice)
        elif heartcrash%4!=0 or heartcrash%4!=3 and heartcrash<=0:
            if heartcrash2%4==1 and heartcrash2%4==2 and heartcrash2>0:
                my_image.paste(relice,(int(my_circle.position[0]),int(my_circle.position[1])),mask=relice)
            elif heartcrash2%4!=0 or heartcrash2%4!=3 and heartcrash2<=0:
                my_image.paste(relice,(int(my_circle.position[0]),int(my_circle.position[1])),mask=relice)
        
    elif delice==1:
        my_draw.ellipse(tuple(my_circle.position),fill = (0, 0, 0,0))
        if heartcrash%4==1 and heartcrash%4==2 and heartcrash>0:
            if heartcrash2%4==1 and heartcrash2%4==2 and heartcrash2>0:
                my_image.paste(lelice,(int(my_circle.position[0]),int(my_circle.position[1])),mask=lelice)
            elif heartcrash2%4!=0 or heartcrash2%4!=3 and heartcrash2<=0:
                my_image.paste(lelice,(int(my_circle.position[0]),int(my_circle.position[1])),mask=lelice)
        elif heartcrash%4!=0 or heartcrash%4!=3 and heartcrash<=0:
            if heartcrash2%4==1 and heartcrash2%4==2 and heartcrash2>0:
                my_image.paste(lelice,(int(my_circle.position[0]),int(my_circle.position[1])),mask=lelice)
            elif heartcrash2%4!=0 or heartcrash2%4!=3 and heartcrash2<=0:
                my_image.paste(lelice,(int(my_circle.position[0]),int(my_circle.position[1])),mask=lelice)
        
        
    if (lifenum==3):
        my_image.paste(ilife,(240-43, 3),mask=ilife)
        my_image.paste(ilife,(240-29, 3),mask=ilife)
        my_image.paste(ilife,(240-15, 3),mask=ilife)
    elif (lifenum==2):
        my_image.paste(ilife,(240-29, 3),mask=ilife)
        my_image.paste(ilife,(240-15, 3),mask=ilife)
    elif (lifenum==1):
        my_image.paste(ilife,(240-15, 3),mask=ilife)
    elif (lifenum==0):
        while True:
            ifail=Image.open('fail.png')
            my_image.paste(ifail,(0,0))
            if not joystick.button_B.value:
                lifenum=3
                break
            joystick.disp.image(my_image)
    

    #좌표는 동그라미의 왼쪽 위, 오른쪽 아래 점 (x1, y1, x2, y2)
    joystick.disp.image(my_image)
    
class R2miro4:
    def __init__(self, width, height):
        self.appearance = 'r2miro4'
        self.position = np.array([50, height/2 - 10, width, height/2 + 10])
        self.outline = "#FFFFFF"
        
    def notdown(self, ego_position, other_position):
        d=1
        if other_position[3] > ego_position[1] and other_position[2] > ego_position[0] and other_position[0] < ego_position[2] and other_position[1] < ego_position[1] :
            d=0
        return d
    
    def notright(self, ego_position, other_position):
    
        r=1
        if other_position[2] > ego_position[0] and other_position[1] < ego_position[3] and other_position[3] > ego_position[1] and other_position[0] < ego_position[0]:
            r=0
        return r
    
    def notup(self, ego_position, other_position):
    
        u=1
        if other_position[1] < ego_position[3] and other_position[0] > ego_position[0] and other_position[0] < ego_position[2] and other_position[3] > ego_position[3]:
            u=0
        return u
    
class Wall:
    def __init__(self,height):
        self.appearance = 'wall'
        #self.state = None
        self.position = np.array([0, height/2 - 8, 50, height/2 + 8])
        self.outline = "#FFFFFF"
        
    def notdown(self, ego_position, other_position):
        
        d=1
        if other_position[3] > ego_position[1] and other_position[2] > ego_position[0] and other_position[0] < ego_position[2] and other_position[1] < ego_position[1] :
            d=0
        return d
    
    def notright(self, ego_position, other_position):
        
        r=1
        if other_position[2] > ego_position[0] and other_position[1] < ego_position[3] and other_position[3] > ego_position[1] and other_position[0] < ego_position[0]:
            r=0
        return r
    
    def notup(self, ego_position, other_position):
        u=1
        if other_position[1] < ego_position[3] and other_position[0] > ego_position[0] and other_position[0] < ego_position[2] and other_position[3] > ego_position[3]:
            u=0
        return u
    
class Flower:
    def __init__(self, width, height):
        self.appearance = 'flower'
        #self.state = None
        self.position = np.array([width-40, height/2-40, width-10, height/2 - 10])
        # 총알 발사를 위한 캐릭터 중앙 점 추가
        self.outline = "#FFFFFF"
    
    def notleft(self, ego_position, other_position):
        l=0
        if other_position[0] < ego_position[2] and other_position[1] < ego_position[3] and other_position[3] > ego_position[1] and other_position[2] > ego_position[2]:
            l=1
        return l
    
    def notright(self, ego_position, other_position):

        r=0
        if other_position[2] > ego_position[0] and other_position[1] < ego_position[3] and other_position[3] > ego_position[1] and other_position[0] < ego_position[0]:
            r=1
        return r
    
    def notdown(self, ego_position, other_position):
    
        d=0
        if other_position[3] > ego_position[1] and other_position[0] < ego_position[2] and other_position[1] < ego_position[1] and other_position[2] > ego_position[0]:
            d=1
        return d
    
# 2라운드
my_circle = Character(joystick.width, joystick.height)
miro1 = Miro1(joystick.width, joystick.height)
miro2 = Miro2(joystick.width, joystick.height)
miro3 = Miro3(joystick.width, joystick.height)
r2miro4 = R2miro4(joystick.width, joystick.height)
miro5 = Miro5(joystick.width, joystick.height)
miro6 = Miro6(joystick.width, joystick.height)
heartcard = heartCard(joystick.width, joystick.height)
heartcard2 = heartCard2(joystick.width, joystick.height)
bottle = Bottle(joystick.width, joystick.height)
hole1 = Hole1(joystick.width, joystick.height)
wall=Wall(joystick.height)
flower=Flower(joystick.width,joystick.height)

ir2miro4=Image.open('r2miro4.png')
iwall=Image.open('wall.png')
openflower=Image.open('openflower.png')
closeflower=Image.open('closeflower.png')

bottle.position[0]=15
bottle.position[1]=205
bottle.position[2]=35
bottle.position[3]=joystick.height-2

heartcard.position[0]=joystick.width/2-10
heartcard.position[1]=joystick.height/2+10
heartcard.position[2]=joystick.width/2+6
heartcard.position[3]=joystick.height/2+34


heartcardslp2=0
heartcrash=30
heartcrash2=30
bottleeat=0
delice=0
floweropen=0
wallopen=0
while True:
    command = {'move': False, 'up_pressed': False , 'down_pressed': False, 'left_pressed': False, 'right_pressed': False}
    
    if not joystick.button_U.value:  # up pressed
        if miro1.notup(miro1.position, my_circle.position) and miro2.notup(miro2.position, my_circle.position) and r2miro4.notup(r2miro4.position, my_circle.position) and miro5.notup(miro5.position, my_circle.position) and wall.notup(wall.position,my_circle.position):
            command['up_pressed'] = True
            command['move'] = True
            
    
    if not joystick.button_D.value:  # down pressed
        if miro1.notdown(miro1.position, my_circle.position) and miro3.notdown(miro3.position, my_circle.position) and r2miro4.notdown(r2miro4.position, my_circle.position) and miro5.notdown(miro5.position, my_circle.position) and miro6.notdown(miro6.position, my_circle.position) and wall.notdown(wall.position,my_circle.position):
            command['down_pressed'] = True
            command['move'] = True

    if not joystick.button_L.value: 
        delice=1
        if miro1.notleft(miro1.position, my_circle.position) and miro2.notleft(miro2.position, my_circle.position) and miro3.notleft(miro3.position, my_circle.position) and miro5.notleft(miro5.position, my_circle.position) and miro6.notleft(miro6.position, my_circle.position):
            command['left_pressed'] = True
            command['move'] = True
            

    if not joystick.button_R.value: 
        delice=0
        if miro2.notright(miro2.position, my_circle.position) and miro3.notright(miro3.position, my_circle.position) and r2miro4.notright(r2miro4.position, my_circle.position) and miro5.notright(miro5.position, my_circle.position) and miro6.notright(miro6.position, my_circle.position) and wall.notright(wall.position,my_circle.position):
            command['right_pressed'] = True
            command['move'] = True
        
    if (heartcard.notup(heartcard.position,my_circle.position) or heartcard.notdown(heartcard.position,my_circle.position) or heartcard.notleft(heartcard.position,my_circle.position) or heartcard.notright(heartcard.position,my_circle.position)) and heartcrash>0:
        heartcrash-=1
        if heartcrash==29:
            lifenum-=1
    elif (heartcard2.notup(heartcard2.position,my_circle.position) or heartcard2.notdown(heartcard2.position,my_circle.position) or heartcard2.notleft(heartcard2.position,my_circle.position) or heartcard2.notright(heartcard2.position,my_circle.position)) and heartcrash2>0:
        heartcrash2-=1
        if heartcrash2==29:
            lifenum-=1
    else:
        my_circle.move(command)
        if heartcard2.position[2]==0:
            heartcardslp2=1
            heartcard2.position[0]=joystick.width/4-1
            heartcard2.position[1]=joystick.height-joystick.height/4-6
            heartcard2.position[2]=joystick.width/4
            heartcard2.position[3]=joystick.height-joystick.height/4+10
                    
        else:
            if heartcardslp2==0:
                heartcard2.position[0]-=2
                heartcard2.position[2]-=2
            else:
                if heartcard2.sleep==0:
                    heartcard2.position[0]=joystick.width/4-10
                    heartcard2.position[2]=joystick.width/4+14
                    heartcardslp2=0
                    heartcard2.sleep=20
                else:
                    heartcard2.sleep-=1
                    
    if (bottle.notup(bottle.position,my_circle.position) or bottle.notdown(bottle.position,my_circle.position) or bottle.notleft(bottle.position,my_circle.position) or bottle.notright(bottle.position,my_circle.position)) and bottleeat==0:  
        bottleeat=1   
        my_circle.position[0]+=8
        my_circle.position[1]+=12
        my_circle.position[2]-=8
        my_circle.position[3]-=12
        relice = relice.resize((8, 12))
        lelice = lelice.resize((8, 12))
    if (flower.notdown(flower.position,my_circle.position) or flower.notleft(flower.position,my_circle.position) or flower.notright(flower.position,my_circle.position)) and floweropen==0:  
        floweropen=1
        wallopen=1
        
    if (hole1.notup(hole1.position,my_circle.position) or hole1.notdown(hole1.position,my_circle.position) or hole1.notleft(hole1.position,my_circle.position) or hole1.notright(hole1.position,my_circle.position)):  
        break
    if (wallopen==1 and int(wall.position[0])<50):
        wall.position[0]+=1
        wall.position[2]+=1
    
    my_draw.rectangle((0, 0, joystick.width, joystick.height), fill = (255, 255, 255, 100))
    my_image.paste(iground,(0,0))
    my_draw.rectangle(tuple(heartcard.position), fill = (0, 0, 0,0))
    my_image.paste(iheartcard,(110,130))
    my_draw.rectangle(tuple(heartcard2.position), fill = (0, 0, 0,0))
    if heartcardslp2==0:
        my_image.paste(iheartcard2,(int(heartcard2.position[0]),int(heartcard2.position[1])))
    if bottleeat==0:
        my_draw.rectangle(tuple(bottle.position), fill = (0, 0, 0,0))
        my_image.paste(ibottle,(15,205),mask=ibottle)

    my_draw.rectangle(tuple(miro1.position), fill = (0, 0, 0,0))
    my_image.paste(imiro1,(0,50))
    my_draw.rectangle(tuple(miro2.position), fill = (0, 0, 0,0))
    my_image.paste(imiro2,(110, 0))
    my_draw.rectangle(tuple(miro3.position), fill = (0, 0, 0,0))
    my_image.paste(imiro3,(170, 50))
    my_draw.rectangle(tuple(wall.position),fill = (0, 0, 0,0))
    my_image.paste(iwall,(int(wall.position[0]), 112),mask=iwall)
    my_draw.rectangle(tuple(r2miro4.position),fill = (0, 0, 0,0))
    my_image.paste(ir2miro4,(50, 110))
    my_draw.rectangle(tuple(miro5.position), fill = (0, 0, 0,0))
    my_image.paste(imiro5,(50, 175))
    my_draw.rectangle(tuple(miro6.position), fill = (0, 0, 0,0))
    my_image.paste(imiro6,(50, 175))
    my_draw.ellipse(tuple(hole1.position), fill = (100, 70, 30, 255))
    
    if floweropen==0:
        my_image.paste(closeflower,(200, 80),mask=closeflower)
    elif floweropen==1:
        my_image.paste(openflower,(200,80),mask=openflower)
    if delice==0:
        my_draw.ellipse(tuple(my_circle.position),fill = (0, 0,0,0))
        if heartcrash%4==1 and heartcrash%4==2 and heartcrash>0:
            if heartcrash2%4==1 and heartcrash2%4==2 and heartcrash2>0:
                my_image.paste(relice,(int(my_circle.position[0]),int(my_circle.position[1])),mask=relice)
            elif heartcrash2%4!=0 or heartcrash2%4!=3 and heartcrash2<=0:
                my_image.paste(relice,(int(my_circle.position[0]),int(my_circle.position[1])),mask=relice)
        elif heartcrash%4!=0 or heartcrash%4!=3 and heartcrash<=0:
            if heartcrash2%4==1 and heartcrash2%4==2 and heartcrash2>0:
                my_image.paste(relice,(int(my_circle.position[0]),int(my_circle.position[1])),mask=relice)
            elif heartcrash2%4!=0 or heartcrash2%4!=3 and heartcrash2<=0:
                my_image.paste(relice,(int(my_circle.position[0]),int(my_circle.position[1])),mask=relice)
        
    elif delice==1:
        my_draw.ellipse(tuple(my_circle.position),fill = (0, 0, 0,0))
        if heartcrash%4==1 and heartcrash%4==2 and heartcrash>0:
            if heartcrash2%4==1 and heartcrash2%4==2 and heartcrash2>0:
                my_image.paste(lelice,(int(my_circle.position[0]),int(my_circle.position[1])),mask=lelice)
            elif heartcrash2%4!=0 or heartcrash2%4!=3 and heartcrash2<=0:
                my_image.paste(lelice,(int(my_circle.position[0]),int(my_circle.position[1])),mask=lelice)
        elif heartcrash%4!=0 or heartcrash%4!=3 and heartcrash<=0:
            if heartcrash2%4==1 and heartcrash2%4==2 and heartcrash2>0:
                my_image.paste(lelice,(int(my_circle.position[0]),int(my_circle.position[1])),mask=lelice)
            elif heartcrash2%4!=0 or heartcrash2%4!=3 and heartcrash2<=0:
                my_image.paste(lelice,(int(my_circle.position[0]),int(my_circle.position[1])),mask=lelice)
        
        
    if (lifenum==3):
        my_image.paste(ilife,(240-43, 3),mask=ilife)
        my_image.paste(ilife,(240-29, 3),mask=ilife)
        my_image.paste(ilife,(240-15, 3),mask=ilife)
    elif (lifenum==2):
        my_image.paste(ilife,(240-29, 3),mask=ilife)
        my_image.paste(ilife,(240-15, 3),mask=ilife)
    elif (lifenum==1):
        my_image.paste(ilife,(240-15, 3),mask=ilife)
    elif (lifenum==0):
        while True:
            ifail=Image.open('fail.png')
            my_image.paste(ifail,(0,0))
            if not joystick.button_B.value:
                lifenum=3
                break
            joystick.disp.image(my_image)
        
    joystick.disp.image(my_image)  
    
class R3miro4:
    def __init__(self, width, height):
        self.appearance = 'r3miro4'
        #self.state = None
        self.position = np.array([0, height/2 - 10, width, height/2 + 10])
        self.outline = "#FFFFFF"
        
    def notdown(self, ego_position, other_position):
    
        d=1
        if other_position[3] > ego_position[1] and other_position[2] > ego_position[0] and other_position[0] < ego_position[2] and other_position[1] < ego_position[1] :
            d=0
        return d
    
    def notright(self, ego_position, other_position):
        r=1
        if other_position[2] > ego_position[0] and other_position[1] < ego_position[3] and other_position[3] > ego_position[1] and other_position[0] < ego_position[0]:
            r=0
        return r
    
    def notup(self, ego_position, other_position):
       
        u=1
        if other_position[1] < ego_position[3] and other_position[0] > ego_position[0] and other_position[0] < ego_position[2] and other_position[3] > ego_position[3]:
            u=0
        return u
    
class Cat:
    def __init__(self, width, height):
        self.appearance = 'flower'
        #self.state = None
        self.position = np.array([width-40, height/2-30, width-10, height/2 - 10])
        # 총알 발사를 위한 캐릭터 중앙 점 추가
        self.outline = "#FFFFFF"
    
    
    def notleft(self, ego_position, other_position):
        
        l=0
        if other_position[0] < ego_position[2] and other_position[1] < ego_position[3] and other_position[3] > ego_position[1] and other_position[2] > ego_position[2]:
            l=1
        return l
    
    def notright(self, ego_position, other_position):
        
        r=0
        if other_position[2] > ego_position[0] and other_position[1] < ego_position[3] and other_position[3] > ego_position[1] and other_position[0] < ego_position[0]:
            r=1
        return r
    
    def notdown(self, ego_position, other_position):
        
        d=0
        if other_position[3] > ego_position[1] and other_position[0] < ego_position[2] and other_position[1] < ego_position[1] and other_position[2] > ego_position[0]:
            d=1
        return d
    
#3라운드
my_circle = Character(joystick.width, joystick.height)
my_circle.position[0]+=8
my_circle.position[1]+=12
my_circle.position[2]-=8
my_circle.position[3]-=12
miro1 = Miro1(joystick.width, joystick.height)
miro2 = Miro2(joystick.width, joystick.height)
miro3 = Miro3(joystick.width, joystick.height)
r3miro4 = R3miro4(joystick.width, joystick.height)
miro5 = Miro5(joystick.width, joystick.height)
miro6 = Miro6(joystick.width, joystick.height)
heartcard = heartCard(joystick.width, joystick.height)
heartcard.position[0]=joystick.width-joystick.width/4-8
heartcard.position[1]=joystick.height-joystick.height/4-1
heartcard.position[2]=joystick.width-joystick.width/4+8
heartcard.position[3]=joystick.height-joystick.height/4
mushroom = Mushroom(joystick.width, joystick.height)
hole1 = Hole1(joystick.width, joystick.height)
cat = Cat(joystick.width, joystick.height)

ir3miro4=Image.open('r3miro4.png')
icat=Image.open('cat.png')
irevcat=Image.open('revcat.png')

heartcardslp=0
heartcrash=30

mushroomeat=0
delice=0
win=0
catport=0
while True:
    command = {'move': False, 'up_pressed': False , 'down_pressed': False, 'left_pressed': False, 'right_pressed': False}
    
    if not joystick.button_U.value:  # up pressed
        if miro1.notup(miro1.position, my_circle.position) and miro2.notup(miro2.position, my_circle.position) and r3miro4.notup(r3miro4.position, my_circle.position) and miro5.notup(miro5.position, my_circle.position):
            command['up_pressed'] = True
            command['move'] = True
            
            
    
    if not joystick.button_D.value:  # down pressed
        if miro1.notdown(miro1.position, my_circle.position) and miro3.notdown(miro3.position, my_circle.position) and r3miro4.notdown(r3miro4.position, my_circle.position) and miro5.notdown(miro5.position, my_circle.position) and miro6.notdown(miro6.position, my_circle.position):
            command['down_pressed'] = True
            command['move'] = True
            

    if not joystick.button_L.value: 
        delice=1
        if miro1.notleft(miro1.position, my_circle.position) and miro2.notleft(miro2.position, my_circle.position) and miro3.notleft(miro3.position, my_circle.position) and miro5.notleft(miro5.position, my_circle.position) and miro6.notleft(miro6.position, my_circle.position):
            command['left_pressed'] = True
            command['move'] = True
            
    if not joystick.button_R.value: 
        delice=0
        if miro2.notright(miro2.position, my_circle.position) and miro3.notright(miro3.position, my_circle.position) and miro5.notright(miro5.position, my_circle.position) and miro6.notright(miro6.position, my_circle.position):
            command['right_pressed'] = True
            command['move'] = True
            
      
       
    if (heartcard.notup(heartcard.position,my_circle.position) or heartcard.notdown(heartcard.position,my_circle.position) or heartcard.notleft(heartcard.position,my_circle.position) or heartcard.notright(heartcard.position,my_circle.position)) and heartcrash>0:
        heartcrash-=1
        if heartcrash==29:
            lifenum-=1
    else:
        my_circle.move(command)
        
        if heartcard.position[1]==joystick.width:
            heartcardslp=1
            heartcard.position[0]=joystick.width-joystick.width/4-8
            heartcard.position[1]=joystick.height-joystick.height/4-1
            heartcard.position[2]=joystick.width-joystick.width/4+8
            heartcard.position[3]=joystick.height-joystick.height/4
                    
        else:
            if heartcardslp==0:
                heartcard.position[1]+=1
                heartcard.position[3]+=1
            else:
                if heartcard.sleep==0:
                    heartcard.position[1]=joystick.height-joystick.height/4
                    heartcard.position[3]=joystick.height-joystick.height/4+24
                    heartcardslp=0
                    heartcard.sleep=20
                else:
                    heartcard.sleep-=1
        
    if (mushroom.notup(mushroom.position,my_circle.position) or mushroom.notdown(mushroom.position,my_circle.position) or mushroom.notleft(mushroom.position,my_circle.position) or mushroom.notright(mushroom.position,my_circle.position)) and mushroomeat==0:  
        mushroomeat=1   
        my_circle.position[0]-=8
        my_circle.position[1]-=12
        my_circle.position[2]+=8
        my_circle.position[3]+=12
        relice=Image.open('elicer.png')
        lelice=Image.open('elicel.png')
    if (hole1.notup(hole1.position,my_circle.position) or hole1.notdown(hole1.position,my_circle.position) or hole1.notleft(hole1.position,my_circle.position) or hole1.notright(hole1.position,my_circle.position)):  
        win=1
        break
    
    if cat.notdown(cat.position,my_circle.position) and catport==0:
        my_circle.position[0]=15
        my_circle.position[1]=joystick.height/2+15
        my_circle.position[2]=25
        my_circle.position[3]=joystick.height/2+35
        catport=1
    
    #그리는 순서가 중요합니다. 배경을 먼저 깔고 위에 그림을 그리고 싶었는데 그림을 그려놓고 배경으로 덮는 결과로 될 수 있습니다.
    my_draw.rectangle((0, 0, joystick.width, joystick.height), fill = (255, 255, 255, 100))
    my_image.paste(iground,(0,0))
    my_draw.rectangle(tuple(heartcard.position), fill = (0, 0, 0,0))
    
    if heartcardslp==0:
        my_image.paste(iheartcard,(int(heartcard.position[0]),int(heartcard.position[1])))
    
    if mushroomeat==0:
        my_draw.rectangle(tuple(mushroom.position), fill = (0, 0, 0,0))
        my_image.paste(imushroom,(10, 205),mask=imushroom)
    my_draw.rectangle(tuple(miro1.position), fill = (0, 0, 0,0))
    my_image.paste(imiro1,(0,50))
    my_draw.rectangle(tuple(miro2.position), fill = (0, 0, 0,0))
    my_image.paste(imiro2,(110, 0))
    my_draw.rectangle(tuple(miro3.position), fill = (0, 0, 0,0))
    my_image.paste(imiro3,(170, 50))
    my_draw.rectangle(tuple(r3miro4.position),fill = (0, 0, 0,0))
    my_image.paste(ir3miro4,(0, 110))
    my_draw.rectangle(tuple(miro5.position), fill = (0, 0, 0,0))
    my_image.paste(imiro5,(50, 175))
    my_draw.rectangle(tuple(miro6.position), fill = (0, 0, 0,0))
    my_image.paste(imiro6,(50, 175))
    my_draw.ellipse(tuple(hole1.position), fill = (100, 70, 30, 255))
    if delice==0:
        my_draw.ellipse(tuple(my_circle.position),fill = (0, 0,0,0))
        if heartcrash%4==1 and heartcrash%4==2 and heartcrash>0:
            my_image.paste(relice,(int(my_circle.position[0]),int(my_circle.position[1])),mask=relice)
        elif heartcrash%4!=0 or heartcrash%4!=3 and heartcrash<=0:
            my_image.paste(relice,(int(my_circle.position[0]),int(my_circle.position[1])),mask=relice)
        
    elif delice==1:
        my_draw.ellipse(tuple(my_circle.position),fill = (0, 0, 0,0))
        if heartcrash%4==1 and heartcrash%4==2 and heartcrash>0:
            my_image.paste(lelice,(int(my_circle.position[0]),int(my_circle.position[1])),mask=lelice)
        elif heartcrash%4!=0 or heartcrash%4!=3 and heartcrash<=0:
            my_image.paste(lelice,(int(my_circle.position[0]),int(my_circle.position[1])),mask=lelice)
    
    
    my_image.paste(icat,(200, 90),mask=icat)
    my_image.paste(irevcat,(10, 130),mask=irevcat)
        
        
    if (lifenum==3):
        my_image.paste(ilife,(240-43, 3),mask=ilife)
        my_image.paste(ilife,(240-29, 3),mask=ilife)
        my_image.paste(ilife,(240-15, 3),mask=ilife)
    elif (lifenum==2):
        my_image.paste(ilife,(240-29, 3),mask=ilife)
        my_image.paste(ilife,(240-15, 3),mask=ilife)
    elif (lifenum==1):
        my_image.paste(ilife,(240-15, 3),mask=ilife)
    elif (lifenum==0):
        while True:
            ifail=Image.open('fail.png')
            my_image.paste(ifail,(0,0))
            if not joystick.button_B.value:
                lifenum=3
                break
            joystick.disp.image(my_image)
        
    joystick.disp.image(my_image)   
    
iwin=Image.open('win.png')
ifail=Image.open('fail.png')
if win==1:
    while True:
        my_image.paste(iwin,(0,0))
        joystick.disp.image(my_image)   