import nltk
from nltk.probability import FreqDist
from nltk.corpus import brown
from collections import Counter
from nltk.corpus import stopwords
import operator
from string import ascii_letters, digits

def process_phraseDict(phraseDict):
    """
    A function that cleans up each individual phrase dictionary in scene_text_dict, and leaving only number and char
    """

    # Filtering -- leaving just numbers and letters
    to_remove = []
    for phrase, count in phraseDict.items():
        if set(phrase).difference(ascii_letters + digits):
            to_remove.append(phrase)
    for word in to_remove:
        phraseDict.pop(word)

    return phraseDict

def convert_dict_to_phraseDict(phrase_dict):
    """
    A function that combines the multiple dictionaries from multiple scenes to one dictionary
    """
    phraseDict = {}
    for i in range(len(phrase_dict)):
        bag_of_word = phrase_dict[i]['bag_of_word']
        for word, count in bag_of_word.items():

            # put the word into the combined phrase dictionary
            cur_count = phraseDict.get(word, -1)
            if cur_count == -1:
                phraseDict[word] = count
            else:
                phraseDict[word] = cur_count + count

    return phraseDict

def remove_stop_words(phraseList):
    """
    A function that remove the common words
    """

    s = set(stopwords.words('english'))
    output = []
    for w in phraseList:
        if w not in s:
            output.append(w)

    return output


def process_by_frequency(phraseDict):
    """
    A function that removes the words in phrase dictionary that has a frequency lower than its
    frequency in the Brown corpus. Returns a phrase list after the removals.
    """
    phraseList = []

    # get the total number of words from phrase list dictionary
    total_phraseList_count = 0
    for word, count in phraseDict.items():
        total_phraseList_count += count

    # a word count dictionary for all brown corpus words
    corpus_word_dict = {}
    brown_total = 0
    for sentence in brown.sents():
        for word in sentence:
            brown_total += 1
            count = corpus_word_dict.get(word.lower(), -1)
            if count == -1:
                corpus_word_dict[word.lower()] = 1
            else:
                corpus_word_dict[word.lower()] = count + 1

    # remove words in phrase list that has less frequency that in brown corpus
    for word, count in phraseDict.items():
        phraseDict_freq = count / total_phraseList_count
        brown_count = corpus_word_dict.get(word, -1)
        if brown_count == -1:
            phraseList.append(word)
        else:
            brown_freq = brown_count / brown_total
            if phraseDict_freq > brown_freq:
                phraseList.append(word)
            else:
                pass

    return phraseList

def sequential_pattern_mining(transcations, min_support):
    """
    A function that extracts the frequent itemsets from the phrase lists from OCR
    Updated version from sequential_pattern_mining: duplicates are removed.
    """

    def make_n(last, second, n, makedict):
        list_last = list(last)
        output = []
        for name in last:
            for second_name in second:
                if name[n - 1] == second_name[0]:
                    temp_list = list(name)
                    tempcpy = temp_list.copy()
                    temp_list.append(second_name[1])
                    output.append(tuple(temp_list))
                    t = frozenset(temp_list)
                    makedict[t] = tempcpy
        return output

    def n_check(trans, names, n):
        n_list = {}
        removelist = []
        subset = []
        for name in names:
            counter = 0
            for sentence in trans:
                for i in range(len(sentence) - n + 1):
                    has = True
                    for j in range(n):
                        if sentence[i + j] != name[j]:
                            has = False
                    if (has):
                        counter += 1
            if (counter >= 2):
                fname = frozenset(name)
                son = makedict[fname]
                son = [son]
                for i in range(len(name) - 1):
                    if i == 0:
                        continue
                    subset = subset + [name[i:len(name)]]
                removelist = removelist + son
                n_list[name] = counter
        return n_list, removelist, subset

    double_base_counter = Counter()
    makedict = {}
    for sentence in transcations:
        for i in range(len(sentence) - 1):
            temp = (sentence[i], sentence[i + 1])
            double_base_counter[temp] += 1

    base_list2 = dict((word_pair, double_base_counter[word_pair]) for word_pair in double_base_counter if
                      double_base_counter[word_pair] >= min_support)
    second_support_names = list(base_list2)

    last = base_list2
    count = 2
    output = base_list2.copy()
    while (len(last) > 0 and count < 5):
        names_new = make_n(last, second_support_names, count, makedict)
        last, removelist, subs = n_check(transcations, names_new, count + 1)
        output.update(last)
        for i in removelist:
            if tuple(i) in output.keys():
                del output[tuple(i)]
        for i in subs:
            if i in output:
                del output[i]
        count += 1

    sorted_a = sorted(output.items())
    sorted_value = sorted(sorted_a, key=operator.itemgetter(1), reverse=True)

    return sorted_value


def patterns_to_list(frequent_patterns):
    """
    A function that takes a phrase dictionary and converts it to the input transactions for sequential pattern mining
    """
    frequent_pattern_list = []
    for words, count in frequent_patterns:
        phrase = ' '.join(words)
        frequent_pattern_list.append(phrase)

    return frequent_pattern_list
