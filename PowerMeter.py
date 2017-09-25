import visa
import time
import os
import csv
import serial.tools.list_ports
import matplotlib.pyplot as plt

# Looks for connected serial ports
# assigns SR570 comport to 'sr570port'
def SR570_search():
    p2 = list(serial.tools.list_ports.comports())
    p1 = []
    ComNames = []
    sr570port = 'None'
    for p in p2:
        p1.append(str(p))
    if len(p2)==0:
        print("No open serial ports, SR570 not found.")
    for i in range(len(p1)):
        ComNames.append(' '.join(p1[i].split(' ')[2:4]))
    # print(ComNames)
    for i in range(len(ComNames)):
        # print(ComNames[i])
        if ComNames[i]=='USB-SERIAL CH340':
            print("SR570 found on "+p1[i].split(' ')[0])
            sr570port = p1[i].split(' ')[0]
    return sr570port

# Opening Connection to SR570 Current Preamplifier (if connected)
def openSR570(sr570port,gain=0,gmode=0,filter=4,lf3dB=3,hf3dB=15):
    if not(sr570port=="None"):
        sr570 = serial.Serial(sr570port,9600,timeout=1,stopbits=2,parity='N')
        # Configuring settings for SR570
        # gain (0-27); 0=1pA/V, to 27=1mA/V
        # gmode Gain Mode (0=low noise, 1=high BW, 2=low drift)
        # filter 0=6HP, 1=12HP, 2=6BP, 3=6LP, 4=12LP, 5=none
        # lf3dB (0-15) 0=0.03Hz, 15=1MHz
        # hf3dB (0-15) 0=0.03Hz, 15=1MHz
        sr570.write(b'*RST\n')
        sr570.write(b'SENS %d\n' % gain)
        sr570.write(b'GNMD %d\n' % gmode)
        sr570.write(b'FLTT %d\n' % filter)
        if 5>filter>1: # if LP filter active
            sr570.write(b'LFRQ %d\n' % lf3dB)
        if filter<3: # if HP filter active
            sr570.write(b'HFRQ %d\n' % hf3dB)

# sources voltage from Kiethley2401
def sourceVoltage(voltage,tlength):
    K2401.write(':SOUR:VOLT:LEV {}'.format(voltage))
    K2401.write(':SENS:CURR:PROT 10E-3')
    K2401.write(':SENS:FUNC "CURR"')
    K2401.write(':SENS:CURR:RANG 10E-3')
    K2401.write(':FORM:ELEM CURR')
    K2401.write(':OUTP ON')
    time.sleep(tlength)
    buf = K2401.query(':READ?')
    print('{0} volts applied'.format(voltage))
    print(buf)
    return buf.split('\n')[0]

# Initializes Kiethley 2401 in current source mode
def sourceCurrentInitialize(Kiethley2401Name,timeout=1,range=100e-3):
    Kiethley2401Name.write('*RST')
    Kiethley2401Name.write(':SOUR:FUNC CURR')
    Kiethley2401Name.write(':SOUR:CURR:MODE FIXED')
    Kiethley2401Name.write(':SOUR:CURR:RANG {}'.format(range))

# sources current from Kiethley2401
def sourceCurrent(Kiethley2401Name,curr,tlength,voltProt=20):
    Kiethley2401Name.write(':SOUR:CURR:LEV {}'.format(curr))
    Kiethley2401Name.write(':SENS:VOLT:PROT {}'.format(voltProt))
    Kiethley2401Name.write(':SENS:FUNC "VOLT"')
    Kiethley2401Name.write(':SENS:VOLT:RANG 20')
    Kiethley2401Name.write(':FORM:ELEM VOLT,CURR')
    Kiethley2401Name.write(':OUTP ON')
    time.sleep(tlength)
    buf = Kiethley2401Name.query(':READ?')
    # print('{0} amps applied'.format(curr))
    # print(buf)
    VIpair = [float(buf.split(',')[0]),float(buf.split(',')[1])]
    return VIpair

def IVsweep(Kiethley2401Name,voltProt,currStart,currStop,currStep,delayTime):
    Kiethley2401Name.write('*RST')
    Kiethley2401Name.write('ROUT:TERM FRON') # front terminals
    Kiethley2401Name.write(':SENS:FUNC:CONC OFF') # turn off concurrent functions
    Kiethley2401Name.write(':SOUR:FUNC CURR') # current source function
    Kiethley2401Name.write(":SENS:FUNC 'VOLT:DC'") # voltage sense function
    Kiethley2401Name.write('SENS:VOLT:PROT {}'.format(voltProt)) # current overprotection (default 20V)
    Kiethley2401Name.write('SOUR:CURR:START {}'.format(currStart)) # current start
    Kiethley2401Name.write('SOUR:CURR:STOP {}'.format(currStop)) # current stop
    Kiethley2401Name.write('SOUR:CURR:STEP {}'.format(currStep)) # current step
    Kiethley2401Name.write('SOUR:CURR:MODE SWE') # current sweep mode
    Kiethley2401Name.write('SOUR:SWE:RANG AUTO') # auto source ranging
    Kiethley2401Name.write('SOUR:SWE:SPAC LIN') # linear staircase sweep
    numSteps = ((currStop - currStart)/currStep) +1
    Kiethley2401Name.write('TRIG:COUN {}'.format(numSteps)) # trigger count = # sweep points
    Kiethley2401Name.write('SOUR:DEL {}'.format(delayTime)) # source delay time
    Kiethley2401Name.write('FORM:ELEM VOLT,CURR') # set output buffer to voltage, current pairs
    Kiethley2401Name.write('OUTP ON') # turn on source output
    buf = Kiethley2401Name.query('READ?') # trigger sweep, request data
    VIlist = buf.split(',')
    # convert to floats:
    for i in range(len(VIlist)):
        VIlist[i] = float(VIlist[i])
    voltageList = VIlist[::2]
    currentList = VIlist[1::2]
    IVpairs = list(zip(currentList,voltageList))
    return IVpairs

