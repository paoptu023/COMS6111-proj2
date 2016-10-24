import urllib2
import json
import base64


def query_bing(enc_site, enc_query, account_key):
    account_key_enc = base64.b64encode(account_key+':'+account_key)
    headers = {'Authorization': 'Basic '+account_key_enc}
    bing_url = 'https://api.datamarket.azure.com/Data.ashx/Bing/SearchWeb/v1/Composite?Query=%27site%3a'+enc_site+'%20'+enc_query+'%27&$top=1&$format=json'
    req = urllib2.Request(bing_url, headers=headers)
    response = urllib2.urlopen(req)
    result = json.loads(response.read())
    return result['d']['results'][0]['WebTotal']


def compose_prob(filename):
    f = open(filename)
    content = f.readlines()
    f.close()
    class_dict = {}
    for prob in content:
        item = prob.split()
        if item[0] not in class_dict:
            class_dict[item[0]] = []
        class_dict[item[0]].append('+'.join(item[1:]))
    return class_dict


def classify(account_key, category, site, tec, tes, path):
    try:
        probes = compose_prob(category.lower()+'.txt')
    except Exception:
        return path
    cov = {}
    spec = {}
    for subcategory in probes.keys():
        if subcategory not in cov:
            cov[subcategory] = 0
            spec[subcategory] = 0.0
        for prob in probes[subcategory]:
            num = int(query_bing(site,prob, account_key))
            cov[subcategory] += num
            #print subcategory, prob, num, cov[subcategory]

    total = float(sum(cov.values()))

    for subcategory in spec.keys():
        spec[subcategory] = cov[subcategory]/total
        print 'for ', subcategory, ' : '
        print '     Specificity : ', spec[subcategory]
        print '     Coverage    : ', cov[subcategory]
        if spec[subcategory] > tes and cov[subcategory] > tec:
            path = classify(account_key, subcategory, site, tec, tes, path + '/' + subcategory)

    return path

if __name__ == "__main__":
    sites = ['health.com', 'fifa.com', 'hardwarecentral.com', 'diabetes.org', 'yahoo.com']
    # Right: 'health.com', 'fifa.com', 'hardwarecentral.com', 'diabetes.org'
    # Wrong: 'yahoo.com' : Root/Sports -- Root/Sports/Basketball
    tec = 100
    tes = 0.6
    account_key = 'VpF0+1+uCEJrUKT5cFOV7eeG8cowehPtdV+sgVA4Tw0'
    for site in sites:
        print 'Classifying...'
        cate = classify(account_key, 'root', site, tec, tes, 'Root')
        print 'Classification: ', cate
        print ''
