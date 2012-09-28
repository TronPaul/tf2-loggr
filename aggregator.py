from parser import TF2LogParser
class Stats():
    def __init__(self):
        """
        id to names dict
        {id:([name1,name2])}
        """
        self.id_all_names = {}
        self.id_name = {}
        """
        id to kills dict
        {id(attkr):{id(victim):num_kills}
        """
        self.id_kill_matrix = {}
        """
        id to suicide matrix
        for accurate death count
        {id:num_deaths}
        """
        self.id_suicide = {}
        """
        id to damage dealt dict
        {id:damage}
        """
        self.id_damage = {}
        self.id_heal_matrix = {}
        """
        id to pick ups dict
        {id:{item:num_picked_up}}
        """
        self.id_pick_ups = {}
        self.score = {}
        self.length = 0

    def __getattr__(self, name):
        if name == 'winner':
            return max(self.score.iteritems(), key=lambda x: x[1])[0]
        raise AttributeError(name)

    def aggregate(self, other):
        #update kill matrix
        for k, v in other.id_kill_matrix.items():
            if k not in self.id_kill_matrix:
                self.id_kill_matrix[k] = {}
            for pk, pv in v.items():
                if pk not in self.id_kill_matrix[k]:
                    self.id_kill_matrix[k][pk] = 0
                self.id_kill_matrix[k][pk] += pv
        for k, v in other.id_heal_matrix.items():
            if k not in self.id_heal_matrix:
                self.id_heal_matrix[k] = {}
            for pk, pv in v.items():
                if pk not in self.id_heal_matrix[k]:
                    self.id_heal_matrix[k][pk] = 0
                self.id_heal_matrix[k][pk] += pv
        for k, v in other.id_suicide.items():
            if k not in self.id_suicide:
                self.id_suicide[k] = 0
            self.id_suicide[k] += v
        for k, v in other.id_damage.items():
            if k not in self.id_damage:
                self.id_damage[k] = 0
            self.id_damage[k] += v
        for k, v in other.id_pick_ups.items():
            if k not in self.id_pick_ups:
                self.id_pick_ups[k] = {}
            for ik, iv in v.items():
                if ik not in self.id_pick_ups[k]:
                    self.id_pick_ups[k][ik] = 0
                self.id_pick_ups[k][ik] += iv
        for k, v in other.score.items():
            if k not in self.score:
                self.score[k] = 0
            self.score[k] += v
        self.length += other.length

    def team_score(self, team):
        if team not in self.score:
            self.score[team] = 0
        self.score[team] += 1

    def player_killed(self, attacker, victim):
        if attacker['steamid'] not in self.id_kill_matrix:
            self.id_kill_matrix[attacker['steamid']] = {}
        attacker_dict = self.id_kill_matrix[attacker['steamid']]
        if victim['steamid'] not in attacker_dict:
            attacker_dict[victim['steamid']] = 0
        attacker_dict[victim['steamid']] += 1

    def player_damaged(self, player, amount):
        if player['steamid'] not in self.id_damage:
            self.id_damage[player['steamid']] = 0
        self.id_damage[player['steamid']] += amount

    def player_healed(self, healer, target, amount):
        if healer['steamid'] not in self.id_heal_matrix:
            self.id_heal_matrix[healer['steamid']] = {}
        healer_dict = self.id_heal_matrix[healer['steamid']]
        if target['steamid'] not in healer_dict:
            healer_dict[target['steamid']] = 0
        healer_dict[target['steamid']] += amount

    def player_picked_up(self, player, item):
        if player['steamid'] not in self.id_pick_ups:
            self.id_pick_ups[player['steamid']] = {}
        p_pickups = self.id_pick_ups[player['steamid']]
        if item not in p_pickups:
            p_pickups[item] = 0
        p_pickups[item] += 1

    def player_suicided(self, player):
        if player['steamid'] not in self.id_suicide:
            self.id_suicide[player['steamid']] = 0
        self.id_suicide[player['steamid']] += 1

    def get_player_stats(self, player):
        pass

    def get_team_stats(self, team):
        pass

    def get_stats(self, s_format='JSON'):
        pass

class TF2LogAggregator():
    def __init__(self):
        self.total_stats = Stats()
        self.round_stats = []

    def aggregate(self, filename):
        parser = TF2LogParser(filename)
        round_num = 0
        in_round = False
        teams = {}
        for event in parser.read():
            if (event['event_name'] == 'world_trigger' and
                        event['event'] == 'Round_Start'):
                if round_num > 0:
                    self.total_stats.aggregate(self.round_stats[round_num-1])
                in_round = True
                round_num += 1
                self.round_stats.append(Stats())
            elif (event['event_name'] == 'world_trigger' and
                        event['event'] == 'Round_Win'):
                self.total_stats.team_score(event['winner'])
                in_round = False
            elif (event['event_name'] == 'world_trigger' and
                        event['event'] == 'Round_Length'):
                self.round_stats[round_num-1].length = float(event['seconds'])
            elif event['event_name'] == 'joined_team':
                if event['team'] not in teams:
                    teams[event['team']] = {}
                teams[event['team']][event['player']['steamid']] = None
            #elif event['event_name'] == 'changed_role':
                #steamid = event['player']['steamid']
                #for team in teams:
                    #if steamid in team:
                        #team[steamid] = event['role']
                    #else:
                        #raise Exception
            elif in_round == True:
                #let's do some aggregating!
                if event['event_name'] == 'player_killed':
                    self.round_stats[round_num-1].player_killed(event['attacker'],
                        event['victim'])
                elif event['event_name'] == 'player_suicided':
                    self.round_stats[round_num-1].player_suicided(event['player'])
                elif event['event_name'] == 'player_picked_up':
                    self.round_stats[round_num-1].player_picked_up(event['player'],
                        event['item'])
                elif event['event_name'] == 'player_triggered':
                    if event['event'] == 'damage':
                        self.round_stats[round_num-1].player_damaged(event['player'],
                                int(event['damage']))
                    elif event['event'] == 'healed':
                        self.round_stats[round_num-1].player_healed(event['player'],
                                event['target'], int(event['healing']))
