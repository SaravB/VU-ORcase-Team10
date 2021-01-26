import numpy as np
import pyomo.environ as pyo


class ScheduledRequest:
    def __init__(self, request, deliveryDay=0):
        self.ID = request.ID
        self.deliveryDay = request.fromDay if deliveryDay == 0 else deliveryDay
        self.earliestPickUpDay = self.deliveryDay + request.numDays
        self.originalRequest = request


class Schedule:
    def __init__(self, instance):
        self.scheduledRequests = []
        self.schedulePerDay = {}
        self.max_daily_use = np.zeros(len(instance.Tools), dtype=int)

    def calc_max_use(self, instance):
        # max daily use berekenen door pick up day te zien als een dag waarop de tool beschikbaar is
        # Want dan haal je hem eerst op en geef je hem later af
        tracker = np.zeros((len(instance.Tools), instance.Days))
        for req in self.scheduledRequests:
            tracker[req.originalRequest.tool - 1][req.deliveryDay -1 : req.earliestPickUpDay-1] += req.originalRequest.toolCount

        for t, tool in enumerate(tracker):
            self.max_daily_use[t] = max(tool)

    def make_day_schedule(self):
        self.schedulePerDay = {}
        for sr in self.scheduledRequests:
            if sr.earliestPickUpDay in self.schedulePerDay:
                self.schedulePerDay[sr.earliestPickUpDay].append(-sr.ID)
            else:
                self.schedulePerDay[sr.earliestPickUpDay] = [-sr.ID]

            if sr.deliveryDay in self.schedulePerDay:
                self.schedulePerDay[sr.deliveryDay].append(sr.ID)
            else:
                self.schedulePerDay[sr.deliveryDay] = [sr.ID]


def make_schedule_earliest_delivery(instance, data):
    data['deliveryDay'] = data.fromDay
    data['pickupDay'] = data.deliveryDay + data.numDays

    schedule = Schedule(instance)
    schedule.scheduledRequests = [ScheduledRequest(r) for r in instance.Requests]
    schedule.calc_max_use(instance)
    schedule.make_day_schedule()

    return schedule


def make_schedule_greedy(instance, data):
    data['deliveryDay'] = None
    schedule = Schedule(instance)
    tool_use_days = np.zeros((instance.Days, len(instance.Tools)))
    schedule.scheduledRequests = []
    for r in instance.Requests:
        deliveryDay = r.fromDay if r.fromDay == r.toDay else r.fromDay + np.argmin(tool_use_days[r.fromDay - 1:r.toDay - 1, r.tool - 1])

        tool_use_days[deliveryDay - 1:deliveryDay + r.numDays, r.tool -1] += r.toolCount
        schedule.scheduledRequests.append(ScheduledRequest(r, deliveryDay))
        data.loc[r.ID, 'deliveryDay'] = deliveryDay

    schedule.scheduleLength = max([l.earliestPickUpDay for l in schedule.scheduledRequests])
    schedule.calc_max_use(instance)
    schedule.make_day_schedule()

    data['pickupDay'] = data.deliveryDay + data.numDays

    return schedule


def createModelForTool(maxDays, toolCount, data):
    m = pyo.ConcreteModel()
    m.i = pyo.Set(initialize = data.index.array)
    m.j = pyo.Set(initialize=range(1,maxDays+1))
    m.f = pyo.Param(m.i,    initialize=lambda m, i: data['fromDay'][i], within=pyo.PositiveIntegers)
    m.t = pyo.Param(m.i,    initialize=lambda m, i: data['toDay'][i], within=pyo.PositiveIntegers)
    m.tc = pyo.Param(m.i,   initialize=lambda m, i: data['toolCount'][i], within=pyo.PositiveIntegers)
    m.nd = pyo.Param(m.i,   initialize=lambda m, i: data['numDays'][i], within=pyo.PositiveIntegers)

    consecutiveDays = [(j-1,j) for j in range(1,maxDays+1)]

    m.x = pyo.Var(m.i, m.j, initialize=lambda m, i, j: m.f[i] == j,         domain=pyo.Binary)
    m.y = pyo.Var(m.i, m.j, initialize=lambda m, i, j: m.f[i]+m.nd[i] == j, domain=pyo.Binary)
    m.d = pyo.Var(m.i,      initialize=lambda m, i: m.f[i],                 domain=pyo.NonNegativeIntegers, bounds=lambda m, i: (m.f[i], m.t[i]))
    m.s = pyo.Var(range(maxDays+1),      initialize=0, domain=pyo.NonNegativeIntegers, bounds=(0, toolCount))

    m.delivery = pyo.Constraint(m.i, rule=lambda m, i: m.d[i]-sum(j*m.x[i,j] for j in m.j) == 0)
    m.oneDelivery = pyo.Constraint(m.i, rule=lambda m, i: sum(m.x[i, j] for j in m.j) == 1)
    m.pickup = pyo.Constraint(m.i, rule=lambda m, i: m.d[i]+m.nd[i]-sum(j*m.y[i,j] for j in m.j) == 0)
    m.onePickup = pyo.Constraint(m.i, rule=lambda m, i: sum(m.y[i, j] for j in m.j) == 1)
    m.stock = pyo.Constraint(consecutiveDays, rule = lambda m, j, k: m.s[j]+sum(m.tc[i]*(m.y[i,k]-m.x[i,k]) for i in m.i) == m.s[k])

    m.objective = pyo.Objective(expr = m.s[0], sense=pyo.minimize)
    return m


def make_schedule_ILP(instance, data, seed=10, log_progress=False):
    data['deliveryDay'] = None

    solver = pyo.SolverFactory('gurobi')
    solver.options['Seed'] = seed
    maxDays = instance.Days

    schedule = Schedule(instance)
    schedule.scheduledRequests = []
    for t in instance.Tools:
        maxToolCount, dataForToolType = t.amount, data[data.toolID.eq(t.ID)]
        model = createModelForTool(maxDays, maxToolCount, dataForToolType)
        result = solver.solve(model)

        if result.solver.termination_condition == pyo.TerminationCondition.optimal:
            if log_progress:
                print("toolID:", t.ID)
                print("maxTools:", maxToolCount, "resultToolcount:", model.s[0].value)
            for i in model.i:
                deliveryDay = int(model.d[i].value)
                request = instance.Requests[i - 1]
                schedule.scheduledRequests.append(ScheduledRequest(request, deliveryDay))
                data.loc[i, 'deliveryDay'] = deliveryDay
        else:
            print("Stopcondition:", result.solver.termination_condition)

    data['pickupDay'] = data.deliveryDay + data.numDays
    schedule.calc_max_use(instance)
    schedule.make_day_schedule()

    return schedule
