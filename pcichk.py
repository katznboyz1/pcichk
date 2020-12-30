import os, datetime, re, difflib

LSPCI_OUTPUT_FOLDER = 'lspci-outputs'
MAILTO = '' # user@domain
MAILFROM = 'Unnamed Linux Server'
SUBJECT = 'PCI Differences Detected'

if (LSPCI_OUTPUT_FOLDER not in os.listdir('.')):
    os.mkdir(LSPCI_OUTPUT_FOLDER)

currentTime = datetime.datetime.utcnow().isoformat().replace(':', '_') # replaces the hour/minute/second colons with underscores to make it filename safe

os.system('lspci -nn > {}/{}.lspcilog'.format(
    LSPCI_OUTPUT_FOLDER,
    currentTime
)) == 0

lspciPreviousOutputs = sorted(os.listdir(LSPCI_OUTPUT_FOLDER))

if (len(lspciPreviousOutputs) >= 2):
    lspciPreviousOutput = str(open('{}/{}'.format(
        LSPCI_OUTPUT_FOLDER,
        lspciPreviousOutputs[-2]
    )).read())
    lspciCurrentOutput = str(open('{}/{}'.format(
        LSPCI_OUTPUT_FOLDER,
        lspciPreviousOutputs[-1]
    )).read())
    
    differenceBetweenTwoFiles = difflib.ndiff(lspciPreviousOutput, lspciCurrentOutput)

    lines = []
    line = ['', ''] # [character, difference, actual line]
    for characterDiffPair in differenceBetweenTwoFiles:
        line[0] += characterDiffPair[-1]
        line[1] += characterDiffPair[0]
        if (characterDiffPair[-1] == '\n'):
            lines.append(line)
            line = ['', '']
    
    differences = ''

    for difference in lines:

        # i wrote these regex by hand so if they arent working for you, please raise an issue on the repo, as i am not too good with regex
        lastIndexOfIommuGroup = re.search('[0-9a-fA-F]{1,9}:[0-9a-fA-F]{1,9}.[0-9a-fA-F]{1,9} ', difference[0]).span()[1]
        indexOfBothEndsOfDeviceVendorIDPair = re.search(' \[[0-9a-fA-F]{4,8}:[0-9a-fA-F]{4,8}\]', difference[0]).span()

        name = difference[0][lastIndexOfIommuGroup:indexOfBothEndsOfDeviceVendorIDPair[0]]
        nameDifference = difference[1][lastIndexOfIommuGroup:indexOfBothEndsOfDeviceVendorIDPair[0]]

        vendorDeviceID = difference[0][indexOfBothEndsOfDeviceVendorIDPair[0]:indexOfBothEndsOfDeviceVendorIDPair[1]][1:] # [1:] since the regex returns a space at the beginning of the line, so this gets rid of it
        vendorDeviceIdDifference = difference[1][indexOfBothEndsOfDeviceVendorIDPair[0]:indexOfBothEndsOfDeviceVendorIDPair[1]][1:]

        vendorDeviceIdPairs = vendorDeviceID.split('[')[1].split(']')[0].split(':') #[1234:5678] but in a list form like ['1234', '5678']

        actualDeviceName = name + ' ' + '[{}:{}]'.format(
            vendorDeviceIdPairs[0][:4],
            vendorDeviceIdPairs[1][:4]
        ) + '\n\n' # double \n because that works better for emails

        # if the name difference is equal to a string of pluses that is equal to the length of the name, then this is a new device
        # ex:
        # name = "ijkhasfgdldkjhdsfg"
        # nameDifference = "++++++++++++++++++"
        # this would mean that name is new since the entire phrase was added
        if (nameDifference == '+' * len(name)):
            differences += ('NEW DEVICE: ' + actualDeviceName)
        
        # if the name difference is equal to a string of minuses that is equal to the length of the name, then this device was removed
        # this follows the same logic as the new device comparison, only with minuses instead of pluses
        elif (nameDifference == '-' * len(name)):
            differences += ('MISSING DEVICE: ' + actualDeviceName)
        
        # since the vendor device ids are 4 characters long, its safe to assume that a vendor device id that has a length of greater than 4 has a new id
        # this is because it would contain the old id "1234" plus the new id "5678" thus forming the string "12345678" together
        elif (len(vendorDeviceIdPairs[0]) > 4 or len(vendorDeviceIdPairs[1]) > 4):
            differences += ('SAME DEVICE BUT DIFFERENT ID: ' + actualDeviceName)

    if (len(differences) > 0):
        differences = 'To: {}\nFrom: {}\nSubject: {}\nFound {} PCI differences:\n'.format(
            MAILTO,
            MAILFROM,
            SUBJECT,
            len(differences.split('\n')) - 1
        ) + differences
        file = open('lastdiff.txt', 'w')
        file.write(differences)
        file.close()

        print(differences)
        
        os.system('cat ./lastdiff.txt | ssmtp {}'.format(MAILTO))