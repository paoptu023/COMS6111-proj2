import urllib2
import json
import base64
import summary


def query_bing(enc_site, enc_query, sub_sample):
    account_key = 'HIWkFhlcqfV0SsO9ac7smysylCtGDsuMVyqgSWPPDZI'
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
        print 'Getting page:', address
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


def classify(category, site, tec, tes, path, doc_dic, cache):
    try:
        probes = compose_prob('./probes/' + category.lower()+'.txt')
    except Exception:
        return path

    cov = {}
    spec = {}
    for subcategory in probes.keys():
        sub_sample = set()
        if subcategory not in cov:
            cov[subcategory] = 0
            spec[subcategory] = 0.0
        for prob in probes[subcategory]:
            # num = query_bing(site, prob, sub_sample)
            num = float(cache[prob][0])
            for i in range(1, len(cache[prob])):
                sub_sample.add(cache[prob][i])
            cov[subcategory] += num
        doc_dic[path + '/' + subcategory] = sub_sample

    total = sum(cov.values())

    for subcategory in spec.keys():
        spec[subcategory] = cov[subcategory]/total
    # print cov, spec, total
    sub = []
    for subcategory in spec.keys():
        if spec[subcategory]>tes and cov[subcategory]>tec:
            sub.append(subcategory)
    print sub

    if len(sub) != 0:
        for subc in sub:
            path = classify(subc, site, tec, tes, path+'/'+subc, doc_dic, cache)
    return path


if __name__ == "__main__":
    site = 'diabetes.org'
    tec = 100
    tes = 0.6
    file_h = open(site + '_query.txt', 'r')
    cache = {}
    for line in file_h:
        words = line.split()
        cache[words[2]] = [words[1]] + words[3:]

    doc_dic = {}
    path = classify('Root', site, tec, tes, 'Root', doc_dic, cache)
    file_h.close()
    print path
    # file = open('sample.txt', 'r')
    # doc_dic = {}
    # for line in file:
    #     words = line.split()
    #     if words[0] not in doc_dic:
    #         doc_dic[words[0]] = set()
    #     doc_dic[words[0]].add(words[1])

    doc_sample = combine_set(doc_dic)
    for node in doc_sample.keys():
        print node, len(doc_sample[node])
    summary.generate_summary(doc_sample, path, site)


