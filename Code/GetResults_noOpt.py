import pandas as pd
import itertools
import CreateSchedule as CS
import CreateRoutes as CR
from VerologCode.InstanceCVRPTWUI import InstanceCVRPTWUI
from CreateSolution import Solution


def instanceToData(instance):
    columnNames = ['toolID', 'toolCount', 'fromDay', 'toDay', 'numDays', 'weight']
    df = pd.DataFrame(data=None, index=None, columns=columnNames)
    for r in instance.Requests:
        df.loc[r.ID] = [r.tool, r.toolCount, r.fromDay, r.toDay, r.numDays, instance.Tools[r.tool-1].weight*r.toolCount]

    return df


def main():
    instanceFolder = "Instances/"
    resultsFolder = "Results/"

    scheduleTypes = ['s1', 's2', 's3']
    routingTypes = ['r1', 'r2', 'r3', 'r4']
    valueTypes = ['f', 'tu', 'vd', 'mnv', 'd', 'c']
    tuples = [t for t in itertools.product(*[['-'], ['f', 'tu']])] + [t for t in itertools.product(*[routingTypes, valueTypes])]
    column_tuples = [('-', '-', 'mtu')] + [(st, t[0], t[1]) for st, t in itertools.product(*[scheduleTypes, tuples])]
    # ('-', '-', 'mtu') is first column per file. This is max tool use for the instance
    # (st, '-', 'f') for each schedule type (st) whether it could be feasible based on tool use
    # (st, '-', 'tu') for each schedule type (st) how many tools are needed based on schedule (this is a list)
    # 'f' for each st&rt whether the solution is feasible
    # 'tu' tool use (this is a list)
    # 'vd' vehicle days
    # 'mnv' max number of vehicles
    # 'd' distance
    # 'c' cost

    instanceNames = ['r100d5', 'r100d10', 'r500d15', 'r1000d25', 'r1000d30']
    costTypes = list(range(1, 6))

    results_df = pd.DataFrame(data = None, index=pd.MultiIndex.from_product([instanceNames, costTypes]), columns=pd.MultiIndex.from_tuples(column_tuples))

    for fn, ct in itertools.product(*[instanceNames, costTypes]):
        instanceFileName = "VeRoLog_" + fn + "_" + str(ct)

        instance = InstanceCVRPTWUI(instanceFolder + instanceFileName + ".txt", None)
        instance.calculateDistances()

        results_df.loc[fn, ct]['-', '-', 'mtu'] = [t.amount for t in instance.Tools]

        data = instanceToData(instance)
        for st in scheduleTypes:
            # Create
            schedule = None
            feasibleSchedule = True
            if st == 's1':
                schedule = CS.make_schedule_earliest_delivery(instance, data)
            elif st == 's2':
                schedule = CS.make_schedule_greedy(instance, data)
            elif st == 's3':
                schedule = CS.make_schedule_ILP(instance, data, seed=100)

            # Check if schedule could get a feasible routing
            for t in instance.Tools:
                if schedule.max_daily_use[t.ID-1] > t.amount:
                    feasibleSchedule = False
                    break

            results_df.loc[fn, ct][st, '-', 'f'] = feasibleSchedule
            results_df.loc[fn, ct][st, '-', 'tu'] = list(schedule.max_daily_use)

            for rt in routingTypes:
                # Create routes
                routes = None
                if rt == 'r1':
                    routes = CR.make_day_routes_simplest(schedule)
                elif rt == 'r2':
                    routes = CR.make_day_routes_simple(instance, schedule, data)
                elif rt == 'r3':
                    routes = CR.make_day_routes(instance, schedule, data, CR.least_tools_fit)
                elif rt == 'r4':
                    routes = CR.make_day_routes(instance, schedule, data, CR.cheapest_fit)

                solution = Solution(routes)
                solution.calc_solution(instance)
                solution.calc_cost(instance)

                results_df.loc[fn, ct][st, rt, 'f'] = solution.Feasible
                results_df.loc[fn, ct][st, rt, 'tu'] = solution.ToolCount
                results_df.loc[fn, ct][st, rt, 'vd'] = solution.NumberOfVehicleDays
                results_df.loc[fn, ct][st, rt, 'mnv'] = solution.MaxNumberOfVehicles
                results_df.loc[fn, ct][st, rt, 'd'] = solution.Distance
                results_df.loc[fn, ct][st, rt, 'c'] = solution.Cost

            results_df.to_csv(resultsFolder + "Results_noOpt.csv")


if __name__ == '__main__':
    main()



