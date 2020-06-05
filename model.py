#!/usr/bin/python

import itertools, random

import numpy as np
import pandas as pd
import plotly.express as px

class Model:
    def __init__(self, N, p_i, p_t, p_d, days_until_transmissible, days_until_detectable, tests_per_day):
        self.N = N # number of people in the group
        self.p_i = p_i # probability that an uninfected group member was innoculated during one day
        self.p_t = p_t # probability that an infected member transmits to another member during one day
        self.p_d = p_d # probability that a detectable member is detected, conditional on being tested
        self.days_until_transmissible = days_until_transmissible
        self.days_until_detectable = days_until_detectable
        self.tests_per_day = tests_per_day
        self.reset()

    def reset(self):
        self.infected = [] # list of days in which someone was infected (non-decreasing)
        self.positive_tests = 0
        self.day = 0

    def one_day_passes(self):
        if random.uniform(0, 1) < (self.N - len(self.infected)) * self.p_i:
            # there is an inoculum today
            self.infected.append(self.day)
        infected_today = 0
        for day in self.infected:
            if day + self.days_until_transmissible <= self.day:
                if random.uniform(0, 1) < self.p_t:
                    infected_today += 1
            if day + self.days_until_detectable <= self.day:
                if random.uniform(0, 1) < (self.tests_per_day / self.N) and random.uniform(0, 1) < self.p_d:
                    self.positive_tests += 1
        infected_today = min(infected_today, self.N - len(self.infected))
        self.infected += [self.day for i in range(infected_today)]
        self.day += 1

    def draw(self, max_days):
        self.reset()
        while self.day < max_days and not self.positive_tests:
            self.one_day_passes()
        return (self.day, self.infected)

def hist(numlist):
    d = {}
    for num in numlist:
        d[num] = 1 + d.get(num, 0)
    return d

def plot():
    random.seed(1) # deterministic
    N = 10
    p_i = 0.002
    p_d = 0.8    # an underestimate because infection can also be detected by symptoms, eventually

    # for each parameterization, plot % of draws with no more than k infections (0-7)
    table = []

    for testfrac in (0.0, 0.1, 0.2, 0.4, 1.0):
       # for reproductive number of 2, 7 transmissible days, p_t = 0.3
       # p_t among dancers will be much worse but balanced against p_t among others
       for p_t in (0.2, 0.3, 0.5):
            model = Model(N, p_i, p_t, p_d, 3, 4, testfrac * N)

            draws = [model.draw(7*6) for i in range(1000)]
            #durations = hist([day for (day, infected) in draws])
            infections = hist([len(infected) for (day, infected) in draws])
            table += [(count, pct*100/len(draws), testfrac, p_t) for (count, pct) in zip(range(len(infections)), itertools.accumulate(infections.values()))]

    data = np.zeros((len(table), ), dtype=[('infected', 'i1'), ('pct', 'i2'), ('testfrac', 'f4'), ('p_t', 'f4')])
    data[:] = table
    dframe = pd.DataFrame(data)
    #fig = px.scatter(dframe, x='infected', y='pct', facet_row='testfrac', facet_col='p_t')
    fig = px.line(dframe, x='infected', y='pct', color='testfrac', facet_row='p_t')
    fig.write_html('first_figure.html', auto_open=True)

def print_hist():
    random.seed(1) # deterministic
    N = 10
    tests_per_day = N
    p_i = 0.002
    # for reproductive number of 2, 7 transmissible days, p_t = 0.3
    # p_t among dancers will be much worse but balanced against p_t among others
    p_t = 0.5
    # this is an underestimate because infection can also be detected by symptoms, eventually
    p_d = 0.8
    model = Model(N, p_i, p_t, p_d, 3, 4, tests_per_day)

    draws = [model.draw(7*6) for i in range(100)]
    durations = hist([day for (day, infected) in draws])
    infections = hist([len(infected) for (day, infected) in draws])

    def count_gte(hist, n):
        return sum([count for (num, count) in hist.items() if num >= n])

    print('Number of draws:', len(draws))
    print('Histogram of days to termination:', durations)
    print('Histogram of number infected at termination:', infections)
    print()
    assert len(draws) == sum(infections.values())
    print('% outcomes with         no infection: ', 100 * infections[0] / len(draws))
    print('% outcomes with     0 or 1 infection: ', 100 * (infections[0] + infections[1]) / len(draws))
    print('% outcomes with 0, 1, or 2 infections:', 100 * (infections[0] + infections[1] + infections[2]) / len(draws))
    gte_4 = count_gte(infections, 4)
    print('% outcomes with 3 or fewer infections:', 100 * (1 - gte_4 / len(draws)))
    print('% outcomes with  4 or more infections:', 100 * gte_4 / len(draws))
    print()
    print('% outcomes with at least 40 days:', 100 * count_gte(durations, 40) / len(draws))
    print('% outcomes with at least 30 days:', 100 * count_gte(durations, 30) / len(draws))
    print('% outcomes with at least 20 days:', 100 * count_gte(durations, 20) / len(draws))

# 48% of outcomes: 0 or 1 infection
# chance of at least: 40 days, 30 days, 20 days

def main():
    #print_hist()
    plot()

main()
