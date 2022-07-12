
from datetime import datetime
import pytesseract
import cv2
import numpy as np
import os

import kivy
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
import win32timezone
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
import easygui
import enchant
import pathlib

class Cookie(GridLayout):

    #txt_fold = ObjectProperty(None)
    def getFold(self):
        fpacz = easygui.diropenbox('Wskaż folder z screenami')
        if fpacz:
            self.ids.txt_fold.text = fpacz

    def getCancel(self):
        App.get_running_app().stop()
        return

    def main(self, fold):
        print(fold)
        class Player:
            imie = "imie"
            sumadmg = 0.0
            avrdmg = 0.0
            ataki = 0

            def __init__(self, im, dmg):
                self.imie = im
                self.sumadmg = float(dmg)
                self.ataki = 1
                self.avrdmg = self.sumadmg / self.ataki

            def dodaj(self, dmg):
                self.sumadmg = self.sumadmg + float(dmg)
                self.ataki = self.ataki + 1
                self.avrdmg = self.sumadmg / self.ataki

            def print(self):
                return self.imie + "\t" + str(int(self.avrdmg)) + "\t" + str(self.ataki)

            def jest(self, im):
                if self.imie == im:
                    return True
                else:
                    return False

        def CzyJest(objs, im):
            zwrot = False
            for ob in objs:
                if ob.jest(im):
                    zwrot = ob
            return zwrot

        # get grayscale image
        def get_grayscale(image):
            return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # noise removal
        def remove_noise(image):
            return cv2.medianBlur(image, 5)

        # thresholding
        def thresholding(image):
            return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

        # dilation
        def dilate(image):
            kernel = np.ones((5, 5), np.uint8)
            return cv2.dilate(image, kernel, iterations=1)

        # erosion
        def erode(image):
            kernel = np.ones((5, 5), np.uint8)
            return cv2.erode(image, kernel, iterations=1)

        # opening - erosion followed by dilation
        def opening(image):
            kernel = np.ones((5, 5), np.uint8)
            return cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)

        # canny edge detection
        def canny(image):
            return cv2.Canny(image, 100, 200)

        # skew correction
        def deskew(image):
            coords = np.column_stack(np.where(image > 0))
            angle = cv2.minAreaRect(coords)[-1]
            if angle >= -45:
                angle = -angle

            else:
                angle = -(90 + angle)

            (h, w) = image.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
            return rotated

        # template matching
        def match_template(image, template):
            return cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)


        if not os.path.isdir(fold + r'/wyniki'):
            #os.mkdir(fold + r'/wyniki')
            pathlib.Path(fold + r'/wyniki').mkdir(parents=True, exist_ok=True)


        nrRead = 0
        nrErro = 0
        now = datetime.now()
        save = open(fold + r'/wyniki/wyniki_' + now.strftime("%Y-%m-%d") + ".txt", "w")
        erro = open(fold + r'/wyniki/errors_' + now.strftime("%Y-%m-%d") + ".txt", "w")
        screeny = [os.path.join(fold, f) for f in os.listdir(fold) if os.path.isfile(os.path.join(fold, f))]
        print(screeny)

        Gracze = []

        for p in screeny:
            print(p)
            img = cv2.imread(p)

            # Adding custom options
            custom_config = r'-l pol+eng --oem 3 --psm 6'
            text = pytesseract.image_to_string(get_grayscale(img), config=custom_config)
            tab = text.split('\n')
            print(tab)
            for line in tab[1:len(tab):]:
                line = line.strip('\r')
                if line != "":
                    rec = line.split(" ")
                    wynik = (''.join(rec[1:len(rec) - 1:]), rec[len(rec) - 1])
                    temp = CzyJest(Gracze, wynik[0])
                    nrRead += 1
                    if (temp != False):
                        try:
                            temp.dodaj(wynik[1])
                        except:
                            nrErro += 1
                            print("Blad w ", p)
                            erro.write("Blad odczytu w " + str(p) + ' (' + line + ')\n')
                    else:
                        try:
                            Gracze.append(Player(wynik[0], wynik[1]))
                        except:
                            nrErro += 1
                            print("Blad w ", p)
                            erro.write("Blad odczytu w " + str(p) + ' (' + line + ')\n')

        for g in Gracze:
            print(g.print())
            # sys.stdout.write(g.print())
            save.write(str(g.print()) + '\n')
        erro.write('Odczytano poprawnie ' + str(nrRead - nrErro) + ' wyników. Bledy - ' + str(nrErro))
        save.close()
        erro.close()
    pass

class CookieApp(App):

    def build(self):
        self.title = r'WSKAŻ FOLDER ZE SCREENAMI'
        #self.icon = r''
        Window.size = (800, 150)
        return Cookie()










if __name__ == '__main__':
    CookieApp().run()
