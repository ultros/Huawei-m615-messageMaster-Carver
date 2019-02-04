from physical import *
import binascii
count = 0

''' contact@nsa.sh 8/19/2014; realjesseshelley@gmail.com 2/4/2019
This script will carve some message
data from:
- m615 Huawei Pillar Prepaid Cellphone Cricket

This is for use within the Cellebrite UFED PA/Physical
analyzer python interpreter.

A new report will be generated within UFED PA based
on the data carved.

This is not a standalone script.
'''

def gpsEpoch2TimeStamp(gpsTimeStampLE):
	# converts datestamp
	gps_be = ""
	for i in range(4):
		gps_be = gps_be + gpsTimeStampLE[6-2*i: 8-2*i]
	#print gps_be
	try:
		ts = TimeStamp.FromUnixTime (int(gps_be, 16) + 315964800)
		return ts
	except:
		print "bad datetime value"

# messageMaster holds the data we will parse
fs = ds.FileSystems[0]
node = fs.GetByPath("/brew/mod/msgapp/mercury/db/messageMaster")

node.seek(437) # set current position in file to start of sms

msgList = [] # array to hold message chunks

# break the file up into 428 byte chunks and append to msgList array
for chunk in range(int((node.Size - 10)/428)):
	msgList.append(binascii.hexlify(node.read(428)))

for msg in msgList:
	#print msg[10:18] - this is the 4 byte datetime value needs to be verified
	
	if msg[10:18] != "00000000": # if datetime value is zero, then skip
		new_msg = SMS()
		count += 1
		new_msg.TimeStamp.Value = gpsEpoch2TimeStamp(msg[10:18])
	
		new_msg.Body.Value = (msg[178:334].replace("00", "")).decode("hex")
		new_msg.Source.Value = "Carved messageMaster"
		
		# party 
		pa = Party()
		pa.Identifier.Value = (msg[342:378].replace("00", "")).decode("hex")
		pa.Name.Value = (msg[602:662].replace("00", "")).decode("hex")
		new_msg.Parties.Add(pa)
			
		''' The values below should be verified once a tester phone is acquired '''
		if msg[18:22] == "0100":
			new_msg.Folder.Value = "Sent"
		
		elif msg[18:22] == "0142":
			new_msg.Folder.Value = "Inbox"
		
		ds.Models.Add(new_msg)
		
		# There are additional fields that can likely be determined with a test device.
