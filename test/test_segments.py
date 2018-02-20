import doctest
import math
import pickle
import random
import sys
import unittest
import importlib
from six.moves import map
from six.moves import range

import pytest

import segments

import verifyutils

#
#  How many times to repeat the algebraic tests
#


algebra_repeats = 8000
algebra_listlength = 200


#
# Some useful code.
#


@pytest.fixture(scope='function', autouse=True,
                params=['segments.segments', 'segments.__segments'])
def segments_implementation(request):
    # override the segments module with the relevant implementation
    mod = importlib.import_module(request.param)
    segments.segment = mod.segment
    segments.segmentlist = mod.segmentlist
    segments.infinity = mod.infinity
    segments.PosInfinity = mod.PosInfinity
    segments.NegInfinity = mod.NegInfinity
    verifyutils.segments = mod


def set1():
    return (
        segments.segment(-2, 2),
        segments.segment(-2, 2),
        segments.segment(-2, 2),
        segments.segment(-2, 2),
        segments.segment(-2, 2),
        segments.segment(-2, 2),
        segments.segment(-2, 2),
        segments.segment(-2, 2),
        segments.segment(-2, 2),
        segments.segment(-2, 2),
        segments.segment(-2, 2),
        segments.segment(-2, 2),
        segments.segment(-2, 2),
        segments.segment(-2, 2)
    )


def set2():
    return (
        segments.segment(-4, -3),
        segments.segment(-4, -2),
        segments.segment(-4,  0),
        segments.segment(-4,  2),
        segments.segment(-4,  4),
        segments.segment(-2,  4),
        segments.segment( 0,  4),
        segments.segment( 2,  4),
        segments.segment( 3,  4),
        segments.segment(-2,  2),
        segments.segment(-1,  1),
        segments.segment(-segments.infinity(), segments.infinity()),
        segments.segment(0, segments.infinity()),
        segments.segment(-segments.infinity(), 0)
    )


#
# Define the components of the test suite.
#


class test_infinity():
    @pytest.mark.skipif(sys.version_info.major >= 3,
                        'Python 3 does not have cmp')
    def test_cmp(self):
        a = segments.infinity()
        assert 0 == cmp(-a, -a)
        assert -1 == cmp(-a,  0)
        assert -1 == cmp(-a,  a)
        assert  1 == cmp( 0, -a)
        assert -1 == cmp( 0,  a)
        assert  1 == cmp( a, -a)
        assert  1 == cmp( a,  0)
        assert  0 == cmp( a,  a)

    def test_add(self):
        a = segments.infinity()
        b = segments.infinity()
        assert  b == (  a) + ( 10)
        assert  b == (  a) + (-10)
        assert -b == ( -a) + ( 10)
        assert -b == ( -a) + (-10)
        assert  b == ( 10) + (  a)
        assert  b == (-10) + (  a)
        assert -b == ( 10) + ( -a)
        assert -b == (-10) + ( -a)
        assert  b == (  a) + (  a)
        assert -b == ( -a) + ( -a)

    def test_sub(self):
        a = segments.infinity()
        b = segments.infinity()
        assert  b == (  a) - ( 10)
        assert  b == (  a) - (-10)
        assert -b == ( -a) - ( 10)
        assert -b == ( -a) - (-10)
        assert -b == ( 10) - (  a)
        assert -b == (-10) - (  a)
        assert  b == ( 10) - ( -a)
        assert  b == (-10) - ( -a)
        assert  b == (  a) - (  a)
        assert -b == ( -a) - ( -a)
        assert  b == (  a) - ( -a)
        assert -b == ( -a) - (  a)

    def test_float(self):
        a = segments.infinity()
        b = -segments.infinity()
        assert math.isinf(a)
        assert math.isinf(b)


