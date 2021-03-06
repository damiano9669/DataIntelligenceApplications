from project.dia_pckg.Config import *
from project.part_2.Utils import *
from project.part_7.SubCampaignHandler import SubCampaignHandler


class FixedPriceBudgetAllocator:

    def __init__(self, artificial_noise_ADV, artificial_noise_CR, multiclasshandler):
        """
        @param artificial_noise_ADV: how much exploration on the advertising learners
        @param multiclasshandler: classes information
        """

        self.artificial_noise_ADV = artificial_noise_ADV
        self.artificial_noise_CR = artificial_noise_CR
        self.mch = multiclasshandler
        self.n_updates = 0
        self.subcampaignHandlers = []
        self.bids = np.linspace(0, max_bid, n_arms_advertising)
        self.prices = np.linspace(product_config["base_price"], product_config["max_price"], n_arms_pricing)

        for s in range(n_subcamp):
            self.subcampaignHandlers.append(
                SubCampaignHandler(list(classes_config.keys())[s], self.bids, self.prices, multiclasshandler))

    def pull_arm_price(self, arm_price, click_per_class):
        """
        takes the daily number of click and the price of the day and returns the number of purchases
        @param arm_price:
        @param click_per_class:
        @return:
        """
        rewards = {}
        for idx, subh in enumerate(self.subcampaignHandlers):
            rewards[subh.class_name] = subh.get_daily_reward(click_per_class[idx], arm_price)
        return rewards

    def update(self, allocation, click_per_class):
        """
        get the advertising information of the past day and update the learner
        @param allocation: budget allocated on each sub-campaign
        @param click_per_class: click received on each sub-campaign
        """
        # print(
        #     f"UPDATE "
        #     f"allocation_arms={list(allocation.values())} "
        #     f"clicks={click_per_class}")
        for idx, subh in enumerate(self.subcampaignHandlers):
            subh.daily_update(allocation[subh.class_name], click_per_class[idx])
        self.n_updates += 1

    def compute_best_allocation(self, arm_price):
        """
        Given an arm corresponding to a price compute the best budget allocation on each sub-campaign
        for each sub-campaign ask for the conversion rate and the estimated clicks for each budget allocation,
        use the optimizer to predict the best allocation
        @param arm_price: arm corresponding to a specific price
        @return: best allocation, expected purchases
        """
        table_all_subs = np.ndarray(shape=(0, n_arms_advertising),
                                    dtype=np.float32)

        for subh in self.subcampaignHandlers:
            estimated_cr = subh.get_estimated_cr(arm_price, self.artificial_noise_CR / self.n_updates)
            estimated_clicks = subh.get_estimated_clicks(self.artificial_noise_ADV / self.n_updates)
            estimated_purchases = estimated_clicks * estimated_cr
            table_all_subs = np.append(table_all_subs, np.atleast_2d(estimated_purchases.T), 0)

        result = fit_table(table_all_subs)
        return result

    def next_price(self):
        """
        Compute the best price based on the demand curves learned so far
        @return: the predicted best price
        """
        while self.n_updates < 2:  # n_arms_pricing:

            if self.n_updates > 0:
                allocation = self.compute_best_allocation(self.n_updates)[0]
            else:
                avg = 1 / n_subcamp
                allocation = [avg, avg, avg]
            allocation_x_class = {}
            for subh, c in zip(self.subcampaignHandlers, range(len(classes_config))):
                allocation_x_class[subh.class_name] = get_idx_arm_from_allocation(allocation[c], self.bids)
            return self.n_updates, allocation_x_class

        max_estimated_reward = -1
        final_allocation = []
        final_arm_price = -1
        for arm_price in range(n_arms_pricing):
            result = self.compute_best_allocation(arm_price)
            allocation_atprice = np.asarray(result[0])
            purch_atprice = result[1]
            if max_estimated_reward < purch_atprice * self.prices[arm_price]:
                max_estimated_reward = purch_atprice * self.prices[arm_price]
                final_allocation = allocation_atprice
                final_arm_price = arm_price
        allocation_x_class = {}
        for subh, c in zip(self.subcampaignHandlers, range(len(classes_config))):
            allocation_x_class[subh.class_name] = get_idx_arm_from_allocation(final_allocation[c], self.bids)
        return final_arm_price, allocation_x_class

    def compute_optimal_reward(self, biddingEnvironment, mch):
        """
        Given the bidding Environment with the exact budget-clicks curves and the multiCampaignHandler with the exact Price-ConversioneRate curves
        it compute the best allocation and price with the corresponding reward.
        @param biddingEnvironment: the Environment for the Advertising campaign
        @param mch: The handler with the information of each class demand curves
        @return: the optimal reward and the best price
        """
        optimal_reward = -1
        best_price = -1
        for arm_price in range(n_arms_pricing):
            table_all_subs = np.ndarray(shape=(0, n_arms_advertising), dtype=np.float32)
            for idx, subh in enumerate(self.subcampaignHandlers):
                cr = mch.get_conv_rate(subh.class_name, arm_price)
                clicks_x_budget = biddingEnvironment.get_optimal_clicks(idx)
                purchases_x_budget = clicks_x_budget * cr
                table_all_subs = np.append(table_all_subs, np.atleast_2d(purchases_x_budget.T), 0)

            result = fit_table(table_all_subs)
            purch_atprice = result[1]
            if optimal_reward < purch_atprice * self.prices[arm_price]:
                best_price = arm_price
                optimal_reward = purch_atprice * self.prices[arm_price]
        return optimal_reward, best_price