######################################################################################
sampleName = "170920A13"
startTime = time.localtime()
startTimeString = str(startTime.tm_year)+str(startTime.tm_mon).zfill(2)+\
                  str(startTime.tm_mday).zfill(2)+'-'+\
                  str(startTime.tm_hour).zfill(2)+'-'+\
                  str(startTime.tm_min).zfill(2)+'-'+\
                  str(startTime.tm_sec).zfill(2)
exptLength = 3600*(.1)
exptStart = time.time()
print("exptStart: ",exptStart)
curDir = os.getcwd()
directory = curDir+"\\"+sampleName+"_"+startTimeString
os.makedirs(directory)
os.chdir(directory)

while (time.time() < exptStart + exptLength):
    print("time left: ",round((exptStart+exptLength)-time.time(),0))
    # Listing Instruments (Serial and GPIB)
    rm = visa.ResourceManager()
    # print(rm.list_resources())
    # Opening connection to Kiethley 2401
    K2401 = rm.open_resource('GPIB0::24::INSTR')
    print(K2401.query('*IDN?'))
    # Opening connection to Kiethley 2000
    K2000 = rm.open_resource('GPIB0::16::INSTR')
    print(K2000.query('*IDN?'))

    Kiethley2000Name = K2000
    Kiethley2000Name.write('*RST')
    Kiethley2000Name.write(":SENS:FUNC 'CURR:DC'") # sense current
    Kiethley2000Name.write('SENS:CURR:DC:RANGE 10e-3') # set current sense range
    # Kiethley2000Name.write(':TRIG:COUN 1') # set one trigger
    # Kiethley2000Name.write(':INIT')
    # Kiethley2000Name.query(':DATA?')



    Kiethley2000Name.write(':TRIG:COUN 4')
    Kiethley2000Name.write(':INIT')

    readBrightnessCurrent = []
    readVoltage = []
    readCurrent = []
    sourceCurrentInitialize(K2401)

    startTime2 = time.localtime()
    startTimeString2 = str(startTime2.tm_year)+str(startTime2.tm_mon).zfill(2)+\
                       str(startTime2.tm_mday).zfill(2)+'-'+\
                       str(startTime2.tm_hour).zfill(2)+'-'+\
                       str(startTime2.tm_min).zfill(2)+'-'+\
                       str(startTime2.tm_sec).zfill(2)
    startTimeEpoch = time.time()
    for i in range(0,2000):
        readV,readI = sourceCurrent(K2401,50*10e-5,1)
        readVoltage.append(readV)
        readCurrent.append(float(readI))
        print("Measurement #{}".format(i))
        Kiethley2000Name.write(':INIT')
        readBrightnessCurrent.append(float(Kiethley2000Name.query(':DATA?').strip('\n').strip('+')))
    endTimeEpoch = time.time()
    runTime = endTimeEpoch - startTimeEpoch
    # print(readVoltage)
    # print(readCurrent)
    # print(readBrightnessCurrent)
    print("startTime: "+str(startTime))
    print("runTime: "+str(runTime))

    # plt.plot(readVoltage,readCurrent)
    # plt.show()
    # plt.figure(1)
    # plt.subplot(211)
    # plt.plot(readVoltage,readCurrent)
    # plt.subplot(212)
    # plt.plot(readCurrent,readBrightnessCurrent,[0,0.001],[0,.000001],'r-')
    # plt.show()

    # buffer = IVsweep(K2401,20,.1e-3,.5e-3,.1e-3,.5)
    # print(buffer)

    with open(sampleName+'_'+startTimeString2+'.csv','w',newline='') as csvfile:
        lis = [readVoltage,readCurrent,readBrightnessCurrent]
        csvfile.write("Sample Name: "+sampleName+"\n")
        csvfile.write("Start Time: "+startTimeString+"\n")
        csvfile.write("Run Length: "+str(round(runTime,2))+"\n")
        csvfile.write("Voltage (V),Current (A), Brightness Current (A)\n")
        for x in zip(*lis):
            csvfile.write("{0},{1},{2}\n".format(*x))
    # Set Current and wait:
    # sourceCurrent(K2401,10e-3,1)
    # time.sleep(600)
    # Close GPIB connection to Kiethleys
    K2000.close()
    K2401.close()































