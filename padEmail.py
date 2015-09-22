import requests
import time
import smtplib
import base64
import pdb
import re
import pickle
from datetime import datetime as dt
import datetime
import sched
import unicodedata
import math
import os
# Takes in a list of lists called groupTimes
# Converts them to EST.
def convertToEST(groupTimes):
	newGroupTimes = [[] for i in range(5)]
	for i in range(len(groupTimes)):
		group = groupTimes[i]
		for j in range(len(group)): #timePair is hour and AM/PM, e.g. 12 pm
			timePair = group[j]
			splitPair = timePair.split()
			hour = float((str(splitPair[0])).replace(":30", ".5")) # Number 1-12 inclusive
			noon = str(splitPair[1]) # either 'am' or 'pm'
			
			noonValues = {"am":"pm", "pm":"am"}
			if(math.fabs(10-hour) <= 1): # If the hour is between 9-12, then flip the noon sign
				noon = noonValues[noon]
			# converts to EST by adding 3 hours
			hour += 3 
			if(hour>12):
				hour -= 12
			hour = str(hour).replace(".5", ":30").replace(".0", "")
			#Set the actual groupTime values to the converted values
			convertedPair = str(hour) + " " + noon
			group[j] = convertedPair
			
			
			
#This takes in an email and his group times
def sendEmail(recipient, groupTimes):
	sender = "pad.dungeon@gmail.com"
	password = base64.b64decode("UEFEc2VwMjM=")
	msg = "\r\n".join([
	  "From: " + sender,
	  "To: " + recipient ,
	  "Subject: PAD Dungeon Times for " + time.strftime("%c"),
	  "",
	  "Your Times Today Are: \n" + "\n".join(groupTimes)
	  ])
	server = smtplib.SMTP('smtp.gmail.com:587')
	server.ehlo()
	server.starttls()
	server.login(sender, password)
	server.sendmail(sender, recipient, msg)
	server.quit()
	print("Email Sent to " + recipient)


def runInstance(emailsList):
	site = requests.get('http://puzzledragonx.com')
	findTables = "<table id=\"event\">"
	findTimes = "metaltime\">"
	tables =  [(a.start(), a.end()) for a in list(re.finditer(findTables, site.text))]
	startTable = tables[1][1]
	endTable = site.text.find("</table>", startTable)
	correctTable = site.text[startTable:endTable]
	occurences = [(a.start(), a.end()) for a in list(re.finditer(findTimes, correctTable))]
	times = []
	
	for pair in occurences:
		times.append((correctTable[pair[1]:correctTable.find("<", pair[1])]))
	times = filter(lambda a: a != "--", times)
	
	groupTimes = [[] for i in range(5)]
	for i in range(len(times)):
		groupNumber = i % 5
		groupTimes[groupNumber].append(times[i])
	convertToEST(groupTimes) # Converts the group times to eastern standard timezone
	for pair in emailsList:
		pdb.set_trace()
		sendEmail(pair[0], groupTimes[pair[1]])
	
def addEmail(originalEmails, email, groupNumber):
	originalEmails.append([email, groupNumber])
	newFile = open('padList.pkl', 'w')
	pickle.dump(originalEmails, newFile)
	print(email + "successfully added to list.")
	
def removeEmail(originalEmails, email):
	for i in range(len(originalEmails)):
		if (originalEmails[i][0] == email):
			originalEmails.pop(i)
			newFile = open('padList.pkl', 'w')
			pickle.dump(originalEmails, newFile)
			print (email + " successfully removed from list.")
			return True
		
def main():
	try:
		with open('padList.pkl', 'rb') as padListFile:
			originalEmails = pickle.load(padListFile)
	except IOError:
		originalEmails = []
	while(True):
		print("Select a choice: ")
		print("		1: Add email")
		print("		2: Remove email")
		print("		3: Show emails")
		print("		4: Run the program")
		print("		0: Exit program")
		choice = input()
		if(choice == 1):
			newEmail = raw_input("Enter the email you'd like to add: ")
			padID = (raw_input("Enter your PAD ID: ")).strip(",")
			groupNumber = int(padID[2]) % 5 # The group number is based of 3rd padID digit.
			addEmail(originalEmails, newEmail, groupNumber)
		elif(choice == 2):
			emailToRemove = raw_input("Enter the email you'd like to remove: ")
			success = removeEmail(originalEmails, emailToRemove)
			if not success:
				print(emailToRemove + " was not found in the list!")
		elif(choice == 3):
			emailStr = ", ".join("'%s'" % emailPair[0] for emailPair in originalEmails).strip('\'')
			if not(emailStr):
				print("There are currently no emails in the list.")
			else:
				print(emailStr)
		elif(choice == 4):
			runInstance(originalEmails)
			break
		elif(choice == 0):
			exit()
		else:
			print("Sorry that wasn't a valid option! Try again! ")
	s = sched.scheduler(time.time, time.sleep)
	while True:
		currentTime = datetime.datetime.today()
		nextTime = currentTime.replace(day=currentTime.day+1, hour = 7, minute = 0, second = 0, microsecond = 0)
		if not s.queue:
			s.enterabs(nextTime, 1, runInstance, (originalEmails,))
			print("Job added to schedule for " + str(nextTime))
		else:
			print("Currently waiting for " + str(nextTime))
			print(str(nextTime-currentTime) + " time remaining")
			time.sleep(60)
	

	

main()