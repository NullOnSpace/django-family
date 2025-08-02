from django.test import TestCase
from django.utils import timezone

from babycare.models import BabyDate, EarlierThanLMPError, LaterThanBirthError, NotBornError


class BabyDateTestCase(TestCase):
    def test_get_gestational_age_days(self):
        baby_date = BabyDate(
            last_menstrual_period=timezone.now().date() - timezone.timedelta(days=30),
        )
        # Test with current date
        self.assertEqual(baby_date.get_gestational_age_days(), 30)

        # Test with ultrasound fixed days
        baby_date.ultrasound_fixed_days = 5
        self.assertEqual(baby_date.get_gestational_age_days(
            ultrasound_fixed=True), 25)

        # Test with a date before the last menstrual period
        date_earlier = timezone.now().date() - timezone.timedelta(days=32)
        with self.assertRaises(EarlierThanLMPError):
            baby_date.get_gestational_age_days(date_earlier)

    def test_get_gestational_age_days_with_birthday(self):
        birthday = timezone.now() - timezone.timedelta(days=10)
        baby_date = BabyDate(
            last_menstrual_period=timezone.now().date() - timezone.timedelta(days=270),
            birthday=birthday
        )
        # Test with a date after the birthday
        self.assertEqual(baby_date.get_gestational_age_days(), 270)

        # Test with a date before the birthday
        date_before_birthday = (birthday - timezone.timedelta(days=5)).date()
        self.assertEqual(baby_date.get_gestational_age_days(
            date_before_birthday), 255)

    def test_get_postmenstrual_age_days(self):
        baby_date = BabyDate(
            last_menstrual_period=timezone.now().date() - timezone.timedelta(days=281),
        )
        # Test with current date without birthday
        with self.assertRaises(NotBornError):
            baby_date.get_postmenstrual_age_days()

        baby_date.birthday = timezone.now() - timezone.timedelta(days=10)

        # Test with a date before birthday
        date_earlier = timezone.now().date() - timezone.timedelta(days=32)
        with self.assertRaises(NotBornError):
            baby_date.get_postmenstrual_age_days(date_earlier)

        # Test with current date after birthday
        self.assertEqual(baby_date.get_postmenstrual_age_days(), 281)

    def test_get_chronological_age_days(self):
        baby_date = BabyDate(
            last_menstrual_period=timezone.now().date() - timezone.timedelta(days=300)
        )
        # Test with current date without birthday
        with self.assertRaises(NotBornError):
            baby_date.get_chronological_age_days()

        baby_date.birthday = timezone.now() - timezone.timedelta(days=10)
        # Test with a date before the birthday
        date_before_birthday = (baby_date.birthday -   # type: ignore
                                timezone.timedelta(days=5)).date()
        with self.assertRaises(NotBornError):
            baby_date.get_chronological_age_days(date_before_birthday)

        # Test with a date after the birthday
        date_after_birthday = (baby_date.birthday +  # type: ignore
                               timezone.timedelta(days=5)).date()
        self.assertEqual(
            baby_date.get_chronological_age_days(date_after_birthday),
            5
        )

    def test_get_corrected_age_days_with_term_baby(self):
        baby_date = BabyDate(
            last_menstrual_period=timezone.now().date() - timezone.timedelta(days=300)
        )
        # Test with current date without birthday
        with self.assertRaises(NotBornError):
            baby_date.get_corrected_age_days()

        # Test with term baby
        baby_date.birthday = timezone.now() - timezone.timedelta(days=10)
        # Test with a date before the birthday
        date_before_birthday = (baby_date.birthday -  # type: ignore
                                timezone.timedelta(days=5)).date()
        with self.assertRaises(NotBornError):
            baby_date.get_corrected_age_days(date_before_birthday)

        # Test with a date after the birthday
        date_after_birthday = (baby_date.birthday +  # type: ignore
                               timezone.timedelta(days=5)).date()
        self.assertEqual(
            baby_date.get_corrected_age_days(date_after_birthday),
            5
        )

    def test_get_corrected_age_days_with_preterm_baby(self):
        birthday = timezone.now() - timezone.timedelta(days=50)
        baby_date = BabyDate(
            last_menstrual_period=timezone.now().date() - timezone.timedelta(days=300),
            birthday=birthday
        )

        date_after_birthday = (birthday + timezone.timedelta(days=5)).date()
        self.assertEqual(
            baby_date.get_corrected_age_days(date_after_birthday),
            -25  # 300 - 50 = 250, so corrected age is 5 - (280 - 250) = -25
        )

        date_after_due = baby_date.get_due_date() + timezone.timedelta(days=5)
        self.assertEqual(
            baby_date.get_corrected_age_days(date_after_due),
            5
        )
