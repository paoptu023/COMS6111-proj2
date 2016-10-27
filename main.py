import urllib2
import json
import base64
import os.path
import summary


def query_bing(enc_site, enc_query, sample, account_key):
    account_key_enc = base64.b64encode(account_key+':'+account_key)
    headers = {'Authorization': 'Basic '+account_key_enc}
    bing_url = 'https://api.datamarket.azure.com/Data.ashx/Bing/SearchWeb/v1/Composite?Query=%27site%3a'+enc_site+'%20'+enc_query+'%27&$top=4&$format=json'
    req = urllib2.Request(bing_url, headers=headers)
    response = urllib2.urlopen(req)
    result = json.loads(response.read())
    num = result['d']['results'][0]['WebTotal']
    
    # get top 4 pages returned by Bing
    line = enc_query + ' ' + str(num)
    for i in range(min(len(result['d']['results'][0]['Web']), 4)):
        address = result['d']['results'][0]['Web'][i]['Url']
        address = address.encode('utf-8')
        sample.add(address)
        line += ' ' + address
    query_cache.write(line + '\n')
    return float(num)


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


def combine_set(doc_dic):
    doc_sample = {}
    for query_path in doc_dic.keys():
        categories = query_path.split('/')
        for c in categories:
            if c not in doc_sample:
                doc_sample[c] = doc_dic[query_path]
                print 'new ' + c, len(doc_sample[c])
            else:
                tmp = doc_sample[c] | doc_dic[query_path]
                doc_sample[c] = tmp
                print 'add ' + c, len(doc_sample[c])
    return doc_sample


def classify(account_key, category, site, tec, tes, path, doc_dic, cache):
    try:
        probes = compose_prob('./query/' + category.lower()+'.txt')
    except Exception:
        return path
    cov = {}
    spec = {}
    doc_dic[path] = set()
    for subcategory in probes.keys():
        if subcategory not in cov:
            cov[subcategory] = 0
            spec[subcategory] = 0.0
        for prob in probes[subcategory]:
            if not cache:
                num = query_bing(site, prob, doc_dic[path], account_key)
            else:
                num = float(cache[prob][0])
                for i in range(1, len(cache[prob])):
                    doc_dic[path].add(cache[prob][i])
            cov[subcategory] += num

    total = float(sum(cov.values()))

    for subcategory in spec.keys():
        spec[subcategory] = cov[subcategory] / total
        print 'for ', subcategory, ' : '
        print '     Specificity : ', spec[subcategory]
        print '     Coverage    : ', cov[subcategory]
        if spec[subcategory] > tes and cov[subcategory] > tec:
            path = classify(account_key, subcategory, site, tec, tes, path + '/' + subcategory, doc_dic, cache)

    return path


if __name__ == "__main__":
    # sites = ['health.com', 'fifa.com', 'hardwarecentral.com', 'diabetes.org', 'yahoo.com']
    # Right: 'health.com', 'fifa.com', 'hardwarecentral.com', 'diabetes.org'
    # Wrong: 'yahoo.com' : Root/Sports -- Root/Sports/Basketball
    # account_key = 'VpF0+1+uCEJrUKT5cFOV7eeG8cowehPtdV+sgVA4Tw0'
    account_key = 'HIWkFhlcqfV0SsO9ac7smysylCtGDsuMVyqgSWPPDZI'
    sites = ['hardwarecentral.com']
    tec = 100
    tes = 0.6

    for site in sites:
        print 'Classifying', site
        file_path = './query/' + site + '_query.txt'

        cache = {}
        # use cached query history if file exists
        if os.path.exists(file_path):
            query_cache = open(file_path, 'r')
            for line in query_cache:
                words = line.split()
                cache[words[0]] = [words[1]] + words[2:]
        else:
            query_cache = open(file_path, 'w')

        doc_dic = {}
        cate = classify(account_key, 'Root', site, tec, tes, 'Root', doc_dic, cache)
        query_cache.close()
        print 'Classification: ' + cate + '\n'

        # create content summary
        doc_sample = combine_set(doc_dic)
        for node in doc_sample.keys():
            print node, len(doc_sample[node])
        summary.generate_summary(doc_sample, cate, site)
