import numpy as np
import pandas as pd

from project.dia_pckg.plot_style.cb91visuals import *
from project.part_2.BiddingEnvironment import BiddingEnvironment
from project.part_2.GPTS_Learner import GPTS_Learner
from project.part_2.Optimizer import fit_table

# # EXPLORATION PHASE

np.random.seed(72)
n_obs = 100
n_obs_exploration = round(n_obs * 1 / 3)
n_obs_exploitation = n_obs - n_obs_exploration
n_subcamp = 3
max_bid = 1
max_clicks = 100
n_arms = 11

bids = np.linspace(0, max_bid, n_arms)
print(bids)

total_click_each_day = pd.DataFrame(columns=['bid_sub1', 'bid_sub2', 'bid_sub3', "click1", "click2", "click3"])

noise_std = 6.0
env = BiddingEnvironment(bids, max_clicks, noise_std)

all_optimal_subs = np.ndarray(shape=(0, len(bids)), dtype=float)
for i in range(0, n_subcamp):
    all_optimal_subs = np.append(all_optimal_subs, np.atleast_2d(env.subs[i](bids)), 0)
optimal_bids = fit_table(all_optimal_subs)[0]

learners = []
for i in range(0, n_subcamp):
    learners.append(GPTS_Learner(n_arms, bids))

for i in range(0, n_obs):
    clicks = []

    # Pull an arm for each sub-campaign:
    # It is pulled the arm belonging to the sub-campaign (i%3) which has the maximum variance
    # For the other 2 sub-campaigns the arm is pulled randomly (s.t. the sum = maximum)
    ### N.B. This behaviour works only for arms linearly distributed  over the array_bids
    first = i % 3
    pulled = [0, 0, 0]

    pulled[first] = learners[first].pull_arm_v2()
    pulled[(first + 1) % 3] = learners[(first + 1) % 3].pull_arm_v3(n_arms - pulled[first])
    pulled[(first + 2) % 3] = learners[(first + 2) % 3].pull_arm_v3(
        n_arms - pulled[first] - pulled[(first + 1) % 3] - 1)

    clicks = env.round(pulled[0], pulled[1], pulled[2])
    optimal_clicks = env.round(optimal_bids[0], optimal_bids[1], optimal_bids[2])

    for x in range(0, n_subcamp):
        learners[x].update(pulled[x], clicks[x])

        total_click_each_day = total_click_each_day.append({
            'bid_sub1': pulled[0],
            'bid_sub2': pulled[1],
            'bid_sub3': pulled[2],
            "click1": clicks[0],
            "click2": clicks[1],
            "click3": clicks[2]
        }, ignore_index=True)

    print(i)
    print('bid', pulled[0], 'clicks', clicks[0], 'optimal bid', optimal_bids[0], 'optimal clicks', optimal_clicks[0],
          'sigma sum', learners[0].get_sigma_sum(), '\n'
                                                    'bid', pulled[1], 'clicks', clicks[1], 'optimal bid',
          optimal_bids[1], 'optimal clicks', optimal_clicks[1], 'sigma sum', learners[1].get_sigma_sum(), '\n'
                                                                                                          'bid',
          pulled[2], 'clicks', clicks[2], 'optimal bid', optimal_bids[2], 'optimal clicks', optimal_clicks[2],
          'sigma sum', learners[2].get_sigma_sum(), '\n'
                                                    'regret', sum(optimal_clicks) - sum(clicks))

    if (learners[0].get_sigma_sum() < 70 and learners[1].get_sigma_sum() < 70 and learners[
        2].get_sigma_sum() < 70 and i > 0):
        break

    import time

    time.sleep(2)

    print()

for s in range(0, n_subcamp):
    learners[s].plot(env.subs[s])

table_all_Subs = np.ndarray(shape=(0, len(bids)), dtype=float)
for l in learners:
    table_all_Subs = np.append(table_all_Subs, np.atleast_2d(l.means.T), 0)

print(table_all_Subs)
best = fit_table(table_all_Subs)
print(best)

# ## Regret Computation

all_optimal_subs = np.ndarray(shape=(0, len(bids)), dtype=float)
for i in range(0, n_subcamp):
    all_optimal_subs = np.append(all_optimal_subs, np.atleast_2d(env.subs[i](bids)), 0)

print(all_optimal_subs)
print(fit_table(all_optimal_subs))

# list of the collected reward
rewards_per_experiment = []
opt = fit_table(all_optimal_subs)[1]
print(opt)

for i in range(0, n_obs):
    num_clicks_day_i = total_click_each_day.values[i][3] + total_click_each_day.values[i][4] + \
                       total_click_each_day.values[i][5]
    rewards_per_experiment.append(num_clicks_day_i)

plt.figure(0)
plt.ylabel("Regret")
plt.xlabel("t")
plt.plot(np.cumsum(opt - rewards_per_experiment, axis=0), 'r')
plt.show()