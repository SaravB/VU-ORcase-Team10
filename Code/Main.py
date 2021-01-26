import GetResults_noOpt
import GetResults_PostOpt_Feasibility
import GetResults_PostOpt_BestAlgo
import Analysis_noOpt
import Analysis_PostOpt
import CreateSchedule as CS
import CreateRoutes as CR
import PostOptimization as PO
from VerologCode.InstanceCVRPTWUI import InstanceCVRPTWUI
from VerologCode.SolutionCVRPTWUI import SolutionCVRPTWUI


def getSolutionForInstance(instanceName, scheduleType, routingType, postoptIterations, seed=100):
    # scheduleType can be:
    #   - 's1': schedule each request at earliest delivery
    #   - 's2': schedule based on least tool usage
    #   - 's3': schedule calculated by ILP

    # routingType can be:
    #   - 'r1': each request gets it's own route/vehicle
    #   - 'r2': next fit routing
    #   - 'r3': best fit routing, where best fit has least tools and least added kilometers
    #   - 'r4': best fit routing, where best fit has least added cost

    instanceFolder = "Instances/"
    instance = InstanceCVRPTWUI(instanceFolder + instanceName + ".txt", None)
    instance.calculateDistances()
    df = GetResults_noOpt.instanceToData(instance)

    # Create schedule
    schedule = None
    if scheduleType == 's1':
        schedule = CS.make_schedule_earliest_delivery(instance, df)
    elif scheduleType == 's2':
        schedule = CS.make_schedule_greedy(instance, df)
    elif scheduleType == 's3':
        schedule = CS.make_schedule_ILP(instance, df, seed=seed)


    # Create routes
    routes = None
    if routingType == 'r1':
        routes = CR.make_day_routes_simplest(schedule)
    elif routingType == 'r2':
        routes = CR.make_day_routes_simple(instance, schedule, df)
    elif routingType == 'r3':
        routes = CR.make_day_routes(instance, schedule, df, CR.least_tools_fit)
    elif routingType == 'r4':
        routes = CR.make_day_routes(instance, schedule, df, CR.cheapest_fit)

    solution = CS.Solution(routes)
    solution.calc_solution(instance)
    solution.calc_cost(instance)

    if postoptIterations > 0:
        solution, _, _ = PO.post_optimization(solution=solution, iterations=postoptIterations, instance=instance, seed=seed)

    resultsFolder = "Results/"
    solution.write_solution(resultsFolder + "Solution_" + instanceName + ".txt", instance, solution)
    checkCalculations = SolutionCVRPTWUI(resultsFolder + "Solution_" + instanceName + ".txt", instance, continueOnErr=True)

    # solution contains costs as calculated by our code
    # checkCalculations contains the costs and error report as calculated by the Solution validator script from https://verolog2017.ortec.com/downloads
    return solution, checkCalculations


def main():
    # Run all algorithm combinations on all instances
    GetResults_noOpt.main()

    # Try to make all algorithms feasible with postOpt
    GetResults_PostOpt_Feasibility.main()

    # Get results with best algorithms for cost types for post-opt analysis
    GetResults_PostOpt_BestAlgo.main()

    # Make graphs for analysis of the algorithm combinations
    Analysis_noOpt.main()

    # Make graphs for analysis of the algorithm combinations
    Analysis_PostOpt.main()


if __name__ == '__main__':
    main()
