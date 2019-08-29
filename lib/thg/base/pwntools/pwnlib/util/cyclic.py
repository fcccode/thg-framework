from __future__ import absolute_import
from __future__ import division

import six
import string

from pwnlib.context import context, LocalContext
from pwnlib.log import getLogger
from pwnlib.util import packing

log = getLogger(__name__)

# Taken from https://en.wikipedia.org/wiki/De_Bruijn_sequence but changed to a generator
def de_bruijn(alphabet = None, n = None):
    """de_bruijn(alphabet = None, n = None) -> generator

    Generator for a sequence of unique substrings of length `n`. This is implemented using a
    De Bruijn Sequence over the given `alphabet`.

    The returned generator will yield up to ``len(alphabet)**n`` elements.

    Arguments:
        alphabet: List or string to generate the sequence over.
        n(int): The length of subsequences that should be unique.
    """
    if alphabet is None:
        alphabet = context.cyclic_alphabet
    if n is None:
        n = context.cyclic_size
    if isinstance(alphabet, bytes):
        alphabet = bytearray(alphabet)
    k = len(alphabet)
    a = [0] * k * n
    def db(t, p):
        if t > n:
            if n % p == 0:
                for j in range(1, p + 1):
                    yield alphabet[a[j]]
        else:
            a[t] = a[t - p]
            for c in db(t + 1, p):
                yield c

            for j in range(a[t - p] + 1, k):
                a[t] = j
                for c in db(t + 1, t):
                    yield c

    return db(1,1)

def cyclic(length = None, alphabet = None, n = None):
    """cyclic(length = None, alphabet = None, n = None) -> list/str

    A simple wrapper over :func:`de_bruijn`. This function returns at most
    `length` elements.

    If the given alphabet is a string, a string is returned from this function. Otherwise
    a list is returned.

    Arguments:
        length: The desired length of the list or None if the entire sequence is desired.
        alphabet: List or string to generate the sequence over.
        n(int): The length of subsequences that should be unique.

    Notes:
        The maximum length is `len(alphabet)**n`.

        The default values for `alphabet` and `n` restrict the total space to ~446KB.

        If you need to generate a longer cyclic pattern, provide a longer `alphabet`,
        or if possible a larger `n`.

    Example:

        Cyclic patterns are usually generated by providing a specific `length`.

        >>> cyclic(20)
        b'aaaabaaacaaadaaaeaaa'

        >>> cyclic(32)
        b'aaaabaaacaaadaaaeaaafaaagaaahaaa'

        The `alphabet` and `n` arguments will control the actual output of the pattern

        >>> cyclic(20, alphabet=string.ascii_uppercase)
        'AAAABAAACAAADAAAEAAA'

        >>> cyclic(20, n=8)
        b'aaaaaaaabaaaaaaacaaa'

        >>> cyclic(20, n=2)
        b'aabacadaeafagahaiaja'

        The size of `n` and `alphabet` limit the maximum length that can be generated.
        Without providing `length`, the entire possible cyclic space is generated.

        >>> cyclic(alphabet = "ABC", n = 3)
        'AAABAACABBABCACBACCBBBCBCCC'

        >>> cyclic(length=512, alphabet = "ABC", n = 3)
        Traceback (most recent call last):
        ...
        PwnlibException: Can't create a pattern length=512 with len(alphabet)==3 and n==3

        The `alphabet` can be set in `context`, which is useful for circumstances
        when certain characters are not allowed.  See :obj:`.context.cyclic_alphabet`.

        >>> context.cyclic_alphabet = "ABC"
        >>> cyclic(10)
        b'AAAABAAACA'

        The original values can always be restored with:

        >>> context.clear()

        The following just a test to make sure the length is correct.

        >>> alphabet, n = range(30), 3
        >>> len(alphabet)**n, len(cyclic(alphabet = alphabet, n = n))
        (27000, 27000)
    """
    if n is None:
        n = context.cyclic_size

    if alphabet is None:
        alphabet = context.cyclic_alphabet

    if length != None and len(alphabet) ** n < length:
        log.error("Can't create a pattern length=%i with len(alphabet)==%i and n==%i" \
                  % (length, len(alphabet), n))

    out = []
    for ndx, c in enumerate(de_bruijn(alphabet, n)):
        if length != None and ndx >= length:
            break
        else:
            out.append(c)

    if isinstance(alphabet, six.text_type):
        return ''.join(out)
    elif isinstance(alphabet, bytes):
        return bytes(bytearray(out))
    else:
        return out

