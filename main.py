from subprocess import check_output
import os.path
import requests
import urllib2
import json
import base64
import re
import sys


def query_bing(enc_query, sample):
    account_key_enc = base64.b64encode(account_key + ':' + account_key)
    headers = {'Authorization': 'Basic '+account_key_enc}
    bing_url = 'https://api.datamarket.azure.com/Data.ashx/Bing/SearchWeb/v1/Composite?Query=%27site%3a'+site+'%20'+enc_query+'%27&$top=4&$format=json'
    req = urllib2.Request(bing_url, headers=headers)
    response = urllib2.urlopen(req)
    result = json.loads(response.read())
    # get the total number of matched docs
    num = result['d']['results'][0]['WebTotal']
    # get top 4 pages returned by Bing
    new_line = enc_query + ' ' + str(num)
    for i in range(min(len(result['d']['results'][0]['Web']), 4)):
        address = result['d']['results'][0]['Web'][i]['Url'].encode('utf-8')
        sample.add(address)
        new_line += (' ' + address)
    query_cache.write(new_line + '\n')
    return float(num)


def compose_prob(filename):
    # get all query from the file and compose the query send to Bing
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


def combine_set():
    # Combine and eliminate the sample documents
    samples = {}
    for query_path in doc_dic.keys():
        categories = query_path.split('/')
        for c in categories:
            if c not in samples:
                samples[c] = doc_dic[query_path]
                print 'new ' + c, len(samples[c])
            else:
                samples[c] |= doc_dic[query_path]
                print 'add ' + c, len(samples[c])
    return samples


def classify(category, path):
    # Classify procedure
    if os.path.exists('./query/' + category + '.txt'):
        probes = compose_prob('./query/' + category + '.txt')
    else:
        return path
    cov = {}
    spec = {}
    doc_dic[path] = set()
    for subcategory in probes.keys():
        if subcategory not in cov:
            cov[subcategory] = 0
            spec[subcategory] = 0.0
        for prob in probes[subcategory]:
            if prob in cache:
                num = float(cache[prob][0])
                for i in range(1, len(cache[prob])):
                    doc_dic[path].add(cache[prob][i])
            else:
                num = query_bing(prob, doc_dic[path])
            cov[subcategory] += num
    total = float(sum(cov.values()))
    for subcategory in spec.keys():
        spec[subcategory] = cov[subcategory] / total
        print 'for ', subcategory, ' : '
        print '     Specificity : ', spec[subcategory]
        print '     Coverage    : ', cov[subcategory]
        if spec[subcategory] > tes and cov[subcategory] > tec:
            path = classify(subcategory, path + '/' + subcategory)
    return path


def generate_summary(path):
    # process sample documents from urls
    nodes = path.split('/')
    # do not have to deal with level 2 categories, only consider the first 2 nodes in path
    for i in range(min(len(nodes), 2)):
        print 'Creating Content Summary for: ' + nodes[i]
        f = open('./summary/' + nodes[i] + '-' + site + '.txt', 'w')
        content_summary = {}
        url_set = doc_sample[nodes[i]]
        j = 1
        for url in url_set:
            print str(j), '/', len(url_set), ' url'
            j += 1
            print 'Getting page: ' + url

            # check HTTP header and process only text html pages
            r = requests.get(url, allow_redirects=False)
            if 'text/html' in r.headers['content-type']:
                # retrieve page content
                page_content = ''
                try:
                    page_content = check_output('lynx --dump \'' + url + '\'', shell=True)
                except Exception:
                    pass
                end = page_content.find('\nReferences\n')
                if end > -1:
                    page_content = page_content[:end]

                page_content = page_content.lower()
                terms = process_page(page_content)
                for term in terms:
                    if term in content_summary:
                        content_summary[term] += 1
                    else:
                        content_summary[term] = 1
            else:
                print 'Skipped, not html'
            print ''

        for term in sorted(content_summary):
            f.write(term + '#' + str(float(content_summary[term])) + '\n')
        f.close()


def process_page(page_content):
    # Parse document
    output = ''
    skip_bracket = False
    add_space = False
    for i in range(len(page_content)):
        char = page_content[i]
        if not skip_bracket:
            if char == '[':
                skip_bracket = True
                if add_space:
                    output += ' '
                    add_space = False
            else:
                if re.match(r'^[a-zA-Z]+\Z', char) is not None:
                    output += char
                    add_space = True
                else:
                    if add_space:
                        output += ' '
                        add_space = False
        else:
            if char == ']':
                skip_bracket = False
    return set(output.split())

if __name__ == '__main__':
    account_key = sys.argv[1]
    tes = float(sys.argv[2])
    tec = int(sys.argv[3])
    site = sys.argv[4]

    print 'Classifying ... '
    file_path = './cache/' + site + '_query.txt'
    cache = {}
    doc_dic = {}

    # use cached query history if file exists
    if os.path.exists(file_path):
        query_cache = open(file_path, 'r')
        for line in query_cache:
            words = line.split()
            cache[words[0]] = [words[1]] + words[2:]
    else:
        query_cache = open(file_path, 'w')

    cate = classify('Root', 'Root')
    query_cache.close()
    print ''
    print 'Classification: ' + cate + '\n'
    print ''
    print 'Extracting topic content summaries...'
    # create content summary
    doc_sample = combine_set()
    for node in doc_sample.keys():
        print node, len(doc_sample[node])
    generate_summary(cate)
