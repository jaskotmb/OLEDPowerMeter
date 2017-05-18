import visa
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
K2401.timeout = 25000

K2401.write('*RST')
K2401.write(':SOUR:FUNC VOLT')
K2401.write(':SOUR:VOLT:MODE FIXED')
K2401.write(':SOUR:VOLT:RANG 1')
K2401.write(':SOUR:VOLT:LEV 0.0005')
K2401.write(':SENS:CURR:PROT 10E-3')
K2401.write(':SENS:FUNC "CURR"')
K2401.write(':SENS:CURR:RANG 10E-3')
K2401.write(':FORM:ELEM CURR')
K2401.write(':OUTP ON')
buf = K2401.query(':READ?')
K2401.write(':OUTP OFF')
#
print(buf)

# voltProt = 1
# currStart = 1E-3
# currStep = 1E-3
# currStop = 10E-3
# K2401.write('*RST')                             # Restore GPIB defaults
# K2401.write(':ROUT:TERM FRON')                  # Use front terminals
# K2401.write(':SENS:FUNC:CONC OFF')              # Turn off concurrent functions
# K2401.write(':SOUR:FUNC CURR')                  # Current source function
# K2401.write(":SENS:FUNC 'VOLT:DC'")             # Voltage sense function
# K2401.write(':SENS:VOLT:PROT %d' % voltProt)    # Voltage compliance set
# K2401.write(':SOUR:CURR:START %d' % currStart)  # Current sweep start
# K2401.write(':SOUR:CURR:STEP %d' % currStep)    # Current sweep step
# K2401.write(':SOUR:CURR:STOP %d' % currStop)    # Current sweep stop
# K2401.write(':SOUR:CURR:MODE SWE')              # Select current sweep mode
# K2401.write(':SOUR:SWE:RANG AUTO')              # Auto source ranging
# K2401.write(':SOUR:SWE:SPAC LIN')               # Linear staircase sweep
# K2401.write(':TRIG:COUN 10')                    # Trigger count = number sweep points
# K2401.write(':SOUR:DEL 0.1')                    # 100ms Source delay
# K2401.write(':OUTP ON')                         # Source output on
# data = K2401.query('READ?')                           # Trigger sweep, request data
# K2401.write(':OUTP OFF')                        # Source output off
#
# # print(data)
# dataList = data.split(',')
# v = []
# curr = []
# res = []
# time = []
# status = []
# for i in range(0,len(dataList),5):
#     v.append(dataList[i])
#     curr.append(dataList[i+1])
#     res.append(dataList[i+2])
#     time.append(dataList[i+3])
#     status.append(dataList[i+4])
# print(len(dataList))
# for i in range(len(v)):
#     print('Voltage: '+v[i]+'  Current: '+curr[i]+'  Resistance: '+res[i])

######################################################################################
# Opening connection to Kiethley 2000
K2000 = rm.open_resource('GPIB0::16::INSTR')
print(K2000.query('*IDN?'))
# Configuration Settings for Kiethley 2000

# Close GPIB connection to Kiethleys
K2000.close()
K2401.close()



