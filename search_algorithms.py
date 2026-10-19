"""
CPS232 - HW2: Searching Algorithms
==================================

PROBLEM 1  (50 pts)
    Given a set S of n arbitrary natural numbers and another natural number w,
    decide whether w is in S.
        Algorithm : merge sort (hand-written)  ->  binary search (hand-written)
        Cost      : sort once  O(n log n)   +   each search  O(log n)

PROBLEM 2  (50 pts)
    Given a SORTED (ascending) list of n numbers, find a number that sits near
    the front (position i, with i much smaller than n).  Beat binary search's O(log n).
        Algorithm : exponential (galloping) search
        Cost      : O(log i)   -> independent of n, so it wins whenever i << n

RULES FOLLOWED
    * The algorithms use only primitive operations: loops, comparisons, indexing,
      append, arithmetic.  No built-in sort / sorted / "in" / bisect, no libraries.
    * Python's own sorted() and "in" appear ONLY in the correctness tests and as a
      speed baseline in the experiments - never inside the algorithms.
    * Extra libraries are used only for the experiments (time, random, csv, matplotlib).

HOW TO RUN
    python search_algorithms.py --quick    # small and fast (about 1 minute) - check everything works
    python search_algorithms.py            # full run (several minutes) - use for final results
    Output: tables in the terminal + CSV files and PNG graphs in the "results" folder.
"""

import argparse   # lets us type --quick on the command line
import csv        # writes experiment tables to .csv files
import os         # builds file paths / creates the results folder
import random     # test data only (never used inside the algorithms)
import sys
import time       # stopwatch for wall-clock measurements

sys.setrecursionlimit(10000)   # merge sort only recurses ~log2(n) deep, this is just a safety margin

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(HERE, "results")

# One shared tally of "element comparisons". Every algorithm adds 1 each time it
# compares array items. This counts operations directly, so the results do not
# depend on how fast the computer is.
comparisons = 0


# =====================================================================================
# PROBLEM 1 - merge sort + binary search
# =====================================================================================
def merge_sort(a):
    """Return a NEW sorted list. Split in half, sort each half, merge.  T(n) = 2T(n/2) + n."""
    global comparisons
    if len(a) <= 1:
        return a                      # base case: 0 or 1 items is already sorted
    mid = len(a) // 2                 # middle index (integer division)
    left = merge_sort(a[:mid])        # sort the left half
    right = merge_sort(a[mid:])       # sort the right half

    merged = []                       # the output list we build
    i = 0                             # next unused item in left
    j = 0                             # next unused item in right
    while i < len(left) and j < len(right):
        comparisons += 1              # one comparison between two items
        if left[i] <= right[j]:       # the smaller front item goes out first
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    while i < len(left):              # one side ran out; copy what is left of the other
        merged.append(left[i])
        i += 1
    while j < len(right):
        merged.append(right[j])
        j += 1
    return merged


def binary_search(a, w, lo=0, hi=None):
    """Search the sorted list a[lo..hi] (inclusive) for w. Return its index or -1."""
    global comparisons
    if hi is None:
        hi = len(a) - 1               # default: search the whole list
    while lo <= hi:                   # the window [lo, hi] still has candidates
        mid = (lo + hi) // 2          # look at the middle of the window
        comparisons += 1              # one comparison of a[mid] against w
        if a[mid] == w:
            return mid                # found it
        elif a[mid] < w:
            lo = mid + 1              # w can only be to the right
        else:
            hi = mid - 1              # w can only be to the left
    return -1                         # window is empty, so w is not in the list


def contains(S, w):
    """PROBLEM 1 answer: is w in the (unsorted) set S?  Sort first, then binary search."""
    sorted_S = merge_sort(S)                      # O(n log n), done once
    return binary_search(sorted_S, w) != -1       # O(log n)


def linear_contains(S, w):
    """Reference only: scan an unsorted list one item at a time, O(n)."""
    global comparisons
    for x in S:
        comparisons += 1
        if x == w:
            return True
    return False


