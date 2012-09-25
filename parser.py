import logging, re

log = logging

#mini regexs
ip_r = r'([\d\.]+:\d+)'
name_r = r'"(.+?)<\d+><((STEAM_0:[01]:\d+)|(Console))><(.*?)>"'
pos_r = r'(((-?\d+) ?)+)'
params_r = r'((\((.+?) "(.+?)"\) ?)+)'
#server regexs
log_start_r = r'Log file started \(file "(.+?)"\) \(game "(.+?)"\) \(version '\
    '"(\d+)"\)'
rcon_r = r'rcon from "%s": command "(.+?)"' % ip_r
#team/world regexs
world_trigger_r = r'World triggered "(\w+)"( reason "(.+?)")?'
team_trigger_r = r'Team "(\w+)" triggered "(\w+)" %s' % params_r
team_score_r = r'Team "(\w+)" (final|current) score "(\d+)" with "(\d+)" players'
#player regexs
say_r = r'%s say ".+?"' % name_r
say_team_r = r'%s say_team ".+?"' % name_r
connected_r = r'%s connected, address "%s"' % (name_r, ip_r)
disconnected_r = r'%s disconnected( \(reason ".+?"\))?' % name_r
validated_r = r'%s STEAM USERID validated' % name_r
enter_r = r'%s entered the game' % name_r
join_r = r'%s joined team "(\w+)"' % name_r
change_r = r'%s changed role to "(\w+)"' % name_r
trigger_r = r'%s triggered "(.+?)"( (against %s )?%s)?' % (name_r, name_r, params_r)
pick_up_r = r'%s picked up item "(.+?)"' % name_r
killed_r = r'%s killed %s with "(\w+)" (\(customkill "(.+?)"\) )?\(attacker_position "%s"\) '\
    '\(victim_position "%s"\)' % (name_r, name_r, pos_r, pos_r)
suicide_r = '%s committed suicide with "(\w+)"( '\
    '\(attacker_position "%s"\))?' % (name_r, pos_r)

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
        date = items[1]
        time = items[3][:-1]
        event = items[4]
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
