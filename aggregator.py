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
        """
        id to pick ups dict
        {id:{item:num_picked_up}}
        """
        self.id_pick_ups = {}
        self.winner = None
        self.length = None

    def aggregate(self, stats_other):
        pass

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

    def get_kills_deaths(self):
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
                in_round = True
                round_num += 1
                self.round_stats.append(Stats())
            elif (event['event_name'] == 'world_trigger' and
                        event['event'] == 'Round_Win'):
                self.round_stats[round_num-1].winner = event['winner']
                in_round = False
            elif (event['event_name'] == 'world_trigger' and
                        event['event'] == 'Round_Length'):
                self.round_stats[round_num-1].length = event['seconds']
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
