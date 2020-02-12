import json

def arrowFormat(raw):
    return ( eval(x) for x in raw.split('\n') )

def pairFormat(raw):
    for x in raw.split('\n'):
        x = x[1:-1].split('), (')
        x = [s.replace(',', ' ,') for s in x]
        yield(x)


raw = open('scope_raw').read().strip()
output = pairFormat(raw)
config = json.load(open('scope_config.json'))
qdict = config['qdict']
prep = config['prep']

def check(x, y):
    if y in {v[0] for v in qdict.values()}: 
        x, y = y, x
    for k, v in qdict.items():
        if x == v[0]:
            for k1, v1 in qdict.items():
                if y == v1[1]:
                    return (k1, k)

def getorder(S):
    O = []
    V = set(qdict)
    while V:
        for k in V:
            if not {h for h in V if (k, h) in S}:
                O.append(k)
                V.remove(k)
                S = {(x, y) for (x, y) in S if y != k}
                break
    
    return ' > '.join(O)


def scope(link):
    line = set()
    med = set()
    for p in link:
        if 'np' not in p:
            x, *_, y = p.split()
            if x in prep: med.add(y)
            if y in prep: med.add(x)
            if not(x in prep or y in prep):
                line.add(check(x, y))

    if med: line.add(check(*tuple(med)))
    line.remove(None)
    return getorder(line)
  
    
if __name__ == '__main__':            
    print('-' * 10 + 'each' + '-' * 10)
    results = set()
    for links in output:
        res = scope(links)
        print(res)
        results.add(res)
    
    print('-' * 10 + 'summary' + '-' * 10)
    for res in sorted(results):
        print(res)
    print('Total:',  len(results))
