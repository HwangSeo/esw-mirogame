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
    '''           
    def collision_check(self, enemys):
        for enemy in enemys:
            collision = self.overlap(self.position, enemy.position)
            
            if collision:
                enemy.state = 'die'
                self.state = 'hit'
    '''
class Miro1:
    def __init__(self, width, height):
        self.appearance = 'miro1'
        #self.state = None
        self.position = np.array([0, height/4 - 10, width/4 + 10, height/4 + 10])
        # 총알 발사를 위한 캐릭터 중앙 점 추가
        # self.center = np.array([(self.position[0] + self.position[2]) - 10, (self.position[1] + self.position[3]) / 2])
        self.outline = "#FFFFFF"
        
    def notdown(self, ego_position, other_position):
        '''
        두개의 사각형(bullet position, enemy position)이 겹치는지 확인하는 함수
        좌표 표현 : [x1, y1, x2, y2]
        
        return :
            True : if overlap
            False : if not overlap
            
        '''
        d=1
        if other_position[3] > ego_position[1] and other_position[0] > ego_position[0] and other_position[0] < ego_position[2] and other_position[1] < ego_position[1]:
            d=0
        return d
    
    def notleft(self, ego_position, other_position):
        '''
        두개의 사각형(bullet position, enemy position)이 겹치는지 확인하는 함수
        좌표 표현 : [x1, y1, x2, y2]
        
        return :
            True : if overlap
            False : if not overlap
            
        '''
        l=1
        if other_position[0] < ego_position[2] and other_position[1] < ego_position[3] and other_position[3] > ego_position[1] and other_position[2] > ego_position[2]:
            l=0
        return l
    
    def notup(self, ego_position, other_position):
        '''
        두개의 사각형(bullet position, enemy position)이 겹치는지 확인하는 함수
        좌표 표현 : [x1, y1, x2, y2]
        
        return :
            True : if overlap
            False : if not overlap
            
        '''
        u=1
        if other_position[1] < ego_position[3] and other_position[0] > ego_position[0] and other_position[0] < ego_position[2] and other_position[3] > ego_position[3]:
            u=0
        return u
class heartCard:
    def __init__(self, width, height):
        '''
        position : 총알을 발사한 Character의 중앙 위치
        command : 조이스틱 입력 값
        '''
        self.appearance = 'heartcard'
        self.sleep=20
        #self.speed = 20
        #self.damage = 10
        self.position = np.array([width/4-8, height/4-10, width/4+8, height/4+14])
        #self.center = np.array([(self.position[0] + self.position[2]) / 2, (self.position[1] + self.position[3]) / 2])

        #self.direction = {'up' : False, 'down' : False, 'left' : False, 'right' : False}
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
        
# 잔상이 남지 않는 코드 & 대각선 이동 가능
class heartCard2:
    def __init__(self, width, height):
        
        self.appearance = 'heartcard2'
        self.sleep=20
        #self.speed = 20
        #self.damage = 10
        self.position = np.array([width/4-10, height-height/4-8, width/4+14, height-height/4+8])
        #self.center = np.array([(self.position[0] + self.position[2]) / 2, (self.position[1] + self.position[3]) / 2])

        #self.direction = {'up' : False, 'down' : False, 'left' : False, 'right' : False}
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
        #self.speed = 20
        #self.damage = 10
        self.position = np.array([width-width/4+25, height/4+13, width-15, height/2-13])
        #self.center = np.array([(self.position[0] + self.position[2]) / 2, (self.position[1] + self.position[3]) / 2])

        #self.direction = {'up' : False, 'down' : False, 'left' : False, 'right' : False}
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
        #self.state = None
        self.position = np.array([width/2-10, 0, width/2 + 10, height/4 + 10])
        # 총알 발사를 위한 캐릭터 중앙 점 추가
        self.outline = "#FFFFFF"
    
    def notleft(self, ego_position, other_position):
        '''
        두개의 사각형(bullet position, enemy position)이 겹치는지 확인하는 함수
        좌표 표현 : [x1, y1, x2, y2]
        
        return :
            True : if overlap
            False : if not overlap
            
        '''
        l=1
        if other_position[0] < ego_position[2] and other_position[1] < ego_position[3] and other_position[3] > ego_position[1] and other_position[2] > ego_position[2]:
            l=0
        return l
    
    def notright(self, ego_position, other_position):
        '''
        두개의 사각형(bullet position, enemy position)이 겹치는지 확인하는 함수
        좌표 표현 : [x1, y1, x2, y2]
        
        return :
            True : if overlap
            False : if not overlap
            
        '''
        r=1
        if other_position[2] > ego_position[0] and other_position[1] < ego_position[3] and other_position[3] > ego_position[1] and other_position[0] < ego_position[0]:
            r=0
        return r
    
    def notup(self, ego_position, other_position):
        '''
        두개의 사각형(bullet position, enemy position)이 겹치는지 확인하는 함수
        좌표 표현 : [x1, y1, x2, y2]
        
        return :
            True : if overlap
            False : if not overlap
            
        '''
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
        '''
        두개의 사각형(bullet position, enemy position)이 겹치는지 확인하는 함수
        좌표 표현 : [x1, y1, x2, y2]
        
        return :
            True : if overlap
            False : if not overlap
            
        '''
        l=1
        if other_position[0] < ego_position[2] and other_position[1] < ego_position[3] and other_position[3] > ego_position[1] and other_position[2] > ego_position[2]:
            l=0
        return l
    
    def notright(self, ego_position, other_position):
        '''
        두개의 사각형(bullet position, enemy position)이 겹치는지 확인하는 함수
        좌표 표현 : [x1, y1, x2, y2]
        
        return :
            True : if overlap
            False : if not overlap
            
        '''
        r=1
        if other_position[2] > ego_position[0] and other_position[1] < ego_position[3] and other_position[3] > ego_position[1] and other_position[0] < ego_position[0]:
            r=0
        return r
    
    def notdown(self, ego_position, other_position):
        '''
        두개의 사각형(bullet position, enemy position)이 겹치는지 확인하는 함수
        좌표 표현 : [x1, y1, x2, y2]
        
        return :
            True : if overlap
            False : if not overlap
            
        '''
        d=1
        if other_position[3] > ego_position[1] and other_position[0] < ego_position[2] and other_position[1] < ego_position[1] and other_position[2] > ego_position[0]:
            d=0
        return d
    
