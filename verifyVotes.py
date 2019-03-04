import sys
# If a voter ID is invalid, overwrite it with an error message and blacklist the vote
def identify_invalid_votes(votes, ids):


    encountered_IDs = {}
    validRows = []
    idCol = len(votes[0])
    for j in range(len(votes[0])):
        if 'VOTER ID' in votes[0][j].upper():
            idCol = j
            break
    for i in reversed(range(1, len(votes))):
        if votes[i][idCol] == '':
            votes[i][idCol] = "INVALID VOTE! EMPTY ID: " + votes[i][idCol]
        elif votes[i][idCol] not in ids:
            votes[i][idCol]=  "INVALID VOTE! UNAUTHORIZED ID: " + votes[i][idCol]
        elif votes[i][idCol] in encountered_IDs:
            votes[i][idCol] =  "INVALID VOTE! REPEATED ID: " + votes[i][idCol]
        else:
            encountered_IDs[votes[i][idCol]] = True
            validRows.append(i)
    return validRows


def exportValidVotes(filename, votes, rows):
    with open(filename, 'w') as data:
        data.write(str(votes[0]).strip() + '\n')
        for row in rows:
            data.write(str(votes[row]).strip() + '\n')

def exportAllVotes(filename, votes):
    with open(filename, 'w') as data:
        for row in range(len(votes)):
            data.write(str(votes[row]).strip() + '\n')

def getIDs(filename):
    ids = []
    with open(filename, 'r') as data:
        while True:
            id = data.readline().strip()
            print(id)
            if id == '':
                break
            ids.append(id)
    return ids

def usage():
    print("usage: \nverifyVotes.py rawVoteData IDFIle ExportName")
    exit(2)



if __name__ == "__main__":
    try:
        data = sys.argv[1]
    except:
        usage()
    with open(data, 'r') as votecsv:
        votes = votecsv.readline()
        votes = [votes.strip().replace('\"', '').strip().split(',')]
        line = votecsv.readline()
        line = line.strip().replace('\"', '').strip().split(',')
        while line != ['']:
            votes.append(line)
            line = votecsv.readline()
            line = line.strip().replace('\"', '').split(',')
    try:
        idFile = sys.argv[2]
        voteFile = sys.argv[3]
    except:
        usage()
    ids = getIDs(idFile)
    rows = identify_invalid_votes(votes, ids)

    exportValidVotes(voteFile, votes, rows)
    exportAllVotes(data, votes)
