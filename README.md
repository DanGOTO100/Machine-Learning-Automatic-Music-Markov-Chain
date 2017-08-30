# Machine-Leaning-Automatic-Music-Markov-Chain
Automatic music composition based on Machine Learning and Markov Chains

This code will generate a music score based on a input score on midi format. Uses **Markov Chains and probabilty tweaks** with 
Pandas in order to build the score. 
It was designed with the "For the love of God" score by Steve Vai - probably the best guitar virtuoso in the music business.
The code also tries to understand the duration between notes and octaves, avoiding sudden changes of those. For example: if we are building 
a melody, then the duration must be similar on the riff. Similar when we are solo-ing, we must concatenate low duration notes.

It basically uses the following functions:


**ConverMiditoList** : This function will convert an input midi file to a Music21 object, that will allows us to later manipulate the score 
efficiently. Note that if the input midi file, you might need to explore the Music21 part, to obtain the istrument you want to analyze. In 
the tab under study it was partStream[5]. See code comments for further info. 

**createMarkovChain** : This function will create a Markov Chain of first order. Computes probabiliites from one note to other.

**buildsong** : This function will build a song on the number of notes specified as input in the Music21 format. It will use Markov chains
and probabilities to  go for one note to other. Pitch and duration are "tweaked" to mantain the duration and octaves, trying to keep melody and solo "modes.".

Further study would be to parametrize automatically the tweaks for duration and octaves and create a numpy array of probabiity for those.
Detecting usual duration, lenght and octaves for each part of the songs and appling it automatically. In this code is set manually via 
conditional statements like:
```
             if durations == 'S':
                x = np.random.choice(['64th','32nd','16th','eighth'], 1, p=[0.20,0.20,0.30,0.30])
```

An example of how to use the code:

```


Convlist = ConverMiditoList('C:\\Tabs\\FTLOG.mid')
Chainfirstorder = createMarkovChain(Convlist)
buildsong(Chainfirstorder,500)
```
