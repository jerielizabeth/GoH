# -*- coding: utf-8 -*-

import GoH.clean
import GoH.utilities
import re

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
    GoH.clean.check_splits(pattern, spelling_dictionary, content, replacements)
    
    if len(replacements) > 0:
        print("; ".join(replacements))
        for replacement in replacements:
            content = GoH.clean.replace_pair(replacement, content)
    else:
        print("No replacement pairs found.")

    return content

def rejoin_split_words(content, spelling_dictionary, get_prior=False):
    """
    """
    tokens = GoH.utilities.tokenize_text(GoH.utilities.strip_punct(content))
    errors = GoH.reports.identify_errors(tokens, spelling_dictionary)

    replacements = GoH.clean.check_if_stem(errors, spelling_dictionary, tokens, get_prior=False)
    
    if len(replacements) > 0:
        for replacement in replacements:
            print(replacement)
            content = GoH.clean.replace_split_words(replacement, content)
    else:
        print("No replacement pairs found.")

    return content