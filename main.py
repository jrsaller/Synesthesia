import sys
import spotipy
import spotipy.util as util
import urllib.request
import tempfile
from PIL import Image,ImageDraw
import cv2
import numpy as np

from client_key import *
import clustering

#AUDIO ANALYSIS HIERARCHY
#sections
#bars
#beats
#segments
#tatums


def askForToken(username):
    #authenticates the user via browser
    #some of this info will change in the future
    return util.prompt_for_user_token(username,'user-library-read',client_id,client_secret,redirect_uri='http://localhost:8888/callback')

def searchForTrackAndAlbumURI(sp,query):
    selection = -1
    i=0
    while ( selection == -1 ):
        results = sp.search(q=query,type='track',offset=i)
        #print(results['tracks']['items'])
        for track in results['tracks']['items']:
            print(i,track['name']," --- ",track['artists'][0]['name'])
            i+=1
        while True:
            try:
                selection = int(input("What song would you like to select? [0-9,-1 to keep looking] ").strip())
                break
            except:
                print("Please enter a number to proceed")
    return results['tracks']['items'][selection%10]['uri'],results['tracks']['items'][selection%10]['album']['images'][0]['url']
    
def downloadAlbumArt(albumURL,location):
    urllib.request.urlretrieve(albumURL,location)
    print("Album Art downloaded!\n")
    return

def getSegmentPercents(analysis):
    segPercents = []
    loudness = analysis['sections'][0]['loudness']
    #print("SECTION LOUDNESS",loudness)
    sectionnum = 0
    for seg in analysis['segments']:
        if seg["start"]  > analysis['sections'][sectionnum]['start'] + analysis['sections'][sectionnum]['duration']:
            sectionnum+=1
            #print("\nNEW SECTION",sectionnum,'\n')
            #print("SECTION LOUDNESS",analysis['sections'][sectionnum]['loudness'])
            loudness = analysis['sections'][sectionnum]['loudness']
        percent =  loudness/seg["loudness_max"]
        #print("PERCENT",percent)
        if abs(percent) > 1:
            percent = 1 / percent
        percent = abs(percent)
        #print("SEGMENTS LOUDNESS MAX",seg['loudness_max'],percent )
        segPercents.append(percent)
        #print(percent)
    print("\nPercentages Loaded!")

    return segPercents

def NormalizeHSV(hsvColor):
    #print(hsvColor)
    hsv = [int(hsvColor[0]),hsvColor[1],hsvColor[2]]
    #print(hsv[0])
    hsv[0] *=2.0
    hsv[0] = int(hsv[0])
    #print(hsv[0])
    hsv[1] *= (1/2.55)
    hsv[1] = int(hsv[1])
    hsv[2] *= (1/2.55)
    hsv[2] = int(hsv[2])
    return hsv

def convertToHSV(colors):
    hsvColors = []
    for color in colors:
        colorInHSV = np.uint8([[color]])
        hsvItem = cv2.cvtColor(colorInHSV,cv2.COLOR_RGB2HSV)[0][0]
        #NormHSVColor = NormalizeHSV(hsvItem)
        #hsvColors.append(NormHSVColor)
        hsvColors.append(hsvItem)
        print("COLOR")
        print(color) 
        #print(NormHSVColor)
        print()
    return hsvColors

def getDominantColors(nodes):
    clusters = clustering.DominantColorsClass("albumcover.jpg",nodes)
    colors = clusters.dominantColors()
    return colors

def arrayMultiply(array, c):
    return [element*c for element in array]

def arraySum(a, b):
    return map(sum, zip(a,b))

def intermediate(a, b, ratio):
    aComponent = arrayMultiply(a, ratio)
    bComponent = arrayMultiply(b, 1-ratio)
    return arraySum(aComponent, bComponent)

def gradient(a, b, steps):
    steps = [n/float(steps) for n in range(steps)]
    gradientList = []
    for step in steps:
        #print("ITEM",step)
        tempList = []
        for item in intermediate(a, b, step):
            #print(item)
            tempList.append(item)
        gradientList.append(tempList)
    return gradientList

