from datetime import date, timedelta

from django.test import SimpleTestCase

from apps.progress.selectors import _split_goal, compute_streaks

TODAY = date(2026, 11, 13)


def days_ago(*offsets):
    return {TODAY - timedelta(days=o) for o in offsets}


class ComputeStreakTests(SimpleTestCase):
    def test_no_activity(self):
        s = compute_streaks([], TODAY)
        self.assertEqual((s.current, s.longest, s.active_today), (0, 0, False))

    def test_active_today_counts(self):
        s = compute_streaks(days_ago(0, 1, 2), TODAY)
        self.assertEqual((s.current, s.longest, s.active_today), (3, 3, True))

    def test_streak_survives_until_end_of_today(self):
        # Active yesterday and the day before, nothing yet today: still a 2-day streak.
        s = compute_streaks(days_ago(1, 2), TODAY)
        self.assertEqual((s.current, s.active_today), (2, False))

    def test_missed_day_breaks_streak(self):
        s = compute_streaks(days_ago(2, 3, 4), TODAY)
        self.assertEqual(s.current, 0)
        self.assertEqual(s.longest, 3)

    def test_longest_is_independent_of_current(self):
        s = compute_streaks(days_ago(0, 5, 6, 7, 8, 20), TODAY)
        self.assertEqual((s.current, s.longest), (1, 4))


class SplitGoalTests(SimpleTestCase):
    def test_round_robin(self):
        self.assertEqual(_split_goal(5, 3), [2, 2, 1])
        self.assertEqual(_split_goal(1, 3), [1, 0, 0])
        self.assertEqual(_split_goal(6, 3), [2, 2, 2])
