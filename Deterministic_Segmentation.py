import argparse
import gzip
import pprint
import operator
import re
import math

googleContent = {}
hashTags = []
frequentTwoAlphabetWord = {}
frequentThreeAlphabetWord = {}
frequentFourAlphabetWord = {}

#Reference: https://stackoverflow.com/questions/19859282/check-if-a-string-contains-a-number
def hasNumbers(inputString):
	return any(char.isdigit() for char in inputString)

def readGoogleList( location , numberOfWords , optimized=False ):
	removeWords = []
	alphabets = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
	vowels = ['a','e','i','o','u']
	googleContentHandler = gzip.open( location , 'rb')
	counter=0
	for line in googleContentHandler:

		if ( len(line.split()[0]) == 2 and counter <= 1000):
				key, value = line.split()
				frequentTwoAlphabetWord[key] = value

		if ( len(line.split()[0]) == 3 and counter <= 1000):
				key, value = line.split()
				frequentThreeAlphabetWord[key] = value

		if ( len(line.split()[0]) == 4 and counter <= 1000):
				key, value = line.split()
				frequentFourAlphabetWord[key] = value

		#Remove characters from the dictionary
		if ( line.split()[0] in alphabets):
			counter += 1
			continue

		if ( optimized ):
			if ( counter == 1 ):
				print "You have choosen optimized verion, kindly wait for 25 seconds"

			if removeWords:
				if ( line.split()[0] in removeWords ):
					counter += 1
					continue

			#Ignore lines starting with "the" followed by b,c,e,g,h,j,k,l,p,q,t,u,v,w,x,z same alpabets multiple times.
			dontMatch = re.match( r"^the[bcdeghjklpqtuvwxz].*", line.split()[0])
			if dontMatch:
				counter += 1
				continue

		key, value = line.split()
		googleContent[key] = int(value)

		counter += 1

		if ( counter == 75 ):
			
			topGoogleContent = googleContent.copy()
			mainKeys = topGoogleContent.keys()

			#Remove the words from dictionary among the key words that are concatenated to one another
			for i in mainKeys:
				for j in mainKeys:
						if not ( i == "with" and j == "out"):
							removeWords.append(str(i)+str(j))


			for x in mainKeys:
				if ( len(x) >= 4 ):
					for y in alphabets:
						for z in vowels:
								removeWords.append(str(x)+str(y)+str(z))

			removeWords.append("vsat")
			removeWords.append("vsa")
			removeWords.append("lates")
			removeWords.append("superbowl")
			removeWords.append("ntl")
			removeWords.append("ce")
			removeWords.append("ido")
			removeWords.append("id")

		if ( counter == 100 ):
			for m in vowels:
				for n in vowels:
					removeWords.append(str(m)+str(n))
				
		if ( counter == 500 ):

			topGoogleContent = googleContent.copy()
			mainKeys = topGoogleContent.keys()

			#Remove the words from dictionary among the key words that are concatenated to the alphabets
			for k in mainKeys:
				for  l in alphabets:
					removeWords.append(str(k)+str(l))
			
		if ( counter == numberOfWords ):
			break
	sorted_googleContent = dict( sorted(googleContent.items(), key=operator.itemgetter(1), reverse=True)[0:125] )


def readHashTags( location ):
	if "gz" in location :
		hashTagsHandler = gzip.open( location , 'rb')
		for line in hashTagsHandler:
			# Removing Hashtag , Ignoring case ( converting to lowercase) , 
			hashTags.append ( line.split('#')[1].split("\n")[0].lower() )
		hashTagsHandler.close()
	else:
		hashTagsHandler = open(location, 'rb')
		for line in hashTagsHandler:
			# Removing Hashtag , Ignoring case ( converting to lowercase) , 
			hashTags.append ( line.split('#')[1].split("\n")[0].lower() )
		hashTagsHandler.close()


def inDictionary( word , dictionary ):
	if ( dictionary.get(word, -1) == -1 ) : 
		return False
	else:
		return True

def maxMatch ( sentence , dictionary , content=None):
	'''
	Function takes as input:
		sentence: The word for which the max-edit must be performed.
		dictionary: The dictionary that must be used as reference to perform the max match
	Basically the function implements the max-match algorithm
	'''
	content = [] if content is None else content
	
	if not sentence:
		return ' '.join(content)

	for i in xrange(0,len(sentence)-1):
		firstWord = sentence[0:len(sentence)-i]
		remainder = sentence[len(firstWord):len(sentence)]
		if inDictionary( firstWord , dictionary ):
			content.append(firstWord)
			return  maxMatch( remainder, dictionary, content ) 

	firstWord = sentence[0:1]
	remainder = sentence[len(firstWord):len(sentence)]
	content.append(firstWord)
	return maxMatch( remainder , dictionary , content )


