import visa
import time
import csv
import serial
import serial.tools.list_ports

# Looks for connected serial ports
# assigns SR570 comport to 'sr570port'
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

# Opening Connection to SR570 Current Preamplifier (if connected)
if not(sr570port=="None"):
    sr570 = serial.Serial(sr570port,9600,timeout=1,stopbits=2,parity='N')
    # print(sr570)

    # Configuring settings for SR570
    gain = 0 #(0-27); 0=1pA/V, to 27=1mA/V
    gmode = 0 # Gain Mode (0=low noise, 1=high BW, 2=low drift)
    filter = 4 #0=6HP, 1=12HP, 2=6BP, 3=6LP, 4=12LP, 5=none
    lf3dB = 3 #(0-15) 0=0.03Hz, 15=1MHz
    hf3dB = 15 #(0-15) 0=0.03Hz, 15=1MHz
    sr570.write(b'*RST\n')
    sr570.write(b'SENS %d\n' % gain)
    sr570.write(b'GNMD %d\n' % gmode)
    sr570.write(b'FLTT %d\n' % filter)
    if 5>filter>1: # if LP filter active
        sr570.write(b'LFRQ %d\n' % lf3dB)
    if filter<3: # if HP filter active
        sr570.write(b'HFRQ %d\n' % hf3dB)

rm = visa.ResourceManager()
# Listing Instruments (Serial and GPIB)
# print(rm.list_resources())

######################################################################################
# Opening connection to Kiethley 2401
K2401 = rm.open_resource('GPIB0::24::INSTR')
print(K2401.query('*IDN?'))

# K2401.timeout = 25000
# K2401.write('*RST')
# K2401.write(':SOUR:FUNC VOLT')
# K2401.write(':SOUR:VOLT:MODE FIXED')
# K2401.write(':SOUR:VOLT:RANG 10')
# for i in range(1,51):
#     appVolts = 3+(i*.2)
#     K2401.write(':SOUR:VOLT:LEV {0}'.format(appVolts))
#     K2401.write(':SENS:CURR:PROT 10E-3')
#     K2401.write(':SENS:FUNC "CURR"')
#     K2401.write(':SENS:CURR:RANG 10E-3')
#     K2401.write(':FORM:ELEM CURR')
#     K2401.write(':OUTP ON')
#     time.sleep(1)
#     buf = K2401.query(':READ?')
#     K2401.write(':OUTP OFF')
#     print('{0} volts applied'.format(appVolts))
#     print(buf)
# K2401.timeout = 1000*60*65
# K2401.write('*RST')
# K2401.write(':SOUR:FUNC VOLT')
# K2401.write(':SOUR:VOLT:MODE FIXED')
# K2401.write(':SOUR:VOLT:RANG 10')

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


K2401.timeout = 1000*60*65
K2401.write('*RST')
K2401.write(':SOUR:FUNC CURR')
K2401.write(':SOUR:CURR:MODE FIXED')
K2401.write(':SOUR:CURR:RANG 10E-3')

def sourceCurrent(curr,tlength):
    K2401.write(':SOUR:CURR:LEV {0}'.format(curr))
    K2401.write(':SENS:VOLT:PROT 20')
    K2401.write(':SENS:FUNC "VOLT"')
    K2401.write(':SENS:VOLT:RANG 25')
    K2401.write(':FORM:ELEM VOLT')
    K2401.write(':OUTP ON')
    time.sleep(tlength)
    buf = K2401.query(':READ?')
    print('{0} amps applied'.format(curr))
    print(buf)
    return buf.split('\n')[0]

# for i in range(1,90):
#     appV = 3+(i*.1)
#     sourceVoltage(appV,.25)

voltMeas = []
minutes = 1
for i in range(1,1+(6*minutes)):
    voltMeas.append(sourceCurrent(3e-3,10))
    print('{0:2.2} min / {1} min'.format(i/6,minutes))




# currMeas = []
# for i in range(1,1+(6*minutes)):
#     currMeas.append(sourceVoltage(10,10))

# K2401.write(':OUTP OFF')

# Write data to output file
# with open('output_OLED.csv','w',newline='') as csvfile:
#     spamwriter = csv.writer(csvfile,delimiter=',')
#     for item in currMeas:
#         spamwriter.writerow([item,])

with open('output_OLED_sourcecurr.csv','w',newline='') as csvfile:
    spamwriter = csv.writer(csvfile,delimiter=',')
    for item in voltMeas:
        spamwriter.writerow([item,])

# Opening connection to Kiethley 2000
K2000 = rm.open_resource('GPIB0::16::INSTR')
print(K2000.query('*IDN?'))
# Configuration Settings for Kiethley 2000

# Close GPIB connection to Kiethleys
K2000.close()
K2401.close()



