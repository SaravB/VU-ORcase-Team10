import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import itertools


def main():
    data = pd.read_csv("Results/Results_noOpt.csv", header=[0, 1,2], index_col=[0,1])
    instanceNames = ['r100d5', 'r100d10', 'r500d15', 'r1000d25', 'r1000d30']
    costTypes = list(range(1, 6))

    scheduleTypes = ['s1', 's2', 's3']
    routingTypes = ['r1', 'r2', 'r3', 'r4']

    new_data = data

    for st, rt in itertools.product(*[scheduleTypes,routingTypes]):
        new_data.loc[data[st, rt, 'f'] == 0, (st, rt,['tu', 'vd', 'mnv', 'd', 'c'])] = None

    best = []
    algs = []

    for i in costTypes:
        for filename in instanceNames:
            costs = new_data.loc[filename, i][:,:,'c'].dropna()
            temp = costs.sort_values(ascending=True).head(3)
            algs += [st+rt for st, rt in temp.axes[0]]
            best.append([filename, i] +[st+rt for st, rt in temp.axes[0]])

    algs = sorted(set(algs))

    print(best)
    best_dict = {}
    for alg in algs:
        counts = np.zeros(5)
        for info in best:
            if len(info) >=3 and info[2] == alg:
                counts[info[1]-1] += 3
            if len(info) >=4 and info[3] == alg:
                counts[info[1] - 1] += 2
            if len(info) >=5 and info[4] == alg:
                counts[info[1] - 1] += 1
        best_dict[alg] = counts

    print(best_dict)

    df = pd.DataFrame(best_dict)
    algorithm_assignment = {}
    for i in range(0, 5):
        type = df.loc[i,:]
        algorithm_assignment[i + 1] = type.axes[0][type.argmax()]


    data = pd.read_csv("Results/Results_PostOpt_BestAlgo_Averages.csv", header=[0], index_col=[0, 1])
    print(data)

    idx = pd.IndexSlice
    i = 1

    for costType in costTypes:
        for filename in instanceNames:

            slice = data.loc[idx[filename, costType],idx[:]]
            max = slice.max()
            slice = (slice / max) * 100
            slice.plot(kind="line", fontsize = "15")

            #labels = ('0', '10.000', '20.000', '30.000', '40.000', '50.000', '60.000', '70.000', '80.000', '90.000', '100.000','110.000', '120.000', '130.000', '140.000', '150.000')

            #ind = np.arange(16)
            labels = ('0',"" ,"" , "","" , '50.000',"" ,"" , "","" ,   '100.000',"" ,"" , "","" ,  '150.000')

            ind = np.arange(16)
            plt.xticks(ind, labels, fontsize = "15")
            plt.xlabel("# of iterations", fontsize = "15" )
            plt.ylabel("% of initial cost", fontsize = "15")
            plt.title("Type " + str(costType) + ", algorithm " + algorithm_assignment[costType], fontsize = "20")
            plt.legend(instanceNames, fontsize = "10")

            if i % 5 == 0:
                plt.show()
            i += 1


if __name__ == '__main__':
    main()
