import copy
import random
from CreateSolution import Solution, SolutionVehicle


def post_optimization(solution, iterations, instance, onlySameRoute=False, onlyMove=False, maxOne=False, seed=13, log_progress=False):
    random.seed(seed)
    feasibleCount = changeCount = 0

    # Print original solution cost
    oldCost = copy.deepcopy(solution.Cost)
    if log_progress:
        print("First solution", solution.Cost)

    # Post optimization changes occur on one day (from either 1 vehicle route or 2 vehicle routes)
    all_days = list(range(1, len(solution.Days) + 1))

    for i in range(iterations):
    # Find random day
        foundRandomDay = False
        while foundRandomDay is False:
            day = random.choice(all_days)  # choose random day
            if len(solution.Days[day -1].Vehicles) > 1 or len(solution.Days[day -1].Vehicles[0].Route) > 3:
                foundRandomDay = True

        # Swap candidate
        vehicle1, vehicle2, candidateRoute1, candidateRoute2 = move_block(day, solution, onlySameRoute, onlyMove, maxOne)

        vehicle1Candidate = checkCandidate(candidateRoute1, instance)
        vehicle2Candidate = checkCandidate(candidateRoute2, instance)


        # Update solution if feasible and lower cost
        if vehicle1Candidate is not None and vehicle2Candidate is not None:
            routesPerDayCandidate = copy.deepcopy(solution.Days)
            if candidateRoute2 is None:
                # it's a swap/move within one vehicle
                routesPerDayCandidate[day-1].Vehicles[vehicle1] = vehicle1Candidate
            elif vehicle1Candidate != 0 and vehicle2Candidate != 0:
                routesPerDayCandidate[day-1].Vehicles[vehicle1] = vehicle1Candidate
                routesPerDayCandidate[day-1].Vehicles[vehicle2] = vehicle2Candidate
            elif vehicle1Candidate == 0:
                # vehicle1 ends up with empty route, it should be deleted
                routesPerDayCandidate[day-1].Vehicles[vehicle2] = vehicle2Candidate
                del routesPerDayCandidate[day-1].Vehicles[vehicle1]
            elif vehicle2Candidate == 0:
                # vehicle2 ends up with empty route, it should be deleted
                routesPerDayCandidate[day-1].Vehicles[vehicle1] = vehicle1Candidate
                del routesPerDayCandidate[day-1].Vehicles[vehicle2]

            solutionCandidate = Solution(routesPerDayCandidate)
            solutionCandidate.calc_solution(instance)
            solutionCandidate.calc_cost(instance)

            if not solution.Feasible or solutionCandidate.Feasible:
                feasibleCount += 1
                if solution.Cost > solutionCandidate.Cost:
                    changeCount += 1
                    solution = copy.deepcopy(solutionCandidate)

        if log_progress and i% 10000 == 9999:
            print("iteration", i+1," ", solution.Cost, "feasiblecount", feasibleCount, "changecount", changeCount)
            feasibleCount = changeCount = 0

    if log_progress:
        print("Solution improved with ", round(((oldCost- solution.Cost)/oldCost)*100, 2) , "%")

    return solution, feasibleCount, changeCount


def checkCandidate(route, instance):
    if route is None:
        return -1
    if len(route) > 2:
        vehicleCandidate = SolutionVehicle(route)
        f1, f2 , f3 = vehicleCandidate.feasibility(instance)
        if not f3:
            vehicleCandidate.remove_consecutive_depot_visits()
            if len(vehicleCandidate.Route) < 3:
                return 0

        return vehicleCandidate if f1 and f2 else None

    return 0


def move_block(day, solution, onlySameRoute=False, onlyMove=False, maxOne=False):
    # if onlySameRoute = True, the second vehicle will be the same as first
    # if onlyMove = True, the length of the routepart to swap will be 0 for the second vehicle
    # if maxOne = True, the length of both routeparts can be zero or 1 (it will be a move or swap of 1 request)
    solution_day = solution.Days[day - 1]
    number_of_vehicles = len(solution_day.Vehicles)
    candidateRoute1 = candidateRoute2 = None

    vehicle1, vehicle2, i1, i2 = 0, 0, 0, 0
    # Find random vehicles and event indices
    while candidateRoute1 is None:
        vehicle1 = random.choice(range(0, number_of_vehicles))
        route1 = solution_day.Vehicles[vehicle1].Route
        rl1 = len(route1)
        i1 = random.choice(range(1, rl1 -1))
        bl1 = random.choice(range(0, 2 if maxOne else rl1 - i1))

        vehicle2 = vehicle1 if onlySameRoute else random.choice(range(0, number_of_vehicles))
        route2 = solution_day.Vehicles[vehicle2].Route
        rl2 = len(route2)
        i2 = random.choice(range(1, rl2 -1))
        bl2 = 0 if onlyMove else random.choice(range(0, 2 if maxOne else rl2 - i2))

        if vehicle1 == vehicle2:
            if i1 == i2 or rl1 == 3:
                #nothing to swap
                continue
            if i1+bl1 <= i2:
                candidateRoute1 = route1[:i1] + route1[i2:i2+bl2] + route1[i1+bl1:i2] + route1[i1:i1+bl1] + route1[i2+bl2:]
            elif i2+bl2 <= i1:
                candidateRoute1 = route1[:i2] + route1[i1:i1+bl1] + route1[i2+bl2:i1] + route1[i2:i2+bl2] + route1[i1+bl1:]

            # overlap of route parts

        elif route2[i2:i2 + bl2] != route1[i1:i1 + bl1]:  # this is only the same if both only contain the depot, or both are empty
            candidateRoute1 = route1[:i1] + route2[i2:i2+bl2] + route1[i1+bl1:]
            candidateRoute2 = route2[:i2] + route1[i1:i1+bl1] + route2[i2+bl2:]

    return vehicle1, vehicle2, candidateRoute1, candidateRoute2