class TestSegment(object):
    def test_new(self):
        assert (-2, 2) == tuple(segments.segment(-2, 2))
        assert (-2, 2) == tuple(segments.segment(2, -2))
        assert (-segments.infinity(), 2) == tuple(segments.segment(-segments.infinity(), 2))
        assert (-segments.infinity(), 2) == tuple(segments.segment(2, -segments.infinity()))
        assert (2, segments.infinity()) == tuple(segments.segment(segments.infinity(), 2))
        assert (2, segments.infinity()) == tuple(segments.segment(2, segments.infinity()))
        assert (-segments.infinity(), segments.infinity()) == tuple(segments.segment(-segments.infinity(), segments.infinity()))

    @pytest.mark.parametrize('a, result', zip(set2(), [
        1,
        2,
        4,
        6,
        8,
        6,
        4,
        2,
        1,
        4,
        2,
        segments.infinity(),
        segments.infinity(),
        segments.infinity()
    ]))
    def test_abs(self, a, result):
        assert abs(a) == result


    @pytest.mark.parametrize('a, b, result', zip(set1(), set2(), [
        False,
        False,
        True,
        True,
        True,
        True,
        True,
        False,
        False,
        True,
        True,
        True,
        True,
        True
    ]))
    def test_intersects(self, a, b, result):
        assert a.intersects(b) == result

    @pytest.mark.parametrize('a, b, result', zip(set1(), set2(), [
        False,
        False,
        False,
        False,
        False,
        False,
        False,
        False,
        False,
        True,
        True,
        False,
        False,
        False
    ]))
    def test_contains_1(self, a, b, result):
        assert (b in a) == result

    def test_contains_2(self):
        assert [1, 2] in segments.segment(0, 4)
        assert [1, 6] not in segments.segment(0, 4)
        assert [-1, 2] not in segments.segment(0, 4)
        assert [-1, 6] not in segments.segment(0, 4)
        assert 2 in segments.segment(0, 4)

        # Paraphrasing the documentation for glue.segment.__contains__
        # in segments/segments.py: if a is a segment or a sequence of length two,
        # then `a in b` tests if `b[0] <= a[0] <= a[1] <= b[1]`. Otherwise,
        # `a in b` tests if `b[0] <= a <= b[1]`. The following four tests
        # happen to work and return False in Python 2, but they raise
        # a TypeError in Python 3 because Python does not permit comparisons
        # of numbers with sequences. The exception message is
        # "'<' not supported between instances of 'list' and 'int'".
        if sys.version_info.major <= 2:
            assert [] not in segments.segment(0, 4)
            assert [0] not in segments.segment(0, 4)
            assert [2] not in segments.segment(0, 4)
            assert [1, 2, 3] not in segments.segment(0, 4)
        else:
            with pytest.raises(TypeError):
                assert [] not in segments.segment(0, 4)
            with pytest.raises(TypeError):
                assert [0] not in segments.segment(0, 4)
            with pytest.raises(TypeError):
                assert [2] not in segments.segment(0, 4)
            with pytest.raises(TypeError):
                assert [1, 2, 3] not in segments.segment(0, 4)

    @pytest.mark.parametrize('a, b, result', zip(set1(), set2(), [
        +1,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        -1,
        0,
        0,
        0,
        0,
        0,
    ]))
    def test_disjoint(self, a, b, result):
        assert a.disjoint(b) == result

    @pytest.mark.parametrize('a, result', zip(set2(), [
        segments.segment(-5, -2),
        segments.segment(-4, -2),
        segments.segment(-2, -2),
        segments.segment(-2,  0),
        segments.segment(-2,  2),
        segments.segment( 0,  2),
        segments.segment( 2,  2),
        segments.segment( 2,  4),
        segments.segment( 2,  5),
        segments.segment( 0,  0),
        segments.segment(-1,  1),
        segments.segment(-segments.infinity(), segments.infinity()),
        segments.segment(2, segments.infinity()),
        segments.segment(-segments.infinity(), -2),
    ]))
    def test_contract(self, a, result):
        assert a.contract(2) == result

    def test_typesafety(self):
        x = "segments.segment(10, 20)"
        y = "(20, 30)"
        z = "None"

        for op in ("|", "&", "-", "^"):
            for arg1, arg2 in (
                (x, z), (z, x)
            ):
                expr = "%s %s %s" % (arg1, op, arg2)
                try:
                    eval(expr)
                except TypeError:
                    pass
                else:
                    raise AssertionError("%s did not raise TypeError" % expr)
        # FIXME:  this doesn't work, should it?
        # assert eval("%s | %s" % (x, y)) == segments.segmentlist([segments.segment(10, 30)])


