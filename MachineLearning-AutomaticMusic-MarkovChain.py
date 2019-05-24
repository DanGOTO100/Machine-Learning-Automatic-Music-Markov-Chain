from music21 import *
import pandas as pd
import numpy  as np
import re
from itertools import groupby
#from scipy import stats

#markov chain
#two additionial sets: try to preserve the octaves in a % of probability to give contiuity to melody building up
#the other, try to set 3 types of duration and assign a % of continuing being in one of then. Example, if we come from a note
#whose duration is tagged as melody (duration seems melody wise), then in a % we will keep the same duration. if not it jumps almost "randomly" from duration and there is less continuity


def ConverMiditoList(path):

    s = converter.parse(path)

    print("Parsed Midi file into Music21 Objects: ")
    print(s)                                         #s is a music21 score object
    print(" ")
    partsinside = s.elements
    partStream = s.parts.stream()

    print("Parts inside the MIDI file: ")
    print(partsinside)                                #get the part  iterator from the score object, In the Steve's Vais case Part 5 (99708208) is where the solo guitar goes
    notestream = partStream[5].flat.notes.stream()   #flat to make all voices inside the part available
    #print(notestream.elements)                       #notestream.show('midi') to make sure we have the rigt part.
    print("")

    ll=[]
    for el in notestream.notes:                 #Let's loop through the notes iterator and create a list with pitch.duration
        pit = str(el.pitches)
        dur = str(el.duration)
        pit = pit.split(" ")[1][0:2]            #Extract the pitch and octave from the music21 standard notation. In element 1 of the spllit is the info. the eelmento "0" is the music21 text
        dur = dur.split(" ")[1][:-1]            #Extract the duration. Same about [1] element as comment above

        if dur.find("/") != -1:                 #convert fractions to floats
            durfrac = dur.split("/")
            dur = float(durfrac[0]) / float(durfrac[1])

        if float(dur) > 0.25:                   #Now, every note that with duration higher than 0.25 is melody assign "M" as an indication
            if float(dur)>0.75:
                dur="L"
            else:
                dur = "M"                           #every note with duration less than 0.25 is solo markit with "S", long melody "L" is for long notes, briding melody "M" are connecting both
        else:                                   #Our Parlov chaings will have different paths if Steve is soloing or buidling up melody
            dur="S"

        joinpitdur = pit+"-"+dur                #We know create a list of composed by "Pitch-duration", the "-" will be used to split later on
        ll.append([joinpitdur])
    return ll


def createMarkovChain(listin):   #function to build Parlov Chains, needs a list with the values, returns Panda DF with note Origin , next note and the associate probability



    songlenght = len(listin)
    pharselenght = 2
    phrasecount = {}


    for elements in range(0, songlenght):
        token = listin[elements:(pharselenght + elements)]  #index the list to take n, n+order elements and added to dictionary or add another occurence
        tokenst = repr(token)
        if tokenst[1] != "#":
            tokenstr = tokenst[3:7]  + "," + tokenst[13:17]               #we need to parse the string a little
        else:
            tokenstr = tokenst[3:8] + "," + tokenst[13:17]
        if tokenst[13:17] == "":
            tokenstr = tokenst[3:8] +  tokenst[3:8]

        if tokenstr not in phrasecount:
            phrasecount[tokenstr] = 1
        else:
            phrasecount[tokenstr] += 1


    #print("DICT created from MIDI file: ", phrasecount)  #In case you want to have a look at the dictionary
                                        #Now let's build a Dataframe of origin note, destiantion note and probability.
    dictkeys, valuekeys = [],[]
    listtoindex, listtocolumn, listtovalue =[], [], []
    dictkeys= phrasecount.keys()   # get the dictonary keys and values into a list to reindex pandaDF lateron
    valuekeys= phrasecount.values()

    for elem in dictkeys:
        sap = elem[:4]
        sop = elem[5:9]
        listtoindex.append(sap)
        listtocolumn.append(sop)
    for elem in valuekeys:
        sip = elem
        listtovalue.append(sip)


                                        # Create Data Frame and normalize probabilities for "next note candidate" for each note that is our Origin
    dataf = pd.DataFrame({'Origin':listtoindex , 'Next': listtocolumn , 'values': listtovalue},index=listtoindex)
    dataf['prob'] = dataf.groupby(level=0)['values'].transform(lambda x: x / x.sum())
    #print('The Dataframe created: ',dataf)   #here in case you want to display the Dataframe.
    return dataf





