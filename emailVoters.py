#!/usr/bin/env python3

#--------------------------------------------------------------------------
# Project:
# Allow a ranked-pairs google form to be emailed to a list of people. This
# will allow them to securely vote. Note that, as of right now, the sent folder
# of the gmail address supplied in this code (which you must change to yours) is
# not deleted, that must be done manually.
#
# See the README.md for more information
#
# Prerequisites:
# Manual survey creation on the Google Forms website
# required. Several gmail configuration steps and library installations are
# required to get this working on a fresh project. See README.md
#
# Author: Jordan Bonilla (minor modifications by Chris Dosen)
# Date  : March 2016 (edits Novemnber 2018)
# License: All rights Reserved. See LICENSE.txt
#--------------------------------------------------------------------------

# Allows Google API calls
import gspread
from oauth2client.service_account import ServiceAccountCredentials
# Common headers
import sys
import random
import time
# Enables basic email functionality
import imaplib
import smtplib
import textwrap

# Allows commandline text to be entered without echoing
import getpass
# Allows pinging to check internet connection
import subprocess
# Allows us to check what OS this script is running on
import os


# Global list of unique numbers used in vote validation
all_voter_ids = []
# Global string holding the survey URL
survey_url = ''
# Global list of all emails invited to this survey
all_email_addresses = []
# Unique id for all voters that identify this particular excution of this script
all_survey_ids = []
# The account that to send all emails.
HOST_GMAIL_ACCOUNT = ""
# Param that allows APIs to read from Google docs
SCOPES = [ "https://docs.google.com/feeds/ https://spreadsheets.google.com/feeds/"]
# Holds the user-specified subject line for emails
SUBJECT = ''
# The number of digits in each voter ID
VOTER_ID_LENGTH = 128
# The number of digits in the survey ID
SURVEY_ID_LENGTH = 4





# Ensure the local machine is connected to the internet. Exit if no internet.
def verify_internet_access():
    success = True
    host = "8.8.8.8" # Google
    #Windows OS
    if(os.name == "nt"):
        output = subprocess.Popen(["ping.exe",host],stdout = subprocess.PIPE).communicate()[0]
        if("0% loss" not in str(output)):
            success = False
    # UNIX
    else:
        output = subprocess.Popen(['ping', '-c 1 -W 1 ', host], stdout=subprocess.PIPE).communicate()[0]
        if("0% packet loss" not in output):
            success = False
    if(success == False):
        print(output)
        print(time.ctime() + " UNABLE TO ACCESS INTERNET")
        sys.exit(-1)


# Generate time-seeded random number with n digits. Used to generate voter IDs and pins
def random_with_N_digits(n):
    # Time-seed random values
    random.seed
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return random.randint(range_start, range_end)




# Called if an email could not be sent. Re-try the email
def email_recovery(server, FROM, TO, message, recipient):
    # Perhaps it was a network error? Wait and try again
    times_attempted = 1
    max_attempts = 5
    while(times_attempted < max_attempts):
        print("Previous email failed. Retying email to " + recipient)
        try:
            time.sleep(10)
            server.sendmail(FROM, TO, message)
            break
        except:
            times_attempted = times_attempted + 1
    if(times_attempted == max_attempts):
            print("FATAL: unable to send email to " + recipient)
            server.quit()
            sys.exit(-1)
    else:
        print("Email successsfully sent to " + recipient)



# delete sent folder to ensure voter anonymity. This prevents association of
# voter ID with email address and prevents pins from being recovered
# TODO debug this function
def delete_sent_folder(sender, password):
    m = imaplib.IMAP4_SSL("imap.gmail.com")  # server to connect to
    m.login(sender, password)

    # Move sent folder to trash
    print("Moving sent folder to trash... ")
    m.select('Sent')
    typ, data = m.search(None, 'ALL')
    for num in data[0].split():
        box.store(num, '+FLAGS', '\\Deleted')
    box.expunge()

    #This block empties trash
    print("Emptying Trash...")
    print(str(m.select('[Gmail]/Trash')))  # select all trash
    m.store("1:*", '+FLAGS', '\\Deleted')  #Flag all Trash as Deleted
    m.expunge()  # not need if auto-expunge enabled

    m.close()
    m.logout()
    print("Sent folder successfully deleted.\n")


def partition(dataList, low, high):
    '''
    partition function for inplace quicksort

    inputs:
        dataList: a list of IDs
        low: the low index in the list
        high: the hiogh index in the list

    returns:
        the index of the pivot
    '''
    pivot = dataList[high]
    i = low - 1
    for j in range(low, high):
        if dataList[j] > pivot:
            i += 1
            temp = dataList[i]
            dataList[i] = dataList[j]
            dataList[j] = temp
    dataList[high] = dataList[i + 1]
    dataList[i + 1] = pivot
    return i + 1


def quicksort(dataList, low, high):
    '''
    typical inplace quicksort alogrithm

    inputs:
        dataList: a list of IDs
        low: the low index in the list
        high: the high index in the list

    returns:
        nothing, but the dataList is sorted in the process
    '''
    if low < high:
        index = partition(dataList, low, high)
        quicksort(dataList, low, index - 1)
        quicksort(dataList, index + 1, high)

