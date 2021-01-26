import copy
from itertools import groupby

class SolutionDay(object):
    def __init__(self, dayNr):
        self.dayNumber = dayNr
        self.GivenNumberOfVehicles = None
        self.Vehicles = []
        self.givenStartDepot = None
        self.givenFinishDepot = None
        self.calcStartDepot = None
        self.calcFinishDepot = None

    def __str__(self):
        strRepr = 'Day: %d' % self.dayNumber
        if self.GivenNumberOfVehicles is not None:
            strRepr += '\tGnofV: %d' % self.GivenNumberOfVehicles
        if self.givenStartDepot is not None:
            strRepr += '\nGSD: %r' % self.givenStartDepot
        if self.givenFinishDepot is not None:
            strRepr += '\nGFD: %r' % self.givenFinishDepot
        if self.calcStartDepot is not None:
            strRepr += '\nCSD: %r' % self.calcStartDepot
        if self.calcFinishDepot is not None:
            strRepr += '\nCFD: %r' % self.calcFinishDepot
        strRepr += '\nVEHICLES:'
        for i in range(len(self.Vehicles)):
            strRepr += '\nVehicle: %d\n%s' % (i, str(self.Vehicles[i]))
        return strRepr

class SolutionVehicle(object):
    def __init__(self, route):
        self.Route = route
        self.routeDistance = None
        self.routeCost = None
        self.calcVisits = []
        self.depotVisits = []

    def __str__(self):
        return 'R: %r\nCD: %r\nCV: %r' % (
        self.Route, self.calcDistance, self.calcVisits)

    def calcDistance(self, instance):
        distance = 0
        if len(self.Route) == 3:
            distance = instance.calcDistance[0][instance.Requests[abs(self.Route[1]) -1].node] * 2

        else:
            for i in range(0, len(self.Route) - 1):

                if self.Route[i] == 0:
                    from_loc = 0
                else:
                    from_loc = instance.Requests[abs(self.Route[i]) - 1].node
                if self.Route[i + 1] == 0:
                    to_loc = 0
                else:
                    to_loc = instance.Requests[abs(self.Route[i + 1]) - 1].node
                distance += instance.calcDistance[from_loc][to_loc]

        self.routeDistance = 0 if distance > instance.MaxDistance else distance

    def calcRoutingCost(self, instance):
        # km cost
        # cost of tools taken from depot at start of day
        self.routeCost = self.routeDistance * instance.DistanceCost
        self.routeCost += sum([abs(self.depotVisits[0][t.ID - 1]) * t.cost for t in instance.Tools])

    def feasibility(self, instance):
        feasibleWeight, feasibleRoute = True, True

        self.calcDistance(instance)
        feasibleDistance = self.routeDistance > 0

        # Check capacity constraint
        toolSize = [t.weight for t in instance.Tools]
        lastNode = None
        currentTools = [0] * len(instance.Tools)
        depotVisits = [[0] * len(instance.Tools)]
        nodeVisits = []

        for node in self.Route:
            if node == 0:
                if lastNode is not None:
                    if lastNode == 0:
                        feasibleRoute = False
                    bringTools = [0] * len(instance.Tools)
                    sumTools = [0] * len(instance.Tools)
                    for tools in nodeVisits:
                        sumTools = [max(x) for x in zip(tools, sumTools)]
                        bringTools = [min(x) for x in zip(bringTools, tools)]
                        sumTools = [max(0, a) for a in sumTools]
                    depotVisits[-1] = [sum(x) for x in zip(bringTools, depotVisits[-1])]
                    loaded = sum([a * -b for a, b in zip(toolSize, depotVisits[-1])])
                    if loaded > instance.Capacity:
                        feasibleWeight = False
                    for tools in nodeVisits:
                        loaded = sum([a * (b - c) for a, b, c in zip(toolSize, tools, depotVisits[-1])])
                        if loaded > instance.Capacity:
                            feasibleWeight = False
                    depotVisits.append([b - a for a, b in zip(bringTools, nodeVisits[-1])])
                    currentTools = [0] * len(instance.Tools)
                    nodeVisits = []
            elif node > 0:
                currentTools[instance.Requests[node - 1].tool - 1] -= instance.Requests[node - 1].toolCount
            elif node < 0:
                node = - node
                currentTools[instance.Requests[node - 1].tool - 1] += instance.Requests[node - 1].toolCount
            nodeVisits.append(copy.copy(currentTools))
            lastNode = node
        self.depotVisits = depotVisits
        return feasibleDistance, feasibleWeight, feasibleRoute

    def remove_consecutive_depot_visits(self):
        self.Route = [r[0] for r in groupby(self.Route)]