@LocalContext
def cyclic_find(subseq, alphabet = None, n = None):
    """cyclic_find(subseq, alphabet = None, n = None) -> int

    Calculates the position of a substring into a De Bruijn sequence.

    .. todo:

       "Calculates" is an overstatement. It simply traverses the list.

       There exists better algorithms for this, but they depend on generating
       the De Bruijn sequence in another fashion. Somebody should look at it:

       https://www.sciencedirect.com/science/article/pii/S0012365X00001175

    Arguments:
        subseq: The subsequence to look for. This can be a string, a list or an
                integer. If an integer is provided it will be packed as a
                little endian integer.
        alphabet: List or string to generate the sequence over.
                  By default, uses :obj:`.context.cyclic_alphabet`.
        n(int): The length of subsequences that should be unique.
                By default, uses :obj:`.context.cyclic_size`.

    Examples:

        Let's generate an example cyclic pattern.

        >>> cyclic(16)
        b'aaaabaaacaaadaaa'

        Note that 'baaa' starts at offset 4.  The `cyclic_find` routine shows us this:

        >>> cyclic_find(b'baaa')
        4

        The *default* length of a subsequence generated by `cyclic` is `4`.
        If a longer value is submitted, it is automatically truncated to four bytes.

        >>> cyclic_find(b'baaacaaa')
        4

        If you provided e.g. `n=8` to `cyclic` to generate larger subsequences,
        you must explicitly provide that argument.

        >>> cyclic_find(b'baaacaaa', n=8)
        3515208

        We can generate a large cyclic pattern, and grab a subset of it to
        check a deeper offset.

        >>> cyclic_find(cyclic(1000)[514:518])
        514

        Instead of passing in the byte representation of the pattern, you can
        also pass in the integer value.  Note that this is sensitive to the
        selected endianness via `context.endian`.

        >>> cyclic_find(0x61616162)
        4
        >>> cyclic_find(0x61616162, endian='big')
        1

        You can use anything for the cyclic pattern, including non-printable
        characters.

        >>> cyclic_find(0x00000000, alphabet=unhex('DEADBEEF00'))
        621
    """

    if n is None:
        n = context.cyclic_size

    if isinstance(subseq, six.integer_types):
        subseq = packing.pack(subseq, bytes=n)

    if len(subseq) != n:
        log.warn_once("cyclic_find() expects %i-byte subsequences by default, you gave %r\n"\
            + "Unless you specified cyclic(..., n=%i), you probably just want the first 4 bytes.\n"\
            + "Truncating the data at 4 bytes.  Specify cyclic_find(..., n=%i) to override this.",
            n, subseq, len(subseq), len(subseq))
        subseq = subseq[:n]

    if alphabet is None:
        alphabet = context.cyclic_alphabet

    if any(c not in alphabet for c in subseq):
        return -1

    n = n or len(subseq)

    return _gen_find(subseq, de_bruijn(alphabet, n))

def metasploit_pattern(sets = None):
    """metasploit_pattern(sets = [ string.ascii_uppercase, string.ascii_lowercase, string.digits ]) -> generator

    Generator for a sequence of characters as per Metasploit Framework's
    `Rex::Text.pattern_create` (aka `pattern_create.rb`).

    The returned generator will yield up to
    ``len(sets) * reduce(lambda x,y: x*y, map(len, sets))`` elements.

    Arguments:
        sets: List of strings to generate the sequence over.
    """
    sets = sets or [ string.ascii_uppercase, string.ascii_lowercase, string.digits ]
    offsets = [ 0 ] * len(sets)
    offsets_indexes_reversed = list(reversed(range(len(offsets))))

    while True:
        for i, j in zip(sets, offsets):
            if isinstance(i, bytes):
                i = bytearray(i)
            yield i[j]
        # increment offsets with cascade
        for i in offsets_indexes_reversed:
            offsets[i] = (offsets[i] + 1) % len(sets[i])
            if offsets[i] != 0:
                break
        # finish up if we've exhausted the sequence
        if offsets == [ 0 ] * len(sets):
            return

def cyclic_metasploit(length = None, sets = None):
    """cyclic_metasploit(length = None, sets = [ string.ascii_uppercase, string.ascii_lowercase, string.digits ]) -> str

    A simple wrapper over :func:`metasploit_pattern`. This function returns a
    string of length `length`.

    Arguments:
        length: The desired length of the string or None if the entire sequence is desired.
        sets: List of strings to generate the sequence over.

    Example:
        >>> cyclic_metasploit(32)
        b'Aa0Aa1Aa2Aa3Aa4Aa5Aa6Aa7Aa8Aa9Ab'
        >>> cyclic_metasploit(sets = [b"AB",b"ab",b"12"])
        b'Aa1Aa2Ab1Ab2Ba1Ba2Bb1Bb2'
        >>> cyclic_metasploit()[1337:1341]
        b'5Bs6'
        >>> len(cyclic_metasploit())
        20280
    """
    sets = sets or [ string.ascii_uppercase.encode(), string.ascii_lowercase.encode(), string.digits.encode() ]
    out = bytearray()

    for ndx, c in enumerate(metasploit_pattern(sets)):
        if length != None and ndx >= length:
            break
        else:
            out.append(c)

    out = bytes(out)

    if length != None and len(out) < length:
        log.error("Can't create a pattern of length %i with sets of lengths %s. Maximum pattern length is %i." \
                  % (length, list(map(len, sets)), len(out)))

    return out

def cyclic_metasploit_find(subseq, sets = None):
    """cyclic_metasploit_find(subseq, sets = [ string.ascii_uppercase, string.ascii_lowercase, string.digits ]) -> int

    Calculates the position of a substring into a Metasploit Pattern sequence.

    Arguments:
        subseq: The subsequence to look for. This can be a string or an
                integer. If an integer is provided it will be packed as a
                little endian integer.
        sets: List of strings to generate the sequence over.

    Examples:

        >>> cyclic_metasploit_find(cyclic_metasploit(1000)[514:518])
        514
        >>> cyclic_metasploit_find(0x61413161)
        4
    """
    sets = sets or [ string.ascii_uppercase.encode(), string.ascii_lowercase.encode(), string.digits.encode() ]

    if isinstance(subseq, six.integer_types):
        subseq = packing.pack(subseq, 'all', 'little', False)

    return _gen_find(subseq, metasploit_pattern(sets))

def _gen_find(subseq, generator):
    """Returns the first position of `subseq` in the generator or -1 if there is no such position."""
    if isinstance(subseq, bytes):
        subseq = bytearray(subseq)
    subseq = list(subseq)
    pos = 0
    saved = []

    for c in generator:
        saved.append(c)
        if len(saved) > len(subseq):
            saved.pop(0)
            pos += 1
        if saved == subseq:
            return pos
    return -1
