import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import itertools


def main():
    instanceNames = ['r100d5', 'r100d10', 'r500d15', 'r1000d25', 'r1000d30']
    costTypes = list(range(1, 6))

    scheduleTypes = ['s1', 's2', 's3']
    routingTypes = ['r1', 'r2', 'r3', 'r4']

    data = pd.read_csv("Results/results_noOpt.csv", header=[0, 1,2], index_col=[0,1])
    new_data = data

    for st, rt in itertools.product(*[scheduleTypes,routingTypes]):
        new_data.loc[data[st, rt, 'f'] == 0, (st, rt,['tu', 'vd', 'mnv', 'd', 'c'])] = None

    def calc_ranking(new_data, letter, dictionary=False):
        best = []
        algs = []

        for i in costTypes:
            counts = np.zeros(5)
            for filename in instanceNames:
                costs = new_data.loc[filename, i][:,:, letter].dropna()
                temp = costs.sort_values(ascending=True).head(3)
                algs += [st+rt for st, rt in temp.axes[0]]
                best.append([filename, i] +[st+rt for st, rt in temp.axes[0]])

        algs = sorted(set(algs))

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

        df = pd.DataFrame(best_dict)

        if dictionary:
            return df.sum(), best_dict
        return df.sum()

    c, best_dict = calc_ranking(new_data, 'c', dictionary=True)

    keys = best_dict.keys()
    specs = ['tu', 'vd', 'mnv', 'd']
    df_algs = new_data['s1', 'r1', 'c'] # just a none column so we start with the right indices
    for key in keys:
        for spec in specs:
            df_algs = pd.concat([df_algs, new_data[key[:2], key[2:], spec]], axis=1)

    d = calc_ranking(df_algs, 'd')
    tu = calc_ranking(df_algs, 'tu')
    mnv = calc_ranking(df_algs, 'mnv')
    vd = calc_ranking(df_algs, 'vd')

    df = pd.concat([tu, vd, mnv, d, c], axis =1)
    df.columns = ['tool use', 'vehicle days', 'max number of vehicles', 'distance', 'cost']   # let op 'c'
    df = df.drop(['s2r3'])
    df = df.apply(lambda x: x*100/sum(x), axis=0)

    df.plot(kind="bar", stacked=False, rot=0)
    plt.title("Algorithm's performance on the different aspects")
    plt.ylabel('Rating')
    plt.xlabel('Best algorithms')
    plt.show()


if __name__ == '__main__':
    main()

