from PIL import Image
from picamera import PiCamera
import Camera_Picture_Code as Cap
import mainCurrent as main;
from guizero import App, Text, Window, TextBox, PushButton, Slider, Picture, Combo, CheckBox, ButtonGroup



'''
Function that pulls up a pop up window to calibrate the spectrometer x-axis.
The buttons are to be hit seperately for each LED. This then will call a new
function
'''
def Calibrate():
    global window1
    try:
        window1.show()
    except:
        global calibrate_1
        global calibrate_2
        global wavelength_1
        global wavelength_2
        window1 = Window(app, title = "Calibrate",bg = '#E1C699')
        text = Text(window1, "This window is for calibrating your wavelength axis\nBelow is an area to enter in the color of the wavelength\nand calibrate for that color.\n Red = 665 nm, Green = 550 nm, Blue = 470 nm\n" )
        value1 = Text(window1, text = "Enter the wavelength value for your first led in nm")
        wavelength_1 = TextBox (window1, text = " ")
        calibrate_1 = PushButton (window1,  text = "calibrate")
        calibrate_1.when_clicked = cal
        value2 = Text(window1, text = "Enter the wavelength value for your second led in nm")
        wavelength_2 = TextBox (window1, text = " ")
        calibrate_2 = PushButton (window1, text = "calibrate")
        calibrate_2.when_clicked = cal
        saveCal = PushButton(window1, align = "bottom",  command = close, text = "save")

def cal(event_data):
    global calibrate_1
    global calibrate_2
    if (event_data.widget == calibrate_1):
        calibrate_1 = cal_LED(event_data)
    else:
        calibrate_2 = cal_LED(event_data)

'''
This function is called when the Calibrate button from the Claibrate window is
hit. This will take a number of pixel column to be labelled as the given wavelength
'''
def cal_LED(event_data):
    capture(event_data)
    try:
        bins = comboBins.value
    except:
        bins = 3
    return main.cal('/home/pi/Documents/SpectrometerData/SpectroPhotos/' + imageName_text.value, imageName_text.value, bins)
        
'''
Function used to make sure user has taken the right steps for photo of beams.
If correct then photo is taken and saved as image.png in Pictures folder
'''
def capture(event_data):
    global sampleName
    global pictureNumber
    global cap_image
    global imageName
    
    try:
        #checks which button was clicked, if capture button, move on from this try block
        try:
            if(event_data.widget == cap_image):
                raise Exception('Beam Capture')
            holderNumber = pictureNumber
            holderName = sampleName
            pictureNumber = '1'
            if(event_data.widget == calibrate_1):
                sampleName = wavelength_1.value + '_calibrate_' + sampleName          
            else:
                sampleName = wavelength_2.value + '_calibrate_' + sampleName
            Cap.main(sampleName, pictureNumber,1)
            imageName_text.value = sampleName +'_' + pictureNumber + '.png'
            sampleName = holderName
            pictureNumber = holderNumber
        except:
            if (sys.exc_info[0] == 'Beam Capture'):
                raise Exception('continue')
    except:
        global photosTaken
        try:
            sampleName = namePhoto.value
            pictureNumber = photosTaken.value
        except:
            sampleName = sampleName
        doubleCheck= app.yesno("Sample vs Reference", "Is your sample on the right side of the screen?")
        if (doubleCheck == True):
            try:
                print(sampleName)
                print (pictureNumber)
                imageName_text.value = Cap.main(sampleName, pictureNumber,0)
                pictureNumber = str(int(pictureNumber) + 1)
            except:
                fileCheck= app.yesno("File Exists", "This file already exists. Would you like to overwrite it?")
                if(fileCheck == True):
                    imageName_text.value = Cap.main(sampleName, pictureNumber,1)
                    pictureNumber = str(int(pictureNumber) + 1)
        else:
            app.error("Error", "Please make sure the sample is on the right side of the screen")        
        
'''
close calibration window
'''
def close():
    window1.hide()

'''
Button to find specific wavelength value
'''
def findValue():
        slider_value = wave_text1.value
        slider_changed(slider_value)

'''
update slide and textbox value.
'''
def slider_changed(slider_value):        
    if(int(slider_value) > int(nmArray[0])):
        slider_value = int(nmArray[0])
    if(int(slider_value) < int(nmArray[len(nmArray)-1])):
        slider_value = int(nmArray[len(nmArray)-1])
    wave_text1.value = int(slider_value)
    abs_text1.value = main.find_abs(int((int(slider_value)-wavelength2)/((wavelength2-wavelength1)/(calibrate2-calibrate1)))+calibrate2, absArray)


