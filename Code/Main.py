import pandas as pd
import GetResults_noOpt
import GetResults_PostOpt_Feasibility
import GetResults_PostOpt_BestAlgo
import Analysis_noOpt
import Analysis_PostOpt





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