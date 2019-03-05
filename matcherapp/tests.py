from django.test import TestCase
from .util import substring_anagram_search, MAX_RETURN_LENGTH

# This is, in fact, the second-letter function copy-pasted from util.py.
# Usually that would be a bad idea, but the idea here is that we know this
# version at least works for the tests; if that one is changed, improved,
# fixed for other situations, etc., having the original here to compare to
# will ensure that it still at least passes these tests.
def second_letter_sort(string):
    if len(string) < 2:
        return 0
    if string[1] == ' ':
        return string[2]
    return string[1]

# TODO: A change in the dictionary might make these tests return None,
# which could break some of these tests.  They need to at least break
# gracefully in that situation.
#
# One option to address this would be to have the test case set up a
# fake dictionary first.
class AnagramRulesTestCase(TestCase):
    # Make sure the ordering function works.
    def test_ordering(self):
        result = substring_anagram_search("oooo")
        sorted_result = sorted(result, key=second_letter_sort)
        self.assertEqual(result, sorted_result)

    # Make sure the output-length limit works.
    # Not a test likely to fail, but it's a core requirement,
    # so it's worth testing.   Also, it's easy to test.
    # Here, we have no choice but to rely on MAX_RETURN_LENGTH,
    # since it might legitimately be changed and the test has to respect that.
    def test_length(self):
        result = substring_anagram_search("atomic")
        self.assertTrue(len(result) <= MAX_RETURN_LENGTH)

    # Of course we have to test the output directly.
    # This one, sadly, depends entirely on the dictionary.
    # See above for ideas to how to get around this problem.
    # This test is a bit of a placeholder for more complex and detailed
    # tests of this nature (ie. confirme expected final output.)
    def test_contents(self):
        expected_results = set(
            ["zzzz zzzz",
            "zzzzzzz",
            "zzzzz",
            "zzzzzzzz",
            "zzzzzz"])
        result = substring_anagram_search("zzzzz")
        # Sets, because aside from the second letter, ordering isn't specified.
        self.assertEqual(set(result), expected_results)

    def test_placeholder(self):
        # Other stuff that needs to be tested...
        # - Dictionary loading function.
        # - Individualized tests for other functions in util.py
        # - Most of the things being tested above should test more variations.
        # - Speed test, making sure queries can be handled in a reasonable time.
        self.assertTrue(True)
