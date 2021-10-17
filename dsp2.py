import wave
import math
import numpy as np
import matplotlib.pyplot as plt
import scipy.io.wavfile as wavfile

waveData = []
waveWidth = 2
waveChannel = 2
frameRate = 0
timeData = []
nframes = 0
freData =[]
endPoint = 0
res = 0
x=0
y=0
def loadWave(filedir):
    global waveData
    global waveWidth
    global waveChannel
    global frameRate
    global timeData
    global nframes
    #open wavefile and read attributes
    wf = wave.open(filedir, "rb")
    nframes = wf.getnframes()
    waveData = wf.readframes(nframes)
    waveWidth = wf.getsampwidth()
    waveChannel = wf.getnchannels()
    frameRate = wf.getframerate()
    time = nframes / frameRate
    bps = frameRate * waveWidth * 8 * waveChannel
    print("frameRate" + str(frameRate) +  "Fps")
    print("Time:" + str(time) + "s")

def wavConvert():
    global timeData
    global x
    n = int(len(waveData) / waveWidth)
    i = 0
    j = 0
    #generate time axis according to wavewidth
    for i in range(0, n):
        b = 0
        for j in range(0, waveWidth):
            temp = waveData[i * waveWidth:(i + 1) * waveWidth][j] * int(math.pow(2, 8 * j))
            b += temp
        if b > int(math.pow(2, 8 * waveWidth - 1)):
            b = b - int(math.pow(2, 8 * waveWidth))
        timeData.append(b)
    #transform the array because different channels connect to each other
    timeData = np.array(timeData)
    timeData.shape = -1, waveChannel
    timeData = timeData.T
    #calculate the backgroud noise and remove it
    noise=np.average(timeData[0][500:550])
    print('noise=',noise)
    for i in range (len(timeData[0])):
        timeData[0][i]=timeData[0][i]-noise 
    x = np.linspace(0, len(timeData[0]), len(timeData[0])) / frameRate

    

def waveFFTEnhance():
    global freData
    global y
    global endPoint
    global res
    N = nframes  
    res = frameRate / (N- 1)  
    freq = [res * n for n in range(0, N)]
    #calculate resolution for F Domain
    temp = timeData[0][0:N]
    output = np.fft.fft(temp)
    tempFre = output * 2 / N
    #do FFT for one channel
    e = int(len(tempFre) / 2)
    freq = freq[:e - 1]
    y = freq
    freData = abs(tempFre[:e - 1])
    #find the end of wave(the highest frequency harmonics)
    for i in range(0,N-100):
        if (np.average(freData[i:i+99])<0.1):
            endPoint=i
            break
    print("Highest endPoint:",endPoint)
    #Enhance the amplitude according to endPoint
    startPoint = int(endPoint*0.80)
    output[startPoint:endPoint]=output[startPoint:endPoint]*5
    #inverse FFT after enhancement
    enhance = np.fft.ifft(output)
    impData = np.real(enhance)
    #write into new wavefile
    wavFile = impData.astype(np.int16)
    wavFile = wavFile / 2**15
    name = "Improved2.wav"
    wavfile.write(name, frameRate, wavFile)
    #continue to detect vowels
    vowelDetect()
    #plot the result, time/FFT/Enhanced FFT
    plt.subplot(311) 
    plt.plot(x, timeData[0])
    plt.title("Time Domain")
    plt.xlabel("time (seconds)")
    plt.subplot(312) 
    plt.plot(y, freData)
    plt.xlabel("Freq (Hz)")
    plt.xlim(0, 8000)
    plt.subplot(313) 
    plt.plot(y, abs(output[:e - 1]*2/N))
    plt.xlabel("Freq (Hz)")
    plt.xlim(0, 8000)
    plt.show()

def peakConfirm(input):
    freq = int(input/res)#Frequency to points
    #creating a very small window to find peaks
    left = np.average(freData[freq-14:freq-10])
    right = np.average(freData[freq+10:freq+14])
    middle = np.average(freData[freq])
    if (middle>right and middle>left):
        if (middle>30 and middle-left>0.15*middle and middle-right>0.15*middle):
            #make sure it is the real peak
            #print("LMR:",input,"here")
            #print(left,middle,right) #Debug information
            return True
def peakWindow(input):
    #find peaks in a tiny and fixed window
    for i in range(input-7,input+7):
        if (peakConfirm(i)):
            return True
def vowelDetect():
    #all the vowels have their F1,F2,F3, here I use F1 and F2 to detect them
    th1 = peakWindow(1760) and peakWindow(800)#æ
    th2 = peakWindow(1320) and peakWindow(760)#ʌ
    th3 = peakWindow(1180) and peakWindow(740)#ɑː
    th4 = peakWindow(2220) and peakWindow(360)#ɪ
    th5 = peakWindow(2620) and peakWindow(280)#ɪː
    th6 = peakWindow(2060) and peakWindow(600)#e
    th7 = peakWindow(920) and peakWindow(560)#ɒ
    th8 = peakWindow(760)  and peakWindow(480)#ɒː
    th9 = peakWindow(640) and peakWindow(380) #ʊ
    th10 = peakWindow(920)  and peakWindow(320)#ʊ̈
    th11 = peakWindow(1480) and peakWindow(560) #ɜː
    print("vowel detected: ")
    if th1:
        print("æ ")
    if th2:
        print("ʌ ")
    if th3:
        print("ɑː ")
    if th4:
        print("ɪ ")
    if th5:
        print("ɪː ")
    if th6:
        print("e ")
    if th7:
        print("ɒ ")
    if th8:
        print("ɒː ")
    if th9:
        print("ʊ ")
    if th10:
        print("ʊː ")
    if th11:
        print("ɜː ")    

loadWave("cup.wav")
wavConvert()
waveFFTEnhance()
