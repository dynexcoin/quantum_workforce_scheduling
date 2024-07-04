# Application Settings
THUMBNAIL = "assets/logo.svg"
APP_TITLE = "Dynex | Scheduling Demo"
MAIN_HEADER = "Workforce Scheduling"
DESCRIPTION = """\
Workforce scheduling is a common industry problem that often becomes complex
due to real-world constraints. This example demonstrates a scheduling
scenario with a variety of employees and rules.
"""
THEME_COLOR = "#1d232f"
THEME_COLOR_SECONDARY = "#1d232f"
REQUESTED_SHIFT_ICON = "✓"
UNAVAILABLE_ICON = "x"


#######################################
# Sliders, buttons and option entries #
#######################################

# min/max number of shifts per employee range slider (value means default)
MIN_MAX_SHIFTS = {
    "min": 1,
    "max": 14,
    "step": 1,
    "value": [5, 7],
}

# min/max number of employees per shift range slider (value means default)
MIN_MAX_EMPLOYEES = {
    "min": 1,
    "max": 100,
    "step": 1,
    "value": [3, 6],
}

# number of employees slider (value means default)
NUM_EMPLOYEES = {
    "min": 4,
    "max": 80,
    "step": 1,
    "value": 12,
}

# max consecutive shifts slider (value means default)
MAX_CONSECUTIVE_SHIFTS = {
    "min": 1,
    "max": 14,
    "step": 1,
    "value": 5,
}

# example scenario labels (must have 4, first is custom scenario)
EXAMPLE_SCENARIO = ["Custom", "Small", "Medium", "Large"]

# default scenarios (don't change order of items)
SMALL_SCENARIO = {
    "num_employees": 12,
    "consecutive_shifts": 5,
    "shifts_per_employee": [5, 7],
    "employees_per_shift": [3, 6],
    "random_seed": "",
}

MEDIUM_SCENARIO = {
    "num_employees": 20,
    "consecutive_shifts": 5,
    "shifts_per_employee": [5, 10],
    "employees_per_shift": [5, 10],
    "random_seed": "",
}

LARGE_SCENARIO = {
    "num_employees": 40,
    "consecutive_shifts": 5,
    "shifts_per_employee": [5, 10],
    "employees_per_shift": [10, 20],
    "random_seed": "",
}
