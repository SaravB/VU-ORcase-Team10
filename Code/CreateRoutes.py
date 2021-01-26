from CreateSolution import SolutionDay, SolutionVehicle


def make_day_routes_simplest(schedule):
    """
    Uses one vehicle for each pickup/delivery
    """
    day_schedules = [None] * len(schedule.schedulePerDay)
    for day, dayschedule in schedule.schedulePerDay.items():
        solutionDay = SolutionDay(day)
        for event in dayschedule:
            route = [0, event, 0]
            vehicle = SolutionVehicle(route)
            solutionDay.Vehicles.append(vehicle)

        day_schedules[day - 1] = solutionDay
    return day_schedules


def make_day_routes_simple(instance, schedule, data):
    """
    based on Bin-Packing algorithm
    1. sorts pickups/deliveries in order of decreasing weight
    2. for each day: fills vehicle with deliveries first,
        continues with pick-ups (if feasible) and then returns
        to depot, repeats as long as possible
    """

    data = data.sort_values("weight", ascending=False)
    day_schedules = [None] * len(schedule.schedulePerDay)

    for day, dayschedule in schedule.schedulePerDay.items():
        solutionDay = SolutionDay(day)
        pickUps = list(-data[data.pickupDay.eq(day)].index)
        deliveries = list(data[data.deliveryDay.eq(day)].index)
        requests = [deliveries, pickUps]
        new = True
        type = 0 # 0: deliveries 1: pick-ups

        while len(requests[0]) + len(requests[1]) > 0:
            events = requests[type]
            if len(events) == 0:
                type = abs(type - 1)
                continue
            request = events[0]
            if new:
                route = [0, 0]
            route = route[:-1] + [request] + route[-1:]
            newVehicle = SolutionVehicle(route)
            fD, fW, fR = newVehicle.feasibility(instance)

            if fD and fR:
                if fW:
                    del requests[type][0]
                    new = False
                else:
                    route = route[:-2] + route[-1:]
                    if type == 1:
                        route = route + [0]
                    if len(requests[abs(1 - type)]) > 0:
                        type = abs(1 - type)
                        continue
                    else:
                        new = True
            elif not fD:
                route = route[:-2] + route[-1:]
                new = True

            if new:
               solutionDay = close_vehicle(route, solutionDay)

        solutionDay = close_vehicle(route, solutionDay)
        day_schedules[day-1] = solutionDay

    return day_schedules


def close_vehicle(route, solutionDay):
    if route[-1] == route[-2]:
        del route[-1]
    vehicle = SolutionVehicle(route)
    solutionDay.Vehicles.append(vehicle)

    return solutionDay


def least_tools_fit(instance, current_vehicle, new_vehicle, i, current_best_vehicle, current_best_value, current_best_index):
    # new vehicle is feasible for distance, weight/capacity and route
    if current_best_vehicle is None or sum(new_vehicle.depotVisits[0]) > sum(current_best_vehicle.depotVisits[0]):
        # no min weight vehicle obtained yet
        # or new route takes less tools from depot
        return new_vehicle, new_vehicle.routeDistance - current_vehicle.routeDistance, i
    elif sum(new_vehicle.depotVisits[0]) == sum(current_best_vehicle.depotVisits[0]) and \
            current_best_value > new_vehicle.routeDistance - current_vehicle.routeDistance:
        # new route takes equal amount of tools as previous best option
        # but adds less distance to total
        return new_vehicle, new_vehicle.routeDistance - current_vehicle.routeDistance, i

    return current_best_vehicle, current_best_value, current_best_index


def cheapest_fit(instance, current_vehicle, new_vehicle, i, current_best_vehicle, current_best_value, current_best_index):
    new_vehicle.calcRoutingCost(instance)
    added_cost = new_vehicle.routeCost - current_vehicle.routeCost
    if current_best_vehicle is None or added_cost < current_best_value:
        return new_vehicle, added_cost, i

    return current_best_vehicle, current_best_value, current_best_index


def make_day_routes(instance, schedule, df, fitProcedure):
    day_schedules = [None] * len(schedule.schedulePerDay)
    sortedTools = sorted(instance.Tools, key=lambda x: x.weight, reverse=True)

    for day, dayschedule in schedule.schedulePerDay.items():
        day_schedule = SolutionDay(day)
        for t in sortedTools:
            df_perTool = df[df.toolID.eq(t.ID)]
            schedule_pertool = list(-df_perTool[df_perTool.pickupDay.eq(day)].index)+list(df_perTool[df_perTool.deliveryDay.eq(day)].index)

            for request in schedule_pertool:
                best_vehicle, best_value, best_index = None, 0, -1
                for i in range(len(day_schedule.Vehicles)):
                    current_vehicle = day_schedule.Vehicles[i]
                    for j in range(1, len(current_vehicle.Route)):
                        new_vehicle = SolutionVehicle(current_vehicle.Route[:-j] + [request] + current_vehicle.Route[-j:])
                        fd, fw, fr = new_vehicle.feasibility(instance)
                        if fd and fw and fr:
                            best_vehicle, best_value, best_index = fitProcedure(instance, current_vehicle, new_vehicle, i, best_vehicle, best_value, best_index)

                if best_vehicle is not None:
                    day_schedule.Vehicles[best_index] = best_vehicle
                else:
                    new_vehicle = SolutionVehicle([0, request, 0])
                    new_vehicle.feasibility(instance)
                    new_vehicle.calcRoutingCost(instance)
                    day_schedule.Vehicles.append(new_vehicle)

        day_schedule.Vehicles = combineRoutes(day_schedule.Vehicles, instance)
        day_schedules[day-1] = day_schedule

    return day_schedules


def combineRoutes(vehicles, instance):
    new_vehicles = []
    # while list not empty
    while vehicles:
        if len(vehicles) == 1 or \
                not (combine(vehicles, new_vehicles, instance, old_vehicle=vehicles[0], skip_depot=True) or
                     combine(vehicles, new_vehicles, instance, old_vehicle=vehicles[0], skip_depot=False)):
            new_vehicles.append(vehicles[0])
            del vehicles[0]

    return new_vehicles


def combine(vehicles, new_vehicles, instance, old_vehicle, skip_depot=False):
    combined = False
    for i in range(1, len(vehicles)):
        # -1 betekend zonder depot, omdat de depot ook aan het begin van de volgende route staat
        # zonder depot stop
        candidate_vehicle = SolutionVehicle(old_vehicle.Route[:-1] + vehicles[i].Route[skip_depot:])
        fd, fw, fr = candidate_vehicle.feasibility(instance)
        if fd and fw and fr:
            new_vehicles.append(candidate_vehicle)
            del vehicles[i]
            del vehicles[0]
            combined = True
            break

    return combined
