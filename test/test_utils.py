import itertools
import random
import sys
import unittest

from segments import segments
from segments import utils
from six.moves import range
from functools import reduce
from six.moves import StringIO

import verifyutils
verifyutils.segments = segments


#
#  How many times to repeat the algebraic tests
#


algebra_repeats = 8000
algebra_listlength = 200


#
# Define the components of the test suite.
#


class TestSegwizard(object):
    def test_fromsegwizard(self):
        """
        Test segwizard parsing.
        """
        data = StringIO("""# This is a comment
 # This is another comment
    # Again a comment
1  10 100 90
2 110 120 10# Here's a comment
3 125 130 5 # Another one

4   0 200 200""")
        assert utils.fromsegwizard(data, strict=True) == (
            segments.segmentlist([segments.segment(10, 100),
                                  segments.segment(110, 120),
                                  segments.segment(125, 130),
                                  segments.segment(0, 200)]))

    def test_tofromseqwizard(self):
        """
        Check that the segwizard writing routine's output is parsed
        correctly.
        """
        correct = segments.segmentlist([
            segments.segment(10, 100),
            segments.segment(110, 120),
            segments.segment(125, 130),
            segments.segment(0, 200),
        ])
        data = StringIO()
        utils.tosegwizard(data, correct)
        data.seek(0)
        assert utils.fromsegwizard(data, strict=True) == correct


class TestVote(object):
    def test_vote(self):
        """
        Test vote().
        """
        for i in range(algebra_repeats):
            seglists = []
            for j in range(random.randint(0, 10)):
                seglists.append(verifyutils.random_coalesced_list(
                    algebra_listlength))
            n = random.randint(0, len(seglists))
            assert utils.vote(seglists, n) == reduce(
                lambda x, y: x | y, (
                    votes and reduce(lambda a, b: a & b, votes) or
                    segments.segmentlist() for votes in
                    itertools.combinations(seglists, n)),
                segments.segmentlist())