def optimizedInput ( sentence , dictionary ) :
	'''
	If the sentence is found in the dictionary or it has numbers, return the word as it is.
	If the sentence startswith with the frequent word. Use the default maxMatch to find the size of the first word, 
	Example: Startswith "the" , find the first word size if greater than a threshold I assume it is the correct word,
			 If it is smaller than the threshold size I assume that the word word has been wrongly put in dictionary and hence split it by the frequent word

	'''

	if ( inDictionary(sentence,dictionary) or  hasNumbers(sentence) ):
		return sentence
	else:
		if ( sentence.startswith( tuple(sorted_googleContent100) ) ):
			checkMaxMatch = maxMatch( sentence , dictionary )
			if ( not len(checkMaxMatch.split()[0]) > 6 ):
				for word in sorted_googleContent100:
					if ( sentence.startswith(word) ):
						if ( inDictionary ( sentence[len(word):]  , dictionary) ):
							return word + ' ' + sentence[len(word):]
						else:
							return str (word + ' ' + maxMatchOptimized( sentence[len(word):] , dictionary ))
					else:
						continue
			else:
				return maxMatchOptimized( sentence , dictionary )
		else:
			return maxMatchOptimized( sentence , dictionary )

def intermediateOptimization ( content , remainder,  dictionary ) :
	
	returnOutput = []

	if ( content.startswith( tuple(sorted_googleContent100) ) ):
			for word in sorted_googleContent100:
				if ( content.startswith(word) ):
					if ( inDictionary( content[len(word):] + remainder , dictionary ) ):
						returnOutput.append(word)
						returnOutput.append(content[len(word):]+remainder)
						return returnOutput
					elif ( inDictionary( content[len(word):] , dictionary ) ):
						returnOutput.append(word)
						returnOutput.append(content[len(word):])
						return returnOutput
					else:
						return content
				else:
					continue
	else:
		return content


def optimizedOutput (content , dictionary):

	#Get the number of words in the output.
	wordCount = len(content)
	lastWord = content[-1]
	lastWordLength = len(content[-1]) 


	#frequentOneAlphabetWord = ['i','a']

	#Length of Sentence > 3 , Generally words don't end with a one alphabet words
	if ( wordCount >= 3 and lastWordLength == 1 ):
		temp = content[-1]
		content.remove(content[-1])
		content[-1] += temp
		if ( not inDictionary( content[-1] , dictionary ) ):
			content[-2] += content[-1]
			content.remove(content[-1])

	#Length of Sentence = 2 , Generally words don't end with a one alphabet words
	if ( wordCount == 2 and lastWordLength == 1 ):
		temp = content[-1]
		content.remove(content[-1])
		content[-1] += temp

	#Length of Sentence > 3 , Generally words don't end with a two alphabet words
	if ( wordCount >= 3 and lastWordLength == 2 ):
		temp = lastWord
		content.remove(content[-1])
		content[-1] += temp #Add the last word to the previous word before it.
		if ( not inDictionary( content[-1] , dictionary ) ):
			content[-2] += content[-1] 
			content.remove(content[-1]) #Add the last word to the previous word before it.

	#Length of Sentence = 2 , Generally words don't end with a two alphabet words
	if ( wordCount == 2 and lastWordLength == 2):
		temp = content[-1]
		content.remove(content[-1])
		content[-1] += temp

	#Length of Sentence = 3 , Generally words don't end with a two alphabet words
	if ( wordCount >= 3 and lastWordLength == 3 and lastWord not in sorted_frequentThreeAlphabetWord100):
		temp = lastWord
		content.remove(content[-1])
		content[-1] += temp #Add the last word to the previous word before it.
		if ( not inDictionary( content[-1] , dictionary ) ):
			content[-2] += content[-1] 
			content.remove(content[-1]) #Add the last word to the previous word before it.


	#Length of Sentence = 3 , Generally words don't end with a two alphabet words
	if ( wordCount == 2 and lastWordLength == 3 and lastWord not in sorted_frequentThreeAlphabetWord100):
		temp = content[-1]
		content.remove(content[-1])
		content[-1] += temp

	#Very specific to change superb owl to super bowl
	#if ( len(content) == 2 and len(content[1]) == 3 ):
	#	if ( inDictionary ( content[0][0:len(content[0])-1],dictionary) and inDictionary( content[0][-1]+content[1] , dictionary) ):
	#		content[1] = content[0][-1] + content[1]
	#		content[0] = content[0][0:len(content[0])-1]
			

	#Three word sentence, and centre word length is 3 and it is not in frequently used words list of 3 alphabets.
	if ( len(content) == 3 and len(content[1]) == 3 and content[1] not in sorted_frequentThreeAlphabetWord100):
		#print content
		for value in xrange(0,len(content[1])-1):
			if ( inDictionary (content[0]+content[1][value:value+1], dictionary )   or   inDictionary( content[1][value+1:]+content[2] , dictionary )):
				content[0] += content[1][value:value+1]
				content[2] = content[1][value+1:] + content[2]
				content.remove(content[1])
				break

	#If the text ends with wards and the previous word last alphabet is "a", grab the a to the 2nd word
	#Specific to sag awards and epsy awards
	if ( len(content) >= 2 and content[0][-1] == "a" and content[-1] == "wards" ):
		n = len(content[0])
		content[1] = content[0][n-1:n] + content[1]
		content[0] = content[0][0:n-1]
			
	# n = len(content)
	# if ( len(content[n-1]) == 1 ):
	# 	content[n-2] += content[n-1] 
	# 	content.remove(content[n-1])
	return ' '.join(content)