def generateColorSpectrum(nodes,spectrumColors):
    fullSpectrum = []
    for col in range(nodes-1):
        #print('\n',col)
        print("\t131\t",spectrumColors[col],spectrumColors[col+1])
        print(100//(nodes-1))
        endColor =spectrumColors[col+1]
        startColor = spectrumColors[col]
        if endColor[0] - startColor[0] < 60:
            midColorList = gradient(spectrumColors[col+1],spectrumColors[col],100//(nodes-1))
            for item in midColorList:
                fullSpectrum.append(item)
        else:
            newStartColor = spectrumColors[col][:]
            newEndColor = spectrumColors[col][:]
            newStartColor[0] = newStartColor[0]-(((100//(nodes-1))/2)-1)
            newEndColor[0] = newEndColor[0] + (((100//(nodes-1))/2)-1)
            midColorList1 = gradient(newStartColor,startColor,(((100//(nodes-1))//2)))
            for item in midColorList1:
                fullSpectrum.append(item)
            midColorList2 = gradient(startColor,newEndColor,(((100//(nodes-1))//2)))
            for item in midColorList2:
                fullSpectrum.append(item)
            print(len(midColorList1))
            print(len(midColorList2))
            fullSpectrum.append(newEndColor)
        print("=======================\nFULL SPECTRUM\n",fullSpectrum)
        print("=======================\n")
        #print('FullSpectrum Size:' , len(fullSpectrum))


    fullSpectrum.append(spectrumColors[-1])
    print(len(fullSpectrum))
    return fullSpectrum

def convertHSVtoRGB(HSV):

    col = cv2.cvtColor(np.uint8([[HSV]]),cv2.COLOR_HSV2RGB)
    return col

def convertHSVtoRGB_midSaturation(HSV):

    newHSV = [HSV[0],.5,HSV[2]]
    col = cv2.cvtColor(np.uint8([[newHSV]]),cv2.COLOR_HSV2RGB)
    return col

def drawSpectrum(spectrum,search):
    print("NEW SPECTRUM STARTED!")
    spectrumImage = Image.new("RGB",(len(spectrum)*3,100))
    spectrumImageDrawing = ImageDraw.Draw(spectrumImage)
    colorChoice = -1
    print(len(spectrum))
    for x in range(len(spectrum)*3):
        #colorChoice += 1
        if x%3 == 0:
            colorChoice+=1
        floodPoints = []
        for y in range(100):
            floodPoints.append((x,y))
        #print(colorCHoice)
        #print(convertHSVtoRGB(spectrum[colorChoice]))
        rgbColor = convertHSVtoRGB(spectrum[colorChoice])[0][0]
        #print(rgbColor)
        rgbString = "rgb( " + str(rgbColor[0])+ ", " + str(rgbColor[1]) + ", " + str(rgbColor[2]) + " )"
        spectrumImageDrawing.point(floodPoints,rgbString)



    spectrumImage.save(''.join(search.split()) + "_Spectrum.jpg")
    print("Spectrum Drawn!")
    return


def main():
    if len(sys.argv) > 1:
        #get username from command line argument
        username = sys.argv[1]
    else:
        print("Usage %s username" % (sys.argv[0]))
        sys.exit()

    token = askForToken(username)

    if token:
        #create the spotify wrapper object
        sp = spotipy.Spotify(auth=token)
        #User enters the song they would like to see
        search = input("Enter the song you would like to search for: ").strip()
        #retrieve the URI for the track and album cover
        track_uri,album_url = searchForTrackAndAlbumURI(sp,search)
        #get the audio analysis information from Spotify
        analysis = sp.audio_analysis(track_uri) 
        #get the percentage for every segment compared to its overall section it is in
        segmentPercents = getSegmentPercents(analysis)
        #download the album art into "albumcover.jpg"
        downloadAlbumArt(album_url,"./albumcover.jpg")
        #generate 5 nodes for the most dominant colors
        nodes = 5
        dominantColors = getDominantColors(nodes)
        hsvColors = convertToHSV(dominantColors)
        
        print(dominantColors)
        spectrumPillars = sorted(hsvColors,key=lambda x: x[0])
        spectrumPillarsExpanded = []
        num = -1
        for i in range(100):
            if i%(100/len(spectrumPillars)) == 0:
                num+=1
            spectrumPillarsExpanded.append(spectrumPillars[num])
        drawSpectrum(spectrumPillarsExpanded,"pillarsExp")
        fullSpectrum = generateColorSpectrum(nodes,spectrumPillars)
        for color in fullSpectrum:
            color[0] = int(color[0])
            color[1] = int(color[1])
            color[2] = int(color[2])

        finalColors = []
        for item in segmentPercents:
            item = int(item * 100)
            finalColors.append(fullSpectrum[item])

        drawSpectrum(finalColors,'Audiogenerated')
        drawSpectrum(fullSpectrum,search + "full")
        
        height = len(segmentPercents)
        width = len(segmentPercents)
        finalImage = Image.new("RGB",(width,height))
        finalImageDrawing = ImageDraw.Draw(finalImage)
        for x in range(width):
            floodPoints = []
            floodPoints.append((x,x))
            for num in range(x):
                floodPoints.append((num,x))
                floodPoints.append((x,num))
            rgbColor = convertHSVtoRGB(finalColors[x])[0][0]
            hsvString = "rgb( " + str(rgbColor[0])+ ", " + str(rgbColor[1]) + ", " + str(rgbColor[2]) + " )"
            finalImageDrawing.point(floodPoints,hsvString)

        finalImage.save(''.join(search.split()) + ".jpg")
        print("final image drawn!")
    
    else:
        print("Can't get token for",username)

if __name__ == "__main__":
    main()