# =====================================================================================
# PROBLEM 2 - exponential (galloping) search on a sorted list
# =====================================================================================
def linear_search(a, x):
    """Baseline 1: walk from the front. Stops early because the list is sorted. O(i)."""
    global comparisons
    for k in range(len(a)):
        comparisons += 1
        if a[k] == x:
            return k
        if a[k] > x:                  # we passed the spot where x would be
            return -1
    return -1


def exponential_search(a, x):
    """
    Baseline 2 is binary_search (above). The improved algorithm is this one:
      Phase 1 (gallop): probe positions 1, 2, 4, 8, ... until we reach a value >= x.
      Phase 2: binary search only inside the last doubling window.
    Both phases take about log2(i) steps, where i is the position of x. Total O(log i).
    """
    global comparisons
    n = len(a)
    if n == 0:
        return -1
    comparisons += 1
    if a[0] >= x:                     # x is at (or before) the very first slot
        return 0 if a[0] == x else -1

    bound = 1                         # a[0] < x is known; start galloping from index 1
    while bound < n:
        comparisons += 1
        if a[bound] < x:
            bound = bound * 2         # still too small, double the step
        else:
            break                     # a[bound] >= x, so x lies in (bound/2, bound]

    lo = bound // 2 + 1               # a[bound // 2] < x, so skip it
    hi = bound if bound < n else n - 1   # do not run past the end of the list
    return binary_search(a, x, lo, hi)   # Phase 2


# =====================================================================================
# TEST DATA HELPERS (not part of the algorithms)
# =====================================================================================
def make_random_set(n):
    """n DISTINCT random natural numbers in random order (a 'set' as a list)."""
    return random.sample(range(1, 10 * n + 1), n)


def make_sorted_list(n):
    """Sorted list of n distinct natural numbers with random gaps (so values are not just 1..n)."""
    a = []
    value = 0
    for _ in range(n):
        value += random.randint(1, 10)
        a.append(value)
    return a


def ceil_log2(n):
    """Smallest L with 2**L >= n, using only a loop (no math library)."""
    L = 0
    while (1 << L) < n:
        L += 1
    return L


# =====================================================================================
# CORRECTNESS TESTS  (compare every algorithm with Python's own answer)
# =====================================================================================
def run_tests(trials):
    print("=" * 78)
    print("CORRECTNESS TESTS")
    print("=" * 78)
    random.seed(1)

    # --- merge sort vs built-in sorted, including duplicates and tiny inputs ---
    assert merge_sort([]) == []
    assert merge_sort([5]) == [5]
    for _ in range(trials):
        n = random.randint(0, 60)
        a = [random.randint(1, 20) for _ in range(n)]     # small range -> many duplicates
        assert merge_sort(a) == sorted(a)
    print("  merge_sort            : matches sorted() on", trials, "random lists (with duplicates)")

    # --- Problem 1: contains() vs the built-in 'in' ---
    for _ in range(trials):
        n = random.randint(0, 60)
        S = [random.randint(1, 80) for _ in range(n)]
        w = random.randint(1, 80)
        assert contains(S, w) == (w in S)
    assert contains([], 7) is False
    assert contains([7], 7) is True
    print("  contains (Problem 1)  : matches the 'in' operator on", trials, "random cases")

    # --- Problem 2: all three searches on sorted lists ---
    for _ in range(trials):
        n = random.randint(0, 80)
        a = merge_sort([random.randint(1, 100) for _ in range(n)])   # duplicates allowed
        x = random.randint(0, 101)
        for fn in (linear_search, binary_search, exponential_search):
            idx = fn(a, x)
            if x in a:
                assert idx != -1 and a[idx] == x, (fn.__name__, a, x, idx)
            else:
                assert idx == -1, (fn.__name__, a, x, idx)
    print("  linear / binary / exponential : correct on", trials, "random sorted lists (hits and misses)")

    # --- edge cases for exponential search ---
    assert exponential_search([], 3) == -1
    assert exponential_search([3], 3) == 0 and exponential_search([3], 2) == -1 and exponential_search([3], 4) == -1
    big = list(range(1, 1001))
    for x in (1, 2, 3, 4, 5, 8, 9, 512, 513, 999, 1000):      # powers of two are the risky spots
        assert exponential_search(big, x) == x - 1
    assert exponential_search(big, 0) == -1 and exponential_search(big, 1001) == -1
    print("  exponential_search    : edge cases OK (empty, 1 item, powers of two, first/last, missing)")
    print("  ALL TESTS PASSED\n")


