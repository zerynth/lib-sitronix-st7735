################################################################################
# Draw Logo Example
#
# Created: 2020-09-18
# Author: S. Torneo
#
################################################################################

import streams
from sitronix.st7735 import st7735
import zLogo

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
    display.clear()
    display.draw_img(zLogo.zz)
except Exception as e:
    print("Error2: ",e)