def buildsong(dataff,numnotes):
                            #it needs the input of the Markov Dataframe and the numnotes the song wants to have
                            # Start with the probabilites
                            #init the vector with a random value on the dataframe
        songc = []
        flag = 0
        tt=dataff.sample(1)   #get random value to start the song
        initnote = tt['Origin'].values
        elements = dataff.loc[initnote,'Next'].values
        probabilities = dataff.loc[initnote,'prob'].values
        x = np.random.choice(elements, 1, p=probabilities)
        songc.append(str(x))
        lastpos = x

        for notes in range(1,numnotes):   #let's make a song of 500 notes
            #Here we get the event from a discrete mass probibliy function as per the values in the dataframe for the note.
            elements = dataff.loc[lastpos, 'Next'].values
            #print(type(elements))
            #print("ELE: ",elements)
            probabilities = dataff.loc[lastpos, 'prob'].values
            x = np.random.choice(elements, 1, p=probabilities)  #the value of the event under the mass prob. function


            # Add routine to keep the current octave in 60% of the time. check lastpos octave and then try to keep it
            #Main issue how to modify numpy value that "x" is now



            if "S" in str(x):                                  # we tweak the use of soloing duration "S"
                if "M" in str(lastpos):                        #if we come from a "M" duration, it is likely we keep on the melody
                    pr = np.random.choice(['M','L','S'], 1, p=[0.7,0.1,0.2]) #let's assign a new duration to the next note if we come from melody based on probabilt. This avoid random up and down into solos
                    flag=1
                    px=str(x).replace('S',str(pr)[2])

            #We fix here some notes that come with no octave, to 5-. Need to iterate over music21 to fix gap
            #if nothing to fix just add the note we have obtained from the probability event and add it to a list called songc.
            if "--" in str(x):
                 xx= str(x).replace("--","5-")
                 songc.append(xx)
            else:                              #If we modified the solo duration for something else, we know it for the flag
                if flag == 0:                     #we have different variables to use to append in the song list in each case.
                    songc.append(str(x))
                if flag == 1:
                    songc.append(px)
                    flag=0

            #print('lastpos: ', lastpos, ' NExt x-> ', x, ' notes:', notes)
            lastpos = x

        #Here we will trim the songc list into a music21 score. Need to work out with music21 object notes in duration and pitch
        m1 = stream.Measure()
        lastp = "B4"
        new = ""
        flago = 0
        for nn in songc:
             if "--" in nn:
                 nn = str(nn).replace("--", "4-")
             ns = nn.split('-')  #we split the notes in format E4-M into pitch: "E4" and duration "M"
             pitchs = ns[0]
             pitchs = pitchs[2:]
             durations = ns[1]
             durations = durations[:-2]
             lastpp = lastp[1]
             pitchsp = pitchs[1]
             if lastpp != pitchsp :
                 pro = np.random.choice(['T','F'], 1, p=[0.7, 0.3]) #if it comes a pitch, preseve it, so no jumping between octaves
                 if pro == 'T':
                     if lastpp == '#':
                         lastpp == '5'
                     new = pitchs[0]+lastpp
                     flago = 1

             if flago == 1:
                 n1 = note.Note(new)
                 flago=0

             if flago == 0:
                 n1 = note.Note(pitchs)


                     #new = pitchs[0]+pitchsp
                 #    print("corregido ptiches ",pitchs)

                                #Durations will random get a value in its interval.
                                #example, in the range "S" Soloing, we will assign different durations within the interval, with equal probability

             if durations == 'S':
                x = np.random.choice(['64th','32nd','16th','eighth'], 1, p=[0.20,0.20,0.30,0.30])
                n1.duration.type  = str(x)[2:-2]
             if durations == 'M':
                x = np.random.choice(['eighth','quarter'], 1, p=[0.5,0.5])
                n1.duration.type  = str(x)[2:-2]
             if durations == 'L':
                x = np.random.choice([1,2,4,8], 1, p=[0.25,0.25,0.40,0.10])
                x=float(x)
                n1.duration.type  = duration.convertQuarterLengthToType(x)
             m1.append(n1)


        #Build the music21 score
        part = stream.Part()
        #This piece of code in case you want to add chords progression to the song
        #parto = stream. Part()
        #ded = duration.Duration(4.0)
        #for a  in range(1,50):
        #         corde = chord.Chord('E4 G5 B5', duration=ded)
        #         parto.append(corde)
        part.append(m1)
        part.insert(0, instrument.ElectricGuitar())
        Songg = stream.Score()
        Songg.insert(0, part)
       # Songg.insert(1,parto) #here you would add the chords

        print("Generated list of notes by the process: ", songc)
        print("Generated Music21 Scoreid: ", Songg)

        #listen in midi!
        Songg.show('midi')



        return






#MAIN PROG
#now we need to built the parlov chains, 1st order for soloing and 2nd order for melody built up

Convlist = ConverMiditoList('C:\\Tabs\\FTLOG.mid')
Chainfirstorder = createMarkovChain(Convlist)
buildsong(Chainfirstorder,500)






