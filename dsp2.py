import wave
import math
import numpy as np
import matplotlib.pyplot as plt
import scipy.io.wavfile as wavfile
import operator

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
    wf = wave.open(filedir, "rb")
    nframes = wf.getnframes()
    waveData = wf.readframes(nframes)
    waveWidth = wf.getsampwidth()
    waveChannel = wf.getnchannels()
    frameRate = wf.getframerate()
    time = nframes / frameRate
    bps = frameRate * waveWidth * 8 * waveChannel
    print("总帧数：" + str(nframes) + "帧")
    print("采样率：" + str(frameRate) +  "帧/s")
    print("声道数：" + str(waveChannel) + "个")
    print("位深：" + str(waveWidth * 8) + "bit")
    print("比特率：" + str(bps / 1000) + "kbps")
    print("时间：" + str(time) + "s")
    print("文件大小：" + str(time * bps / 8 / 1000) + "KB")

def wavConvert():
    global timeData
    global x
    n = int(len(waveData) / waveWidth)
    i = 0
    j = 0
    for i in range(0, n):
        b = 0
        for j in range(0, waveWidth):
            temp = waveData[i * waveWidth:(i + 1) * waveWidth][j] * int(math.pow(2, 8 * j))
            b += temp
        if b > int(math.pow(2, 8 * waveWidth - 1)):
            b = b - int(math.pow(2, 8 * waveWidth))
        timeData.append(b)
    timeData = np.array(timeData)
    timeData.shape = -1, waveChannel
    timeData = timeData.T
    #Remove noise
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
    temp = timeData[0][0:N]
    output = np.fft.fft(temp)
    tempFre = output * 2 / N
    e = int(len(tempFre) / 2)
    freq = freq[:e - 1]
    y = freq
    freData = abs(tempFre[:e - 1])
    for i in range(0,N-100):
        if (np.average(freData[i:i+99])<0.1):
            endPoint=i
            break
    print("Highest endPoint:",endPoint)
    startPoint = int(endPoint*0.80)
    output[startPoint:endPoint]=output[startPoint:endPoint]*5
    enhance = np.fft.ifft(output)
    impData = np.real(enhance)
    wavFile = impData.astype(np.int16)
    wavFile = wavFile / 2**15
    name = "Improved2.wav"
    wavfile.write(name, frameRate, wavFile)

    vowelDetect()

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
    freq = int(input/res)
    left = np.average(freData[freq-14:freq-10])
    right = np.average(freData[freq+10:freq+14])
    middle = np.average(freData[freq])
    if (middle>right and middle>left):
        if (middle>30 and middle-left>0.15*middle and middle-right>0.15*middle):
            print("LMR:",input,"here")
            print(left,middle,right)
            return True
def peakWindow(input):
    for i in range(input-10,input+10):
        if (peakConfirm(i)):
            return True
def vowelDetect():
    th1 = peakWindow(1760) or peakWindow(800)#æ
    th2 = peakWindow(1320) or peakWindow(760)#ʌ
    th3 = peakWindow(1180) or peakWindow(740)#ɑː
    th4 = peakWindow(2220) or peakWindow(360)#ɪ
    th5 = peakWindow(2620) or peakWindow(280)#ɪː
    th6 = peakWindow(2060) or peakWindow(600)#e
    th7 = peakWindow(920) or peakWindow(560)#ɒ
    th8 = peakWindow(760)  or peakWindow(480)#ɒː
    th9 = peakWindow(640) or peakWindow(380) #ʊ
    th10 = peakWindow(920)  or peakWindow(320)#ʊ̈
    th11 = peakWindow(1480) or peakWindow(560) #ɜː
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

loadWave("orange.wav")
#pass the ball to me 

wavConvert()
waveFFTEnhance()
