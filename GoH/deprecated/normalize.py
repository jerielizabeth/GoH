# -*- coding: utf-8 -*-

import GoH.utilities
import operator
from pyxdameraulevenshtein import normalized_damerau_levenshtein_distance


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


def run_spell_check_program(errors, spelling_dictionary, c):
    replacements = []
    for error in errors:
        if 2 < len(error) < 15:
            print("Error under consideration: {}".format(error))
            print(c.concordance(error))

            # try to find substitution. Once substitution is chosen, move on.
            found_sub = check_for_substitutes(error, spelling_dictionary, replacements)

            # if unable to find substitution
            if not found_sub is True:
                manual_entry = input("Provide manual response? (y/n) ")

                if manual_entry is 'y':
                    replacement_word = input("Corrected word: ")
                    replacements.append((error, replacement_word))
                else:
                    pass
    return replacements


def auto_spell_check(errors, spelling_dictionary, WORDS):
    replacements = []
    for error in errors:
        if 2 < len(error) < 15:
            found_subs = check_for_substitutes(error, spelling_dictionary, WORDS)
            if len(found_subs) > 0:
                replacements.append((error, found_subs[0][0]))
    return replacements
