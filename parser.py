import logging, re
from datetime import datetime

log = logging

#mini regexs
def get_ip_r(i=0):
    return r'(?P<ipaddr_%d>[\d\.]+:\d+)' % i
def get_name_r(i=0):
    return r'(?P<name_%d>.+?)<\d+><(?P<steamid_%d>(STEAM_0:[01]:\d+)'\
        '|(Console))><(.*?)>' % (i, i)
def get_pos_r(i=0):
    return r'(?P<pos_%d>((-?\d+) ?)+)' % i
params_r = r'(?P<params>(\((.+?) "(.+?)"\) ?)+)'
#server regexs
log_start_r = r'Log file started \(file "(?P<file>.+?)"\) \(game "(?P<game>.+?)"\) \(version '\
    '"(?P<version>\d+)"\)'
rcon_r = r'rcon from "%s": command "(?P<command>.+?)"' % get_ip_r()
#team/world regexs
world_trigger_r = r'World triggered "(?P<event>\w+)"( reason "(?P<reason>.+?)")?'
team_trigger_r = r'Team "(?P<team>\w+)" triggered "(\w+)" %s' % params_r
team_score_r = r'Team "(?P<team>\w+)" (?P<score_type>final|current) score "(?P<score>\d+)"'\
    ' with "(?P<num_players>\d+)" players'
#player regexs
say_r = r'"%s" say "(?P<message>.+?)"' % get_name_r()
say_team_r = r'"%s" say_team "(?P<message>.+?)"' % get_name_r()
connected_r = r'"%s" connected, address "%s"' % (get_name_r(), get_ip_r())
disconnected_r = r'"%s" disconnected( \(reason "(?P<reason>.+?)"\))?' % get_name_r()
validated_r = r'"%s" STEAM USERID validated' % get_name_r()
enter_r = r'"%s" entered the game' % get_name_r()
join_r = r'"%s" joined team "(?P<team>\w+)"' % get_name_r()
change_r = r'"%s" changed role to "(?P<role>\w+)"' % get_name_r()
trigger_r = r'"%s" triggered "(?P<event>.+?)"( (against "%s" )?%s)?' % (get_name_r(0),
    get_name_r(1), params_r)
pick_up_r = r'"%s" picked up item "(?P<item>.+?)"' % get_name_r()
killed_r = r'"%s" killed "%s" with "(?P<weapon>\w+)" (\(customkill "(?P<type>.+?)"\) )?\(attacker_position "%s"\) '\
    '\(victim_position "%s"\)' % (get_name_r(0), get_name_r(1),
        get_pos_r(0), get_pos_r(1))
suicide_r = '"%s" committed suicide with "(?P<thing>\w+)"( '\
    '\(attacker_position "%s"\))?' % (get_name_r(), get_pos_r())

#Now for the compiled patterns
log_start_p = re.compile(log_start_r)
rcon_p = re.compile(rcon_r)
world_trigger_p = re.compile(world_trigger_r)
team_trigger_p = re.compile(team_trigger_r)
team_score_p = re.compile(team_score_r)
say_p = re.compile(say_r)
say_team_p = re.compile(say_team_r)
connected_p = re.compile(connected_r)
disconnected_p = re.compile(disconnected_r)
validated_p = re.compile(validated_r)
enter_p = re.compile(enter_r)
join_p = re.compile(join_r)
change_p = re.compile(change_r)
trigger_p = re.compile(trigger_r)
pick_up_p = re.compile(pick_up_r)
killed_p = re.compile(killed_r)
suicide_p = re.compile(suicide_r)

class LogParser():
    """
    Converts log files to a sequence of events (ie dictionaries) of data
    """
    def __init__(self, filename):
        self.open(filename)

    def open(self, filename):
        self._filename = filename
        self._file = open(filename)

    def read(self):
        """
        Read all events
        """
        for line in self._file:
            yield self._readevent(line)

    def readline(self):
        """
        Read one event
        """
        return self._readevent(self._file.readline())

    def _readevent(self, line):
        """
        Read one event
        """
        items = line.split(None, 4)
        _datetime = datetime.strptime('%s %s' % (items[1], items[3][:-1]),
            '%m/%d/%Y %H:%M:%S')
        date = items[1]
        time = items[3][:-1]
        event = items[4]
        event_dict = {'datetime':_datetime}
        #check what the event matches
        if log_start_p.match(event):
            pass
        elif rcon_p.match(event):
            pass
        elif world_trigger_p.match(event):
            pass
        elif team_trigger_p.match(event):
            pass
        elif team_score_p.match(event):
            pass
        elif say_p.match(event):
            pass
        elif say_team_p.match(event):
            pass
        elif connected_p.match(event):
            pass
        elif disconnected_p.match(event):
            pass
        elif validated_p.match(event):
            pass
        elif enter_p.match(event):
            pass
        elif join_p.match(event):
            pass
        elif change_p.match(event):
            pass
        elif trigger_p.match(event):
            pass
        elif pick_up_p.match(event):
            pass
        elif killed_p.match(event):
            pass
        elif suicide_p.match(event):
            pass
        else:
            log.error("""The following event text did not match\n%s""" % event)
