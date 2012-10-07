import codecs
from tfparser import TF2LogParser

class Stats():
    def __init__(self):
        """
        id to names dict
        {id:([name1,name2])}
        """
        self.id_all_names = {}
        self.id_name = {}
        self.id_team = {}
        """
        id to kills dict
        {id(attkr):{id(victim):num_kills}
        """
        self.id_kill_matrix = {}
        self.id_hs = {}
        self.id_assist_matrix = {}
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
        def aggregate_dict(s_dict, o_dict):
            for k, v in o_dict.items():
                if k not in s_dict:
                    s_dict[k] = 0
                s_dict[k] += v
        def aggregate_dual_dict(s_dict, o_dict):
            for k, v in o_dict.items():
                if k not in s_dict:
                    s_dict[k] = {}
                aggregate_dict(s_dict[k], v)
        aggregate_dual_dict(self.id_kill_matrix,
                other.id_kill_matrix)
        aggregate_dual_dict(self.id_assist_matrix,
                other.id_assist_matrix)
        aggregate_dual_dict(self.id_heal_matrix,
                other.id_heal_matrix)
        aggregate_dict(self.id_suicide,
                other.id_suicide)
        aggregate_dict(self.id_damage,
                other.id_damage)
        aggregate_dual_dict(self.id_pick_ups,
                other.id_pick_ups)
        aggregate_dict(self.score,
                other.score)
        aggregate_dict(self.id_hs, other.id_hs)
        self.id_name.update(other.id_name)
        self.id_team.update(other.id_team)
        self.length += other.length

    def team_score(self, team):
        if team not in self.score:
            self.score[team] = 0
        self.score[team] += 1

    def update_player_dict(self, player):
        if player['steamid'] not in self.id_name:
            self.id_name[player['steamid']] = player['name']
        if player['team'] != None:
            self.id_team[player['steamid']] = player['team']

    def player_killed(self, attacker, victim, k_type=None):
        self.update_player_dict(attacker)
        self.update_player_dict(victim)
        if k_type != None:
            #fucking dead ringer
            if k_type == 'feign_death':
                return
            elif k_type == 'headshot':
                if attacker['steamid'] not in self.id_hs:
                    self.id_hs[attacker['steamid']] = 0
                self.id_hs[attacker['steamid']] += 1
        if attacker['steamid'] not in self.id_kill_matrix:
            self.id_kill_matrix[attacker['steamid']] = {}
        attacker_dict = self.id_kill_matrix[attacker['steamid']]
        if victim['steamid'] not in attacker_dict:
            attacker_dict[victim['steamid']] = 0
        attacker_dict[victim['steamid']] += 1

    def player_assisted(self, assister, victim, k_type=None):
        self.update_player_dict(assister)
        self.update_player_dict(victim)
        if k_type != None:
            #fucking dead ringer
            if k_type == 'feign_death':
                return
        if assister['steamid'] not in self.id_assist_matrix:
            self.id_assist_matrix[assister['steamid']] = {}
        assister_dict = self.id_assist_matrix[assister['steamid']]
        if victim['steamid'] not in assister_dict:
            assister_dict[victim['steamid']] = 0
        assister_dict[victim['steamid']] += 1

    def player_damaged(self, player, amount):
        self.update_player_dict(player)
        if player['steamid'] not in self.id_damage:
            self.id_damage[player['steamid']] = 0
        self.id_damage[player['steamid']] += amount

    def player_healed(self, healer, target, amount):
        self.update_player_dict(healer)
        self.update_player_dict(target)
        if healer['steamid'] not in self.id_heal_matrix:
            self.id_heal_matrix[healer['steamid']] = {}
        healer_dict = self.id_heal_matrix[healer['steamid']]
        if target['steamid'] not in healer_dict:
            healer_dict[target['steamid']] = 0
        healer_dict[target['steamid']] += amount

    def player_picked_up(self, player, item):
        self.update_player_dict(player)
        if player['steamid'] not in self.id_pick_ups:
            self.id_pick_ups[player['steamid']] = {}
        p_pickups = self.id_pick_ups[player['steamid']]
        if item not in p_pickups:
            p_pickups[item] = 0
        p_pickups[item] += 1

    def player_suicided(self, player):
        self.update_player_dict(player)
        if player['steamid'] not in self.id_suicide:
            self.id_suicide[player['steamid']] = 0
        self.id_suicide[player['steamid']] += 1

    def get_player_deaths(self, player):
        deaths = {player:self.id_suicide.get(player, 0)}
        for k, v in self.id_kill_matrix.items():
            if player in v:
                deaths[k] = v[player]
        return deaths

    def get_simple_player_stats(self, player):
        stats = {}
        stats['kills'] = (sum(self.id_kill_matrix[player].values())
                if player in self.id_kill_matrix else 0)
        stats['deaths'] = sum(self.get_player_deaths(player).values())
        stats['assists'] = (sum(self.id_assist_matrix[player].values())
                if player in self.id_assist_matrix else 0)
        stats['damage'] = self.id_damage.get(player, 0)
        stats['headshots'] = (0 if player not in self.id_hs else
                self.id_hs[player])
        return stats

    def get_team_stats(self, team):
        pass

    def write_stats(self, fp, s_format='json'):
        #simple stats
        simple_stats = {}
        for steamid, name in self.id_name.items():
            simple_stats[name] = self.get_simple_player_stats(steamid)
        #kill matrix
        def cmp_player(player_id):
            return (self.id_team[player_id], self.id_name[player_id])
        players = sorted(self.id_name.keys(), key=cmp_player)
        kill_mat = []
        kill_mat.append([])
        kill_mat[0].append('')
        kill_mat[0].extend(map(lambda x: self.id_name[x], players))
        for i, player in enumerate(players):
            kill_mat.append([])
            kill_mat[i+1].append(self.id_name[player])
            kill_mat[i+1].extend([0] * len(players))
            if player in self.id_kill_matrix:
                for victim, num in self.id_kill_matrix[player].items():
                    kill_mat[i+1][players.index(victim)+1] = num
            kill_mat[i+1][i+1] = ''
        if s_format == 'csv':
            fp.write('Simple Stats\n')
            fp.write('Name,Kills,Assists,Deaths,Damage,Headshot Kills\n')
            for name, s_dict in simple_stats.items():
                fp.write('%s,%s,%s,%s,%s,%s\n' % (name, s_dict['kills'],
                        s_dict['assists'], s_dict['deaths'],
                        s_dict['damage'], s_dict['headshots']))
            fp.write('\nKill Matrix - rows = kills cols = deaths\n')
            #make the kill matrix
            for row in kill_mat:
                fp.write(u','.join(map(lambda x: unicode(x), row)) + '\n')

class TF2LogAggregator():
    def __init__(self):
        self.total_stats = Stats()
        self.round_stats = []

    def clear(self):
        self.total_stats = Stats()
        self.round_stats = []

    def aggregate(self, filename):
        parser = TF2LogParser(filename)
        round_num = 0
        in_round = False
        teams = {}
        last_kill_type = ''
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
                        event['event'] == 'Round_Stalemate'):
                in_round = False
            elif (event['event_name'] == 'world_trigger' and
                        (event['event'] == 'Round_Length' or
                         event['event'] == 'Mini_Round_Length')):
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
                        event['victim'], event['type'])
                    last_kill_type = event['type']
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
                    elif event['event'] == 'kill assist':
                        self.round_stats[round_num-1].player_assisted(event['player'],
                                event['target'], last_kill_type)
        self.total_stats.aggregate(self.round_stats[-1])

    def write_stats(self, out_file, **kwargs):
        fp = codecs.open(out_file, 'w', 'utf8')
        fp.write('Total Stats\n')
        self.total_stats.write_stats(fp, **kwargs)
        for i, round_stats in enumerate(self.round_stats):
            fp.write('\nRound %d\n' % (i+1))
            round_stats.write_stats(fp, **kwargs)
        fp.close()
