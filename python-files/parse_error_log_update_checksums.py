# Requires python 3.x
import os
import re
import sys
import zipfile
import shutil

dlcsProcessed = []


def find_new_checksums( errorLogPath ):
	newChecksums = {}
	if os.path.isfile(errorLogPath):
		with open(errorLogPath, 'r') as errorLogFile:
			contents = errorLogFile.read()

			pattern = 'dlc\/(dlc.*)\/.*\[checksum="(\w*)"\]'
			for match in re.finditer(pattern, contents):
				if len(match.groups()) == 2:
					newChecksums[match.groups()[0]] = match.groups()[1]
				else:
					print ( 'Weird error log file!' )

	else:
		print ( 'Could not find any error log file!' )

	return newChecksums


def update_checksum( dlcId, directory, newChecksums ):

	print ( 'Checking ' + dlcId + '...' )

	if not dlcId in newChecksums:
		return

	for file in os.listdir(directory):
		suffix = '.dlc'
		if suffix in os.path.basename(file):
			dlcIdFilePath = os.path.join(directory, file) #./dlc00X_<name>/dlc00X.dlc
			break
			
	print ( dlcIdFilePath + '...' )

	if os.path.isfile(dlcIdFilePath):

		with open(dlcIdFilePath, 'r+') as dlcFile:
			contents = dlcFile.read()

			contents = re.sub('checksum\\s*=\\s*\\\"\\w*\"', 'checksum = \"' + newChecksums[dlcId] + '\"' , contents)

			dlcFile.seek( 0 )
			dlcFile.write( contents )
			dlcFile.truncate()

			dlcsProcessed.append(dlcId)

#Parse arguments
DLCDir = "."
errorLogPath = os.path.expanduser('~/Documents/Paradox Interactive/Europa Universalis IV/logs/error.log')

if len(sys.argv) >= 2:
	DLCDir = sys.argv[1]

if len(sys.argv) >= 3:
	errorLogPath = sys.argv[2]

#Find new checksums
newChecksums = {}
print ( 'DLC directory (1st arg): ' + DLCDir )
print ( 'Error log path (2nd arg): ' + errorLogPath )
newChecksums = find_new_checksums( errorLogPath )

if newChecksums:
	#Do the checksum update on all folders
	for content in os.listdir(DLCDir):
		if os.path.isdir(content):
			update_checksum(content, os.path.join(DLCDir, content), newChecksums)

if dlcsProcessed:
	#Print results
	dlcsProcessed.sort()
	print ( 'Updated the following DLCs checksums:' )
	for dlc in dlcsProcessed:
		print ( dlc )
