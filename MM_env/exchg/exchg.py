from .exchg_helper import Exchg_Helper
from .orderbook import OrderBook
from .trader import Trader

# The exchange environment
class Exchg(Exchg_Helper):
    def __init__(self, num_of_agents=2, init_cash=100, tape_display_length=10, max_step=100):
        self.LOB = OrderBook(0.25, tape_display_length) # limit order book
        self.LOB_STATE = {}
        self.LOB_NEXT_STATE = {}
        self.done_set = set()
        # list of agents or traders
        self.agents = [Trader(ID, init_cash) for ID in range(0, num_of_agents)]
        # step when actions by all traders are executed, not tick time
        # within a step, multiple trades(ticks) could happened
        self.t_step = 0
        self.max_step = max_step
        self.next_states = {}
        self.rewards = {}
        self.dones = {}
        self.infos = {}
        self.trades = {} # a trade between init_party & counter_party
        self.order_in_book = {} # unfilled orders goes to LOB

    # reset
    def reset(self, tape_display_length):
        self.LOB = OrderBook(0.25, tape_display_length) # new limit order book
        self.LOB_STATE = {}
        self.LOB_NEXT_STATE = {}
        self.t_step = 0
        self.next_states = {}
        self.rewards = {}
        self.trades = {} # a trade between init_party & counter_party
        self.order_in_book = {} # unfilled orders goes to LOB

        # ********** reset traders' accounts but keep the original traders **********

        return self.LOB_state()

    # actions is a list of actions from all agents (traders) at t step
    # each action is a list of (ID, type, side, size, price)
    def step(self, actions):
        self.next_states, self.rewards, self.dones, self.infos = {}, {}, {}, {}
        self.LOB_STATE = self.LOB_state() # LOB state at t before processing LOB
        actions = self.rand_exec_seq(actions, 0) # randomized traders execution sequence
        self.do_actions(actions) # Begin processing LOB
        self.mark_to_mkt() # mark to market
        # after processing LOB
        state_input = self.prep_next_state()
        self.next_states, self.rewards, self.dones, self.infos = self.set_step_outputs(state_input)
        self.t_step += 1
        return self.next_states, self.rewards, self.dones, self.infos

    # render
    def render(self):
        print('\nLOB:\n', self.LOB)
        print('\nLOB_STATE:\n', self.LOB_STATE)
        print('\nLOB_STATE_NEXT:\n', self.LOB_NEXT_STATE)
        print('\nnext_states (state_diff):\n', self.next_states)
        print('\nrewards:\n', self.rewards)
        self.print_accs()
        print('total_sys_profit:', self.total_sys_profit())
        print('total_sys_nav:', self.total_sys_nav())
        return 0
