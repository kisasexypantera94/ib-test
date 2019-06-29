from unittest import TestCase

from magic.magic import Magic


class TestMagic(TestCase):
    def test_integration(self):
        a = Magic(range(100))

        a.filter_(__gt=3).filter_(__lte=5).or_(__lt=20, __gt=13).not_(__eq=15)
        self.assertEqual(list(a), [4, 5, 14, 16, 17, 18, 19])

        a.filter_(__gt=3).not_(__gte=4, __lte=5)
        self.assertEqual(list(a), [14, 16, 17, 18, 19])
