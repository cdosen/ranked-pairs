import sys
import ast
# If a voter ID is invalid, overwrite it with an error message and blacklist the vote
def identify_invalid_votes(votes, ids):


    encountered_IDs = set()
    validRows = []
    idCol = -1
    for j in range(len(votes[0])):
        if 'VOTER ID' in votes[0][j].upper():
            idCol = j
            break
    for i in reversed(range(1, len(votes))):
        try:
            if votes[i][idCol] not in ids:
                votes[i][idCol]=  "INVALID VOTE! UNAUTHORIZED ID: " + str(votes[i][idCol])
            elif votes[i][idCol] in encountered_IDs:
                votes[i][idCol] =  "INVALID VOTE! REPEATED ID: " + str(votes[i][idCol])
            else:
                encountered_IDs.add(votes[i][idCol])
                validRows.append(i)
        except:
            votes[i].append("INVALID VOTE! EMPTY ID")
    return validRows


def exportValidVotes(filename, votes, rows):
    with open(filename, 'w') as data:
        print(votes[0], file=data)
        for row in rows:
            print(votes[row], file=data)

def exportAllVotes(filename, votes):
    with open(filename, 'w') as data:
        for row in range(len(votes)):
            print(votes[row], file=data)

def getIDs(filename):
    ids = set()
    with open(filename, 'r') as data:
        while True:
            id = data.readline()
            if id == '':
                break
            ids.add(ast.literal_eval(id))
    return ids

def usage():
    print("usage: \nverifyVotes.py rawVoteData IDFIle")
    exit(2)



if __name__ == "__main__":
    try:
        data = sys.argv[1]
    except:
        usage()
    with open(data, 'r') as votecsv:
        votes = '[\'' + votecsv.readline().strip().replace(',','\',\'')
        votes = votes + '\']'
        votes = [ast.literal_eval(votes)]
        line = ast.literal_eval('['+votecsv.readline().replace(',,',',0,').strip()+']')
        while line != []:
            votes.append(line)
            line = ast.literal_eval('['+votecsv.readline().replace(',,',',0,').strip()+']')
    try:
        idFile = sys.argv[2]
    except:
        usage()

    ids = getIDs(idFile)
    rows = identify_invalid_votes(votes, ids)

    exportValidVotes('VALID_' + data, votes, rows)
    exportAllVotes('PROCESSED_' + data, votes)
