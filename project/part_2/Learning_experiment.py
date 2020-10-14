import numpy as np
import pandas as pd

from project.part_2.Optimizer import fit_table
from project.part_2.Utils import get_idx_arm_from_allocation


def execute_experiment(args):
    learner = args['learner']
    env = args['environment']
    bids = args['bids']
    n_arms = args['n_arms']
    n_subcamp = args['n_subcamp']
    n_obs = args['n_obs']
    print_span = args['print_span']

    env.reset()
    first_day = True
    learners = []
    click_each_day = pd.DataFrame(columns=['bid_sub1', 'bid_sub2', 'bid_sub3', "click1", "click2", "click3"])

    for i in range(0, n_subcamp):
        if learner.__name__ == 'DLChangeDetect':
            dl_change_detect_min_len = args['dl_change_detect_min_len']
            dl_change_detect_test_stat = args['dl_change_detect_test_stat']
            learners.append(
                learner(n_arms, bids, min_len=dl_change_detect_min_len, test_stat=dl_change_detect_test_stat))
        else:
            learners.append(learner(n_arms, bids))

    for d in range(0, n_obs):
        if first_day:
            avg = 1 / len(env.subs)
            allocations = [avg, avg, avg]
            pulled = [get_idx_arm_from_allocation(allocation, bids) for allocation in allocations]

            first_day = False
        else:
            # uso l'algoritmo della tabella per selezionare gli arm che mi danno un reward massimo
            table_all_subs = np.ndarray(shape=(0, len(bids)), dtype=float)
            for l in learners:
                table_all_subs = np.append(table_all_subs, np.atleast_2d(l.means.T), 0)
            allocations = fit_table(table_all_subs)[0]
            # conversion to arm index
            pulled = [get_idx_arm_from_allocation(allocation, bids) for allocation in allocations]

        clicks = env.round(pulled)

        for x in range(0, n_subcamp):
            learners[x].update(pulled[x], clicks[x])

        click_each_day = click_each_day.append({
            'bid_sub1': pulled[0],
            'bid_sub2': pulled[1],
            'bid_sub3': pulled[2],
            "click1": clicks[0],
            "click2": clicks[1],
            "click3": clicks[2]
        }, ignore_index=True)

        if (d + 1) % print_span == 0:
            # TIME TO PRINT THE PLOTS
            # try:
            # for s in range(0, len(learners)):
            # learners[s].plot(env.subs[s])
            # except:
            #    print(f"not able to plot {learners[0].name}")
            print(f"DAY: {d}\nPULLED:{pulled}\nCLICKS: {clicks}\nTOT: {clicks.sum()}\n")

    return click_each_day, args
