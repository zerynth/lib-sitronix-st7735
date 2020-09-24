################################################################################
# Draw text on display Example
#
# Created: 2020-09-17
# Author: S. Torneo
#
################################################################################

import streams
from sitronix.st7735 import st7735
import fonts

streams.serial()

try:
    # Setup sensor 
    print("start...")
    display = st7735.ST7735(SPI0, D5, D23, bl=D27, rst=D26)
    print("Ready!")
    print("--------------------------------------------------------")
except Exception as e:
    print("Error: ",e)

try:
    # clear screen
    display.clear()
    # draw text "Hello Zerynth" with blue background
    display.draw_text("Hello Zerynth", x=30, y=10, w=100, h=50, font_text=fonts.guiFont_Tahoma_7_Regular, background=[0,0,255])
except Exception as e:
    print("Error2: ",e)
