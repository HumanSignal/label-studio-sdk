"""Penn Treebank word tokenizer used by the CONLL2003 export.

Vendored from NLTK 3.10.3 (``nltk.tokenize.treebank.TreebankWordTokenizer``,
``nltk.tokenize.destructive.MacIntyreContractions`` and
``nltk.tokenize.util.align_tokens``) so the SDK no longer depends on ``nltk``.

Copyright (C) 2001-2026 NLTK Project
Authors: Edward Loper, Michael Heilman, Tom Aarsen
Licensed under the Apache License, Version 2.0: https://www.apache.org/licenses/LICENSE-2.0

Changes from upstream:
- ``PUNCTUATION`` also splits off ``/`` (the override the converter used to apply to the NLTK class).
- Only ``tokenize`` and ``span_tokenize`` are kept; ``convert_parentheses`` and ``return_str`` are dropped.
"""

import re
from typing import Iterator, List, Tuple

# List of contractions adapted from Robert MacIntyre's tokenizer.
_CONTRACTIONS2 = [
    r"(?i)\b(can)(?#X)(not)\b",
    r"(?i)\b(d)(?#X)('ye)\b",
    r"(?i)\b(gim)(?#X)(me)\b",
    r"(?i)\b(gon)(?#X)(na)\b",
    r"(?i)\b(got)(?#X)(ta)\b",
    r"(?i)\b(lem)(?#X)(me)\b",
    r"(?i)\b(more)(?#X)('n)\b",
    r"(?i)\b(wan)(?#X)(na)(?=\s)",
]
_CONTRACTIONS3 = [r"(?i) ('t)(?#X)(is)\b", r"(?i) ('t)(?#X)(was)\b"]


def align_tokens(tokens: List[str], sentence: str) -> List[Tuple[int, int]]:
    """Return the ``(start, end)`` offsets of each token in ``sentence``."""
    point = 0
    offsets = []
    for token in tokens:
        try:
            start = sentence.index(token, point)
        except ValueError as e:
            raise ValueError(f'substring "{token}" not found in "{sentence}"') from e
        point = start + len(token)
        offsets.append((start, point))
    return offsets


class TreebankWordTokenizer:
    """Tokenize text with the regular expressions of the Penn Treebank tokenizer.

    - split standard contractions, e.g. ``don't`` -> ``do n't`` and ``they'll`` -> ``they 'll``
    - treat most punctuation characters as separate tokens
    - split off commas and single quotes, when followed by whitespace
    - separate periods that appear at the end of line
    """

    STARTING_QUOTES = [
        (re.compile(r"^\""), r"``"),
        (re.compile(r"(``)"), r" \1 "),
        (re.compile(r"([ \(\[{<])(\"|\'{2})"), r"\1 `` "),
    ]

    PUNCTUATION = [
        (re.compile(r"([:,])([^\d])"), r" \1 \2"),
        (re.compile(r"([:,])$"), r" \1 "),
        (re.compile(r"\.\.\."), r" ... "),
        (re.compile(r"[;@#$/%&]"), r" \g<0> "),
        (
            re.compile(r'([^\.])(\.)([\]\)}>"\']*)\s*$'),
            r"\1 \2\3 ",
        ),  # Handles the final period.
        (re.compile(r"[?!]"), r" \g<0> "),
        (re.compile(r"([^'])' "), r"\1 ' "),
    ]

    PARENS_BRACKETS = (re.compile(r"[\]\[\(\)\{\}\<\>]"), r" \g<0> ")

    DOUBLE_DASHES = (re.compile(r"--"), r" -- ")

    ENDING_QUOTES = [
        (re.compile(r"''"), " '' "),
        (re.compile(r'"'), " '' "),
        (re.compile(r"([^' ])('[sS]|'[mM]|'[dD]|') "), r"\1 \2 "),
        (re.compile(r"([^' ])('ll|'LL|'re|'RE|'ve|'VE|n't|N'T) "), r"\1 \2 "),
    ]

    CONTRACTIONS2 = list(map(re.compile, _CONTRACTIONS2))
    CONTRACTIONS3 = list(map(re.compile, _CONTRACTIONS3))

    def tokenize(self, text: str) -> List[str]:
        """Return the list of tokens in ``text``."""
        for regexp, substitution in self.STARTING_QUOTES:
            text = regexp.sub(substitution, text)

        for regexp, substitution in self.PUNCTUATION:
            text = regexp.sub(substitution, text)

        regexp, substitution = self.PARENS_BRACKETS
        text = regexp.sub(substitution, text)

        regexp, substitution = self.DOUBLE_DASHES
        text = regexp.sub(substitution, text)

        # add extra space to make things easier
        text = " " + text + " "

        for regexp, substitution in self.ENDING_QUOTES:
            text = regexp.sub(substitution, text)

        for regexp in self.CONTRACTIONS2:
            text = regexp.sub(r" \1 \2 ", text)
        for regexp in self.CONTRACTIONS3:
            text = regexp.sub(r" \1 \2 ", text)

        return text.split()

    def span_tokenize(self, text: str) -> Iterator[Tuple[int, int]]:
        """Yield the ``(start, end)`` offsets of the tokens in ``text``."""
        raw_tokens = self.tokenize(text)

        # Convert converted quotes back to original double quotes
        # Do this only if original text contains double quote(s) or double
        # single-quotes (because '' might be transformed to `` if it is
        # treated as starting quotes).
        if ('"' in text) or ("''" in text):
            matched = [m.group() for m in re.finditer(r"``|'{2}|\"", text)]
            tokens = [matched.pop(0) if tok in ['"', "``", "''"] else tok for tok in raw_tokens]
        else:
            tokens = raw_tokens

        yield from align_tokens(tokens, text)
