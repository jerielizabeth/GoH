# -*- coding: utf-8 -*-

"""
Collection of functions for cleaning the periodical text files.
"""

import GoH.clean
import GoH.utilities
import operator
from pyxdameraulevenshtein import normalized_damerau_levenshtein_distance
import re


def period_at_end(token):
    if list(token).pop() is ".":
        return True
    else:
        return False


def create_substitution(tokens, stem, get_prior, spelling_dictionary):
    locations = [i for i, j in enumerate(tokens) if j == stem]
    for location in locations:
        # Option 1
        if get_prior:
            prior_word = tokens[location - 1]
            sub_word = ''.join([prior_word, stem])

            if sub_word.lower() in spelling_dictionary:
                return (prior_word, stem)
            else:
                pass
        # Option 2
        else:
            try:
                next_word = tokens[location + 1]
                sub_word = ''.join([stem, next_word])

                if sub_word.lower() in spelling_dictionary:
                    return (stem, next_word)
                else:
                    if period_at_end(sub_word):
                        sub_stripped = "".join(list(sub_word)[:-1])
                        if sub_stripped.lower() in spelling_dictionary:
                            return (stem, "".join(list(next_word)[:-1]))
                        else:
                            pass
                    else:
                        pass
            except IndexError:
                pass


def check_if_stem(stems, spelling_dictionary, tokens, get_prior=True):
    replacements = []
    for stem in stems:
        if len(stem) > 1:
            if period_at_end(stem):
                stem_stripped = "".join(list(stem)[:-1])
                if not stem_stripped.lower() in spelling_dictionary:
                    result = create_substitution(tokens, stem, get_prior, spelling_dictionary)
                    if result is None:
                        pass
                    else:
                        replacements.append(result)

            else:
                if not stem.lower() in spelling_dictionary:
                    result = create_substitution(tokens, stem, get_prior, spelling_dictionary)
                    if result is None:
                        pass
                    else:
                        replacements.append(result)

    return replacements


def replace_split_words(pair, content):
    return re.sub('{}\s+{}'.format(pair[0], pair[1]), '{}{}'.format(pair[0], pair[1]), content)


def replace_pair(pair, content):
    """
    Uses regex to locate a pair.
    First element of the tuple is the original error token.
    Second element of the tuple is the replacement token.
    """
    return re.sub(pair[0], ' {} '.format(pair[1]), content)


def find_split_words(pattern, content):
    return pattern.findall(content)


def check_splits(pattern, spelling_dictionary, content, replacements):
    # Use regex pattern to identify "split words"
    split_words = find_split_words(pattern, content)

    # Regex pattern finds last character as a separate match. Take the first match.
    for split_word in split_words:
        test_word = split_word[0]

        restored_word = re.sub(r'\s', r'', test_word)

        if restored_word.lower() in spelling_dictionary:
            replacements.append((split_word[0], restored_word))

        # Check if the restored word failed because it is two capitalized words combined
        # into one. Check for capital letter.
        elif re.search(r'[A-Z]', test_word):
            # Find the words by looking for Aaaa pattern
            words = re.findall('([A-Z][a-z]+)', test_word)
            for word in words:
                combo = re.sub(r'\s', r'', word)
                if combo.lower() in spelling_dictionary:
                    replacements.append((word, combo))
                else:
                    pass
        else:
            pass

def check_for_repeating_characters(tokens, character):
    replacements = []
    pattern = "([" + character + "{2,}]{2,4})"

    for token in tokens:
        if len(token) > 12:
            if not re.findall(r'{}'.format(pattern), token):
                pass
            else:
                m_strings = re.findall(r'{}'.format(pattern), token)
                if len(m_strings) > 2:
                    replacements.append((token, ' '))
                else:
                    pass
        else:
            pass

    return replacements
    

def normalize_chars(content):
    """Use regex to normalizes dash and apostrophe characters.
    
    Args:
        content(str): File content as string
    Returns:
        str: file content with normalized characters as a string.
    """
    # Substitute for all other dashes
    content = re.sub(r"—-—–‑", r"-", content)

    # Substitute formatted apostrophe
    content = re.sub(r"\’\’\‘\'\‛\´", r"'", content)

    return content


def remove_special_chars(content):
    """Use regex to remove special characters except for punctuation.
    Note:
        Modify this function before use if content includes characters from languages other than English.
    Args:
        content(str): File content as string
    Returns:
        str: File content with special characters removed.

    """
    # Replace all special characters with a space (as these tend to occur at the end of lines)
    return re.sub(r"[^a-zA-Z0-9\s,.!?$:;\-&\'\"]", r" ", content)


def replace_apostrophe_error(content):
    """Use regex to 
    Note:
        Use this function before running :func:`remove_special_chars`.
    Args:
        content(str): File content as string
    Returns
        str: Files content with apostrophes correctly.
    """
    return re.sub(r"(\w+)(õ|Õ)", r"\1'", content)


def connect_line_endings(content):
    """Use regex to reconnect two word segments separated by "- ".

    Note:
        Use :func:`normalize_chars` before running `correct_line_endings`

    Args:
        content(str): File content.
    Returns:
        str: File content with words rejoined.
    """
    return re.sub(r"(\w+)(\-\s{1,})([a-z]+)", r"\1\3", content)


