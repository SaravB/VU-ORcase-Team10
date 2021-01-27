import pandas as pd
import itertools
import CreateSchedule as CS
import CreateRoutes as CR
from GetResults_noOpt import instanceToData
from VerologCode.InstanceCVRPTWUI import InstanceCVRPTWUI
from CreateSolution import Solution
from PostOptimization import post_optimization


def main():
    instanceFolder = "Instances/"
    resultsFolder = "Results/"

    seed = 100

    scheduleTypes = ['s1', 's2', 's3']
    routingTypes = ['r1', 'r2', 'r3', 'r4']
    valueTypes = ['it', 'c']
    # it denotes the number of iterations needed to become feasible
    # c denotes the cost at the first feasible point

    instanceNames = ['r100d5', 'r100d10', 'r500d15', 'r1000d25', 'r1000d30']
    costTypes = list(range(1, 6))

    results_df = pd.DataFrame(data = None, index=pd.MultiIndex.from_product([instanceNames, costTypes]), columns=pd.MultiIndex.from_product([scheduleTypes, routingTypes, valueTypes]))

    for fn, ct in itertools.product(*[instanceNames, costTypes]):
        instanceFileName = "VeRoLog_" + fn + "_" + str(ct)

        instance = InstanceCVRPTWUI(instanceFolder + instanceFileName + ".txt", None)
        instance.calculateDistances()

        data = instanceToData(instance)
        last_st, feasibleSchedule = None, True
        for st, rt in itertools.product(*[scheduleTypes, routingTypes]):

            if st == last_st and not feasibleSchedule:
                continue

            last_st, feasibleSchedule = st, True

            # Create schedule
            schedule = None
            if st == 's1':
                schedule = CS.make_schedule_earliest_delivery(instance, data)
            elif st == 's2':
                schedule = CS.make_schedule_greedy(instance, data)
            elif st == 's3':
                schedule = CS.make_schedule_ILP(instance, data, seed=seed)

            # Check if schedule could get a feasible routing
            for t in instance.Tools:
                if schedule.max_daily_use[t.ID-1] > t.amount:
                    feasibleSchedule = False
                    break

            if not feasibleSchedule:
                continue

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

            if solution.Feasible:
                results_df.loc[fn, ct][st, rt, 'it'] = 0
                results_df.loc[fn, ct][st, rt, 'c'] = solution.Cost
                continue

            iterationSeed = seed
            # 15 times 10.000 iterations
            for ic in range(15):
                iterationSeed += 3
                solution, fc, cc = post_optimization(solution=solution, iterations=10000, instance=instance, log_progress=False, seed=iterationSeed)

                if solution.Feasible:
                    results_df.loc[fn, ct][st, rt, 'it'] = (ic+1)*10000
                    results_df.loc[fn, ct][st, rt, 'c'] = solution.Cost
                    break

        results_df.to_csv(resultsFolder + "Results_PostOpt_Feasibility.csv")


if __name__ == '__main__':
    main()



