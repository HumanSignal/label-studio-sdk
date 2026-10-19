import pytest

from label_studio_sdk.converter.treebank import TreebankWordTokenizer

# Expected spans were produced by nltk 3.10.3 TreebankWordTokenizer with the converter's
# PUNCTUATION override, so the vendored copy must keep CONLL2003 exports byte-for-byte identical.
CASES = [
    (
        'Good muffins cost $3.88\nin New (York).  Please (buy) me\ntwo of them.\n(Thanks).',
        [(0, 4), (5, 12), (13, 17), (18, 19), (19, 23), (24, 26), (27, 30), (31, 32), (32, 36), (36, 37), (37, 38),
         (40, 46), (47, 48), (48, 51), (51, 52), (53, 55), (56, 59), (60, 62), (63, 68), (69, 70), (70, 76), (76, 77),
         (77, 78)],
    ),
    (
        "They'll save and invest more, but I can't.",
        [(0, 4), (4, 7), (8, 12), (13, 16), (17, 23), (24, 28), (28, 29), (30, 33), (34, 35), (36, 38), (38, 41),
         (41, 42)],
    ),
    (
        "Gimme the cannot gonna 'tis",
        [(0, 3), (3, 5), (6, 9), (10, 13), (13, 16), (17, 20), (20, 22), (23, 25), (25, 27)],
    ),
    (
        '"Hello," she said, "it\'s ``fine\'\'."',
        [(0, 1), (1, 6), (6, 7), (7, 8), (9, 12), (13, 17), (17, 18), (19, 20), (20, 22), (22, 24), (25, 27),
         (27, 31), (31, 33), (33, 34), (34, 35)],
    ),
    (
        'a/b c&d #tag @user 50% 3:30 1,234 -- e.g. ...',
        [(0, 1), (1, 2), (2, 3), (4, 5), (5, 6), (6, 7), (8, 9), (9, 12), (13, 14), (14, 18), (19, 21), (21, 22),
         (23, 27), (28, 33), (34, 36), (37, 41), (42, 45)],
    ),
    (
        'Привет, мир! “smart” quotes',
        [(0, 6), (6, 7), (8, 11), (11, 12), (13, 20), (21, 27)],
    ),
]


@pytest.mark.parametrize("text, expected", CASES)
def test_span_tokenize_matches_nltk(text, expected):
    assert list(TreebankWordTokenizer().span_tokenize(text)) == expected


@pytest.mark.parametrize("text, expected", CASES)
def test_tokenize_matches_spans(text, expected):
    tokens = TreebankWordTokenizer().tokenize(text)
    if '"' not in text and "''" not in text:
        assert tokens == [text[start:end] for start, end in expected]
    else:
        assert len(tokens) == len(expected)