# =====================================================================================
# MEASURING HELPERS
# =====================================================================================
def time_call(fn, *args):
    """Average seconds per call. Fast calls are repeated many times, best of 3 batches."""
    t0 = time.perf_counter()
    fn(*args)
    one = time.perf_counter() - t0                       # rough cost of a single call
    reps = max(1, min(20000, int(0.02 / max(one, 1e-9))))   # aim for ~20 ms per batch
    best = None
    for _ in range(3):
        t0 = time.perf_counter()
        for _ in range(reps):
            fn(*args)
        t = (time.perf_counter() - t0) / reps
        if best is None or t < best:
            best = t
    return best


def count_ops(fn, *args):
    """Run fn once and return how many element comparisons it made."""
    global comparisons
    comparisons = 0
    fn(*args)
    return comparisons


def save_csv(name, header, rows):
    os.makedirs(RESULTS_DIR, exist_ok=True)
    path = os.path.join(RESULTS_DIR, name)
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print("  saved", os.path.join("results", name))


def print_table(header, rows):
    widths = [max(len(str(h)), *(len(str(r[c])) for r in rows)) for c, h in enumerate(header)]
    print("  " + "  ".join(str(h).rjust(w) for h, w in zip(header, widths)))
    for r in rows:
        print("  " + "  ".join(str(v).rjust(w) for v, w in zip(r, widths)))
    print()


def line_plot(name, title, xlabel, ylabel, x, series, logx=False, logy=False, ymin0=False):
    """series = {label: list_of_y}. Saves a PNG into results/."""
    import matplotlib
    matplotlib.use("Agg")                   # draw to files, no window needed
    import matplotlib.pyplot as plt
    plt.figure(figsize=(8, 5))
    for label, y in series.items():
        plt.plot(x, y, marker="o", markersize=4, label=label)
    if logx:
        plt.xscale("log")
    if logy:
        plt.yscale("log")
    if ymin0:
        plt.ylim(bottom=0)              # start the y-axis at zero so flat really looks flat
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True, which="both", alpha=0.3)
    plt.legend()
    plt.tight_layout()
    os.makedirs(RESULTS_DIR, exist_ok=True)
    plt.savefig(os.path.join(RESULTS_DIR, name), dpi=130)
    plt.close()
    print("  saved", os.path.join("results", name))