class Solution(object):
    def __init__(self, routes):
        self.MaxNumberOfVehicles = None
        self.NumberOfVehicleDays = None
        self.Distance = None
        self.ToolCount = None
        self.Cost = None
        self.Days = routes
        self.Feasible = True

    def __str__(self):
        if not self.MaxNumberOfVehicles or not self.NumberOfVehicleDays or not self.Distance or not self.ToolCount or not self.Cost:
            return 'Max number of vehicles: %r\nNumber of vehicle days: %r\nDistance: %r\nCost: %r\nTool count: %r' % (
            self.MaxNumberOfVehicles, self.NumberOfVehicleDays, self.Distance, self.Cost, self.ToolCount)
        else:
            return 'Max number of vehicles: %d\nNumber of vehicle days: %d\nDistance: %d\nCost: %d\nTool count: %r' % (
            self.MaxNumberOfVehicles, self.NumberOfVehicleDays, self.Distance, self.Cost, self.ToolCount)


    def calc_solution(self, Instance):
        totalDistance = 0
        maxNumVehicles = 0
        dayNumVehicles = 0
        RequestDeliver = [None] * (len(Instance.Requests) + 1)
        RequestPickup = [None] * (len(Instance.Requests) + 1)
        toolUse = [0] * len(Instance.Tools)
        toolStatus = [0] * len(Instance.Tools)
        toolSize = [t.weight for t in Instance.Tools]

        for day in self.Days:
            day.calcStartDepot = [0] * len(Instance.Tools)
            day.calcFinishDepot = [0] * len(Instance.Tools)
            maxNumVehicles = max(maxNumVehicles, len(day.Vehicles))
            dayNumVehicles += len(day.Vehicles)
            day.GivenNumberOfVehicles = dayNumVehicles
            for i in range(0, len(day.Vehicles)):
                vehicle = day.Vehicles[i]
                distance = 0
                lastNode = None
                currentTools = [0] * len(Instance.Tools)
                depotVisits = [[0] * len(Instance.Tools)]
                nodeVisits = []
                for node in vehicle.Route:
                    if node == 0:
                        if lastNode is not None:
                            if lastNode == 0:
                                self.Feasible = False
                            bringTools = [0] * len(Instance.Tools)
                            sumTools = [0] * len(Instance.Tools)
                            for tools in nodeVisits:
                                sumTools = [max(x) for x in zip(tools, sumTools)]
                                bringTools = [min(x) for x in zip(bringTools, tools)]
                                sumTools = [max(0, a) for a in sumTools]
                            depotVisits[-1] = [sum(x) for x in zip(bringTools, depotVisits[-1])]

                            loaded = sum([a * -b for a, b in zip(toolSize, depotVisits[-1])])
                            if loaded > Instance.Capacity:
                                self.Feasible = False
                            for tools in nodeVisits:
                                loaded = sum([a * (b - c) for a, b, c in zip(toolSize, tools, depotVisits[-1])])
                                if loaded > Instance.Capacity:
                                    self.Feasible = False
                            depotVisits.append([b - a for a, b in zip(bringTools, nodeVisits[-1])])
                            currentTools = [0] * len(Instance.Tools)
                            nodeVisits = []
                    elif node > 0:

                        RequestDeliver[node] = day.dayNumber
                        currentTools[Instance.Requests[node - 1].tool - 1] -= Instance.Requests[
                            node - 1].toolCount
                    elif node < 0:
                        node = - node
                        RequestPickup[node] = day.dayNumber
                        currentTools[Instance.Requests[node - 1].tool - 1] += Instance.Requests[
                            node - 1].toolCount
                    nodeVisits.append(copy.copy(currentTools))
                    if lastNode is not None:
                        fromCoord = Instance.DepotCoordinate if lastNode == 0 else Instance.Requests[
                            lastNode - 1].node
                        toCoord = Instance.DepotCoordinate if node == 0 else Instance.Requests[
                            node - 1].node
                        distance += Instance.calcDistance[fromCoord][toCoord]
                    lastNode = node
                distance += Instance.calcDistance[toCoord][Instance.DepotCoordinate]
                if distance > Instance.MaxDistance:
                    self.Feasible = False
                vehicle.routeDistance = distance
                vehicle.calcVisits = depotVisits
                totalDistance += distance
                visitTotal = [0] * len(Instance.Tools)
                totalUsedAtStart = [0] * len(Instance.Tools)
                for visit in vehicle.calcVisits:
                    visitTotal = [sum(x) for x in zip(visit, visitTotal)]
                    totalUsedAtStart = [b - min(0, a) for a, b in zip(visitTotal, totalUsedAtStart)]
                    visitTotal = [max(0, a) for a in visitTotal]
                day.calcStartDepot = [b - a for a, b in zip(totalUsedAtStart, day.calcStartDepot)]
                day.calcFinishDepot = [b + a for a, b in zip(visitTotal, day.calcFinishDepot)]
            toolStatus = [sum(x) for x in zip(toolStatus, day.calcStartDepot)]
            toolUse = [max(-a, b) for a, b in zip(toolStatus, toolUse)]
            toolStatus = [sum(x) for x in zip(toolStatus, day.calcFinishDepot)]

            for i in range(len(Instance.Tools)):
                if toolUse[i] > Instance.Tools[i].amount:
                    self.Feasible = False

        self.MaxNumberOfVehicles = maxNumVehicles
        self.NumberOfVehicleDays = dayNumVehicles
        self.Distance = totalDistance
        self.ToolCount = toolUse

    def calc_cost(self, instance):
        cost = self.MaxNumberOfVehicles * instance.VehicleCost
        cost += self.NumberOfVehicleDays * instance.VehicleDayCost
        cost += self.Distance * instance.DistanceCost
        for i in range(len(instance.Tools)):
            cost += self.ToolCount[i] * instance.Tools[i].cost
        self.Cost = cost

    def write_solution(self, outputfile, instance,solution):

            output_days = []

            for day in solution.Days:
                output_days.append(
                    "DAY = " + str(day.dayNumber) + "\n" + "NUMBER_OF_VEHICLES = " + str(day.GivenNumberOfVehicles) + "\n")
                veh_counter = 1
                for vehicle in day.Vehicles:
                    output_days.append(str(veh_counter) + " R ")
                    output_days.append(" ".join(map(str, vehicle.Route)) + "\n")
                    veh_counter +=1
                output_days.append("\n")

            # Open outputfile
            file1 = open(outputfile, "w")
            output = ["DATASET = " + str(instance.Dataset) + "\n",
                      "NAME = " + str(instance.Name) + "\n \n",
                      "MAX_NUMBER_OF_VEHICLES = " + str(solution.MaxNumberOfVehicles) + "\n",
                      "NUMBER_OF_VEHICLE_DAYS = " + str(solution.NumberOfVehicleDays) + "\n",
                      "TOOL_USE = " + " ".join(str(x) for x in solution.ToolCount) + "\n",
                      "DISTANCE = " + str(solution.Distance) + "\n",
                      "COST = " + str(solution.Cost) + "\n \n"]

            # write output lines
            file1.writelines(output)
            file1.writelines(output_days)
            file1.close()  # to change file access modes
            return