class TestSegmentlist(object):

    @pytest.mark.parametrize('a, b', [
        (segments.segmentlist([]),
         segments.segmentlist([]) - segments.segmentlist([])),
        (segments.segmentlist([]),
         segments.segmentlist([]) -
             segments.segmentlist([segments.segment(-1, 1)])),
        (segments.segmentlist([segments.segment(-1,1)]) -
             segments.segmentlist([segments.segment(-1,1)]),
         segments.segmentlist([])),
        (segments.segmentlist([]),
         segments.segmentlist([segments.segment(-1,1)]) -
             segments.segmentlist([segments.segment(-1,1)])),
        #(segments.segmentlist([]),
        # segments.segmentlist([segments.segment(0,0)]) -
        #     segments.segmentlist([segments.segment(0,0)])),
        (segments.segmentlist([segments.segment(0,1)]),
         segments.segmentlist([segments.segment(0,1)]) -
             segments.segmentlist([segments.segment(2,3)])),
        (segments.segmentlist([segments.segment(0,1)]),
         segments.segmentlist([segments.segment(0,1)]) -
             segments.segmentlist([segments.segment(2,3),
                                   segments.segment(4,5)])),
        (segments.segmentlist([segments.segment(0,1)]),
         segments.segmentlist([segments.segment(0,1), segments.segment(2,3)]) -
             segments.segmentlist([segments.segment(2,3)])),
        (segments.segmentlist([segments.segment(2,3)]),
         segments.segmentlist([segments.segment(0,1), segments.segment(2,3)]) -
             segments.segmentlist([segments.segment(0,1)])),
        (segments.segmentlist([segments.segment(0,1), segments.segment(4,5)]),
         segments.segmentlist([segments.segment(0,1), segments.segment(2,3),
                               segments.segment(4,5)]) -
             segments.segmentlist([segments.segment(2,3)])),
        (segments.segmentlist([segments.segment(0,1)]),
         segments.segmentlist([segments.segment(0,2)]) -
             segments.segmentlist([segments.segment(1,2)])),
        (segments.segmentlist([segments.segment(0.8, 0.9),
                               segments.segment(1.0, 1.8)]),
         segments.segmentlist([segments.segment(0, 2)]) -
             segments.segmentlist([segments.segment(0, 0.8),
                                   segments.segment(0.9, 1.0),
                                   segments.segment(1.8, 2)])),
        (segments.segmentlist([segments.segment(-5, 10)]),
         segments.segmentlist([segments.segment(-10,10)]) -
             segments.segmentlist([segments.segment(-15,-5)])),
        (segments.segmentlist([segments.segment(-10, -5),
                               segments.segment(5, 10)]),
         segments.segmentlist([segments.segment(-10,10)]) -
             segments.segmentlist([segments.segment(-5,5)])),
        (segments.segmentlist([segments.segment(-10, 5)]),
         segments.segmentlist([segments.segment(-10,10)]) -
             segments.segmentlist([segments.segment(5,15)])),
        (segments.segmentlist([segments.segment(0,5),
                               segments.segment(45,50)]),
         segments.segmentlist([segments.segment(0,10), segments.segment(20,30),
                               segments.segment(40,50)]) -
             segments.segmentlist([segments.segment(5, 45)])),
    ])
    def test_sub(self, a, b):
        assert a == b

    @pytest.mark.parametrize('a, b', [
        (segments.segmentlist([segments.segment(-segments.infinity(),
                                                segments.infinity())]),
         segments.segmentlist([])),
        (segments.segmentlist([]),
         segments.segmentlist([segments.segment(-segments.infinity(),
                                                segments.infinity())])),
        (segments.segmentlist([segments.segment(-segments.infinity(), -5),
                               segments.segment(5, segments.infinity())]),
         segments.segmentlist([segments.segment(-5,5)])),
    ])
    def test_invert(self, a, b):
        assert a == ~b

    def test_and(self):
        for i in range(algebra_repeats):
            a = verifyutils.random_coalesced_list(
                random.randint(1, algebra_listlength))
            b = verifyutils.random_coalesced_list(
                random.randint(1, algebra_listlength))
            c = a & b
            assert c == a - (a - b)
            assert c == b - (b - a)

    def test_or(self):
        for i in range(algebra_repeats):
            a = verifyutils.random_coalesced_list(
                random.randint(1, algebra_listlength))
            b = verifyutils.random_coalesced_list(
                random.randint(1, algebra_listlength))
            c = a | b

            # make sure c is coalesced
            assert verifyutils.iscoalesced(c)
            # make sure c contains all of a
            assert a == c & a
            # make sure c contains all of b
            assert b == c & b
            # make sure c contains nothing except a and b
            assert segments.segmentlist([]) == c - a - b

    def test_xor(self):
        for i in range(algebra_repeats):
            a = verifyutils.random_coalesced_list(
                random.randint(1, algebra_listlength))
            b = verifyutils.random_coalesced_list(
                random.randint(1, algebra_listlength))
            c = a ^ b

            # c contains nothing that can be found in
            # the intersection of a and b
            assert not c.intersects(a & b)
            # c contains nothing that cannot be found
            # in either a or b
            assert segments.segmentlist([]) == c - a - b
            # that c + the intersection of a and b
            # leaves no part of either a or b
            # unconvered
            assert segments.segmentlist([]) == a - (c | a & b)
            assert segments.segmentlist([]) == b - (c | a & b)

    def test_protract(self):
        assert segments.segmentlist([segments.segment(0, 20)]) == (
            segments.segmentlist([segments.segment(3, 7),
                                  segments.segment(13, 17)]).protract(3))

        # confirm that .protract() preserves the type of the
        # segment objects
        class MyCustomSegment(segments.segment):
            pass
        class MyCustomSegmentList(segments.segmentlist):
            def coalesce(self):
                # must override for test, but don't have to
                # implement because test case is too simple
                return self
        assert type(MyCustomSegmentList(
            [MyCustomSegment(0, 10)]).protract(1)[0]) is MyCustomSegment

    def test_contract(self):
        assert segments.segmentlist([segments.segment(0, 20)]) == (
            segments.segmentlist([segments.segment(3, 7),
                                  segments.segment(13, 17)]).contract(-3))

        # confirm that .contract() preserves the type of the
        # segment objects
        class MyCustomSegment(segments.segment):
            pass
        class MyCustomSegmentList(segments.segmentlist):
            def coalesce(self):
                # must override for test, but don't have to
                # implement because test case is too simple
                return self
        assert type(MyCustomSegmentList([
            MyCustomSegment(0, 10)]).contract(1)[0] ) is MyCustomSegment

    def test_intersects(self):
        for i in range(algebra_repeats):
            a = verifyutils.random_coalesced_list(
                random.randint(1, algebra_listlength))
            b = verifyutils.random_coalesced_list(
                random.randint(1, algebra_listlength))
            c = a - b
            d = a & b

            if len(c):
                assert not c.intersects(b)
            if len(d):
                assert d.intersects(a)
                assert d.intersects(b)
                assert a.intersects(b)

    def test_extent(self):
        assert segments.segmentlist([(1, 0)]).extent() == (
            segments.segment(0, 1))

    def test_coalesce(self):
        # check that mixed-type coalescing works
        x = segments.segmentlist([segments.segment(1, 2), segments.segment(3, 4), (2, 3)])
        try:
            assert x.coalesce() == segments.segmentlist(
                [segments.segment(1, 4)])
        except AssertionError as e:
            raise AssertionError("mixed type coalesce failed:  got %s" % str(x))

        # try a bunch of random segment lists
        for i in range(algebra_repeats):
            a = verifyutils.random_uncoalesced_list(
                random.randint(1, algebra_listlength))
            b = segments.segmentlist(a[:]).coalesce()
            assert verifyutils.iscoalesced(b)
            for seg in a:
                assert seg in b
            for seg in a:
                b -= segments.segmentlist([seg])
            assert b == segments.segmentlist([])

    def test_typesafety(self):
        w = "segments.segmentlist([segments.segment(0, 10), segments.segment(20, 30)])"
        x = "segments.segment(10, 20)"
        y = "[(10, 20)]"
        z = "None"

        for op in ("|", "&", "-", "^"):
            for arg1, arg2 in (
                (w, x), (x, w),
                (w, z), (z, w)
            ):
                expr = "%s %s %s" % (arg1, op, arg2)
                try:
                    eval(expr)
                except TypeError:
                    pass
                else:
                    raise AssertionError("%s did not raise TypeError" % expr)
        assert eval("%s | %s" % (w, y)) == segments.segmentlist(
            [segments.segment(0, 30)])


