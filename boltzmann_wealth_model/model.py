import mesa
import random

def compute_gini(model):
    agent_wealths = [agent.wealth for agent in model.agents]
    N = len(agent_wealths)
    if N == 0 or sum(agent_wealths) == 0:
        return 0

    x = sorted(agent_wealths)
    B = sum(xi * (N - i) for i, xi in enumerate(x)) / (N * sum(x))
    return (1 + (1 / N) - 2 * B)


class BoltzmannWealthModel(mesa.Model):
    """A simple model of an economy where agents exchange currency at random.

    All the agents begin with one unit of currency, and each time step can give
    a unit of currency to another agent. Note how, over time, this produces a
    highly skewed distribution of wealth.
    """

    def __init__(self, N=100, width=10, height=10):
        super().__init__()
        self.num_agents = N
        self.schedule = mesa.time.RandomActivation(self)
        self.agents = []
        self.grid = mesa.space.MultiGrid(width, height, True)

        self.datacollector = mesa.DataCollector(
            model_reporters={"Gini": compute_gini}, agent_reporters={"Wealth": "wealth"}
        )
        # Create agents
        for _ in range(self.num_agents):
            a = MoneyAgent(self.next_id(), self)
            self.schedule.add(a)
            # Add the agent to a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

        self.datacollector = mesa.DataCollector(
            model_reporters={"Gini": compute_gini}, agent_reporters={"Wealth": "wealth"}
        )
        self.running = True
        self.datacollector.collect(self)

    def step(self):
        # self.agents.shuffle_do("step")
        # # collect data
        # self.datacollector.collect(self)
        self.datacollector.collect(self)
        self.schedule.step()

    def run_model(self, n):
        for i in range(n):
            self.step()


class MoneyAgent(mesa.Agent):
    """An agent with fixed initial wealth."""

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)#
        self.wealth = random.randint(1, 5) # set the value randomly
        self.color = self.set_color() # set color for agent

    # based on wealth defined color of agent
    def set_color(self):
        """Set agent color based on wealth."""
        if self.wealth <= 2:
            return "blue"
        elif self.wealth <= 5:
            return "green"
        return "red"

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

    def give_money(self):
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        cellmates.pop(cellmates.index(self))  # Ensure agent is not giving money to itself
        if len(cellmates) > 0 and self.wealth > 1: # only give money if wealth > 1
            other = self.random.choice(cellmates)
            other.wealth += 1
            self.wealth -= 1

    # new function for bonus
    def receive_bonus(self):
        """Receive a bonus for wealth greater than a certain threshold."""
        if self.wealth > 5:
            bonus = 2
            self.wealth += bonus

    def step(self):
        self.move()
        if self.wealth > 1: # only attempt to give money if wealth > 1
            self.give_money()
        self.receive_bonus()  # check for bonuses
        self.color = self.set_color()
        print(f"Agent {self.unique_id} has {self.wealth} wealth")