# =====================================================================================
# PROBLEM 1 EXPERIMENTS
# =====================================================================================
def exp1a_time_vs_n(sizes):
    print("-" * 78)
    print("EXP 1A: Problem 1 - total time (merge sort + binary search) vs n")
    print("-" * 78)
    rows = []
    for n in sizes:
        S = make_random_set(n)
        w = S[n // 2]                                         # a value that is present
        t_sort = time_call(merge_sort, S)                     # hand-written sort
        t_builtin = time_call(sorted, S)                      # Python's C sort, baseline only
        srt = merge_sort(S)
        t_search = time_call(binary_search, srt, w)
        t_total = t_sort + t_search
        nlogn = n * ceil_log2(n)
        rows.append([n, round(t_sort, 6), round(t_search * 1e6, 2), round(t_builtin, 6),
                     round(t_total / nlogn * 1e9, 1)])
    header = ["n", "merge_sort_s", "bin_search_us", "builtin_sorted_s", "ns_per_(n*log2n)"]
    print_table(header, rows)
    save_csv("exp1A_time_vs_n.csv", header, rows)
    ns = [r[0] for r in rows]
    line_plot("exp1A_time_vs_n.png", "Problem 1: running time vs n (log-log)", "n (number of elements)",
              "seconds", ns,
              {"our merge sort": [r[1] for r in rows],
               "Python built-in sorted (baseline)": [r[3] for r in rows]}, logx=True, logy=True)
    line_plot("exp1A_normalized.png", "Problem 1: time / (n log2 n) stays flat  =>  O(n log n)",
              "n (number of elements)", "nanoseconds per (n * log2 n)", ns,
              {"merge sort + search": [r[4] for r in rows]}, logx=True, ymin0=True)
    return rows


def exp1b_comparison_bound(max_n):
    print("-" * 78)
    print("EXP 1B: merge sort comparison count vs the proven bound  T(n) <= n * ceil(log2 n)")
    print("-" * 78)
    rows = []
    ns = []
    n = 1
    while n <= max_n:
        ns.append(n)
        n = n * 2 if n >= 8 else n + 1
    ns += [3, 5, 7, 100, 1000, 12345]                          # some non-powers of two as well
    ns = sorted(set(x for x in ns if x <= max_n))
    for n in ns:
        S = make_random_set(n)
        c = count_ops(merge_sort, S)
        bound = n * ceil_log2(n)
        assert c <= bound, (n, c, bound)                       # the induction claim, checked
        rows.append([n, c, bound, round(c / bound, 3) if bound else 0])
    header = ["n", "comparisons", "n*ceil(log2 n)", "ratio"]
    print_table(header, rows[-12:])
    print("  bound held for every n tested (assertion passed)\n")
    save_csv("exp1B_comparison_bound.csv", header, rows)
    big = [r for r in rows if r[0] >= 2]
    line_plot("exp1B_comparison_bound.png", "Merge sort comparisons never exceed n*ceil(log2 n)",
              "n", "comparisons", [r[0] for r in big],
              {"measured comparisons": [r[1] for r in big],
               "bound n*ceil(log2 n)": [r[2] for r in big]}, logx=True, logy=True)


def exp1c_amortization(n, query_counts):
    print("-" * 78)
    print("EXP 1C: many queries on the same set (n = %d) - sort once vs scan every time" % n)
    print("-" * 78)
    S = make_random_set(n)
    srt = merge_sort(S)
    queries = [random.choice(S) if random.random() < 0.5 else random.randint(1, 10 * n) for _ in range(200)]
    t_sort = time_call(merge_sort, S)
    t_bin = sum(time_call(binary_search, srt, q) for q in queries[:50]) / 50
    t_lin = sum(time_call(linear_contains, S, q) for q in queries[:50]) / 50
    print("  one-time sort: %.4f s   per binary query: %.2f us   per linear scan: %.2f us"
          % (t_sort, t_bin * 1e6, t_lin * 1e6))
    cross = t_sort / (t_lin - t_bin)
    print("  sorting pays for itself after about %.0f queries\n" % cross)
    rows = []
    for q in query_counts:
        rows.append([q, round(q * t_lin, 5), round(t_sort + q * t_bin, 5)])
    header = ["queries", "scan_every_time_s", "sort_once_then_binary_s"]
    print_table(header, rows)
    save_csv("exp1C_amortization.csv", header, rows)
    line_plot("exp1C_amortization.png", "Sorting once vs scanning every time (n = %d)" % n,
              "number of queries", "total seconds", query_counts,
              {"scan every time  O(n) each": [r[1] for r in rows],
               "sort once + binary  O(n log n) + O(log n) each": [r[2] for r in rows]},
              logx=True, logy=True)


def exp1d_input_shapes(n):
    print("-" * 78)
    print("EXP 1D: does the input order change merge sort?  (n = %d)" % n)
    print("-" * 78)
    shapes = {
        "random": make_random_set(n),
        "already sorted": list(range(n)),
        "reverse sorted": list(range(n, 0, -1)),
        "all equal": [7] * n,
        "few distinct (5 values)": [random.randint(1, 5) for _ in range(n)],
    }
    rows = []
    for name, data in shapes.items():
        rows.append([name, count_ops(merge_sort, data), round(time_call(merge_sort, data), 5)])
    header = ["input shape", "comparisons", "seconds"]
    print_table(header, rows)
    save_csv("exp1D_input_shapes.csv", header, rows)
    print("  Takeaway: counts stay within a small factor of n log n for every shape - no bad case.\n")


# =====================================================================================
# PROBLEM 2 EXPERIMENT HELPERS
# =====================================================================================
def avg_cost_miss(fn, a, xs):
    """Same as avg_cost but for targets that are NOT in the list (search must return -1)."""
    global comparisons
    comparisons = 0
    for x in xs:
        assert fn(a, x) == -1
    cmp_avg = comparisons / len(xs)

    def run_all():
        for x in xs:
            fn(a, x)
    return cmp_avg, time_call(run_all) / len(xs) * 1e6


def targets_near(a, i):
    """
    Up to 24 hit-targets at random positions in [i, 2i) (1-based, never past the end).
    One lucky target can make binary search look better or worse than it really is
    (e.g. a target sitting exactly on a midpoint), so we average over several.
    """
    positions = []
    for _ in range(24):
        p = random.randint(i, 2 * i - 1)
        if p <= len(a) and p not in positions:
            positions.append(p)
    if not positions:
        positions.append(min(i, len(a)))
    return [a[p - 1] for p in positions]


def avg_cost(fn, a, xs):
    """Average (comparisons, microseconds) per search over the targets in xs."""
    global comparisons
    comparisons = 0
    for x in xs:
        assert fn(a, x) != -1                       # every hit target must be found
    cmp_avg = comparisons / len(xs)

    def run_all():                                  # one timed pass over all targets
        for x in xs:
            fn(a, x)
    return cmp_avg, time_call(run_all) / len(xs) * 1e6


# =====================================================================================
# PROBLEM 2 EXPERIMENTS
# =====================================================================================
def exp2a_position_sweep(n, positions):
    print("-" * 78)
    print("EXP 2A: Problem 2 - cost vs target position i  (n = %d, i = 1-based position)" % n)
    print("-" * 78)
    a = make_sorted_list(n)
    rows = []
    for i in positions:
        xs = targets_near(a, i)
        row = [i]
        costs = [avg_cost(fn, a, xs) for fn in (linear_search, binary_search, exponential_search)]
        row += [round(c[0], 1) for c in costs]          # average comparisons
        row += [round(c[1], 3) for c in costs]          # average microseconds
        rows.append(row)
    header = ["i", "linear_cmp", "binary_cmp", "expo_cmp", "linear_us", "binary_us", "expo_us"]
    print_table(header, rows)
    save_csv("exp2A_position_sweep.csv", header, rows)
    xs = [r[0] for r in rows]
    line_plot("exp2A_comparisons_vs_i.png", "Comparisons vs target position i (n = %d)" % n,
              "i (position of the target, log scale)", "comparisons (log scale)", xs,
              {"linear  O(i)": [r[1] for r in rows],
               "binary  O(log n)": [r[2] for r in rows],
               "exponential  O(log i)": [r[3] for r in rows]}, logx=True, logy=True)
    line_plot("exp2A_time_vs_i.png", "Wall-clock time vs target position i (n = %d)" % n,
              "i (position of the target, log scale)", "microseconds per search (log scale)", xs,
              {"linear  O(i)": [r[4] for r in rows],
               "binary  O(log n)": [r[5] for r in rows],
               "exponential  O(log i)": [r[6] for r in rows]}, logx=True, logy=True)
    # when does exponential stop beating binary? (comparison count)
    beats = [r[0] for r in rows if r[3] < r[2]]
    worse = [r[0] for r in rows if r[3] > r[2]]
    print("  exponential uses FEWER comparisons than binary for i up to %d" % (max(beats) if beats else 0))
    if worse:
        print("  binary wins only once i is large (first seen at i = %d)" % min(worse))
    cross = [r[0] for r in rows if r[1] > r[3]]
    print("  linear is cheaper than exponential only for very small i (it loses from i = %d on)\n"
          % (min(cross) if cross else 0))


def exp2b_n_sweep(sizes, i):
    print("-" * 78)
    print("EXP 2B: Problem 2 - cost vs n with the target held at position i = %d" % i)
    print("-" * 78)
    biggest = make_sorted_list(max(sizes))
    rows = []
    for n in sizes:
        a = biggest[:n]                                        # first n items are still sorted
        xs = targets_near(a, i)
        row = [n]
        costs = [avg_cost(fn, a, xs) for fn in (binary_search, exponential_search)]
        row += [round(c[0], 1) for c in costs]
        row += [round(c[1], 3) for c in costs]
        rows.append(row)
    header = ["n", "binary_cmp", "expo_cmp", "binary_us", "expo_us"]
    print_table(header, rows)
    save_csv("exp2B_n_sweep_i%d.csv" % i, header, rows)
    xs = [r[0] for r in rows]
    line_plot("exp2B_comparisons_vs_n_i%d.png" % i, "Comparisons vs n with target at position %d" % i,
              "n (list length, log scale)", "comparisons", xs,
              {"binary  O(log n) - keeps growing": [r[1] for r in rows],
               "exponential  O(log i) - flat": [r[2] for r in rows]}, logx=True)
    line_plot("exp2B_time_vs_n_i%d.png" % i, "Wall-clock time vs n with target at position %d" % i,
              "n (list length, log scale)", "microseconds per search", xs,
              {"binary": [r[3] for r in rows], "exponential": [r[4] for r in rows]}, logx=True)


def exp2c_headline(n, i_values):
    print("-" * 78)
    print("EXP 2C: headline comparison  (n = %d, small i, hits and misses)" % n)
    print("-" * 78)
    a = make_sorted_list(n)
    rows = []
    for i in i_values:
        hits = targets_near(a, i)
        # a miss = a number just above a hit that is NOT in the list (gaps are random, so check)
        misses = [x + 1 for x in hits if (x + 1) not in a[: i * 2 + 40]]
        for label, xs in (("hit", hits), ("miss", misses)):
            if not xs:
                continue
            if label == "hit":
                cb, tb = avg_cost(binary_search, a, xs)
                ce, te = avg_cost(exponential_search, a, xs)
            else:                                   # misses return -1, so cost them separately
                cb, tb = avg_cost_miss(binary_search, a, xs)
                ce, te = avg_cost_miss(exponential_search, a, xs)
            rows.append([i, label, round(cb, 1), round(ce, 1), round(tb, 3), round(te, 3), round(tb / te, 2)])
    header = ["i", "case", "binary_cmp", "expo_cmp", "binary_us", "expo_us", "speedup_x"]
    print_table(header, rows)
    save_csv("exp2C_headline.csv", header, rows)


# =====================================================================================
# MAIN
# =====================================================================================
def main():
    parser = argparse.ArgumentParser(description="CPS232 HW2 - searching algorithms")
    parser.add_argument("--quick", action="store_true", help="small, fast run for checking")
    args = parser.parse_args()
    random.seed(232)                                            # same data every run -> reproducible

    if args.quick:
        sizes1 = [500 * 2 ** k for k in range(0, 6)]            # up to 16,000
        max_n_b, n_c, n_d = 2000, 10000, 10000
        n2, sizes2 = 50000, [1000, 4000, 16000, 64000]
        trials = 300
    else:
        sizes1 = [1000 * 2 ** k for k in range(0, 10)]          # 1,000 ... 512,000
        max_n_b, n_c, n_d = 100000, 100000, 100000
        n2, sizes2 = 1000000, [1000 * 4 ** k for k in range(0, 7)]   # up to 4,096,000
        trials = 2000

    positions = [p for p in (1, 2, 3, 4, 5, 6, 8, 10, 16, 32, 64, 100, 1000, 10000, 100000, 1000000) if p <= n2]
    query_counts = [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 5000]

    run_tests(trials)
    exp1a_time_vs_n(sizes1)
    exp1b_comparison_bound(max_n_b)
    exp1c_amortization(n_c, query_counts)
    exp1d_input_shapes(n_d)
    exp2a_position_sweep(n2, positions)
    exp2b_n_sweep(sizes2, 10)
    exp2b_n_sweep(sizes2, 1000)
    exp2c_headline(n2, [1, 10, 100, 1000])

    print("=" * 78)
    print("DONE. Open the 'results' folder for the CSV files and PNG graphs.")
    print("=" * 78)


if __name__ == "__main__":
    main()
