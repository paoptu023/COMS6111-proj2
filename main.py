import urllib2
import json
import base64


def query_bing(enc_site, enc_query):
    account_key = 'VpF0+1+uCEJrUKT5cFOV7eeG8cowehPtdV+sgVA4Tw0'
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


def classify(category, site, tec, tes, path):
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
            num = float(query_bing(site,prob))
            print prob, num
            cov[subcategory] += num

    total = sum(cov.values())

    for subcategory in spec.keys():
        spec[subcategory] = cov[subcategory]/total
    print cov, spec, total
    sub = []
    for subcategory in spec.keys():
        if spec[subcategory]>tes and cov[subcategory]>tec:
            sub.append(subcategory)
    print sub

    if len(sub) != 0:
        for subc in sub:
            path = classify(subc.lower(), site, tec, tes, path+'/'+subc.lower())
    return path

if __name__ == "__main__":
    site = 'diabetes.org'
    tec = 100
    tes = 0.6
    path = ''
    print classify('root', site, tec, tes, 'root')