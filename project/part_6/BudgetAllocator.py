import numpy as np

from project.part_2.Optimizer import fit_table
from project.part_2.Utils import get_idx_arm_from_allocation
from project.part_6.MultiSubCampaignHandler import MultiSubCampaignHandler


class BudgetAllocator:
    """
    This class decides how much budget to allocate to each sub-campaign, using information collected in the past and
    solving the updated Knapsack problem
    """

    def __init__(self,
                 multi_class_handler,
                 n_arms_pricing,
                 n_arms_advertising,
                 enable_pricing=True,
                 keep_daily_price=False):
        """
        :param multi_class_handler:
        :param n_arms_pricing:
        :param n_arms_advertising:
        """
        self.msh = MultiSubCampaignHandler(multi_class_handler=multi_class_handler,
                                           n_arms_pricing=n_arms_pricing,
                                           n_arms_advertising=n_arms_advertising,
                                           keep_daily_price=keep_daily_price)

        self.enable_pricing = enable_pricing
        self.n_arms_pricing = self.msh.subcampaigns_handlers[0].pricing.n_arms
        self.n_arms_advertising = self.msh.subcampaigns_handlers[0].advertising.n_arms
        self.n_subcampaigns = len(self.msh.subcampaigns_handlers)

        # it has been moved to Testing_Env_6.py, after the initialization of the object.
        # self.best_allocation = self.day_zero_initialization()

        self.regret = [0]
        self.optimal_total_revenue = self.get_optimal_total_revenue()

    def day_zero_initialization(self):
        """
        At the very first day of the algorithm, allocations are initialized to an average value for each sub-campaign
        """
        avg = 1 / self.n_subcampaigns
        allocation = [avg, avg, avg]
        self.msh.update_all_subcampaign_handlers(allocation)
        return allocation

    def update(self):
        """
        This method retrieves the information we have collected so far and updates the table we use to solve the
        Knapsack problem
        """
        table_all_subs = np.ndarray(shape=(0, len(self.msh.subcampaigns_handlers[0].advertising.env.bids)),
                                    dtype=np.float32)

        for subcampaign_handler in self.msh.subcampaigns_handlers:
            learner_clicks = subcampaign_handler.get_updated_parameters()
            v = subcampaign_handler.campaign_value

            revenue_clicks = np.multiply(learner_clicks, v) if self.enable_pricing else learner_clicks

            table_all_subs = np.append(table_all_subs, np.atleast_2d(revenue_clicks.T), 0)

        # self.best_allocation = fit_table(table_all_subs)[0]
        self.best_allocation = np.asarray(fit_table(table_all_subs)[0])
        print('BEST ALLOCATION FOUND:', self.best_allocation)

        if round(sum(self.best_allocation), 3) != 1:
            raise Exception("Allocation unfeasible")

        # updates
        self.msh.update_all_subcampaign_handlers(self.best_allocation)
        self.regret.append(self.optimal_total_revenue - self.msh.daily_revenue)

    def get_optimal_total_revenue(self):
        """
            This function is to compute the total optimal revenue, for the computation of the non-agnostic regret.
            Note: the so called "agnostic" regret is the regret in which the optimal revenue
                is computed using the "optimal number of clicks",
                but the "optimal number of clicks" is NOT computed knowing the pricing.
                Below, we compute the "optimal number of clicks" using the pricing!
        """
        table_all_subs = np.ndarray(shape=(0, len(self.msh.subcampaigns_handlers[0].advertising.env.bids)),
                                    dtype=np.float32)

        # for loop to initialize the table with the product between the unknown curves and the optimal revenues
        for sub_idx, subcampaign_handler in enumerate(self.msh.subcampaigns_handlers):
            unknown_clicks_curve = subcampaign_handler.advertising.env.subs[sub_idx].means['phase_0']
            revenue_clicks = np.multiply(unknown_clicks_curve, subcampaign_handler.pricing.optimal_revenue)
            table_all_subs = np.append(table_all_subs, np.atleast_2d(revenue_clicks.T), 0)

        # computation of the optimal allocation
        optimal_allocation = fit_table(table_all_subs)[0]

        # Once we have computed the optimal allocation, we can compute the total revenue
        # using the pricing
        optimal_total_revenue = 0
        for sub_idx, (allocation, subcampaign_handler) in enumerate(zip(optimal_allocation,
                                                                        self.msh.subcampaigns_handlers)):
            hypothetical_pulled_arm = get_idx_arm_from_allocation(
                allocation=allocation,
                bids=self.msh.subcampaigns_handlers[0].advertising.env.bids)
            optimal_clicks = self.msh.bidding_environment.subs[sub_idx].means['phase_0'][hypothetical_pulled_arm]
            optimal_total_revenue += optimal_clicks * subcampaign_handler.pricing.optimal_revenue

        return optimal_total_revenue