class Miro4:
    def __init__(self, width, height):
        self.appearance = 'miro4'
        #self.state = None
        self.position = np.array([10, height/2 - 10, width, height/2 + 10])
        self.outline = "#FFFFFF"
        
    def notdown(self, ego_position, other_position):
        '''
        두개의 사각형(bullet position, enemy position)이 겹치는지 확인하는 함수
        좌표 표현 : [x1, y1, x2, y2]
        
        return :
            True : if overlap
            False : if not overlap
            
        '''
        d=1
        if other_position[3] > ego_position[1] and other_position[2] > ego_position[0] and other_position[0] < ego_position[2] and other_position[1] < ego_position[1] :
            d=0
        return d
    
    def notright(self, ego_position, other_position):
        '''
        두개의 사각형(bullet position, enemy position)이 겹치는지 확인하는 함수
        좌표 표현 : [x1, y1, x2, y2]
        
        return :
            True : if overlap
            False : if not overlap
            
        '''
        r=1
        if other_position[2] > ego_position[0] and other_position[1] < ego_position[3] and other_position[3] > ego_position[1] and other_position[0] < ego_position[0]:
            r=0
        return r
    
    def notup(self, ego_position, other_position):
        '''
        두개의 사각형(bullet position, enemy position)이 겹치는지 확인하는 함수
        좌표 표현 : [x1, y1, x2, y2]
        
        return :
            True : if overlap
            False : if not overlap
            
        '''
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
        '''
        두개의 사각형(bullet position, enemy position)이 겹치는지 확인하는 함수
        좌표 표현 : [x1, y1, x2, y2]
        
        return :
            True : if overlap
            False : if not overlap
            
        '''
        d=1
        if other_position[3] > ego_position[1] and other_position[2] > ego_position[0] and other_position[0] < ego_position[2] and other_position[1] < ego_position[1] :
            d=0
        return d
    
    def notright(self, ego_position, other_position):
        '''
        두개의 사각형(bullet position, enemy position)이 겹치는지 확인하는 함수
        좌표 표현 : [x1, y1, x2, y2]
        
        return :
            True : if overlap
            False : if not overlap
            
        '''
        r=1
        if other_position[2] > ego_position[0] and other_position[1] < ego_position[3] and other_position[3] > ego_position[1] and other_position[0] < ego_position[0]:
            r=0
        return r
    
    def notleft(self, ego_position, other_position):
        '''
        두개의 사각형(bullet position, enemy position)이 겹치는지 확인하는 함수
        좌표 표현 : [x1, y1, x2, y2]
        
        return :
            True : if overlap
            False : if not overlap
            
        '''
        l=1
        if other_position[0] < ego_position[2] and other_position[1] < ego_position[3] and other_position[3] > ego_position[1] and other_position[2] > ego_position[2]:
            l=0
        return l
    
    def notup(self, ego_position, other_position):
        '''
        두개의 사각형(bullet position, enemy position)이 겹치는지 확인하는 함수
        좌표 표현 : [x1, y1, x2, y2]
        
        return :
            True : if overlap
            False : if not overlap
            
        '''
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
        '''
        두개의 사각형(bullet position, enemy position)이 겹치는지 확인하는 함수
        좌표 표현 : [x1, y1, x2, y2]
        
        return :
            True : if overlap
            False : if not overlap
            
        '''
        l=1
        if other_position[0] < ego_position[2] and other_position[1] < ego_position[3] and other_position[3] > ego_position[1] and other_position[2] > ego_position[2]:
            l=0
        return l
    
    def notright(self, ego_position, other_position):
        '''
        두개의 사각형(bullet position, enemy position)이 겹치는지 확인하는 함수
        좌표 표현 : [x1, y1, x2, y2]
        
        return :
            True : if overlap
            False : if not overlap
            
        '''
        r=1
        if other_position[2] > ego_position[0] and other_position[1] < ego_position[3] and other_position[3] > ego_position[1] and other_position[0] < ego_position[0]:
            r=0
        return r
    
    def notdown(self, ego_position, other_position):
        '''
        두개의 사각형(bullet position, enemy position)이 겹치는지 확인하는 함수
        좌표 표현 : [x1, y1, x2, y2]
        
        return :
            True : if overlap
            False : if not overlap
            
        '''
        d=1
        if other_position[3] > ego_position[1] and other_position[0] < ego_position[2] and other_position[1] < ego_position[1] and other_position[2] > ego_position[0]:
            d=0
        return d
