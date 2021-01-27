# VU-ORcase-Team10
VeRoLog 2017
Sara van Bezooijen, Kim van den Houten, Finnbar van Lennep

In this repository we will present our code and results to an optimisation problem, namely the VeRoLog Solver Challenge2016-2017.The challenge is a simplification of a real-life problem encountered by a cattle improvement company. We assume the reader is already acquainted with the challenge, rather than reiterating the full problem description we refer to.
The main objective is to minimise the cost while serving all requests. There are four different types of costs, namely: costs per distance traveled, costs for using a vehicle for a day, costs for using a vehicle at all and costs for each tool type. The complexity of the problem lies in finding an algorithm that is able to minimise the cost for a variety of problem instances, where each problem instance emphasises a different type of cost.  
This type of vehicle routing problem has not been studied extensively in the literature. Nonetheless, since the end of the challenge a few papers have been published on this topic. We identified two main ways of approaching the problem. Both approaches made a distinction between scheduling and routing, the difference of the two methods lies within the order of solving the problem. Since the approach that first solves the scheduling part and then solves the routing part yielded a solution of higher quality, we used this approach as the basis for our algorithm.
  
For the scheduling and routing part we constructed multiple algorithms, varying in complexity. For the scheduling part we defined: an earliest delivery algorithm, a greedy algorithm and an integer linear program. For the routing part we experimented with the following algorithms: one vehicle per request algorithm, Next Fit algorithm, Best Fit cost algorithm and a Best Fit tools algorithm. With these algorithms we could make different combinations. Regardless of the combination chosen, the final stage in our algorithm was the post-optimisation stage. In this stage the routes found were further improved by randomly selecting improvement heuristics. 

Files:
- **Report.pdf**                        results of our research and calculations
- **Code**                              folder containing all code
  - **Instances**                           folder containing text files for all instances used
  - **Results**                             csv files as produced by our code and used in the report
    - **Results_noOpt.csv**                     csv for our analysis before postopt is used
    - **Results_PostOpt_Feasibility.csv**       csv for our analysis of feasibility before and after postopt
    - **Results_PostOpt_BestAlgo_Averages.csv** csv for our analysis of postopt on the best algorithms per instance (averages of 15 runs with different seeds)
    - **Results_PostOpt_BestAlgo.csv**          csv for our analysis of ranking results
  - **Solutions**                           folder in which solution files are written when getSolutionForInstance from Main.py is used
  - **VerologCode**                         folder containing the code as used from verolog
  - **Main.py**                             run this to get all results as used in the report. Also contains method getSolutionForInstance, with which you can run a specific algorithm with a specific number of postopt iterations
  - **CreateSchedule.py**                   methods to make the schedule with different algorithms
  - **CreateRoutes.py**                     methods to make the routing based on the predetermines schedule with different algorithms
  - **CreateSolution.py**                   methods to make and validate the solutions (partly copied from Verolog code)
  - **PostOptimization.py**                 method to improve the found solution
  - **GetResults_noOpt.py**                 method to get and write the results in csv for our analysis before postopt is used
  - **GetResults_PostOpt_Feasibility.py**   method to get and write the results in csv for our analysis of feasibility before and after postopt
  - **GetResults_PostOpt_BestAlgo.py**      method to get and write the results in csv for our analysis of postopt on the best algorithms per instance
  - **Analysis_noOpt.py**                   method to get the graphs for our analysis before postopt is used
  - **Analysis_PostOpt.py**                 method to get the graphs for our analysis of postopt on the best algorithms per instance
