"""
    This class extend the base Environment.
    It is used to iterate over the days of the campaign and to compute the reward obtained by the incoming users.
"""

import numpy as np

from project.dia_pckg.Environment import Environment


class Env_4(Environment):

    def __init__(self, initial_date, n_days, users_per_day, multi_class_handler, n_arms):
        """
        :param initial_date: when the campaign begins
        :param n_days: number of days of the campaign
        :param users_per_day: number of users per day
        :param multi_class_handler: MultiClassHandler object
        :param n_arms: number of arms of the Thomson Sampling algorithm
        """
        super().__init__(initial_date, n_days)

        self.round_per_day = users_per_day
        self.count_rounds_today = 0

        self.mch = multi_class_handler

        self.n_arms = n_arms
        self.arm_prices = self.get_candidate_prices()

        self.daily_pulled_arm = None

    def round(self, pulled_arm, user):
        """
            This method performs a round considering the number of steps per day
            Only after n rounds it perform a step in the implemented class
        :param pulled_arm: arm to pull
        :return: (reward, current date, done) done is a boolean -> True if the "game" is finished
        """
        reward, opt_revenue = self.one_user_round(pulled_arm, user)

        current_date = self.get_current_date()
        done = False
        new_day = False

        if self.count_rounds_today == self.round_per_day:
            self.count_rounds_today = 0
            current_date, done = self.step()
            new_day = True

        return reward, current_date, new_day, done, opt_revenue

    def one_user_round(self, pulled_arm, user):
        """
            This method performs a round taking the probability from the user's class
        :param pulled_arm: arm to pull
        :param user: User object
        :return: reward
        """
        self.count_rounds_today += 1
        # class of the user
        conv_rate = self.mch.get_class(class_name=user.class_name).conv_rates['phase_0']

        # taking the probability from the conversion curve, associated to the pulled_arm
        probability = conv_rate['probabilities'][self.arm_prices['indices'][pulled_arm]]
        opt = self.mch.get_optimal(class_name=user.class_name)
        optimal_revenue = opt['price'] * opt['probability']

        if probability < 0:
            probability = 1e-3
        reward = np.random.binomial(1, probability)
        return reward, optimal_revenue

    def reset(self):
        """
            to reset the environment
        :return: None
        """
        self.count_rounds_today = 0
        return super(Env_4, self).reset()

    def get_candidate_prices(self):
        """
            This method return the candidate prices, one price for each arm.
            The "indices" array contains the positions of the specified prices in the aggregate curve
        :return:
        """
        arm_distance = int(self.mch.aggregate_demand_curve['prices'].shape[0] / self.n_arms)
        idx = [int(arm_distance * arm) for arm in range(self.n_arms)]
        prices = self.mch.aggregate_demand_curve['prices'][idx]
        return {'indices': idx, 'prices': prices}