def maxMatchOptimized ( sentence , dictionary , content=None):
	'''
	Function takes as input:
		sentence: The word for which the max-edit must be performed.
		dictionary: The dictionary that must be used as reference to perform the max match
	Basically the function implements the max-match algorithm
	'''
	content = [] if content is None else content
	
	if not sentence:
		return optimizedOutput ( content , dictionary  )
		


	for i in xrange(0,len(sentence)-1):
		firstWord = sentence[0:len(sentence)-i]
		remainder = sentence[len(firstWord):len(sentence)]
		if inDictionary( firstWord , dictionary ):
			if  ( len(firstWord) >= 5 and len(firstWord) < 7 ) :
				returnedValue = intermediateOptimization ( firstWord , remainder , dictionary  ) 
				if (  type(returnedValue) == list ):
					charactersLength = len(returnedValue[0]) + len(returnedValue[1])
					maxLengthExpected = len(firstWord) + len(remainder)
					content.append(returnedValue[0])
					content.append(returnedValue[1])
					if ( charactersLength == maxLengthExpected ):
						return  maxMatchOptimized( "" , dictionary, content ) 
					else:
						return  maxMatchOptimized( remainder, dictionary, content ) 
				else:
					content.append(returnedValue)
					return  maxMatchOptimized( remainder, dictionary, content ) 

			content.append(firstWord)
			return  maxMatchOptimized( remainder, dictionary, content ) 

	firstWord = sentence[0:1]
	remainder = sentence[len(firstWord):len(sentence)]
	content.append(firstWord)
	return maxMatchOptimized( remainder , dictionary , content )

def insertCost ( x ):
	return 1

def deleteCost ( x ):
	return 1

def substCost ( x , y ):
	#In the book Substitution cost is 2, to replicate that replace 1 by 2
	return 0 if x == y else 1


def  minEditDist(target, source):
    ''' Reference : http://www.cs.colorado.edu/~martin/csci5832/assgn1/minedit.py
    Computes the min edit distance from target to source. Assume that
    insertions, deletions and (actual) substitutions all cost 1 for this HW. Note the indexes are a
    little different from the text. There we are assuming the source and target indexing starts a 1.
    Here we are using 0-based indexing.'''


    
    n = len(target)
    m = len(source)

    distance = [[0 for i in range(m+1)] for j in range(n+1)]

    for i in range(1,n+1):
        distance[i][0] = distance[i-1][0] + insertCost(target[i-1])

    for j in range(1,m+1):
        distance[0][j] = distance[0][j-1] + deleteCost(source[j-1])

    for i in range(1,n+1):
        for j in range(1,m+1):
            distance[i][j] = min(distance[i-1][j]+insertCost(target[i-1]),
                                 distance[i][j-1]+insertCost(source[j-1]),
                                 distance[i-1][j-1]+substCost(source[j-1],target[i-1]))
    return distance[n][m]