def rejoin_burst_words(content, spelling_dictionary):
    """Use regex to find likely split candidates and rejoin them

    Args: 
        content(str): File content
        spelling_dictionary(list): List of words to check formed words against
    Returns: 
        str: Content with splits rejoined.

    """
    pattern = re.compile("(\s(\w{1,2}\s){5,})")
    
    replacements = []
    check_splits(pattern, spelling_dictionary, content, replacements)
    
    if len(replacements) > 0:
        print("; ".join(replacements))
        for replacement in replacements:
            content = replace_pair(replacement, content)
    else:
        print("No replacement pairs found.")

    return content

def rejoin_split_words(content, spelling_dictionary, get_prior=False):
    """
    """
    tokens = GoH.utilities.tokenize_text(GoH.utilities.strip_punct(content))
    errors = GoH.describe.identify_errors(tokens, spelling_dictionary)

    replacements = check_if_stem(errors, spelling_dictionary, tokens, get_prior=False)
    
    if len(replacements) > 0:
        for replacement in replacements:
            print(replacement)
            content = replace_split_words(replacement, content)
    else:
        print("No replacement pairs found.")

    return content
def get_approved_tokens(content, spelling_dictionary, verified_tokens):
    text = GoH.utilities.strip_punct(content)
    tokens = GoH.utilities.tokenize_text(text)

    for token in tokens:
        if token.lower() in spelling_dictionary:
            verified_tokens.append(token)


def verify_split_string(list_split_string, spelling_dictionary):
    total_len = len(list_split_string)
    verified_splits = 0
    short_splits = 0
    
    for split in list_split_string:
        if split.lower() in spelling_dictionary:
            verified_splits = verified_splits + 1
            if len(split) < 3:
                short_splits = short_splits +1
        else:
            pass

    if verified_splits / total_len > .6:
        if short_splits / total_len < .5:
            return True
    else:
        return False


def infer_spaces(s, wordcost, maxword):
    """Uses dynamic programming to infer the location of spaces in a string
    without spaces."""

    # solution from http://stackoverflow.com/questions/8870261/how-to-split-text-without-spaces-into-list-of-words

    # Find the best match for the i first characters, assuming cost has
    # been built for the i-1 first characters.
    # Returns a pair (match_cost, match_length).
    def best_match(i):
        candidates = enumerate(reversed(cost[max(0, i-maxword):i]))
        return min((c + wordcost.get(s[i-k-1:i], 9e999), k+1) for k,c in candidates)

    # Build the cost array.
    cost = [0]
    for i in range(1,len(s)+1):
        c,k = best_match(i)
        cost.append(c)

    # Backtrack to recover the minimal-cost string.
    out = []
    i = len(s)
    while i>0:
        c,k = best_match(i)
        assert c == cost[i]
        out.append(s[i-k:i])
        i -= k

    return " ".join(reversed(out))


def check_probability(word, WORDS):
    N = sum(WORDS.values())
    return WORDS[word]/N


def check_for_substitutes(error, spelling_dictionary, WORDS):
    potential_subs = {}
    range = (len(error) - 2, len(error) + 2)
    for word in spelling_dictionary:
        if range[0] < len(word) < range[1]:
            distance = normalized_damerau_levenshtein_distance(error, word)
            if distance < .20:
                if check_probability(word, WORDS) > .000001:
                    potential_subs.update({word: check_probability(word, WORDS)})
                elif check_probability(word.title(), WORDS) > .000001:
                    potential_subs.update({word.title(): check_probability(word.title(), WORDS)})
                else:
                    pass
            else:
                pass
    return sorted(potential_subs.items(), key=operator.itemgetter(1), reverse=True)

# def interactive_check(error, subs):
#
#     print("Error = {}: Substitution = {}".format(error, word))
#     decision = input("Approve substitution? y/n: ")
#     if decision is 'y':
#         replacements.append((error, word))
#         return True
#     else:
#         pass


# def run_spell_check_program(errors, spelling_dictionary, c):
#     replacements = []
#     for error in errors:
#         if 2 < len(error) < 15:
#             print("Error under consideration: {}".format(error))
#             print(c.concordance(error))

#             # try to find substitution. Once substitution is chosen, move on.
#             found_sub = check_for_substitutes(error, spelling_dictionary, replacements)

#             # if unable to find substitution
#             if not found_sub is True:
#                 manual_entry = input("Provide manual response? (y/n) ")

#                 if manual_entry is 'y':
#                     replacement_word = input("Corrected word: ")
#                     replacements.append((error, replacement_word))
#                 else:
#                     pass
#     return replacements


# def auto_spell_check(errors, spelling_dictionary, WORDS):
#     replacements = []
#     for error in errors:
#         if 2 < len(error) < 15:
#             found_subs = check_for_substitutes(error, spelling_dictionary, WORDS)
#             if len(found_subs) > 0:
#                 replacements.append((error, found_subs[0][0]))
#     return replacements