from picamera import PiCamera
from time import sleep
from datetime import datetime
import os
from PIL import Image

def main(sample, number, n):
    if (n == 0):
        if(os.path.isfile('/home/pi/Documents/SpectrometerData/SpectroPhotos/'+sample + '_' + number+'.png')==True):
            raise Exception("File exists")
    camera = PiCamera()
    camera.start_preview()
    image = camera.capture('/home/pi/Documents/SpectrometerData/SpectroPhotos/'+sample+'_' + number+'.png')
    camera.stop_preview()
    camera.close()
    image = Image.open('/home/pi/Documents/SpectrometerData/SpectroPhotos/'+sample+'_' + number+'.png')
    picture = image.rotate(270, expand=True)
    picture = picture.transpose(method=Image.FLIP_TOP_BOTTOM)
    picture = picture.transpose(method=Image.FLIP_LEFT_RIGHT)
    picture.save('/home/pi/Documents/SpectrometerData/SpectroPhotos/'+sample+'_' + number+'.png')
    return sample+'_' + number+'.png'