'''
checks to see if user has done proper steps for set up in terms of calibration.
These are the "prereqs" to runSpec
'''
def main1():
    doubleCheck= app.yesno("Calibrate?", "Did you calibrate the spectrometer?")
    if(doubleCheck == False):
        reAsk = app.yesno("Calibrate?", "Would you like to continue with preset values instead?")
        if (reAsk == False):
            Calibrate()
        else:
            global calibrate1
            global calibrate2
            global wavelength1
            global wavelength2
            calibrate1 = 40
            calibrate2 = 205
            wavelength1 = 470
            wavelength2 = 665
            runSpec()
    else:
        calibrate1 = calibrate_1
        calibrate2 = calibrate_2
        wavelength1 = int(wavelength_1.value)
        wavelength2 = int(wavelength_2.value)
        runSpec()
'''
run backend code. Ran after "Run Spectrometer" button is pressed and "prereqs" are met
'''
def runSpec():
    global absArray
    global nmArray
    global bins
    textbox = TextBox(app, grid = [1,0])
    try:
        if (comboVersion.value == 'Advanced'):
            v = int(1)
        else:
            v = int(0)
        bins = comboBins.value
    except:
        bins = 3
        v = int(0)
    absArray, nmArray = main.main('/home/pi/Documents/SpectrometerData/SpectroPhotos/' + imageName_text.value, imageName_text.value[0:-4], bins, v, wavelength1, wavelength2, calibrate1, calibrate2)
    pic = Picture(app,'/home/pi/Documents/SpectrometerData/AbsGraphs/'+imageName_text.value[0:-4]+'_absGraph.png', grid =[1,0,1,9])
    wavelength_slider = Slider(app, command = slider_changed, end = nmArray[0], start = nmArray[len(nmArray)-1], grid = [1,9,8,7], width = 485)
 
'''
Settings widnow for user to set up spectrometer
'''  
def settings():
    global window
    try:
        window.show()
    except:
        window = Window(app, title = "Settings",bg = '#E1C699')
        modeText = Text(window, "Spectrometer Mode")
        global comboVersion
        comboVersion = Combo(window, options=["Beginner", "Advanced"])
        global comboBins
        binsText =  Text(window, "Bins")
        comboBins = Combo(window, options=["3", "5", "7", "9"])
        global bins
        bins = comboBins.value
        global version
        version = comboVersion.value
        global photosTaken
        global namePhoto
        Text(window, "Sample Name")
        namePhoto = TextBox(window, text = "sample")
        Text(window,"Samples Taken")
        photosTaken = TextBox(window, text = pictureNumber)         
        pushbuttonSave = PushButton(window, text = "save", command = save)

'''
Method to close settings window and set global variables
'''
def save():
    bins = comboBins.value
    version = comboVersion.value
    global sampleName
    global pictureNumber
    sampleName = namePhoto.value
    pictureNumber = photosTaken.value
    window.hide()
    

# Name of the app window and app window layout
app = App( bg = '#E1C699',width = '800', layout = 'grid')
app.title = "Dual-Beam Spectrophotometer"

global sampleName
sampleName = "sample"

global pictureNumber
pictureNumber = "1"

global cap_image
cap_image = PushButton(app, text = 'Capture Beams\t', grid=[0,0])
cap_image.when_clicked = capture

imageName_text = TextBox(app, text= sampleName + '_' + pictureNumber + '.png', grid = [0,1], width = "fill")

calibrate = PushButton(app, text = 'Calibrate\t\t', command = Calibrate, grid = [0,2])

run_spec = PushButton(app, text = 'Run Spectrometer\t', command = main1, grid=[0,3])

#wavelength
wave_text = Text(app, text= 'wavelength', grid = [0,4])
wave_text1 = TextBox(app, text= '0', grid = [0,5])

#absorbance value at a given wavelength
abs_text = Text(app, text= 'absobance', grid = [0,6])
abs_text1 = TextBox(app, text= '0', grid = [0,7])

customValue = PushButton(app, text = 'Find Absorbance\t', grid = [0,8], command = findValue)
settingButton = PushButton(app, text = 'Settings\t\t', command = settings, grid = [0,9])

app.display()
