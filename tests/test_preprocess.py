from unittest import TestCase

from productionreport.preprocess import Preprocess


class TestPreprocess(TestCase):
    def test_get_date_based_on_6am_format(self):
        tests = [
            (('23/02/2021', '04:50:30'), '22/02/2021'),
            (('01/02/2021', '04:50:30'), '31/01/2021'),
            (('31/01/2021', '06:00:00'), '31/01/2021')
        ]
        for args, expected in tests:
            got = Preprocess.get_date_based_on_6am_format(args[0], args[1])
            print(got)
            self.assertEqual(got, expected)