def encryptIDs():
    '''
    uses quicksort to sort pairs by margin of victory, with number of votes for
    the losing candidate as the tiebreaker

    inputs:
        voteData: a dictionary of dictionaires of ints reprensting the number of
            people preferring the first key over the second key
    returns:
        a sorted list of 4-tuples, the first element being the winner, second
        the loser third the margin of victory, and 4th the votes for loser
    '''

    global all_voter_ids
    quicksort(all_voter_ids, 0, len(all_voter_ids) -1)









# Send links to the survey, along with the unique voter IDs (embedded in URL), and survey pin
# returns an "encrypted" list of IDs. (It's actually just sorted in numerical order
# with no way to tie a number to a voter)
def email_the_links(gmail_password):
    print("Sending emails to all eligible voters...")
    if(all_email_addresses == []):
        print("FATAL: no email addresses loaded")
        sys.exit(-1)
    num_voters = len(all_email_addresses)
    if(num_voters == 0):
        print('FATAL: No email addresses')
        sys.exit(-1)
    elif(SUBJECT == ''):
        print('FATAL: No subject line')
        sys.exit(-1)

    sender = HOST_GMAIL_ACCOUNT
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.ehlo()
    server.starttls()
    server.ehlo()

    server.login(sender, gmail_password)
    FROM = sender

    global all_voter_ids
    global all_survey_ids
    unique_urls = []
    # Generate voter IDs and pins
    used_voter_ids = {}
    message = None
    for i in range(num_voters):
        this_voter_id = random_with_N_digits(VOTER_ID_LENGTH)
        while(this_voter_id in used_voter_ids):
            this_voter_id = random_with_N_digits(VOTER_ID_LENGTH)
        used_voter_ids[this_voter_id] = True
        all_voter_ids.append(str(this_voter_id))
        all_survey_ids.append(str(random_with_N_digits(SURVEY_ID_LENGTH)))
        unique_urls.append(survey_url + all_voter_ids[i])

    BODY = \
            textwrap.fill("This is a unique link assigned to you. For this reason, " \
            + "please do not share this link or forward this email to anyone else. " \
            + "Please save this email message so " \
            + "that you have your unique pin and url on file should a vote's legitimacy " \
            + "fall into question.\n\nYOUR VOTER ID IS CONTAINED IN THE URL")
    for i in range(num_voters):
        try:
            TO = all_email_addresses[i]
            TEXT = 'Hi, ' \
            + "\n\nHere is your link to vote: \n" + unique_urls[i] \
            + "\n\n" + BODY \
            + "\n\nThank you for voting in Dabney Elections!"
            # Prepare actual message
            message = """\From: %s\nTo: %s\nSubject: %s\n\n%s
            """ % (FROM, TO, SUBJECT, TEXT)
            server.sendmail(FROM, TO, message)
        except:
            email_recovery(server, FROM, TO, message, TO)
        # Don't risk sending too many emails in too short a time span
        time.sleep(2)
        # Write progress to local terminal
        #sys.stdout.write('\r')
        #sys.stdout.write("[%-20s] %d%%" % ('='*(20 * (i+1)/num_voters), 100 * (i+1)/num_voters))
        #sys.stdout.flush()
    print("\nAll unique links sent. Total number of emails sent: " + str(num_voters) + " / " + str(num_voters))

    #uncomment this when debugged
    #delete_sent_folder(sender, gmail_password)
    server.quit()




# Verify survey URL meets specifications
def verify_survey(survey_url):
    if(survey_url[-1] != '='):
        print('FATAL: Invalid spreadsheet URL, did you remember to change the URL to pre-fill ID?')
        sys.exit(-1)
    elif('https://docs.google.com/forms' not in survey_url):
        print("FATAL: Invalid spreadsheet URL. Please check for typos.")
        sys.exit(-1)



# Make sure that the gmail password associated with the host is correct
def verify_gmail_pass(gmail_password):
    try:
        sender = HOST_GMAIL_ACCOUNT
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(sender, gmail_password)
        server.quit()
    except:
        print("Wrong gmail password name. Exiting")
        sys.exit(-1)


def reportIDs(filename, IDList):
    with open(filename, 'w') as log:
        for ID in IDList:
            log.write(str(ID)+ '\n')


def get_all_elgible_email_address():
    filename = input('enter file containing emails: ')
    with open(filename, 'r') as emails:
        while True:
            email = emails.readline().strip()
            if email == '':
                break
            all_email_addresses.append(email)

# Entry point
if __name__ == "__main__":
    verify_internet_access()
    # URL retrived from manually-created Google survey
    survey_url = input('Enter survey URL:')
    verify_survey(survey_url)
    HOST_GMAIL_ACCOUNT = input("Enter gmail account name:")
    # Password to gmail account
    gmail_password = getpass.getpass('[ECHO DISABLED] Enter password to gmail account:')
    verify_gmail_pass(gmail_password)
    # Subject as it will appear in emails
    SUBJECT = input('Enter email subject:')

    # Load all email addresses to be used in this survey into global variable "all_email_addresses"
    get_all_elgible_email_address()
    # All input params are good. Email links to the survey
    email_the_links(gmail_password)
    encryptIDs()
    fileID = input('Enter filename to write IDs to: ')
    reportIDs(fileID, all_voter_ids)
