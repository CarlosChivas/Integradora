# Util
import random
import time

# Model
import agentpy as ap
import matplotlib.animation

# Visualization
import matplotlib.pyplot as plt
import IPython

# Server
import client

VALID_MOVES = {
    'RIGHT': (0, 1),
    'DOWN': (1, 0)
}

position = 0

GREEN = 1
YELLOW = 2
RED = 3
BLUE = 4

COLOR_STRINGS = {
    GREEN: 'GREEN',
    YELLOW: 'YELLOW',
    RED: 'RED',
    BLUE: 'BLUE'
}


class Car(ap.Agent):
    def setup(self):
        self.dir = random.choice(list(VALID_MOVES.keys()))
        self.color = BLUE
        self.type = 'CAR'

    def get_dir(self):
        return VALID_MOVES[self.dir] if random.uniform(0, 1) > 0.1 else (0, 0)

    def get_dir_name(self):
        return self.dir


class TrafficLight(ap.Agent):
    def setup(self):
        global position
        self.color = YELLOW
        self.type = 'TRAFFIC_LIGHT'
        self.pos = position
        position += 1


class Interseccion(ap.Model):

    def add_car(self):
        self.new_car = ap.AgentList(self, 1, Car)

        start_positions = {
            'LEFT': (self.v_pos, 0),
            'UP1': (0, self.h_pos),
            'UP2': (0, self.h_pos * 2)
        }

        for car in self.new_car:
            dir_name = car.get_dir_name()

            if dir_name == 'RIGHT':
                position = [start_positions['LEFT']]
            elif dir_name == 'DOWN':
                position = [start_positions['UP1']] if random.random() < 0.5 else [start_positions['UP2']]

        self.grid.add_agents(self.new_car, position)
        self.car_count += 1

        # Add to database
        car = list(self.new_car)[0]
        car_id = car.id
        position = self.grid.positions[car]
        self.client.add_car(car_id, position)

    def check_car_horizontal(self, a, b):
        started = False
        for neighbor in self.grid.neighbors(self.semaforos[a]):
            semaforo_pos = self.grid.positions[self.semaforos[a]]
            if self.grid.positions[neighbor][1] == semaforo_pos[1] - 1:
                self.semaforos[a].color = GREEN
                self.client.update_traffic_light(self.semaforos[a].id, COLOR_STRINGS[self.semaforos[a].color])
                self.semaforos[b].color = RED
                self.client.update_traffic_light(self.semaforos[b].id, COLOR_STRINGS[self.semaforos[b].color])
                self.duracion_semaforo = self.p.duracion_semaforo
                self.duracion_semaforo2 = self.p.duracion_semaforo
                started = True

        return started

    def check_car_vertical(self, a, b):
        started = False
        for neighbor in self.grid.neighbors(self.semaforos[b]):
            semaforo_pos = self.grid.positions[self.semaforos[b]]
            if self.grid.positions[neighbor][0] == semaforo_pos[0] - 1:
                self.semaforos[b].color = GREEN
                self.client.update_traffic_light(self.semaforos[b].id, COLOR_STRINGS[self.semaforos[b].color])
                self.semaforos[a].color = RED
                self.client.update_traffic_light(self.semaforos[a].id, COLOR_STRINGS[self.semaforos[a].color])
                self.duracion_semaforo = self.p.duracion_semaforo
                self.duracion_semaforo2 = self.p.duracion_semaforo
                started = True

        return started

    def setup(self):

        self.client = client.Client("https://testappagent.us-south.cf.appdomain.cloud/")

        # Create streets
        street_length = self.street_length = self.p.size
        self.h_pos = street_length // 3
        self.v_pos = street_length // 2

        # Create lights

        self.semaforos = ap.AgentList(self, 4, TrafficLight)
        self.status_semaforos = False
        posiciones_semaforos = [(self.v_pos, self.h_pos - 1), (self.v_pos - 1, self.h_pos),
                                (self.v_pos, 2 * self.h_pos - 1), (self.v_pos - 1, 2 * self.h_pos)]
        nombres_semaforos = ['A', 'B', 'C', 'D']

        # semaforos[0]: horizontal
        # semaforos[1]: vertical

        i = 0
        for semaforo in self.semaforos:
            self.client.add_traffic_light(semaforo.id, COLOR_STRINGS[semaforo.color], nombres_semaforos[i])
            i += 1

        # Create grid (calles)
        self.grid = ap.Grid(self, (self.p.size, self.p.size), track_empty=True)
        self.grid.add_agents(self.semaforos, posiciones_semaforos)

        # Counters
        self.step_count = 0
        self.car_count = 0
        # self.duracion_semaforo = self.p.duracion_semaforo

    def step(self):
        if self.car_count < self.p.n_cars:
            self.add_car()

        """
        1. verificar si uno no está amarillo
        2. encontrar verde
        3. esperar 5 segundos
        4. verificar si el otro semáforo tiene carros en espera
                si: otro semáforo cambia a verde
                no: los dos amarillos
        """
        if self.semaforos[0].color == YELLOW and self.semaforos[1].color == YELLOW:
            started = self.check_car_horizontal(0, 1)
            if not started:
                started = self.check_car_vertical(0, 1)

        elif self.semaforos[0].color == GREEN:
            self.duracion_semaforo -= 1
            if self.duracion_semaforo == 0:
                if not self.check_car_vertical(0, 1):
                    self.semaforos[0].color = YELLOW
                    self.client.update_traffic_light(self.semaforos[0].id, COLOR_STRINGS[self.semaforos[0].color])
                    self.semaforos[1].color = YELLOW
                    self.client.update_traffic_light(self.semaforos[1].id, COLOR_STRINGS[self.semaforos[1].color])

        elif self.semaforos[1].color == GREEN:
            self.duracion_semaforo -= 1
            if self.duracion_semaforo == 0:
                if not self.check_car_horizontal(0, 1):
                    self.semaforos[0].color = YELLOW
                    self.client.update_traffic_light(self.semaforos[0].id, COLOR_STRINGS[self.semaforos[0].color])
                    self.semaforos[1].color = YELLOW
                    self.client.update_traffic_light(self.semaforos[1].id, COLOR_STRINGS[self.semaforos[1].color])

        if self.semaforos[2].color == YELLOW and self.semaforos[3].color == YELLOW:
            started = self.check_car_horizontal(2, 3)
            if not started:
                started = self.check_car_vertical(2, 3)

        elif self.semaforos[2].color == GREEN:
            self.duracion_semaforo2 -= 1
            if self.duracion_semaforo2 == 0:
                if not self.check_car_vertical(2, 3):
                    self.semaforos[2].color = YELLOW
                    self.client.update_traffic_light(self.semaforos[2].id, COLOR_STRINGS[self.semaforos[2].color])
                    self.semaforos[3].color = YELLOW
                    self.client.update_traffic_light(self.semaforos[3].id, COLOR_STRINGS[self.semaforos[3].color])

        elif self.semaforos[3].color == GREEN:
            self.duracion_semaforo2 -= 1
            if self.duracion_semaforo2 == 0:
                if not self.check_car_vertical(2, 3):
                    self.semaforos[2].color = YELLOW
                    self.client.update_traffic_light(self.semaforos[2].id, COLOR_STRINGS[self.semaforos[2].color])
                    self.semaforos[3].color = YELLOW
                    self.client.update_traffic_light(self.semaforos[3].id, COLOR_STRINGS[self.semaforos[3].color])

        for agent in list(self.grid.agents):
            agent_pos = self.grid.positions[agent]
            move = True
            if agent.type == 'CAR':
                for neighbor in self.grid.neighbors(agent):
                    if agent.get_dir_name() == 'RIGHT':
                        # si el vecino es el de uno en frente y corresponde a la misma calle (posición vertical)
                        if self.grid.positions[neighbor][1] == agent_pos[1] + 1 and self.grid.positions[neighbor][0] == \
                                agent_pos[0]:
                            if (neighbor.type == 'TRAFFIC_LIGHT' and neighbor.color == RED) or neighbor.type == 'CAR':
                                move = False
                                break
                    elif agent.get_dir_name() == 'DOWN':
                        if self.grid.positions[neighbor][0] == agent_pos[0] + 1 and self.grid.positions[neighbor][1] == \
                                agent_pos[1]:
                            if (neighbor.type == 'TRAFFIC_LIGHT' and neighbor.color == RED) or neighbor.type == 'CAR':
                                move = False
                                break
                if move:
                    self.grid.move_by(agent, agent.get_dir())
                    new_pos = self.grid.positions[agent]
                    self.client.update_car(agent.id, new_pos)

                if (self.grid.positions[agent] == (self.v_pos, self.p.size - 1) or self.grid.positions[agent] == (
                        self.p.size - 1, self.h_pos) or self.grid.positions[agent] == (
                        self.p.size - 1, self.h_pos * 2)):
                    self.grid.remove_agents(agent)
                    self.client.delete_car(agent.id)

        if self.p.time == self.step_count:
            self.stop()

        # upload changes to cloud
        self.client.commit()

        self.step_count += 1

        time.sleep(self.p.step_dur)

    def end(self):
        for agent in self.grid.agents:
            self.client.delete_car(agent.id)
            self.client.delete_traffic_light(agent.id)


def animation_plot(model, ax):
    attr_grid = model.grid.attr_grid('color')
    color_dict = {1: '#00ff00', 2: '#ffff00', 3: '#ff0000', 4: '#0000ff', None: '#eeeeee'}
    ap.gridplot(attr_grid, ax=ax, color_dict=color_dict, convert=True)
    ax.set_title(f"Simulation of street intersection\n"
                 f"Time-step: {model.t}")


parameters = {
    'size': 20,
    'n_cars': 8,
    'time': 40,
    'step_dur': 0.1,
    'duracion_semaforo': 5
}

"""
fig, ax = plt.subplots()
model = Interseccion(parameters)
animation = ap.animate(model, fig, ax, animation_plot)
IPython.display.HTML(animation.to_jshtml(fps=8))
"""

if __name__ == "__main__":
    model = Interseccion(parameters)
    model.run()
