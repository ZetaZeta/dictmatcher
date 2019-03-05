from django.shortcuts import render
from .forms import InputTextForm
import os

# This is used to find all anagram candidates.
# Doing so is a major bottleneck for the program.
import itertools

# This library is used to search for matches quickly.
# It's written in C++ and is faster than anything I could reasonably put together in this timeframe.
from suffixtree import SuffixQueryTree

# Maximum number of items a matching can return.
MAX_RETURN_LENGTH = 10

# TODO: Potential memory issue with multiword anagram cache getting too big.
# We need to cap its size and trim it sometimes.
multiword_anagram_cache = {}
ana_map = {}
tree = None

# Gets the text input from the given request.
def get_text_input(request):
    if 'input_text' in request.POST:
        form = InputTextForm(request.POST)
        if not form.is_valid():
            return None
        return(form.cleaned_data['input_text'])

# Performs the appropriate matching based on the button pressed, and returns the results.
# This makes it easier to add new matching methods later.
def get_matching_by_button(request):
    input_text = get_text_input(request)
    if not input_text:
        #TODO:  Handle blank inputs distinctly from finding no anagrams?
        return None
    if 'anagram_button' in request.POST:
        return substring_anagram_search(input_text)
    raise Exception("Unrecognized button type.")

# Loads a dictionary into the data structures used to rapidly access its content.
# Also clears the caches.
# At some point we may want to store dictionary data in a database instead.
# TODO:  Have some indicator for when loading is complete, and handle requests before then more gracefully.
# TODO:  Indicate completed dictionary load in a better / more accessible way.
#
# If I had more time, a better solution would be to store the dictionary in a database,
# along with all anagrams that can be made from each word.  When new words are added to
# to removed from the database, all words would have to be updated with new possible
# anagrams, but this would still be faster than computing it on the fly and would still
# keep most dictionary updates reasonable even for a living dictionary - after a process
# had finished setting the database up, of course.  It would use up a lot of disk space, but
# disk space is cheap compared to time or memory.
#
# Obviously, this comment is a bit longer than most should be in production - detailed comments are good,
# but they have to be readable in a reasonable timeframe to be useful!
def load_dict(dict_path):
    global ana_map, tree
    multiword_anagram_cache.clear()
    with open(dict_path, 'r') as f:
        lines = []
        for line in f:
            line = line.strip()
            letters = tuple(sorted(line))
            if not letters in ana_map:
                ana_map[letters] = set()
            ana_map[letters].add(line)
            lines.append(line)
        tree = SuffixQueryTree(True, lines)
    print("Dictionary successfully loaded.")

# Gets all single-word anagrams we can make using the entire given string.
def single_word_anagrams(string):
    letters = tuple(sorted(string))
    if letters in ana_map:
        return ana_map[letters]
    else:
        return None

# Gets all sorted substrings we can build from the given string.
def all_sorted_substrings(string):
    string = sorted(string)
    return itertools.chain.from_iterable(
        [list(itertools.combinations(string,i)) for i in range(1, len(string) + 1)])

# Gets all sorted substrings from the given string that can produce valid anagrams.
def all_sorted_substring_anagrams(string):
    return filter(lambda x: x in ana_map, all_sorted_substrings(string))

# Gets all multiword anagrams we can get from the given string.
# Caches results in memory to avoid redundancy.
# If "is_first_word_ is set to true, it eliminates results that could never fit the MAX_RETURN_LENGTH.
# TODO:  This cannot handle retrieving massive amounts of anagrams in a reasonable timeframe.
def all_multiword_anagrams(string, is_first_word = True):
    if string in multiword_anagram_cache:
        return multiword_anagram_cache[string]
    if string == '':
        return []
    out = []
    for word in all_sorted_substring_anagrams(string):
        # If we're doing the first word of an anagram, skip anything that could no longer
        # appear within the MAX_RETURN_LENGTH.
        if is_first_word and len(out) >= MAX_RETURN_LENGTH:
            if second_letter_sort(out[-1]) < second_letter_sort(word):
                # Any anagram that starts with this word will never be in our return candidates, so skip it.
                continue
        
        # For words that use the remaining string, just add them to the output.
        if len(word) == len(string):
            out.extend(single_word_anagrams(string))
            continue

        # For others, we'll have to recurse to see if and how we can use the remaining string.
        # First, remove the letters they use from the pool.
        letterlist = list(string)
        for letter in word:
            letterlist.remove(letter)

        # See how we can use the remaining letters to form an anagram.  If we can't, skip this word.
        rest = all_multiword_anagrams(''.join(letterlist), False)
        if len(rest) == 0:
            continue

        # Otherwise, append the other words we found to the ones we found here and add them to the output:
        for first_anagram_word in single_word_anagrams(word):
            for other_words in rest:
                out.append(first_anagram_word + ' ' + other_words)

        # While doing the first word, keep the output sorted and constrain its length to viable output candidates.
        # This will make it easier for us to skip non-viable output candidates.
        if is_first_word:
            out = sorted(out, key=second_letter_sort)
            out = out[:MAX_RETURN_LENGTH]
    multiword_anagram_cache[string] = out
    return out

# Returns a value used for sorting strings by their second letter.
# If the second letter is a space, the third is returned.
# This assumes no doubles-spaced strings or strings ending with spaces.
# A string of length < 2 sorts as 0.
def second_letter_sort(string):
    if len(string) < 2:
        return 0
    if string[1] == ' ':
        return string[2]
    return string[1]

# From spec:
# takes a user submitted string as input
# finds all entries in the dictionary for which the input is a valid substring
# locates the combined set of all valid anagrams that can be made from each of the matching entries
# orders the valid set of anagrams alphabetically by their second letter
# returns the anagrams from the sorted anagram set (limit to maximum of 10)
# returns `None` if no matches were found
#
# (When the spec is reasonably short, I feel it's best to quote / summarize / reference it at key points,
# so anyone who later reads the code will know exactly what it was meant to do.)
#
# This could be made a bit more general to support adding new matching methods, but it's a bit unclear
# how those will work; it seems likely they may not benefit from being structured this way.
# It's also unclear if the other rules used here will apply to them.
def substring_anagram_search(string):
    # Find every entry in the dictionary for which the input is a valid substring.
    # Sort them and gather them in a set, since words that are anagrams of each other will
    # produce the same anagrams and are redundant.
    entries = set([''.join(sorted(x)) for x in tree.findString(string)])

    # Gather the anagrams of these and put them in a set to remove duplicates.
    anagrams = set()
    for entry in entries:
        for anagram in all_multiword_anagrams(entry):
            anagrams.add(anagram)

    # Sort by second letter and return the first 10.
    sorted_anagrams = sorted(anagrams, key=second_letter_sort)
    if len(sorted_anagrams) == 0:
        return None
    return sorted_anagrams[:MAX_RETURN_LENGTH]
