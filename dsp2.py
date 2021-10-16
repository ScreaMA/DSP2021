import wave
import math
import numpy as np
import matplotlib.pyplot as plt
import scipy.io.wavfile as wavfile
import operator
from scipy import signal

waveData = []
waveWidth = 2
waveChannel = 2
frameRate = 0
timeData = []
nframes = 0
freData =[]
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
    x = np.linspace(0, len(timeData[0]), len(timeData[0])) / frameRate
    # 绘制波形

    

def waveFFT():
    global freData
    global y
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
    plt.subplot(211) 
    plt.plot(x, timeData[0])
    plt.xlabel("time (seconds)")
    plt.subplot(212) 
    plt.plot(y, freData)
    plt.xlabel("Freq (Hz)")
    plt.xlim(0, 7000)
    plt.show()

def waveEnhance():
    global freData





loadWave("one sentence.wav")
wavConvert()
waveFFT()