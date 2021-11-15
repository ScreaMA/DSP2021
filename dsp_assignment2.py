import math
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
def loadFile(filePath):
    #Read ECG data from file 
    a = open(filePath, 'r')
    timeData = []
    #convert string to float
    for temp in a.readlines():
        temp = temp.strip('\n')
        timeData.append(float(temp))
    a.close()
    return timeData
class generateCoefficients:
    def __init__(self,stopFrequency,sampleRate,filePath = "ECG_msc_matric_7.dat",bandwidth = 5):
        #initialize function
        self.fre = stopFrequency
        self.sampleRate = sampleRate
        self.bandwidth = bandwidth
        self.timeData = loadFile(filePath)
        self.N = len(self.timeData)
        super().__init__()

    def FFTprocess(self):
        #calculate points, resolution and fft output, to get a refrence for further filtering
        self.N = len(self.timeData)
        self.res = self.sampleRate/(self.N-1)
        self.freq = [self.res * n for n in range(0, self.N)]
        self.output = np.fft.fft(self.timeData)
        e = int(len(self.output) / 2)
        #y is the x-axis in frequency domain and x in time domain
        self.y = self.freq[0:e - 1]
        self.x = np.linspace(0,20,5000)
        plt.figure(1)
        plt.subplot(211) 
        plt.plot(self.x, self.timeData)
        plt.title("Time Domain")
        plt.xlabel("time (seconds)")
        freData = abs(self.output[0:e-1]*2/self.N)
        plt.subplot(212) 
        plt.plot(self.y, freData)
        plt.xlabel("Freq (Hz)")
        #plt.xlim(0, 100)
        #plt.show()
    def highpassDesign(self):
        highpassOutput = np.zeros(self.N)
        highpassPoint = int(self.fre/self.sampleRate*self.N)
        highpassOutput[0:highpassPoint] =0
        highpassOutput[int(self.N/2)+highpassPoint:self.N-1] =0
        highpassOutput[highpassPoint:int(self.N/2)] =1
        highpassOutput[int(self.N/2):int(self.N/2)+highpassPoint] =1
        highpassInput = np.real(np.fft.ifft(highpassOutput))
        #debug info
        print("Highpass Design:",len(highpassInput),highpassInput)
        return highpassInput
    def bandstopDesign(self):
        #calculate bandstop filter as the same
        bandstopOutput = np.ones(self.N)
        bandstopPointLeft = int((self.fre-self.bandwidth)/self.sampleRate*self.N)
        bandstopPointRight = int((self.fre+self.bandwidth)/self.sampleRate*self.N)
        bandstopOutput[bandstopPointLeft:bandstopPointRight] = 0;
        bandstopInput = np.real(np.fft.ifft(bandstopOutput))
        print("Bandstop Design:",len(bandstopInput),bandstopInput)
        return bandstopInput

        
class FIRFilter:
    def __init__(self,_coefficients,buffer):
        self.coefficients = _coefficients
        self.N = len(self.coefficients)
        self.buffer = buffer

    def dofilter(self,v):

        index = self.N-1
        while index > 0:
            self.buffer[index]=self.buffer[index-1]
            index=index-1
        self.buffer[0]=v
        output=0
        for i in range(len(self.coefficients)):
            output=output+self.buffer[i]*self.coefficients[i]
        #print("normal inner:",output)
        return output
    def dofilterLMS(self, v):
        for j in range(self.N - 1):
            self.buffer[self.N - 1 - j] = self.buffer[self.N - 2 - j]
        self.buffer[0] = v 
        result = np.inner(self.buffer, self.coefficients)
        #print("LMS inner:",result)
        return result
    def doFilterAdaptive(self,signal, noise, learningRate):
        cancellor = self.dofilterLMS(noise)
        output_signal = signal - cancellor
        self.lns(output_signal, learningRate)
        return output_signal

        print("LMS Desgin:",self.coefficients)
    def lns(self,error,mu = 0.005):
        for j in range(self.N):
            self.coefficients[j] =self.coefficients[j]+ error *mu*self.buffer[j]
filePath = "ECG_msc_matric_8.dat"
timeData = loadFile(filePath)
N=len(timeData)
'''
avr = np.average(timeData)
for i in range(N):
    timeData[i] = timeData[i] -avr
'''
a = generateCoefficients(50,250,filePath)
b = generateCoefficients(1,250,filePath)
a.FFTprocess()
highpassCoefficients = b.highpassDesign()
buffer = np.zeros(N)
highpassFIR = FIRFilter(highpassCoefficients,buffer)
output = np.zeros(N)
#for i in range(N):
#    output[i] = highpassFIR.dofilter(timeData[i])
buffer = np.zeros(N)
bandstopCoefficients = a.bandstopDesign()
bandstopFIR = FIRFilter(bandstopCoefficients,buffer)
#for i in range(N):
#    output[i] = bandstopFIR.dofilter(output[i])
output[0]=output[1]
output[N-1]=output[N-2]
plt.figure(2)
plt.subplot(211)
x = np.linspace(0,20,N)
plt.plot(x, output)

#plt.show()

buffer = np.zeros(N)
lmsCoefficients = np.zeros(N)
lmsOutput = np.zeros(N)
lmsFIR = FIRFilter(lmsCoefficients,buffer)
for i in range(N):
    ref_noise = np.sin(2.0 * np.pi * (i/5))
    lmsOutput[i]=lmsFIR.doFilterAdaptive(timeData[i],ref_noise,0.0005)
lmsOutput[0]=lmsOutput[1]
lmsOutput[N-1]=lmsOutput[N-2]
plt.subplot(212)
plt.plot(x, lmsOutput)
plt.show()

'''
    def highpassDesign(self):
        highpassOutput = copy.deepcopy(self.output)
        highpassPoint = int(self.fre/self.sampleRate*self.N)
        highpassOutput[2:highpassPoint] =0
        highpassOutput[self.N-highpassPoint:self.N-2] =0
        highpassInput = np.fft.ifft(highpassOutput)
        highpassFilter = signal.deconvolve(self.timeData,highpassInput)
        plt.subplot(313) 
        plt.plot(self.x, highpassInput)
        #plt.plot(self.freq, highpassOutput)
        #plt.xlabel("Tims (s)")
        print("Design:",highpassFilter[0])
        print("Design:",len(highpassFilter[1]),highpassFilter[1])
        plt.show()
        return highpassFilter
'''