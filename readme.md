## Online Ranked Pairs Voting Programs

# Citations
Credit for the code used to emailVoters goes to Jordan Bonilla. The security and anonymity section of this readme was written by him for a similar project.

# Usage Instructions:

1. Prep the google account and the computer running emailVoters as specified in below, in the one-time-prep section

2. Set up a google form (see format for forms, below)

3. run emailVoters.py. You will need a file with one email address per line prepared. You will be prompted for everything you need.

4. Let people vote. Also delete the sent folder of your email address for the purpose of anonymity.

5. run verifyVotes.py. include as commandline args a downloaded copy of the output of the form in .csv format, the file containing the IDs from step 3, and the name of a file you want the valid votes exported to. These files should be in that order.

6. make a file that is just the headers of the result from step 5. Then delete all entries from that new file that are not candidates in the current election.

7. run countVotes.py. Include as commandline args the file from step 5, then the file from step 6. you may include --file [insert name for an output text file here], if you want a full report of the process, as opposed to just the result.


# Security and anonymity:

1. The python script generates a unique 128-digit-time-seeded random int for each email address that is eligible to vote. This number is embedded in the URL of the Google survey link and is automatically added to the “voter ID” field in the survey. When votes are read from the Python script, it will check the “voter ID” field of submitted votes and confirms that they corresponding to originally-generated ID. This makes it so duplicate/unauthorized votes can be invalidated.

2. If someone manually adds a vote to the spreadsheet, it will certainly not have a valid 128-digit entry and will be invalidated in the final count.

3. If a voter votes more than once, only the most recent vote counts (this allows people to change their vote, or to have staggered elections for multiple offices on the same form).

4. The IDs are sorted in numerical order after being sent out. This prevents tying them back to an individual. However, you still need to delete the contents of the sent folder of your email to fully secure the anonymity of voters at this time.




# One time Prep:

1. Ensure you have Python 3.x and the following libraries:
      - gspread
      - oauth2client

2. Allow access to less secure apps on your google account.
    - you can google how to do this, it's very straight forward

# Format for Forms
    - The survey questions must be multiple choice grids, allow for multiple responses per column
    - For every candidate, make a new row with their name
    - Columns are ints that go from 0 to num_candidates with 1 being the worst, 0 abstain
    - Last question must be a short answer question that holds voter ID (it doesn't have to be the last question, it just has to be a question)
    - Get the URL from the pre-fill link such that values appended to the URL automatically fill in "voter ID". You will need to "inspect element" to do this on your browser. Make sure you are pretending to fill out a ballot when doing this. Inspect element on the box, and look for an attribute in the code that has "entry.xxx" where xxx is some number. Add that to the url and make sure the url looks like below:
    - This URL looks something like: https://docs.google.com/forms/d/xxx...xxx/viewform?entry.xxx...xxx=
    - I recommend testing this url by adding the letter a at the end of it, and then going to that page when not logged in to your google account. If you see the letter a in the box pre-filled out, it worked. Just make sure to remove the letter a from the url before sending it out.
    - Suggested survey options: shuffle row order, disable all confirmation page links
    - hide show summary of responses
    - the voter id input box must have the phrase "voter id" contained within the title of it. it is not case sensitive


# License
For emailVoters.py:
Copyright (c) 2016, Jordan Bonilla
All rights reserved.

For everything else:
Copyright (c) 2018, Chris Dosen
All rights reserved.


Notice:
Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in
      the documentation and/or other materials provided with the distribution

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