class TestSegmentlistdict(object):
    def test_extent_all(self):
        a = segments.segmentlistdict({
            "H1": segments.segmentlist(),
            "L1": segments.segmentlist([segments.segment(25, 35)])})
        assert a.extent_all() == segments.segment(25, 35)

    def test_intersects(self):
        a = segments.segmentlistdict({
            "H1": segments.segmentlist([segments.segment(0, 10),
                                        segments.segment(20, 30)])})
        b = segments.segmentlistdict({
            "H1": segments.segmentlist([segments.segment(5, 15)]),
            "L1": segments.segmentlist([segments.segment(25, 35)])})
        c = segments.segmentlistdict({
            "V1": segments.segmentlist([segments.segment(7, 13),
                                        segments.segment(27, 40)])})

        assert a.intersects(b)
        assert b.intersects(a)
        assert a.intersects(a)
        assert not a.intersects(c)
        assert not b.intersects(segments.segmentlistdict({}))
        assert not segments.segmentlistdict({}).intersects(segments.segmentlistdict({}))

        assert not a.intersects_all(b)
        assert b.intersects_all(a)

        assert a.all_intersects(b)
        assert not b.all_intersects(a)

        assert not a.all_intersects_all(b)

    def test_pickle(self):
        a = segments.segmentlistdict({
            "H1": segments.segmentlist([segments.segment(0, 10),
                                        segments.segment(20, 30)])})
        a.offsets["H1"] = 10.0
        assert a == pickle.loads(pickle.dumps(a, protocol = 0))
        assert a == pickle.loads(pickle.dumps(a, protocol = 1))
        assert a == pickle.loads(pickle.dumps(a, protocol = 2))
