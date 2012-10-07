from aggregator import TF2LogAggregator

if __name__ == '__main__':
    import optparse
    a = TF2LogAggregator()
    parser = optparse.OptionParser()
    options, (log, out) = parser.parse_args()
    a.aggregate(log)    
    a.total_stats.write_stats(out, s_format='csv')
    for i, m_round in enumerate(a.round_stats[:-1]):
        print m_round.id_hs
        m_round.write_stats('%d-%s' % (i, out), s_format='csv')
