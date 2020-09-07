# -*- coding: utf-8 -*-
"""A single place for different frequency values to be read from."""
import copy

# TODO EOBS-840: Make frequencies.py a model and split it across modules as
# appropriate.
# Frequencies in minutes.
FIVE_MINUTES = 5
TEN_MINUTES = 10
FIFTEEN_MINUTES = 15
THIRTY_MINUTES = 30
ONE_HOUR = 60
TWO_HOURS = 120
FOUR_HOURS = 240
SIX_HOURS = 360
EIGHT_HOURS = 480
TEN_HOURS = 600
TWELVE_HOURS = 720
ONE_DAY = 1440
THREE_DAYS = 4320
ONE_WEEK = 10080

# Tuples with the time and a label.
EVERY_5_MINUTES = (FIVE_MINUTES, 'Every 5 Minutes')
EVERY_10_MINUTES = (TEN_MINUTES, 'Every 10 Minutes')
EVERY_15_MINUTES = (FIFTEEN_MINUTES, 'Every 15 Minutes')
EVERY_30_MINUTES = (THIRTY_MINUTES, 'Every 30 Minutes')
EVERY_HOUR = (ONE_HOUR, 'Every Hour')
EVERY_2_HOURS = (TWO_HOURS, 'Every 2 Hours')
EVERY_4_HOURS = (FOUR_HOURS, 'Every 4 Hours')
EVERY_6_HOURS = (SIX_HOURS, 'Every 6 Hours')
EVERY_8_HOURS = (EIGHT_HOURS, 'Every 8 Hours')
EVERY_10_HOURS = (TEN_HOURS, 'Every 10 Hours')
EVERY_12_HOURS = (TWELVE_HOURS, 'Every 12 Hours')
EVERY_DAY = (ONE_DAY, 'Every Day')
EVERY_3_DAYS = (THREE_DAYS, 'Every 3 Days')
EVERY_WEEK = (ONE_WEEK, 'Every Week')

# Dictionary to lookup tuples by frequency in minutes.
ALL_FREQUENCIES = {
    FIVE_MINUTES: EVERY_5_MINUTES,
    TEN_MINUTES: EVERY_10_MINUTES,
    FIFTEEN_MINUTES: EVERY_15_MINUTES,
    THIRTY_MINUTES: EVERY_30_MINUTES,
    ONE_HOUR: EVERY_HOUR,
    TWO_HOURS: EVERY_2_HOURS,
    FOUR_HOURS: EVERY_4_HOURS,
    SIX_HOURS: EVERY_6_HOURS,
    EIGHT_HOURS: EVERY_8_HOURS,
    TEN_HOURS: EVERY_10_HOURS,
    TWELVE_HOURS: EVERY_12_HOURS,
    ONE_DAY: EVERY_DAY,
    THREE_DAYS: EVERY_3_DAYS,
    ONE_WEEK: EVERY_WEEK
}

# Frequency tuples organised by risk and frequency in minutes.
FREQUENCIES_BY_RISK = {
    'None': {
        EVERY_15_MINUTES[0]: EVERY_15_MINUTES,
        EVERY_12_HOURS[0]: EVERY_12_HOURS,
        EVERY_DAY[0]: EVERY_DAY,
        EVERY_3_DAYS[0]: EVERY_3_DAYS,
        EVERY_WEEK[0]: EVERY_WEEK
    },
    'Low': {
        EVERY_5_MINUTES[0]: EVERY_5_MINUTES,
        EVERY_10_MINUTES[0]: EVERY_10_MINUTES,
        EVERY_15_MINUTES[0]: EVERY_15_MINUTES,
        EVERY_30_MINUTES[0]: EVERY_30_MINUTES,
        EVERY_HOUR[0]: EVERY_HOUR,
        EVERY_2_HOURS[0]: EVERY_2_HOURS,
        EVERY_4_HOURS[0]: EVERY_4_HOURS,
        EVERY_6_HOURS[0]: EVERY_6_HOURS,
        EVERY_8_HOURS[0]: EVERY_8_HOURS,
        EVERY_12_HOURS[0]: EVERY_12_HOURS,
        EVERY_DAY[0]: EVERY_DAY,
        EVERY_3_DAYS[0]: EVERY_3_DAYS,
        EVERY_WEEK[0]: EVERY_WEEK
    },
    'Medium': {
        EVERY_HOUR[0]: EVERY_HOUR
    },
    'High': {
        EVERY_30_MINUTES[0]: EVERY_30_MINUTES
    },
    'Unknown': EVERY_4_HOURS,
    'Transfer': EVERY_15_MINUTES,
    'Obs Restart': EVERY_HOUR
}

# A patient on custom frequency means that any frequency is possible
# for all risk ratings. So if the observation is refused, regardless of
# what the normal frequency might be for that risk rating all options
# must be available

def get_refusal_adjustments():
    frequencies = {
        EVERY_5_MINUTES[0]: EVERY_5_MINUTES,
        EVERY_10_MINUTES[0]: EVERY_10_MINUTES,
        EVERY_15_MINUTES[0]: EVERY_15_MINUTES,
        EVERY_30_MINUTES[0]: EVERY_30_MINUTES,
        EVERY_HOUR[0]: EVERY_HOUR,
        EVERY_2_HOURS[0]: EVERY_2_HOURS,
        EVERY_4_HOURS[0]: EVERY_4_HOURS,
        EVERY_6_HOURS[0]: EVERY_6_HOURS,
        EVERY_8_HOURS[0]: EVERY_8_HOURS,
        EVERY_12_HOURS[0]: EVERY_12_HOURS,
        EVERY_DAY[0]: EVERY_DAY,
        EVERY_3_DAYS[0]: EVERY_3_DAYS,
        EVERY_WEEK[0]: EVERY_WEEK
    }
    frequencies_by_risk = {
        'None': frequencies,
        'Low': frequencies,
        'Medium': frequencies,
        'High': frequencies,
        'Unknown': frequencies,
        'Transfer': frequencies,
        'Obs Restart': frequencies,
    }
    return frequencies_by_risk

PATIENT_REFUSAL_ADJUSTMENTS = get_refusal_adjustments()


def as_list(max=None):
    """
    Returns frequency tuples in a list.
    Passing the max keyword argument will only return frequencies up to and
    including that frequency (in ascending order).

    :param max:
    :type max: int
    :return:
    """
    frequency_tuples = sorted(ALL_FREQUENCIES.values())
    if max:
        frequency_minutes = sorted(ALL_FREQUENCIES.keys())
        index = frequency_minutes.index(max) + 1
        frequency_tuples = frequency_tuples[:index]
    return frequency_tuples


def minutes_only():
    return [minutes for minutes, _ in as_list()]


def get_label_for_minutes(minutes):
    label = ''
    for frequency in as_list():
        if frequency[0] == minutes:
            label = frequency[1]
    return label
