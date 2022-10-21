import requests
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA, ENTITY_ID_FORMAT
from homeassistant.const import CONF_ID, CONF_NAME
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity import async_generate_entity_id

DEFAULT_NAME = 'MPK Łódź'

CONF_NUM = 'num'
CONF_STOPS = 'stops'
CONF_LINES = 'lines'
CONF_DIRECTIONS = 'directions'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Required(CONF_STOPS): vol.All(cv.ensure_list, [
        vol.Schema({
            vol.Optional(CONF_ID, default=0): cv.positive_int,
            vol.Optional(CONF_NUM, default=0): cv.positive_int,
            vol.Optional(CONF_NAME): cv.string,
            vol.Optional(CONF_LINES, default=[]): cv.ensure_list,
            vol.Optional(CONF_DIRECTIONS, default=[]): cv.ensure_list
        })])
})


def setup_platform(hass, config, add_entities, discovery_info=None):
    name = config.get(CONF_NAME)
    stops = config.get(CONF_STOPS)
    dev = []
    for stop_cfg in stops:
        stop_id = str(stop_cfg.get(CONF_ID))
        stop_num = str(stop_cfg.get(CONF_NUM))
        use_stop_num = stop_num != "0"
        stop = stop_num if use_stop_num else stop_id
        print(stop_id)
        print(stop_num)
        lines = stop_cfg.get(CONF_LINES)
        directions = stop_cfg.get(CONF_DIRECTIONS)
        real_stop_name = MpkLodzSensor.get_stop_name(stop, use_stop_num)
        if real_stop_name is None:
            raise Exception(f"Invalid stop id/num: {stop_id} / {stop_num} / {use_stop_num} / {stop}")
        stop_name = stop_cfg.get(CONF_NAME) or stop_id
        if use_stop_num:
            stop_name = stop_cfg.get(CONF_NAME) or f"num_{stop_num}"
        uid = '{}_{}'.format(name, stop_name)
        entity_id = async_generate_entity_id(ENTITY_ID_FORMAT, uid, hass=hass)
        dev.append(MpkLodzSensor(entity_id, name, stop, use_stop_num, stop_name, real_stop_name, lines, directions))
    add_entities(dev, True)


class MpkLodzSensor(Entity):
    def __init__(self, entity_id, name, stop, use_stop_num, stop_name, real_stop_name, watched_lines, watched_directions):
        self.entity_id = entity_id
        self._name = name
        self._stop = stop
        self._use_stop_num = use_stop_num
        self._watched_lines = watched_lines
        self._watched_directions = watched_directions
        self._stop_name = stop_name
        self._real_stop_name = real_stop_name
        self._departures = []
        self._departures_number = 0
        self._departures_by_line = dict()

    @property
    def name(self):
        return '{} - {}'.format(self._name, self._stop_name)

    @property
    def icon(self):
        return "mdi:bus-clock"

    @property
    def state(self):
        if self._departures_number is not None and self._departures_number > 0:
            dep = self._departures[0]
            return MpkLodzSensor.departure_to_str(dep)
        return None

    @property
    def unit_of_measurement(self):
        return None

    @property
    def extra_state_attributes(self):
        attr = dict()
        attr['stop_name'] = self._real_stop_name
        if self._departures is not None:
            attr['list'] = self._departures
            attr['html_timetable'] = self.get_html_timetable()
            attr['html_departures'] = self.get_html_departures()
            if self._departures_number > 0:
                dep = self._departures[0]
                attr['line'] = dep["line"]
                attr['direction'] = dep["direction"]
                attr['departure'] = dep["departure"]
                attr['time_to_departure'] = dep["time_to_departure"]
        return attr

    def update(self):
        now = datetime.now()
        data = MpkLodzSensor.get_data(self._stop, self._use_stop_num)
        if data is None:
            return
        departures = data[0][0]
        parsed_departures = []
        for departure in departures:
            line = departure.attrib["nr"]
            direction = departure.attrib["dir"]
            if len(self._watched_lines) > 0 and line not in self._watched_lines \
                    or len(self._watched_directions) > 0 and direction not in self._watched_directions:
                continue
            time_in_seconds = int(departure[0].attrib["s"])
            departure = now + timedelta(seconds=time_in_seconds)
            time_to_departure = time_in_seconds // 60
            parsed_departures.append(
                {
                    "line": line,
                    "direction": direction,
                    "departure": "{:02}:{:02}".format(departure.hour, departure.minute),
                    "time_to_departure": int(time_to_departure),
                })
        self._departures = parsed_departures
        self._departures_number = len(parsed_departures)
        self._departures_by_line = MpkLodzSensor.group_by_line(self._departures)

    def get_html_timetable(self):
        html = '<table width="100%" border=1 style="border: 1px black solid; border-collapse: collapse;">\n'
        lines = list(self._departures_by_line.keys())
        lines.sort()
        for line in lines:
            directions = list(self._departures_by_line[line].keys())
            directions.sort()
            for direction in directions:
                if len(direction) == 0:
                    continue
                html = html + '<tr><td style="text-align: center; padding: 4px"><big>{}, kier. {}</big></td>'.format(
                    line, direction)
                departures = ', '.join(map(lambda x: x["departure"], self._departures_by_line[line][direction]))
                html = html + '<td style="text-align: right; padding: 4px">{}</td></tr>\n'.format(departures)
        if len(lines) == 0:
            html = html + '<tr><td style="text-align: center; padding: 4px">Brak połączeń</td>'
        html = html + '</table>'
        return html

    def get_html_departures(self):
        html = '<table width="100%" border=1 style="border: 1px black solid; border-collapse: collapse;">\n'
        for departure in self._departures:
            html = html + '<tr><td style="text-align: center; padding: 4px">{}</td></tr>\n'.format(
                MpkLodzSensor.departure_to_str(departure))
        html = html + '</table>'
        return html

    @staticmethod
    def departure_to_str(dep):
        return '{}, kier. {}: {} ({}m)'.format(dep["line"], dep["direction"], dep["departure"],
                                               dep["time_to_departure"])

    @staticmethod
    def group_by_line(departures):
        departures_by_line = dict()
        for departure in departures:
            line = departure["line"]
            direction = departure["direction"]
            if line not in departures_by_line:
                departures_by_line[line] = dict()
            if direction not in departures_by_line[line]:
                departures_by_line[line][direction] = []
            departures_by_line[line][direction].append(departure)
        return departures_by_line

    @staticmethod
    def get_stop_name(stop, use_stop_num):
        data = MpkLodzSensor.get_data(stop, use_stop_num)
        if data is None:
            return None
        return data[0].attrib["name"]

    @staticmethod
    def get_data(stop, use_stop_num):
        address = "http://rozklady.lodz.pl/Home/GetTimeTableReal?busStopId={}".format(stop)
        if use_stop_num:
            address = "http://rozklady.lodz.pl/Home/GetTimeTableReal?busStopNum={}".format(stop)
        headers = {
            'referer': address,
        }
        response = requests.get(address, headers=headers)
        if response.status_code == 200 and response.content.__len__() > 0:
            return ET.fromstring(response.text)
        return None
