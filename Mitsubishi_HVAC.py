#!/usr/bin/python
import array
import sys

MITSUBISHI_BIT_MARK = 450
MITSUBISHI_ONE_SPACE = 1250
MITSUBISHI_ZERO_SPACE = 390
MITSUBISHI_HEADER_MARK = 3500
MITSUBISHI_HEADER_SPACE = 1700
MITSUBISHI_MIN_GAP = 9000

MITSUBISHI_COOL = 0x18
MITSUBISHI_DRY = 0x10
MITSUBISHI_AUTO = 0x20
MITSUBISHI_HEAT = 0x08
MITSUBISHI_FAN = 0x38

BYTE8_COOL = 0x06
BYTE8_FAN = 0x00
BYTE8_DRY = 0x02
BYTE8_HEAT = 0x00
BYTE8_AUTO = 0x06


FAN_AUTO = 0x00
FAN_LOW = 0x01
FAN_NORM = 0x02
FAN_HIGN = 0x03
FAN_MAX = 0x04
FAN_QUIET = 0x05

VANE_AUTO = 0x40
VANE_MOVE = 0x78

VANEHOR_LEFT = 0x10
VANEHOR_LEFTMID = 0x20
VANEHOR_MID = 0x30
VANEHOR_RIGHTMID = 0x40
VANEHOR_RIGHT = 0x50
VANEHOR_AUTO = 0xC0

def getbyte8(mode):
    return {
        MITSUBISHI_COOL:BYTE8_COOL,
        MITSUBISHI_DRY:BYTE8_DRY,
        MITSUBISHI_AUTO:BYTE8_AUTO,
        MITSUBISHI_HEAT:BYTE8_HEAT,
        MITSUBISHI_FAN:BYTE8_FAN,
    }[mode]

def labelfan(fanmode):
    return {
        FAN_AUTO: "auto",
        FAN_LOW: "low",
        FAN_NORM: "normal",
        FAN_HIGN: "high",
        FAN_MAX: "highest",
        FAN_QUIET: "quiet"
    }[fanmode]

def labelmode(mode):
    return {
        MITSUBISHI_AUTO: "auto",
        MITSUBISHI_COOL: "cool",
        MITSUBISHI_DRY: "dry",
        MITSUBISHI_HEAT: "heat",
        MITSUBISHI_FAN: "fan_only",
    }[mode]

def checksum(datalist):
    csum = 0
    for elmt in datalist:
        csum += elmt
    return ((csum & 0xFF))

def GetHVACCodes(DataHex, ON=True, MODE=MITSUBISHI_AUTO, TEMP=16, FANSPEED=FAN_AUTO, VANE=VANE_AUTO, VANEHOR=VANEHOR_AUTO):
    if ON:
        # On/OFF
        DataHex[5] |= 0x20
    # Mode
    DataHex[6] |= MODE
    # Temp
    DataHex[7] |= (TEMP-16)
    # Horizonal Vane + Mode
    DataHex[8] |= VANEHOR
    DataHex[8] |= getbyte8(MODE)
    # Vert Vane + Fan Speed
    DataHex[9] |= VANE
    DataHex[9] |= FANSPEED

    DataHex[17] |= checksum(DataHex)

    return DataHex

def Convert2Raw(DataHex):
    raw = []
    
    # Header only
    raw.append(MITSUBISHI_HEADER_MARK)
    raw.append(-1*MITSUBISHI_HEADER_SPACE)
    for i in range(5):
        for bitn in range(8):
            if ((DataHex[i] >> bitn) & 0x01):
                raw.append(MITSUBISHI_BIT_MARK)
                raw.append(-1*MITSUBISHI_ONE_SPACE)
            else:
                raw.append(MITSUBISHI_BIT_MARK)
                raw.append(-1*MITSUBISHI_ZERO_SPACE)

    raw.append(MITSUBISHI_BIT_MARK)
    raw.append(-1*MITSUBISHI_MIN_GAP)

    # Header + Data
    raw.append(MITSUBISHI_HEADER_MARK)
    raw.append(-1*MITSUBISHI_HEADER_SPACE)
    for i in DataHex:
        for bitn in range(8):
            if ((i >> bitn) & 0x01):
                raw.append(MITSUBISHI_BIT_MARK)
                raw.append(-1*MITSUBISHI_ONE_SPACE)
            else:
                raw.append(MITSUBISHI_BIT_MARK)
                raw.append(-1*MITSUBISHI_ZERO_SPACE)
    
    raw.append(MITSUBISHI_BIT_MARK)

    return raw

if __name__ == "__main__":

    temps = [16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]
    fanmodes = [FAN_AUTO, FAN_QUIET, FAN_LOW, FAN_NORM, FAN_HIGN, FAN_MAX]
    modes = [MITSUBISHI_AUTO, MITSUBISHI_COOL, MITSUBISHI_HEAT, MITSUBISHI_DRY, MITSUBISHI_FAN]
    #temp = [16]
    with open('file.txt', 'w') as f:

        for idmode, mode in enumerate(modes):
            if (idmode != 0):
                print(',', file=f)
            
            tempstr = '"' + labelmode(mode) + '": {'
            print(tempstr, file=f)

            for idfan, fan in enumerate(fanmodes):
                if (idfan != 0):
                    print(',', file=f)

                tempstr = '  "' + labelfan(fan) + '": {'
                print(tempstr, file=f)

                for idtemp, temp in enumerate(temps):
                    
                    DataHex = [0x23, 0xCB, 0x26, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]

                    if (idtemp != 0):
                        print(',', file=f)

                    a = GetHVACCodes(DataHex, ON=True, MODE=mode, TEMP=temp, FANSPEED=fan, VANE=VANE_AUTO)
                    print(labelfan(fan) + ' ' + str(temp))
                    print ('[{}]'.format(', '.join(hex(x) for x in a)))
                    b = Convert2Raw(a)
                    tempstr = '    "' + str(temp) + '": ' + '"' + str(b) + '"'
                    print(tempstr, file=f, end='')
                
                print('\n  }', file=f, end='')
            print('\n}', file=f, end='')
        print('', file=f)