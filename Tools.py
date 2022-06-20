import json
import os


def readthedict(dictname,mypath='none'):
    """Read the json file specified in mydict
     mydict = 'myfile.json' """
    if mypath == 'none':
        path = os.path.dirname(__file__)

    else:
        path = mypath


    pathandname = os.path.join(path, dictname)
    try:
        with open(pathandname, "r") as source:
            readeddict = json.load(source)
    except Exception as mes:
        print('Oops! something went wrong when reading json : ' + str(mes))
        readeddict = {}

    return readeddict


def readthestyle(stylename):
    """Read the css file specified in mydict
        mydict = 'mystyle.css' """
    path = os.path.dirname(__file__)
    pathandname = os.path.join(path, stylename)
    try:
        with open(pathandname, "r") as source:
            readedstyle = source.read()
    except Exception as mes:
        print('Oops! something went wrong when reading style : ' + str(mes))
        readedstyle = ''

    return readedstyle


def writethedict(mydict, dictname='poub.json', mypath='none'):
    """Write the dict in the json file in dictname = 'myfile.json'"""
    if mypath == 'none':
        path = os.path.dirname(__file__)
    else:
        if not os.path.exists(mypath):
            os.makedirs(mypath)
        path = mypath

    pathandname = os.path.join(path, dictname)

    try:
        with open(pathandname, "w") as source:
            json.dump(mydict, source, indent=4)
        answer = True
    except Exception as mes:
        print('Oops! something went wrong when writing json : ' + str(mes))
        answer = False

    return answer


def writedictinTxt(mystring, filename='poub.txt', mypath='none'):
    if mypath == 'none':
        path = os.path.dirname(__file__)
    else:
        if not os.path.exists(mypath):
            os.makedirs(mypath)
        path = mypath
    pathandname = os.path.join(path, filename)
    fichier = open(pathandname, "w")
    fichier.write(mystring)
    fichier.close()


if __name__ == '__main__':

    duck = {'duck': 'walk like a duck'}
    if writethedict(duck, 'duck.json'):
        isaduck = readthedict('duck.json')
        print(isaduck)
