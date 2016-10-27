from subprocess import check_output
import re


def generate_summary(doc_sample, path, site):
    nodes = path.split('/')
    for i in range(min(len(nodes), 2)):
        file = open(nodes[i] + '-' + site + '.txt', 'w')
        content_summary = {}
        url_set = doc_sample[nodes[i]]
        for url in url_set:
            # process only html files
            if url.split('.')[-1] == 'html':
                # retrieve page content
                page_content = ''
                try:
                    page_content = check_output("lynx --dump " + url, shell=True)
                except Exception:
                    pass
                end = page_content.find('\nReferences\n')
                if end > -1:
                    page_content = page_content[:end]

                page_content = page_content.lower()
                words = process_page(page_content)
                for word in words:
                    if word in content_summary:
                        content_summary[word] += 1
                    else:
                        content_summary[word] = 1
        for word in sorted(content_summary):
            file.write(word + '#' + str(float(content_summary[word])) + '\n')
        file.close()
    return


def process_page(page_content):
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