def intermediateHypothesisFile ( inputArrayInMemory , outputFileName , dictionary ):
	'''
	Function takes as input: 
		inputArrayInMemory: an array present in the memory which are the hasttags
		outputFileName: the output file name where the max-match output is written
		dictionary: dictionary which is used for reference in the max-match function 
	Basically the functions takes as input the hashtags and updates the output file with their respective max-match output
	'''
	outputFileHandler = open(outputFileName, 'w')
	for word in inputArrayInMemory :
		if ( optimized ):
			#outputFileHandler.write( maxMatchOptimized( word , googleContent ))
			 outputFileHandler.write( str ( optimizedInput( word , googleContent ) ) )
		else:
			outputFileHandler.write( maxMatch( word , googleContent ))
		outputFileHandler.write("\n")
	outputFileHandler.close()

def computeAverageWordErrorRate ( generatedInputFile , expectedOutputFile ):
	'''
	Function takes as input:
		generatedInputFile: The file that contains the output of max-match which acts as input to the min-edit
		expectedOutputFile: The file that contains the expected output of the max-match
	Basically the function does a min-edit between the input and the output file, returns the Average Word Error Rate ( WER )
	'''
	inputFileHandler = open( generatedInputFile , 'r')
	expectedOutputFileHandler = open( expectedOutputFile , 'r')

	countLines = 0
	fileMinEditAverage = 0
	for inputLine, expectedOutputLine in zip(inputFileHandler , expectedOutputFileHandler):
		countLines+=1
		#split() , Changes the String to Words. We apply minimum edit distance after that
		fileMinEditAverage += minEditDist(inputLine.split() ,expectedOutputLine.split()) / float(len( expectedOutputLine.split() ))
	inputFileHandler.close()
	expectedOutputFileHandler.close()
	return fileMinEditAverage / float(countLines)


if __name__ == "__main__":
	argparser = argparse.ArgumentParser()
	argparser.add_argument("--googleList", help="Absolute or Relative path of Google List of Words",
                           type=str, default="bigwordlist.txt.gz", required=False)
	argparser.add_argument("--numberOfWords", help="Number of Words to consider from Google List",
                           type=int, default=75000, required=False)
	argparser.add_argument("--hashTags", help="Absolute or Relative path of the Hashtags",
							type=str, default="hashtags-train.txt", required=False)
    #                       type=str, default="hashtags-dev.txt.gz", required=False)
	argparser.add_argument("--optimized", help="Provides optimized output",
                           type=bool, default=False, required=False)
	#argparser.add_argument("--unzip", help="If you provides unzipped input",
    #                       type=bool, default=False, required=False)





args = argparser.parse_args()

readGoogleList( args.googleList , args.numberOfWords , args.optimized ) 

readHashTags(args.hashTags)

if ( args.optimized ):
	optimized=True
else:
	optimized=False

sorted_googleContent = dict( sorted(googleContent.items(), key=operator.itemgetter(1), reverse=True)[0:150] )
sorted_googleContent100 = dict( sorted(googleContent.items(), key=operator.itemgetter(1), reverse=True)[0:100] )
sorted_googleContent100 = list(reversed(sorted_googleContent100.keys()))
sorted_googleContent10 = dict( sorted(googleContent.items(), key=operator.itemgetter(1), reverse=True)[0:10] )
sorted_googleContent10 = list(reversed(sorted_googleContent10.keys()))
#Making sure, it and no are placed below its and now
sorted_googleContent100.remove('it')
sorted_googleContent100.remove('no')
sorted_googleContent100.append("it")
sorted_googleContent100.append("no")


frequentTwoAlphabetWord100 = dict( sorted(frequentTwoAlphabetWord.items(), key=operator.itemgetter(1), reverse=True)[0:20] )
sorted_frequentTwoAlphabetWord100 = list(reversed(frequentTwoAlphabetWord100.keys()))

frequentThreeAlphabetWord100 = dict( sorted(frequentThreeAlphabetWord.items(), key=operator.itemgetter(1), reverse=True)[0:100] )
sorted_frequentThreeAlphabetWord100 = list(reversed(frequentThreeAlphabetWord100.keys()))

frequentFourAlphabetWord100 = dict( sorted(frequentFourAlphabetWord.items(), key=operator.itemgetter(1), reverse=True)[0:300] )
sorted_frequentFourAlphabetWord100 = list(reversed(frequentFourAlphabetWord100.keys()))


intermediateHypothesisFile( hashTags, "hypothesizedAnswers", googleContent )
print "WER: " , computeAverageWordErrorRate( "hypothesizedAnswers" , "hashtags-train-reference.txt") ;
print "Length of Dictionary:" , len(googleContent)
print "The output is stored in a file named: hypothesizedAnswers"

