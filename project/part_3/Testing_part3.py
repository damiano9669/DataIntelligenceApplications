import multiprocessing
from multiprocessing import Pool

import numpy as np

from project.dia_pckg.Config import *
from project.dia_pckg.plot_style.cb91visuals import *
from project.part_2.GPTS_Learner import GPTS_Learner as Learner
from project.part_2.Optimizer import fit_table
from project.part_3.AbruptBiddingEnvironment import AbruptBiddingEnvironment
from project.part_3.DLChangeDetect import DLChangeDetect
from project.part_3.DynamicLearner import DynamicLearner
from project.part_2.Learning_experiment import execute_experiment

np.random.seed(13337)

if __name__ == '__main__':
    bids = np.linspace(0, max_bid, n_arms)
    env = AbruptBiddingEnvironment(bids)

    args1 = {}
    args1['learner'] = Learner
    args1['environment'] = env
    args1['bids'] = bids
    args1['n_subcamp'] = n_subcamp
    args1['n_arms'] = n_arms
    args1['n_obs'] = n_days
    args1['print_span'] = print_span

    args2 = {}
    args2['learner'] = DynamicLearner
    args2['environment'] = env
    args2['bids'] = bids
    args2['n_subcamp'] = n_subcamp
    args2['n_arms'] = n_arms
    args2['n_obs'] = n_days
    args2['print_span'] = print_span

    args3 = {}
    args3['learner'] = DLChangeDetect
    args3['environment'] = env
    args3['bids'] = bids
    args3['n_subcamp'] = n_subcamp
    args3['n_arms'] = n_arms
    args3['n_obs'] = n_days
    args3['print_span'] = print_span

    with Pool(processes=multiprocessing.cpu_count()) as phase:
        basic_total_click_each_day, sw_total_click_each_day, dc_total_click_each_day = phase.map(execute_experiment,
                                                                                                 [args1, args2, args3])

    clicks_opt = np.array([])

    for phase in range(0, n_abrupts_phases):
        all_optimal_subs = np.ndarray(shape=(0, len(bids)), dtype=np.float32)
        for i in range(0, n_subcamp):
            all_optimal_subs = np.append(all_optimal_subs, np.atleast_2d(env.subs[i].means[f'phase_{phase}']), 0)
        opt = fit_table(all_optimal_subs)[1]
        for days in range(0, phase_len):
            clicks_opt = np.append(clicks_opt, opt)

    sw_clicks_obtained = sw_total_click_each_day["click1"] + \
                         sw_total_click_each_day["click2"] + \
                         sw_total_click_each_day["click3"]

    basic_clicks_obtained = basic_total_click_each_day["click1"] + \
                            basic_total_click_each_day["click2"] + \
                            basic_total_click_each_day["click3"]

    dc_clicks_obtained = dc_total_click_each_day["click1"] + \
                         dc_total_click_each_day["click2"] + \
                         dc_total_click_each_day["click3"]

    np.cumsum(clicks_opt - basic_clicks_obtained).plot(label="Without SW")
    np.cumsum(clicks_opt - sw_clicks_obtained).plot(label="Sliding Window")
    np.cumsum(clicks_opt - dc_clicks_obtained).plot(label="Change Detect")

    plt.legend(loc='lower right')
    plt.show()

    plt.show()

    print("SLIDING WINDOWS")
    print(np.sum(sw_clicks_obtained))

    print("\n\nWITHOUT SLIDING WINDOWS")
    print(np.sum(basic_clicks_obtained))

    print("\n\nCHANGE DETECT")
    print(np.sum(dc_clicks_obtained))
