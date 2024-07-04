from collections import defaultdict
from dimod import BinaryQuadraticModel
import dynex
from utils import DAYS, SHIFTS

def _debug(message):
    with open("chpa.ca", "a") as f:
        f.write(message + "\n")

def _format_sample(sample):
    fs = []
    items = list(sample.items())
    for i in range(0, len(items), 5):
        chunk = items[i:i + 5]
        fs.append(", ".join(f"{k}: {v}" for k, v in chunk))
    return "\n".join(fs)

def _format_bqm(bqm):
    fbqm = []
    linear_items = list(bqm.linear.items())
    fbqm.append("[DYNEX] :: Linear terms:")
    for i in range(0, len(linear_items), 5):
        chunk = linear_items[i:i + 5]
        fbqm.append(", ".join(f"{k}: {v}" for k, v in chunk))
    qi = list(bqm.quadratic.items())
    fbqm.append("[DYNEX] :: Quadratic terms:")
    for i in range(0, len(qi), 5):
        chunk = qi[i:i + 5]
        fbqm.append(", ".join(f"{(k1, k2)}: {v}" for (k1, k2), v in chunk))
    return "\n".join(fbqm)

def build_bqm(
    availability,
    shifts,
    min_shifts,
    max_shifts,
    shift_min,
    shift_max,
    requires_manager,
    allow_isolated_days_off,
):
    bqm = BinaryQuadraticModel('BINARY')
    employees = list(availability.keys())

    x = {(employee, shift): employee + "_" + shift for shift in shifts for employee in employees}
    for employee, schedule in availability.items():
        for i, shift in enumerate(shifts):
            if schedule[i] == 2:
                bqm.add_variable(x[employee, shift], -1)
    num_s = (min_shifts + max_shifts) / 2
    for employee in employees:
        shift_vars = [x[employee, shift] for shift in shifts]
        bqm.add_linear_equality_constraint(
            [(var, 1) for var in shift_vars],
            constant=-num_s,
            lagrange_multiplier=1
        )
    for employee, schedule in availability.items():
        for i, shift in enumerate(shifts):
            if schedule[i] == 0:
                bqm.set_linear(x[employee, shift], 100000)
    for employee in employees:
        shift_vars = [x[employee, shift] for shift in shifts]
        bqm.add_linear_inequality_constraint(
            [(var, 1) for var in shift_vars],
            constant=-max_shifts,
            lagrange_multiplier=1,
            label=f"overtime,{employee}"
        )
        bqm.add_linear_inequality_constraint(
            [(var, -1) for var in shift_vars],
            constant=min_shifts,
            lagrange_multiplier=1,
            label=f"insufficient,{employee}"
        )
    for shift in shifts:
        shift_vars = [x[employee, shift] for employee in employees]
        bqm.add_linear_inequality_constraint(
            [(var, 1) for var in shift_vars],
            constant=-shift_min,
            lagrange_multiplier=1,
            label=f"understaffed,,{shift}"
        )
        bqm.add_linear_inequality_constraint(
            [(var, -1) for var in shift_vars],
            constant=shift_max,
            lagrange_multiplier=1,
            label=f"overstaffed,,{shift}"
        )
    if not allow_isolated_days_off:
        for employee in employees:
            for i in range(len(shifts) - 2):
                bqm.add_interaction(x[employee, shifts[i]], x[employee, shifts[i+2]], 1)
    if requires_manager:
        for shift in shifts:
            manager_vars = [x[manager, shift] for manager in employees if manager.endswith("Mgr")]
            bqm.add_linear_inequality_constraint(
                [(var, 1) for var in manager_vars],
                constant=-1,
                lagrange_multiplier=1,
                label=f"at_least_one_manager,,{shift}"
            )
            bqm.add_linear_inequality_constraint(
                [(var, -1) for var in manager_vars],
                constant=1,
                lagrange_multiplier=1,
                label=f"at_most_one_manager,,{shift}"
            )

    return bqm



def run_bqm(bqm):
    model = dynex.BQM(bqm)
    _debug(f"[DYNEX] :: Building BQM {_format_bqm(bqm)}")
    _debug(f"[DYNEX] :: Total BQM Variables {len(bqm.variables)}")
    _debug("[DYNEX] :: Starting Dynex n.quantum Computing..")
    sampler = dynex.DynexSampler(model, mainnet=True, description='Quantum Scheduling', bnb=False)
    _debug(f"[DYNEX] :: Quantum Circuits In Use = 1000 || STEPS = 100 || Description : Quantum Scheduling")
    sampleset = sampler.sample(num_reads=1000, annealing_time=100)
    _debug("[DYNEX] :: Solution obtained from Dynex Network..")
    errors = defaultdict(list)
    sol = sampleset.first.sample
    _debug(f"[DYNEX] :: {_format_sample(sol)}")
    s_vals = set(sol.values())
    if s_vals == {0.0}:
        sol[list(bqm.variables)[0]] = 1.0
        _debug("[DYNEX] :: All solutions were zero, setting the first variable to 1")

    msgs = {
        "unavailable": (
            "Employees scheduled when unavailable",
            "{employee} on {day}"
        ),
        "overtime": (
            "Employees with scheduled overtime",
            "{employee}"
        ),
        "insufficient": (
            "Employees with not enough scheduled time",
            "{employee}"
        ),
        "understaffed": (
            "Understaffed shifts",
            "{day} is understaffed"
        ),
        "overstaffed": (
            "Overstaffed shifts",
            "{day} is overstaffed"
        ),
        "isolated": (
            "Isolated shifts",
            "{day} is an isolated day off for {employee}"
        ),
        "manager_issue": (
            "Shifts with no manager",
            "No manager scheduled on {day}"
        ),
        "too_many_consecutive": (
            "Employees with too many consecutive shifts",
            "{employee} starting with {day}"
        ),
        "trainee_issue": (
            "Shifts with trainee scheduling issues",
            "Trainee scheduling issue on {day}"
        ),
    }
    constraint_labels = sampleset.info.get("constraint_labels", [])
    for i, label in enumerate(constraint_labels):
        key, *data = label.split(",")
        try:
            heading, error_msg = msgs[key]
        except KeyError:
            _debug(f"[DYNEX] :: Unknown key in constraint labels: {key}")
            continue
        format_dict = dict(zip(["employee", "day"], data))
        if format_dict["day"]:
            index = int(format_dict["day"]) - 1
            format_dict["day"] = f"{DAYS[index % 7]} {SHIFTS[index]}"
        errors[heading].append(error_msg.format(**format_dict))
        _debug(f"[DYNEX] :: Error logged: {heading} - {error_msg.format(**format_dict)}")
        
    return sol, errors

