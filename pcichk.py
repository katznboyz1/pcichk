import os, datetime, re

LSPCI_OUTPUT_FOLDER = 'lspci-outputs'

if (LSPCI_OUTPUT_FOLDER not in os.listdir('.')):
    os.mkdir(LSPCI_OUTPUT_FOLDER)
'''
currentTime = datetime.datetime.utcnow().isoformat().replace(':', '_') # replaces the hour/minute/second colons with underscores to make it filename safe

os.system('lspci -nn > {}/{}.lspcilog'.format(
    LSPCI_OUTPUT_FOLDER,
    currentTime
)) == 0
'''
lspciPreviousOutputs = os.listdir(LSPCI_OUTPUT_FOLDER)

def parseLspciOutputFile(logName) -> list: # [DEVICE_NAMES, VENDOR_DEVICE_IDS]
    logFile = str(open('{}/{}'.format(
        LSPCI_OUTPUT_FOLDER,
        logName
    )).read())

    # both of these lists will be the same length, with the same indexes for each line
    listOfDeviceNames = []
    listOfVendorDeviceIDs = []

    for line in logFile.split('\n'):

        # im not great with regex so hopefully this works
        indexOfStartOfDeviceName = 0 #re.search('[0-9A-Fa-f][0-9A-Fa-f]:[0-9A-Fa-f][0-9A-Fa-f].[0-9A-Fa-f] ', line).span()[1]
        indexOfVendorDeviceIDs = re.search('\[[0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f]:[0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f]\]', line)

        listOfDeviceNames.append(line[indexOfStartOfDeviceName:indexOfVendorDeviceIDs.span()[0]])
        listOfVendorDeviceIDs.append(line[indexOfVendorDeviceIDs.span()[0]:indexOfVendorDeviceIDs.span()[1]])
    
    return [
        listOfDeviceNames, 
        listOfVendorDeviceIDs
    ]

if (len(lspciPreviousOutputs) >= 2):

    # [DIFFERENCE_TYPE, DEVICE_NAME, VENDOR_DEVICE_ID]
    # DIFFERENCE_TYPE:
    #   0 = new device
    #   1 = missing device
    #   2 = same device with a different vendor:device id
    differences = []

    currentOutput = parseLspciOutputFile(lspciPreviousOutputs[-1])
    previousOutput = parseLspciOutputFile(lspciPreviousOutputs[-2])

    # loop through the previous and current device ids/names and check if they are equal
    # if name is the same, but the id is different, assume that the device is the same and DIFFERENCE_TYPE is 2
    # if the name and vendor id are different, assume that DIFFERENCE_TYPE is 0 (and decrease the current device count, since there was no existing card in that index before)
    # if the current card/current id are not in the previous output, then the card is new

    previousDevice = 0
    for currentDevice in range(len(previousOutput[1])):
        try:
            deviceNameIsEqual = previousOutput[0][previousDevice] == currentOutput[0][currentDevice]
            deviceIdIsEqual = previousOutput[1][previousDevice] == currentOutput[1][currentDevice]

            if (deviceNameIsEqual and not deviceIdIsEqual):
                differences.append([
                    2,
                    currentOutput[0][currentDevice],
                    currentOutput[1][currentDevice]
                ]) # device is same but with a different vendor:device id

            elif (currentOutput[0][currentDevice] not in previousOutput[0] or currentOutput[1][currentDevice] not in previousOutput[1]):
                differences.append([
                    0,
                    currentOutput[0][currentDevice],
                    currentOutput[1][currentDevice]
                ]) # device is new
                previousDevice -= 1

            elif (previousOutput[0][currentDevice] not in currentOutput[0] or previousOutput[1][currentDevice] not in currentOutput[1]):
                differences.append([
                    1,
                    previousOutput[0][previousDevice],
                    previousOutput[1][previousDevice]
                ]) # device is missing
                previousDevice -= 1

        except IndexError:
            pass

    output = ''
    for difference in differences:
        print(difference)