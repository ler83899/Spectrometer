from PIL import Image
import numpy
import matplotlib.pyplot as plt
import math
from xlwt import Workbook
from datetime import date

# calculates and returns absorbance
# abs = -log(T)
def absorbance(array1, array2, cal1NM, cal2NM, index1, index2):
    if(cal1NM>cal2NM):
        holder = cal2NM
        cal2NM = cal1NM
        cal1NM= holder
        holder = index1
        index1 = index2
        index2 = holder
    print (cal1NM)
    print (cal2NM)
    print (index1)
    print (index2)
    print ( int(((cal2NM-cal1NM)/(index2-index1))*(205-index2)+cal2NM))
    print ( int(((cal2NM-cal1NM)/(index2-index1))*(0-index2)+cal2NM))
    
    a = numpy.zeros(array1.size)
    b = numpy.zeros(array1.size)
    for i in range(0, array1.size):
        a[array1.size-1-i] = (-1)*math.log(array1[i]/array2[i])
        b[array1.size-1-i] = int(((cal2NM-cal1NM)/(index2-index1))*(i-index2)+cal2NM)  
    return a, b

'''
# calculates and returns absorbance
# abs = -log(T)
def absorbance1(array1, array2):
    a = numpy.zeros(array1.size)
    b = numpy.zeros(array1.size)
    for i in range(0, array1.size):
        a[i] = (-1)*math.log(array1[i]/array2[i])
        b[i] = int((195/-165)*(i-275)+665)  
    return a, b
'''

def cal(image, name, binTotal):
    bottom = imageAnalysis(Image.open(image), 0, 'max', 400, 440, int(binTotal))
    return numpy.argmax(bottom)


def find_abs(number, array1):
    return array1[number]
 
# graphs both a spectrograph and histogram for an image
def graph(array1, array2, name, title, xlabel, ylabel, color1, v):
    # figure setup
    plt.close()
    fig = plt.figure(figsize=(6, 3.5))
    a1 = fig.add_subplot(111)

    # 1st spectrograph
    
    a1.set_xlim( array2[len(array2)-1]-10, array2[0]+10)
    a1.set_xlabel(xlabel, fontsize = 10)
    a1.set_ylabel(ylabel, fontsize = 10)
    a1.set_title(name + " Spectrograph")
    a1.plot(array2, array1, color1)
    
    plt.savefig('/home/pi/Documents/SpectrometerData/AbsGraphs/' + name+'_absGraph.png')
       
    if (v == 1):
        plt.ion()
        plt.show()
        
    return '/home/pi/Documents/SpectrometerData/AbsGraphs/' + name+ '_absGraph.png'

# takes an image and finds the average intensity of each column of pixels
def imageAnalysis(image, columnStart, columnEnd, rowStart, rowEnd, binTotal):

    picture = image.convert("RGB")
    i = 0
    j = 0
    
    binRadius = int((binTotal-1)/2)

    if columnEnd == 'max':
        totalColumns = numpy.size(picture,1)
    else:
        totalColumns = columnEnd - columnStart

    if rowEnd == 'max':
        totalRows = numpy.size(picture,0)
    else:
        totalRows = rowEnd - rowStart
    
    gleamPixelMatrix = numpy.zeros(shape=(totalColumns, totalRows))
    gleamAverageIntensity = numpy.zeros(totalColumns)
    
    binWeights = numpy.zeros(binRadius)
    for i in range(binRadius):
        binWeights[i] = 1/(pow(2, i+1))
    binAverageIntensity = numpy.zeros(totalColumns)

    for i in range(0, totalColumns):
        for j in range(0, totalRows):
            #print(picture.getpixel((i+columnStart, j+rowStart)))
            r, g, b = picture.getpixel((i+columnStart, j+rowStart))
            gleamPixelMatrix[i][j] = (1 / 3) * (pow(r, (1 / 2.2)) + pow(g, (1 / 2.2)) + pow(b, (1 / 2.2)))
            gleamAverageIntensity[i] = gleamAverageIntensity[i] + gleamPixelMatrix[i][j]

            # when a column is complete, divide entry by the number of columns
            # to get the average of that column
            if j == totalRows - 1:
                gleamAverageIntensity[i] = gleamAverageIntensity[i] / numpy.size(gleamAverageIntensity)
    
    for i in range(totalColumns):
        for j in range(1, binRadius+1):
            if i >= j:
                binAverageIntensity[i] = binAverageIntensity[i] + (binWeights[j-1]*gleamAverageIntensity[i-j])
            if i+j < totalColumns:
                binAverageIntensity[i] = binAverageIntensity[i] + (binWeights[j-1]*gleamAverageIntensity[i+j])
    
    return binAverageIntensity

def toSpreadsheet(data1, data2, sampleName, binWidth):
    today = date.today()
    day = today.strftime("%m/%d/%Y")
    wb = Workbook()
    
    s1 = wb.add_sheet("Sheet 1")
    s1.write(0, 0 ,"sample_runNumber: " + sampleName)
    s1.write(1,0,day)
    s1.write(2,0, "Bin Width: " + str(binWidth))
    s1.write(2,2, "Index:")
    s1.write(2,3, "Absorbance:")
    for i in range(len(data2)):
        s1.write(i+4, 2, data2[i])
        s1.write(i+4,3,data1[i])
        
    wb.save('/home/pi/Documents/SpectrometerData/SpectroTxtFiles/'+ sampleName +".xls")
        

def main(image, name, binTotal, v, cal1NM, cal2NM, index1, index2):
    
    top = imageAnalysis(Image.open(image), 0, 'max', 300, 340, int(binTotal))
    bottom = imageAnalysis(Image.open(image), 0, 'max', 400, 440, int(binTotal))
    absArray, nmArray = absorbance(top, bottom, cal1NM, cal2NM, index1, index2)    
    
    toSpreadsheet(absArray, nmArray, name, binTotal)
    
    graph(absArray, nmArray, name, 'Absorbance (Sample vs. Control)', 'Wavelength (nm)', 'Absorbance', 'royalblue', v)
    return absArray, nmArray


if __name__ == '__main__':
        main('/home/pi/Documents/SpectrometerData/SpectroPhotos/image2.png', 'image2', 7, 1)
    