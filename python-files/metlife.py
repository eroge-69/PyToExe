import random
import time
import pyautogui
import keyboard
from playsound import playsound
import pyautogui
import cv2
import numpy as np


class Database:
    def __init__ (self, images=None, regions_for=None, dot_colors=None, already_converted=False):
        self.images = images
        self.dot_colors = dot_colors
        self.regions_for = regions_for
        
        if type(self.images) != list and self.images!= None:
            self.images = [self.images] 
        if type(self.regions_for) != list and self.regions_for!= None:
            self.regions_for = [self.regions_for] 
        if type(self.dot_colors) != list and self.dot_colors!= None:
            self.dot_colors = [self.dot_colors] 
        if type(self.regions_for) != list and self.regions_for!= None:
            self.regions_for = [self.regions_for]
        
        if images != None:
            self.images = [cv2.cvtColor(cv2.imread(image+'.png'), cv2.COLOR_BGR2GRAY) for image in self.images]

        
            
        if self.regions_for != [] and not already_converted:
            screen_size_x, screen_size_y = pyautogui.size()
            coof_x, coof_y = (screen_size_x/1920, screen_size_y/954)
            for index, regs in enumerate(self.regions_for):
                temp = []
                for index2, reg in enumerate(regs):
                    if index2%2 == 0:
                        coof = coof_x
                    else:
                        coof = coof_y
                    temp.append(int(reg*coof))
                self.regions_for[index] = tuple(temp)
    def search_dot (self, need_to_click = True, waiting_for_hide = False, offsetX=0, offsetY=0):
        """searchs dot

        Args:
            need_to_click (bool, optional): Clicks on found element. Defaults to True.
            waiting_for_hide (bool, optional): Return True when element will hide (instead of appear). Defaults False.

        Returns:
            bool: True if found the dot
        """
        if self.regions_for == None or self.dot_colors == None:
            return "Add coordinates and color of the dot what you search!"
        
        for color in self.dot_colors:
            for reg in self.regions_for:
                if len(reg) == 2:
                    temp_reg = list(reg)
                    temp_reg.append(1)
                    temp_reg.append(1)
                    reg = tuple(temp_reg)
                screen = pyautogui.screenshot(region=reg)
                pixels = screen.load()
                        
                for x in range(screen.width):
                    for y in range(screen.height):
                        if pixels[x,y] == color:
                            if waiting_for_hide:
                                return None
                            else:
                                if need_to_click:
                                    pyautogui.click(x+reg[0]+offsetX, y+reg[1]+offsetY)
                                return True
        if waiting_for_hide:
            return True
                
    def search_pix (self, need_to_click = True, waiting_for_hide = False, persentage = 0.8, offsetX = 0, offsetY=0):
        """searchs image in specific region

        Args:
            need_to_click (bool, optional): Clicks on found element. Defaults to True.
            waiting_for_hide (bool, optional): Waiting, return True when element will hide (instead of appear). Defaults to False. 
            Cannot click and waiting for hide in the same moment

        Returns:
            bool: True if found the image
        """
        #if self.image == None or self.regions_for == None:
         #   return "Add coordinates and color of the dot what you search!"
        
        for reg in self.regions_for:
            screenshot = cv2.cvtColor(np.array(pyautogui.screenshot(region=reg)), cv2.COLOR_RGB2GRAY)
            for img in self.images:
                _, max_val, _ , max_loc = cv2.minMaxLoc(cv2.matchTemplate(screenshot, img, cv2.TM_CCOEFF_NORMED)) 
                print(max_val, max_loc)
                if waiting_for_hide:
                    max_val, persentage = max_val * -1, persentage * -1 
                    need_to_click = False
                if max_val > persentage:
                    if need_to_click:
                        pyautogui.click(max_loc[0] + reg[0]+offsetX, max_loc[1] + reg[1]+offsetY)
                    return True
                
                
if __name__ == "__main__":                
    p1 = Database(dot_colors=[(23, 131, 255),(0, 119, 255)], regions_for=(260,250))
    p1.search_dot()

    p2 = Database(dot_colors=(23, 131, 255), regions_for=(260,250))
    p2.search_dot()

    to_you = Database('continue_letter', 'continue_letter_alt', (300,340,150,370))
    to_you.search_pix()

    to_you2 = Database(['to_you', 'reply'], [(180,200,300,250),(180,200,300,250)])
    to_you.search_pix()
    
    
    
    
    
screen_size_x, screen_size_y = pyautogui.size()
next_button = Database(['next_button'], regions_for=[(0, 0, screen_size_x, screen_size_y)], already_converted=True)
answer_circle = Database(['answer_circle'], regions_for=[(0, 0, screen_size_x, screen_size_y)], already_converted=True)
working = True
while True:
    
    if working:
        if keyboard.is_pressed('q') or answer_circle.search_pix(need_to_click=False):
            working = False
            time.sleep(1)
        
        pause = 200 + random.randint(-1000,1000)/10
        print(pause)
        n=0
        while n < pause:
            n += 1
            
            if keyboard.is_pressed('q') or answer_circle.search_pix(need_to_click=False):
                working = False
                # time.sleep(1)
                break
            time.sleep(0.1)
            
        while not next_button.search_pix():
            pyautogui.scroll(-200)
            if keyboard.is_pressed('q') or answer_circle.search_pix(need_to_click=False):
                working = False
                time.sleep(1)
                break
    playsound('CLAP.mp3')
    while not working:
        if keyboard.is_pressed('q'):
            working = True
            time.sleep(1)
            
                
                
        