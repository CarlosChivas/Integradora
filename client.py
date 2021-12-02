import json
import uuid
import requests as req


class SimulationDatabase:

    def __init__(self):
        self.data = {
            'cars': [],
            'trafficLights': []
        }

    def _find_car(self, obj_key):
        car_list = self.data['cars']
        for i in range(len(car_list)):
            if car_list[i]['id'] == obj_key:
                return i
        raise ValueError

    def _find_light(self, obj_key):
        traffic_lights_list = self.data['trafficLights']
        for i in range(len(traffic_lights_list)):
            if traffic_lights_list[i]['id'] == obj_key:
                return i
        raise ValueError

    def add_car(self, x=0, y=0, z=0, car_id=None):
        if car_id is None:
            car_id = str(uuid.uuid4())

        new_car = {
            'id': car_id,
            'x': x,
            'y': y,
            'z': z
        }

        self.data['cars'].append(new_car)
        return car_id

    def update_car(self, car_id, x=0, y=0, z=0):
        try:
            ind = self._find_car(car_id)
            car_list = self.data['cars']
            car_list[ind]['x'] = x
            car_list[ind]['y'] = y
            car_list[ind]['z'] = z
            return True
        except ValueError:
            print("Car not found")
            return False

    def delete_car(self, car_id):
        try:
            ind = self._find_car(car_id)
            car_list = self.data['cars']
            del car_list[ind]
            return True
        except ValueError:
            print("Object not found")
            return False

    def add_traffic_light(self, id, color, tag):
        traffic_light = {
            'id': id,
            'color': color,
            'tag': tag
        }

        self.data['trafficLights'].append(traffic_light)
        return id

    def update_traffic_light(self, id, color):
        try:
            ind = self._find_light(id)
            traffic_light_list = self.data['trafficLights']
            traffic_light_list[ind]['color'] = color
            return True
        except ValueError:
            print("Traffic light not found")
            return False

    def delete_traffic_light(self, car_id):
        try:
            ind = self._find_light(car_id)
            traffic_light_list = self.data['trafficLights']
            del traffic_light_list[ind]
            return True
        except ValueError:
            print("Object not found")
            return False

    def string(self):
        return json.dumps(self.data)

    def getJSON(self):
        return self.data

    def print(self):
        print(self.data)


db = SimulationDatabase()


class Client:
    def __init__(self, url=None):
        self.url = url

    def add_car(self, id, pos):
        db.add_car(pos[1], pos[0], 0, id)

    def update_car(self, id, pos):
        db.update_car(id, pos[1], pos[0], 0)

    def delete_car(self, id):
        db.delete_car(id)

    def add_traffic_light(self, id, color, tag):
        db.add_traffic_light(id, color, tag)

    def update_traffic_light(self, id, color):
        db.update_traffic_light(id, color)

    def delete_traffic_light(self, id):
        db.delete_traffic_light(id)

    def commit(self):
        r = req.post(self.url, data=db.string())
        print(r.text)

        return r.status_code


if __name__ == "__main__":
    url = "https://testappagent.us-south.cf.appdomain.cloud/"
    cl = Client(url)

