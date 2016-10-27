import urllib2
import json
import base64
import summary


def query_bing(enc_site, enc_query, sub_sample, account_key):
    account_key_enc = base64.b64encode(account_key+':'+account_key)
    headers = {'Authorization': 'Basic '+account_key_enc}
    bing_url = 'https://api.datamarket.azure.com/Data.ashx/Bing/SearchWeb/v1/Composite?Query=%27site%3a'+enc_site+'%20'+enc_query+'%27&$top=4&$format=json'
    req = urllib2.Request(bing_url, headers=headers)
    response = urllib2.urlopen(req)
    result = json.loads(response.read())
    num = result['d']['results'][0]['WebTotal']
    
    # get top 4 pages returned by Bing
    # line = subcategory + ' ' + str(num) + ' ' + enc_query
    for i in range(min(len(result['d']['results'][0]['Web']), 4)):
        address = result['d']['results'][0]['Web'][i]['Url']
        sub_sample.add(str(address))
        # line += ' ' + address
    # file_h.write(line + '\n')
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
        probes = compose_prob('./probes/' + category.lower()+'.txt')
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
            # num = query_bing(site, prob, sub_sample, account_key)
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
    sites = ['diabetes.org']
    tec = 100
    tes = 0.6

    for site in sites:
        print 'Classifying...'
        file_h = open(site + '_query.txt', 'r')
        cache = {}
        for line in file_h:
            words = line.split()
            cache[words[2]] = [words[1]] + words[3:]
        doc_dic = {}
        cate = classify(account_key, 'Root', site, tec, tes, 'Root', doc_dic, cache)
        file_h.close()
        print 'Classification: ' + cate + '\n'
        doc_sample = combine_set(doc_dic)
        for node in doc_sample.keys():
            print node, len(doc_sample[node])
        summary.generate_summary(doc_sample, cate, site)
