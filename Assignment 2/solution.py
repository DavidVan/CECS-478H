import sys
import math
import random
from math import log10
from itertools import islice

# Old stuff commented out... rot() would take in a character and rotate it n times.
# def rot(c, n):
#     charOrder = ord(c)
#     newOrder = charOrder + n
#     if (c.isupper() and newOrder > 90 or newOrder > 122):
#         newOrder = newOrder - 26
#     return chr(newOrder)

# def unscramble(sentence, rotations):
#     answer = ''
#     for character in sentence:
#         if (character != ' '):
#             answer += rot(character, rotations)
#         else:
#             answer += ' '
#     return answer

# Create a substitutor object that allows us to map from one character set to another character set
def substitutor(original_chars, new_chars):
    return bytes.maketrans(original_chars.encode(), new_chars.encode())

# Encode a given sentence with a key
def encode(sentence, key):
    return sentence.translate(substitutor('abcdefghijklmnopqrstuvwxyz', key))

# Decode a given sentence with a key
def decode(sentence, key):
    return sentence.translate(substitutor(key, 'abcdefghijklmnopqrstuvwxyz'))

# Encode a given sentence with a key - with capital letters version
def encode_with_caps(sentence, key):
    return sentence.translate(substitutor('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', key))

# Decode a given sentence with a key
def decode_with_caps(sentence, key):
    return sentence.translate(substitutor(key, 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'))

# Removes spaces from a sentence
def remove_spaces(sentence):
    return sentence.replace(' ', '')

# From https://docs.python.org/release/2.3.5/lib/itertools-example.html
def window(seq, n=2):
    """Returns a sliding window (of width n) over data from the iterable
       s -> (s0,s1,...s[n-1]), (s1,s2,...,sn), ...                   """
    it = iter(seq)
    result = tuple(islice(it, n))
    if len(result) == n:
        yield result
    for elem in it:
        result = result[1:] + (elem,)
        yield result

# Create a bigram given a sentence (e.g. "abcde" => ["ab", "bc", "cd", "de"])
def bigram(sentence):
    sentence = remove_spaces(sentence)
    return [''.join(x) for x in window(sentence, 2)]

# Create a trigram given a sentence (e.g. "abcde" => ["abc", "bcd", "cde"])
def trigram(sentence):
    sentence = remove_spaces(sentence)
    return [''.join(x) for x in window(sentence, 3)]

# Create a quadgram given a sentence (e.g. "abcde" => ["abcd", "bcde"])
def quadgram(sentence):
    sentence = remove_spaces(sentence)
    return [''.join(x) for x in window(sentence, 4)]

# Given the ngrams, calculate a fitness score
def calculate_fitness(ngrams):
    fitness = 0
    for ngram in ngrams:
        if ngram in ngram_scores:
            fitness += ngram_scores[ngram]
        else:
            fitness += does_not_exist_value
    return fitness

# Shuffle all the lowercase English alphabet to create a random "key"
def get_random_key():
    key_chars = [x for x in 'abcdefghijklmnopqrstuvwxyz']
    random.shuffle(key_chars)
    return key_chars

# Adapted/Used algorithm explanation (not code) from http://www.practicalcryptography.com/cryptanalysis/stochastic-searching/cryptanalysis-simple-substitution-cipher/
# Takes in cipher text and an answer (so we can stop the algoritm)
def hillclimb(ciphertext, ngram_function, answer=None):
    ciphertext = remove_spaces(ciphertext.lower()) # Process the text... Should already be fine though... Just to be safe...
    max_fitness = -math.inf # Negative infinity for now so we can make sure we can replace it with the current best fitness score
    while True:
        count = 0 # We do about 1000 iterations per parent key before moving onto a new parent key
        parent_key = get_random_key() # Get a random key, size 26, that contains all the letters of the alphabet (lowercase)
        decoded_ciphertext = decode(ciphertext, ''.join(parent_key)) # Try to decode the ciphertext with the new key
        if decoded_ciphertext == answer: # In case we got the right answer on the first decode... return it...
            return decoded_ciphertext
        parent_fitness = calculate_fitness(ngram_function(decoded_ciphertext)) # Calculate the fitness score on the "decoded" ciphertext
        while count < 1000:
            child_key = parent_key[:] # Copy the parent key, so we can modify it without worry
            # Generate two random indexes so we can swap the letters inside the child key
            a = random.randint(0, 25)
            b = random.randint(0, 25)
            child_key[a], child_key[b] = child_key[b], child_key[a] # Swap two random characters inside the key
            decoded_ciphertext = decode(ciphertext, ''.join(child_key)) # Attempt to decode it again
            child_fitness = calculate_fitness(ngram_function(decoded_ciphertext)) # Calculate the fitness score for the new decode
            if child_fitness > parent_fitness: # If the new fitness score is lower, update the parent key with the child key and reset the counter so we can improve upon this key
                parent_fitness = child_fitness
                parent_key = child_key[:]
                count = 0
            count += 1 # Looks like we got a worse fitness score... Continue on...
        # After 1000 iterations...
        if parent_fitness > max_fitness: # If the parent fitness is greater than the max fitness, update it...
            max_fitness = parent_fitness
            parent_decode = decode(ciphertext, ''.join(parent_key)) # Try and decode the ciphertext with the current best key...
            if parent_decode == answer: # If the decoded text matches the answer we're looking for, return it.
                return parent_decode
            else: # Else, tell the user the best guess so far...
                print('Best guess so far: ' + parent_decode)
    return None # Should not reach here...

########################################################################################################################################
### Program Starts Here ################################################################################################################
########################################################################################################################################
user_choice = input('Which portion of the assignment do you want to run? Run: "regular" or "honors"?\n')
if user_choice == 'regular':
    user_choice = input('How do you want to decode the sentences? Using: "bigram", "trigram", or "quadgram" (I recommend using quadgram)?\n')
    if user_choice == 'bigram':
        ngram_filename = 'english_bigrams.txt'
        ngram_function = bigram
    elif user_choice == 'trigram':
        ngram_filename = 'english_trigrams.txt'
        ngram_function = trigram
    elif user_choice == 'quadgram':
        ngram_filename = 'english_quadgrams.txt'
        ngram_function = quadgram
    else:
        print('Invalid choice... exiting...')
        sys.exit(1)

    # Thanks to http://www.practicalcryptography.com/cryptanalysis/text-characterisation/quadgrams/ for providing the math on how to calculate a fitness score and also for providing premade bigram, trigram, and quadgram-score files.
    with open(ngram_filename) as ngram_file: # Process ngram-score file... This is used to calculate the fitness...
        ngram_scores = {}
        for line in ngram_file:
            line_score = line.lower().strip().split(' ')
            ngram = line_score[0]
            score = int(line_score[1])
            ngram_scores[ngram] = score
        n = sum(ngram_scores.values())
        for key in ngram_scores.keys():
            ngram_scores[key] = log10(float(ngram_scores[key] / n))
        does_not_exist_value = log10(0.01 / n)

    sentence1 = 'fqjcb rwjwj vnjax bnkhj whxcq nawjv nfxdu mbvnu ujbbf nnc'
    sentence2 = 'oczmz vmzor jocdi bnojv dhvod igdaz admno ojbzo rcvot jprvi oviyv aozmo cvooj ziejt dojig toczr dnzno jahvi fdiyv xcdzq zoczn zxjiy'
    sentence3 = 'ejitp spawa qleji taiul rtwll rflrl laoat wsqqj atgac kthls iraoa twlpl qjatw jufrh lhuts qataq itats aittk stqfj cae'
    sentence4 = 'iyhqz ewqin azqej shayz niqbe aheum hnmnj jaqii yuexq ayqkn jbeuq iihed yzhni ifnun sayiz yudhe sqshu qesqa iluym qkque aqaqm oejjs hqzyu jdzqa diesh niznj jayzy uiqhq vayzq shsnj jejjz nshna hnmyt isnae sqfun dqzew qiead zevqi zhnjq shqze udqai jrmtq uishq ifnun siiqa suoij qqfni syyle iszhn bhmei squih nimnx hsead shqmr udquq uaqeu iisqe jshnj oihyy snaxs hqihe lsilu ymhni tyz'

    print('Notice: you may need to run this program several times to get the right answers for all sentences.\n')

    print('Decrypting Sentence 1...')
    print('\nSentence 1 Decrypted: ' + hillclimb(sentence1, ngram_function, 'whatsinanamearosebyanyothernamewouldsmellassweet'))
    print('\nSentence 1 Cleaned Up: whats in a name a rose by any other name would smell as sweet\n')

    print('Decrypting Sentence 2...')
    print('\nSentence 2 Decrypted: ' + hillclimb(sentence2, ngram_function, 'therearetwothingstoaimatinlifefirsttogetwhatyouwantandafterthattoenjoyitonlythewisestofmankindachievethesecond'))
    print('\nSentence 2 Cleaned Up: there are two things to aim at in life first to get what you want and after that to enjoy it only the wisest of man kind achieve the second\n')

    print('Decrypting Sentence 3...')
    print('\nSentence 3 Decrypted: ' + hillclimb(sentence3, ngram_function, 'contrariwisecontinuedtweedledeeifitwassoitmightbeandifitweresoitwouldbebutasitisntitaintthatslogic'))
    print('\nSentence 3 Cleaned Up: contrariwise continued tweedle dee if it was so it might be and if it were so it would be but as it isnt it aint thats logic\n')

    print('Decrypting Sentence 4...')
    print('\nSentence 4 Decrypted: ' + hillclimb(sentence4, ngram_function, 'sohewaxesinwealthnowisecanharmhimillnessoragenoevilcaresshadowhisspiritnoswordhatethreatensfromeveranenemyalltheworldwendsathiswillnoworseheknowethtillallwithinhimobstinatepridewaxesandwakeswhilethewardenslumbersthespiritssentrysleepistoofastwhichmastershismightandthemurderernearsstealthilyshootingtheshaftsfromhisbow'))
    print('\nSentence 4 Cleaned Up: so he waxes in wealth no wise can harm him illness or age no evil cares shadow his spirit no sword hate threatens from ever an enemy all the world wends at his will no worse he knoweth till all within him obstinate pride waxes and wakes while the warden slumbers the spirits sentry sleep is too fast which masters his might and the murderer nears stealthily shooting the shafts from his bow\n')
elif user_choice == 'honors':
    honors_sentence1 = 'He who fights with monsters should look to it that he himself does not become a monster. And if you gaze long into an abyss, the abyss also gazes into you.'
    honors_sentence2 = 'There is a theory which states that if ever anybody discovers exactly what the Universe is for and why it is here, it will instantly disappear and be replaced by something even more bizarre and inexplicable. There is another theory which states that this has already happened.'
    honors_sentence3 = 'Whenever I find myself growing grim about the mouth; whenever it is a damp, drizzly November in my soul; whenever I find myself involuntarily pausing before coffin warehouses, and bringing up the rear of every funeral I meet; and especially whenever my hypos get such an upper hand of me, that it requires a strong moral principle to prevent me from deliberately stepping into the street, and methodically knocking people\'s hats off - then, I account it high time to get to sea as soon as I can.'
    # Clean up sentences...
    # honors_sentence1 = remove_spaces(honors_sentence1.lower().replace(' ', '').replace('.', '').replace(',', ''))
    # honors_sentence2 = remove_spaces(honors_sentence2.lower().replace(' ', '').replace('.', '').replace(',', ''))
    # honors_sentence3 = remove_spaces(honors_sentence3.lower().replace(' ', '').replace('.', '').replace(',', '').replace('\'', '').replace(';', '').replace('-', ''))
    print('\nEncoding: sentence 1 using key (includes caps): mgquykncxptdhvzaserlofjwbiMGQUYKNCXPTDHVZASERLOFJWBI')
    print('Original: ' + honors_sentence1)
    print('Encoded: ' + encode_with_caps(honors_sentence1, 'mgquykncxptdhvzaserlofjwbiMGQUYKNCXPTDHVZASERLOFJWBI'))
    print('Decoded: ' + decode_with_caps(encode_with_caps(honors_sentence1, 'mgquykncxptdhvzaserlofjwbiMGQUYKNCXPTDHVZASERLOFJWBI'), 'mgquykncxptdhvzaserlofjwbiMGQUYKNCXPTDHVZASERLOFJWBI'))
    print('\nEncoding: sentence 2... using key (includes caps): bknqzulactseowpdvhmfyxgijrBKNQZULACTSEOWPDVHMFYXGIJR')
    print('Original: ' + honors_sentence2)
    print('Encoded: ' + encode_with_caps(honors_sentence2, 'bknqzulactseowpdvhmfyxgijrBKNQZULACTSEOWPDVHMFYXGIJR'))
    print('Decoded: ' + decode_with_caps(encode_with_caps(honors_sentence2, 'bknqzulactseowpdvhmfyxgijrBKNQZULACTSEOWPDVHMFYXGIJR'), 'bknqzulactseowpdvhmfyxgijrBKNQZULACTSEOWPDVHMFYXGIJR'))
    print('\nEncoding: sentence 3... using key (includes caps): iyarwtufjenvdoqxlcskzpghbmIYARWTUFJENVDOQXLCSKZPGHBM')
    print('Original: ' + honors_sentence3)
    print('Encoded: ' + encode_with_caps(honors_sentence3, 'iyarwtufjenvdoqxlcskzpghbmIYARWTUFJENVDOQXLCSKZPGHBM'))
    print('Decoded: ' + decode_with_caps(encode_with_caps(honors_sentence3, 'iyarwtufjenvdoqxlcskzpghbmIYARWTUFJENVDOQXLCSKZPGHBM'), 'iyarwtufjenvdoqxlcskzpghbmIYARWTUFJENVDOQXLCSKZPGHBM'))
else:
    print('Invalid choice... exiting...')
    sys.exit(1)