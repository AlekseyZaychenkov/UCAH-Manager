import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "UCA_Manager.settings")
import django
django.setup()

from django.test import SimpleTestCase
from workspace_editor.utils.event_utils import get_day_numbers


class TestEventUtils(SimpleTestCase):


    def test_get_day_numbers(self):
        test_get_day_numbers_cases = [{"total_days": 2,
                                       "right_result": [0, 1, 2]},

                                     {"total_days": 3,
                                       "right_result": [0, 2,   1, 3]},

                                      {"total_days": 4,
                                       "right_result": [0, 2, 4,   1, 3]},

                                      {"total_days": 8,
                                       "right_result": [0, 4, 8,   2, 6,   1, 3, 5, 7]},

                                      {"total_days": 16,
                                       "right_result": [0, 8, 16,   4, 12,   2, 6, 10, 14,
                                                        1, 3, 5, 7, 9, 11, 13, 15] },
                                      ]

        for case in test_get_day_numbers_cases:
            result = get_day_numbers(total_days=case.get('total_days'))

            self.assertEqual(case.get('right_result'), result,
                             msg=f"Wrong calculation for '{case.get('total_days')}' days")






