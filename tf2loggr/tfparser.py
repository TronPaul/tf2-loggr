import logging, re, codecs
from datetime import datetime

log = logging

#mini regexs
def get_ip_r(i=0):
    return r'(?P<ipaddr_%d>[\d\.]+:\d+)' % i
def get_name_r(i=0):
    return r'(?P<name_%d>.+?)<\d+><(?P<steamid_%d>(STEAM_0:[01]:\d+)'\
        '|(Console))><(?P<team_%d>.*?)>' % (i, i, i)
def get_pos_r(i=0):
    return r'(?P<pos_%d>((-?\d+) ?)+)' % i
params_r = r'(?P<params>(?:\((?:.+?) "(?:.+?)"\) ?)+)'
#regex to use in post
params_post_r = r'\((?P<param_key>.+?) "(?P<param_value>.+?)"\)'
#server regexs
log_start_r = r'Log file started \(file "(?P<file>.+?)"\) \(game "(?P<game>.+?)"\) \(version '\
        '"(?P<version>\d+)"\)'
rcon_r = r'rcon from "%s": command "(?P<command>.+?)"' % get_ip_r()
steamauth_r = r'STEAMAUTH: Client (?P<name>.+?) received failure code'\
        ' (?P<code>\d+)'
#team/world regexs
world_trigger_r = r'World triggered "(?P<event>\w+?)"(?: %s)?' % params_r
team_trigger_r = r'Team "(?P<team>\w+?)" triggered "(?P<event>\w+?)"(?: %s)?' % params_r
team_score_r = r'Team "(?P<team>\w+?)" (?P<score_type>final|current) score'\
        ' "(?P<score>\d+?)" with "(?P<num_players>\d+?)" players'
#player regexs
say_r = r'"%s" say "(?P<message>.+?)"' % get_name_r()
say_team_r = r'"%s" say_team "(?P<message>.+?)"' % get_name_r()
connected_r = r'"%s" connected, address "%s"' % (get_name_r(), get_ip_r())
disconnected_r = r'"%s" disconnected( \(reason "(?P<reason>.+?)"\))?' % get_name_r()
validated_r = r'"%s" STEAM USERID validated' % get_name_r()
enter_r = r'"%s" entered the game' % get_name_r()
join_r = r'"%s" joined team "(?P<team>\w+)"' % get_name_r()
change_r = r'"%s" changed role to "(?P<role>\w+)"' % get_name_r()
trigger_r = r'"%s" triggered "(?P<event>.+?)"(?: against "%s")?(?: %s)?' % (get_name_r(0),
        get_name_r(1), params_r)
pick_up_r = r'"%s" picked up item "(?P<item>.+?)"' % get_name_r()
killed_r = r'"%s" killed "%s" with "(?P<weapon>\w+)" (\(customkill "(?P<type>.+?)"\) )?\(attacker_position "%s"\) '\
        '\(victim_position "%s"\)' % (get_name_r(0), get_name_r(1),
            get_pos_r(0), get_pos_r(1))
suicide_r = '"%s" committed suicide with "(?P<thing>\w+)"( '\
        '\(attacker_position "%s"\))?' % (get_name_r(), get_pos_r())

#Now for the compiled patterns
params_post_p = re.compile(params_post_r)
log_start_p = re.compile(log_start_r)
rcon_p = re.compile(rcon_r)
steamauth_p = re.compile(steamauth_r)
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

def get_player_info(matcher, player_num=0):
    p_dict = {}
    p_dict['name'] = matcher.group('name_%d' % player_num)
    p_dict['steamid'] = matcher.group('steamid_%d' % player_num)
    p_dict['team'] = matcher.group('team_%d' % player_num)
    return p_dict

def get_params(matcher):
    params_dict = {}
    params = matcher.group('params')
    if params:
        for m in params_post_p.finditer(params):
            params_dict[m.group('param_key')] = m.group('param_value')
    return params_dict

