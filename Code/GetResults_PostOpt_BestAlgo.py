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

    base_seed = 100

    iterationCounts = list(range(10, 160, 10))

    instanceNames = ['r100d5', 'r100d10', 'r500d15', 'r1000d25', 'r1000d30']
    costTypes = list(range(1, 6))

    results_df = pd.DataFrame(data = 0.0, index=pd.MultiIndex.from_product([instanceNames, costTypes]), columns=[0] + iterationCounts)

    # run the whole thing 15 times and take averages
    for i in range(15):
        seed = (i+1)*base_seed

        for fn, ct in itertools.product(*[instanceNames, costTypes]):
            instanceFileName = "VeRoLog_" + fn + "_" + str(ct)

            instance = InstanceCVRPTWUI(instanceFolder + instanceFileName + ".txt", None)
            instance.calculateDistances()

            data = instanceToData(instance)

            # Create schedule
            schedule = CS.make_schedule_ILP(instance, data, seed=seed)

            # Create routes
            # Only file type 3 uses a different routing algorithm
            if ct == 3:
                routes = CR.make_day_routes(instance, schedule, data, CR.least_tools_fit)
            else:
                routes = CR.make_day_routes(instance, schedule, data, CR.cheapest_fit)

            solution = Solution(routes)
            solution.calc_solution(instance)
            solution.calc_cost(instance)

            results_df.loc[fn, ct][0] = (results_df.loc[fn, ct][0] * i + solution.Cost) / (i + 1)

            iterationSeed = seed
            for ic in iterationCounts:
                iterationSeed += 3
                solution, _, _ = post_optimization(solution=solution, iterations=10000, instance=instance, log_progress=False, seed=iterationSeed)

                results_df.loc[fn, ct][ic] = (results_df.loc[fn, ct][ic] * i + solution.Cost) / (i + 1)

        if i == 0:
            results_df.to_csv(resultsFolder + "Results_PostOpt_BestAlgo.csv")
        else:
            results_df.to_csv(resultsFolder + "Results_PostOpt_BestAlgo_Averages.csv")


if __name__ == '__main__':
    main()



