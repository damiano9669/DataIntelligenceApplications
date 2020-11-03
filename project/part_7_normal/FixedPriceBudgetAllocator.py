from project.dia_pckg.Config import *
from project.part_2.Utils import *
from project.part_7.FixedPriceBudgetAllocator import FixedPriceBudgetAllocator as fp_binomial
from project.part_7_normal.SubCampaignHandler import SubCampaignHandler


class FixedPriceBudgetAllocator(fp_binomial):

    def __init__(self,
                 artificial_noise_ADV,
                 artificial_noise_CR, multiclasshandler):
        """
        @param artificial_noise_ADV: how much exploration on the advertising learners
        @param artificial_noise_CR: how much exploration on the conversion rates learners
        @param multiclasshandler: classes information
        """
        super().__init__(artificial_noise_ADV, multiclasshandler)
        self.artificial_noise_CR = artificial_noise_CR

        self.n_updates = 0
        self.subcampaignHandlers = []

        for s in range(n_subcamp):
            self.subcampaignHandlers.append(
                SubCampaignHandler(list(classes_config.keys())[s], self.bids, self.prices, multiclasshandler))

    def complete_update(self, price, allocation, click_per_class, purchases_per_class):
        """
        get all the information of the past day and update the learners
        @param price: arm corresponding to the price of the day
        @param allocation: budget allocated on each sub-campaign
        @param click_per_class: click received on each sub-campaign
        @param purchases_per_class: purchases received from users from each class
        """
        # print(
        #     f"UPDATE price={price} "
        #     f"allocation_arms={list(allocation.values())} "
        #     f"clicks={click_per_class} "
        #     f"purch={list(purchases_per_class.values())}")
        for idx, subh in enumerate(self.subcampaignHandlers):
            subh.comlete_daily_update(price, allocation[subh.class_name], click_per_class[idx],
                                      purchases_per_class[subh.class_name])
        self.n_updates += 1

