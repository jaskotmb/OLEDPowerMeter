import visa
import time
import csv
import serial.tools.list_ports

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
    K2401.write(':SOUR:VOLT:LEV {0}'.format(voltage))
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
def sourceCurrentInitialize(Kiethley2401Name,timeout=1,range=10e-3):
    Kiethley2401Name.write('*RST')
    Kiethley2401Name.write(':SOUR:FUNC CURR')
    Kiethley2401Name.write(':SOUR:CURR:MODE FIXED')
    Kiethley2401Name.write(':SOUR:CURR:RANG {}'.format(range))

# sources current from Kiethley2401
def sourceCurrent(Kiethley2401Name,curr,tlength):
    Kiethley2401Name.write(':SOUR:CURR:LEV {0}'.format(curr))
    Kiethley2401Name.write(':SENS:VOLT:PROT 20')
    Kiethley2401Name.write(':SENS:FUNC "VOLT"')
    Kiethley2401Name.write(':SENS:VOLT:RANG 25')
    Kiethley2401Name.write(':FORM:ELEM VOLT')
    Kiethley2401Name.write(':OUTP ON')
    time.sleep(tlength)
    buf = Kiethley2401Name.query(':READ?')
    print('{0} amps applied'.format(curr))
    print(buf)
    return buf.split('\n')[0]

######################################################################################
# Listing Instruments (Serial and GPIB)
rm = visa.ResourceManager()
# print(rm.list_resources())
# Opening connection to Kiethley 2401
K2401 = rm.open_resource('GPIB0::24::INSTR')
print(K2401.query('*IDN?'))

def IVsweep(Kiethley2401Name,prot=20,currStart,currStop,currStep,delayTime):
    Kiethley2401Name.write('*RST')
    Kiethley2401Name.write(':SENS:FUNC:CONC OFF') # turn off concurrent functions
    Kiethley2401Name.write(':SOUR:FUNC CURR') # current source function
    Kiethley2401Name.write(":SENS:FUNC 'VOLT:DC'") # voltage sense function
    Kiethley2401Name.write('SENS:VOLT:PROT {}'.format(prot)) # current overprotection (default 20V)
    Kiethley2401Name.write('SOUR:CURR:START {}'.format(currStart)) # current start
    Kiethley2401Name.write('SOUR:CURR:STOP {}'.format(currStop)) # current stop
    Kiethley2401Name.write('SOUR:CURR:STEP {}'.format(currStep)) # current step
    Kiethley2401Name.write('SOUR:CURR:MODE SWE') # current sweep mode
    Kiethley2401Name.write('SOUR:SWE:RANG AUTO') # auto source ranging
    Kiethley2401Name.write('SOUR:SWE:SPAC LIN') # linear staircase sweep
    numSteps = ((currStop - currStart)/currStep) +1
    Kiethley2401Name.write('TRIG:COUN {}'.format(numSteps)) # trigger count = # sweep points
    Kiethley2401Name.write('SOUR:DEL {}'.format(delayTime)) # source delay time
    Kiethley2401Name.write('OUTP ON') # turn on source output
    Kiethley2401Name.write('READ?') # trigger sweep, request data





# voltMeas = []
# minutes = 1
# for i in range(1,1+(6*minutes)):
#     voltMeas.append(sourceCurrent(3e-3,10))
#     print('{0:2.2} min / {1} min'.format(i/6,minutes))
#
#
# with open('output_OLED_sourcecurr.csv','w',newline='') as csvfile:
#     spamwriter = csv.writer(csvfile,delimiter=',')
#     for item in voltMeas:
#         spamwriter.writerow([item,])

# Opening connection to Kiethley 2000
K2000 = rm.open_resource('GPIB0::16::INSTR')
print(K2000.query('*IDN?'))
# Configuration Settings for Kiethley 2000

# Close GPIB connection to Kiethleys
K2000.close()
K2401.close()

# Modules needed:
# sweep IV, measure brightness
# constant current, record voltage, brightness occasionally































