# -*- coding: utf-8 -*-

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
