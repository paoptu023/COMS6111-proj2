import main
import pprint

def test_query_bing():
    print 'Testing the query_bing method ... '
    try:
        print main.query_bing('hardwarecentral.com', 'computer')
        print main.query_bing('yahoo.com', 'sports+soccer')
        print main.query_bing('health.com', 'diet')
        print main.query_bing('fifa.com', 'soccer')
        print 'Testing finished'
    except Exception:
        print 'query_bing fails'+repr(Exception)


def test_compose_probe():
    try:
        print 'Testing the compose_probe method ... '
        pprint.pprint(main.compose_prob('root.txt'))
        print 'Testing finished'
    except Exception:
        print 'compose_probe fails' + repr(Exception)


def test_classify():
    # health.com: Root / Health / Fitness
    # fifa.com: Root / Sports / Soccer
    # diabetes.org: Root / Health
    # hardwarecentral.com:  Root / Computers
    # yahoo.com: Root / Sports
    #print main.classify('root', 'health.com', 100, 0.6, '')
    print 'hi'


test_query_bing()
#test_compose_probe()
#test_classify()