'''
class HeartCard:
    def __init__(self, position, command):
        
        position : 총알을 발사한 Character의 중앙 위치
        command : 조이스틱 입력 값
        
        self.appearance = 'rectangle'
        self.speed = 20
        self.damage = 10
        self.position = np.array([position[0]-3, position[1]-3, position[0]+3, position[1]+3])
        self.center = np.array([(self.position[0] + self.position[2]) / 2, (self.position[1] + self.position[3]) / 2])

        self.direction = {'up' : False, 'down' : False, 'left' : False, 'right' : False}
        self.state = None
        self.outline = "#0000FF"
        
        if command['up_pressed']:
            self.direction['up'] = True
        if command['down_pressed']:
            self.direction['down'] = True
        if command['right_pressed']:
            self.direction['right'] = True
        if command['left_pressed']:
            self.direction['left'] = True

    def move(self):
        if self.direction['up']:
            self.position[1] -= self.speed
            self.position[3] -= self.speed

        if self.direction['down']:
            self.position[1] += self.speed
            self.position[3] += self.speed

        if self.direction['left']:
            self.position[0] -= self.speed
            self.position[2] -= self.speed
            
        if self.direction['right']:
            self.position[0] += self.speed
            self.position[2] += self.speed
    '''
joystick = Joystick() #조이스틱 객체 선언
my_image = Image.new("RGB", (joystick.width, joystick.height)) #게임 배경 만듬?? 내가 만든 배경을 넣으려면 어떻게 할까
my_draw = ImageDraw.Draw(my_image) #도화지와 도구를 연결 
# 잔상이 남지 않는 코드 & 대각선 이동 가능
my_circle = Character(joystick.width, joystick.height)
my_draw.rectangle((0, 0, joystick.width, joystick.height), fill = (255, 255, 255, 100))
miro1 = Miro1(joystick.width, joystick.height)
my_draw.rectangle(tuple(miro1.position), outline = miro1.outline, fill = (0, 0, 255))
miro2 = Miro2(joystick.width, joystick.height)
my_draw.rectangle(tuple(miro2.position), outline = miro2.outline, fill = (0, 0, 255))
miro3 = Miro3(joystick.width, joystick.height)
my_draw.rectangle(tuple(miro3.position), outline = miro3.outline, fill = (0, 0, 255))
miro4 = Miro4(joystick.width, joystick.height)
my_draw.rectangle(tuple(miro4.position), outline = miro4.outline, fill = (0, 0, 255))
miro5 = Miro5(joystick.width, joystick.height)
my_draw.rectangle(tuple(miro5.position), outline = miro5.outline, fill = (0, 0, 255))
miro6 = Miro6(joystick.width, joystick.height)
my_draw.rectangle(tuple(miro6.position), outline = miro6.outline, fill = (0, 0, 255))
heartcard = heartCard(joystick.width, joystick.height)
my_draw.rectangle(tuple(heartcard.position), outline = heartcard.outline, fill = (0, 0, 255))
heartcard2 = heartCard2(joystick.width, joystick.height)
my_draw.rectangle(tuple(heartcard2.position), outline = heartcard2.outline, fill = (0, 0, 255))
bottle = Bottle(joystick.width, joystick.height)
my_draw.rectangle(tuple(bottle.position), outline = bottle.outline, fill = (0, 0, 255))
'''
enemy_1 = Enemy((50, 50))
enemy_2 = Enemy((200, 200))
enemy_3 = Enemy((150, 50))

enemys_list = [enemy_1, enemy_2, enemy_3]


bullets = []
'''
heartcardslp=0
heartcardslp2=0
heartcrash=30
heartcrash2=30
bottleeat=0
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

    if not joystick.button_L.value:  # left pressed
        if miro1.notleft(miro1.position, my_circle.position) and miro2.notleft(miro2.position, my_circle.position) and miro3.notleft(miro3.position, my_circle.position) and miro5.notleft(miro5.position, my_circle.position) and miro6.notleft(miro6.position, my_circle.position):
            command['left_pressed'] = True
            command['move'] = True

    if not joystick.button_R.value:  # right pressed
        if miro2.notright(miro2.position, my_circle.position) and miro3.notright(miro3.position, my_circle.position) and miro4.notright(miro4.position, my_circle.position) and miro5.notright(miro5.position, my_circle.position) and miro6.notright(miro6.position, my_circle.position):
            command['right_pressed'] = True
            command['move'] = True
    '''
    if not joystick.button_A.value: # A pressed
        bullet = Bullet(my_circle.center, command)
        bullets.append(bullet)
    '''
    
        
    if (heartcard.notup(heartcard.position,my_circle.position) or heartcard.notdown(heartcard.position,my_circle.position) or heartcard.notleft(heartcard.position,my_circle.position) or heartcard.notright(heartcard.position,my_circle.position)) and heartcrash!=0:
        heartcrash-=1
        
    elif (heartcard2.notup(heartcard2.position,my_circle.position) or heartcard2.notdown(heartcard2.position,my_circle.position) or heartcard2.notleft(heartcard2.position,my_circle.position) or heartcard2.notright(heartcard2.position,my_circle.position)) and heartcrash2!=0:
        heartcrash2-=1
    
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
            heartcard2.position[1]=joystick.height-joystick.height/4-8
            heartcard2.position[2]=joystick.width/4
            heartcard2.position[3]=joystick.height-joystick.height/4+8
                    
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
        
    #그리는 순서가 중요합니다. 배경을 먼저 깔고 위에 그림을 그리고 싶었는데 그림을 그려놓고 배경으로 덮는 결과로 될 수 있습니다.
    my_draw.rectangle((0, 0, joystick.width, joystick.height), fill = (255, 255, 255, 100))
    my_draw.rectangle(tuple(heartcard.position), outline = heartcard.outline, fill = (0, 0, 255))
    my_draw.rectangle(tuple(heartcard2.position), outline = heartcard2.outline, fill = (0, 0, 255))
    if bottleeat==0:
        my_draw.rectangle(tuple(bottle.position), outline = bottle.outline, fill = (0, 0, 255))
    my_draw.rectangle(tuple(miro1.position), outline = miro1.outline, fill = (0, 0, 255))
    my_draw.rectangle(tuple(miro2.position), outline = miro2.outline, fill = (0, 0, 255))
    my_draw.rectangle(tuple(miro3.position), outline = miro3.outline, fill = (0, 0, 255))
    my_draw.rectangle(tuple(miro4.position), outline = miro4.outline, fill = (0, 0, 255))
    my_draw.rectangle(tuple(miro5.position), outline = miro5.outline, fill = (0, 0, 255))
    my_draw.rectangle(tuple(miro6.position), outline = miro6.outline, fill = (0, 0, 255))
    my_draw.ellipse(tuple(my_circle.position), outline = my_circle.outline, fill = (0, 0, 0))
    '''
    for enemy in enemys_list:
        if enemy.state != 'die':
            my_draw.ellipse(tuple(enemy.position), outline = enemy.outline, fill = (255, 0, 0))

    for bullet in bullets:
        if bullet.state != 'hit':
            my_draw.rectangle(tuple(bullet.position), outline = bullet.outline, fill = (0, 0, 255))
    '''

    #좌표는 동그라미의 왼쪽 위, 오른쪽 아래 점 (x1, y1, x2, y2)
    joystick.disp.image(my_image)
    #11/19 4:24 수정