class TF2LogParser():
    """
    Converts log files to a sequence of events (ie dictionaries) of data
    """
    def __init__(self, filename):
        self.open(filename)

    def open(self, filename):
        self._filename = filename
        self._file = codecs.open(filename, 'r', 'utf-8')

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
            event_dict['event_name'] = 'log_start'
            m = log_start_p.match(event)
            event_dict['file'] = m.group('file')
            event_dict['game'] = m.group('game')
            event_dict['version'] = m.group('version')
        elif rcon_p.match(event):
            event_dict['event_name'] = 'rcon'
            m = rcon_p.match(event)
            event_dict['ipaddr'] = m.group('ipaddr_0')
            event_dict['command'] = m.group('command')
        elif steamauth_p.match(event):
            event_dict['event_name'] = 'AUTH_FAILURE'
        elif world_trigger_p.match(event):
            event_dict['event_name'] = 'world_trigger'
            m = world_trigger_p.match(event)
            event_dict['event'] = m.group('event')
            event_dict.update(get_params(m))
        elif team_trigger_p.match(event):
            event_dict['event_name'] = 'team_trigger'
            m = team_trigger_p.match(event)
            event_dict['team'] = m.group('team')
            event_dict.update(get_params(m))
        elif team_score_p.match(event):
            event_dict['event_name'] = 'team_score'
            m = team_score_p.match(event)
            event_dict['team'] = m.group('team')
            event_dict['score_type'] = m.group('score_type')
            event_dict['score'] = m.group('score')
            event_dict['num_players'] = m.group('num_players')
        elif say_p.match(event):
            event_dict['event_name'] = 'player_say'
            m = say_p.match(event)
            event_dict['player'] = get_player_info(m)
            event_dict['message'] = m.group('message')
        elif say_team_p.match(event):
            event_dict['event_name'] = 'player_say_team'
            m = say_team_p.match(event)
            event_dict['player'] = get_player_info(m)
            event_dict['message'] = m.group('message')
        elif connected_p.match(event):
            event_dict['event_name'] = 'player_connected'
            m = connected_p.match(event)
            event_dict['ip_addr'] = m.group('ipaddr_0')
            event_dict['player'] = get_player_info(m)
        elif disconnected_p.match(event):
            event_dict['event_name'] = 'player_disconnected'
            m = disconnected_p.match(event)
            event_dict['reason'] = m.group('reason')
            event_dict['player'] = get_player_info(m)
        elif validated_p.match(event):
            event_dict['event_name'] = 'steamid_validated'
            m = validated_p.match(event)
            event_dict['player'] = get_player_info(m)
        elif enter_p.match(event):
            event_dict['event_name'] = 'entered_game'
            m = enter_p.match(event)
            event_dict['player'] = get_player_info(m)
        elif join_p.match(event):
            event_dict['event_name'] = 'joined_team'
            m = join_p.match(event)
            event_dict['team'] = m.group('team')
            event_dict['player'] = get_player_info(m)
        elif change_p.match(event):
            event_dict['event_name'] = 'changed_role'
            m = change_p.match(event)
            event_dict['role'] = m.group('role')
            event_dict['player'] = get_player_info(m)
        elif trigger_p.match(event):
            event_dict['event_name'] = 'player_triggered'
            m = trigger_p.match(event)
            event_dict['event'] = m.group('event')
            event_dict['player'] = get_player_info(m, 0)
            event_dict['target'] = get_player_info(m, 1)
            event_dict.update(get_params(m))
        elif pick_up_p.match(event):
            event_dict['event_name'] = 'player_picked_up'
            m = pick_up_p.match(event)
            event_dict['player'] = get_player_info(m)
            event_dict['item'] = m.group('item')
        elif killed_p.match(event):
            event_dict['event_name'] = 'player_killed'
            m = killed_p.match(event)
            event_dict['attacker'] = get_player_info(m, 0)
            event_dict['victim'] = get_player_info(m, 1)
            event_dict['attacker']['pos'] = m.group('pos_0')
            event_dict['victim']['pos'] = m.group('pos_1')
            event_dict['type'] = m.group('type')
        elif suicide_p.match(event):
            event_dict['event_name'] = 'player_suicided'
            m = suicide_p.match(event)
            event_dict['player'] = get_player_info(m)
            event_dict['player']['pos'] = m.group('pos_0')
        else:
            log.error("""The following event text did not match\n%s""" % event)
            event_dict['event_name'] = None
            #raise Exception #TODO make our own exception
        return event_dict
