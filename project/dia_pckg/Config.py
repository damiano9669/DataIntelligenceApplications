##########################################
#             Configurations             #
##########################################

# campaign
initial_date = '20200101'
n_days = 365

# Seller wallet and ambitions
seller_max_budget = 20000  # $
max_n_clicks = 1000
avg_users_per_day = 100  # this param must be changed after budget allocation available!

# one product to sell
product_config = {
    'name': 'shoes',
    'base_price': 100,
    'max_price': 500,
    'production_cost': 0
}

# features space
features_space = {
    'age': ['<30', '>30'],
    'profession': ['student', 'worker']
}

# three classes of users
classes_config = {
    'elegant': [1, 1],  # >30, worker
    'casual': [0, 0],  # <30, student
    'sports': [0, 1]  # <30, worker
}

# number of abrupt phases
n_abrupts_phases = 3
# directory to store the curves
demand_path = 'demand_curves'

# PART 3 CONFIG
multiple_len_window = [round(n_days/6)]#, round(n_days/3), round(2*n_days/3)]
min_lens = [10]
z_score = 2.58
phase_len = n_days // n_abrupts_phases
# Since n_abrupts_phases is odd and n_days could be even we add 1 to obtain equal phases
phase_len = phase_len + 1 if n_days % 2 == 0 else phase_len


n_subcamp = 3

max_bid = 1
n_arms_advertising = 21
n_arms_pricing = 21


noise_std = 0.05