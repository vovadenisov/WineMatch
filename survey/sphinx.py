from django.db import connections

SPHINX_LIMIT = 10
SPHINX_INDEX = 'wines'

def _search(query):
    #db = pymysql.connect(**SPHINX_CONNECTION)
    cur = connections['sphinx'].cursor()
    qry = '''
        SELECT id, weight() FROM {} WHERE MATCH(%s) LIMIT {}
        OPTION field_weights=(title=100, tranlist_title=100, description=30, stylistic=30)
    '''.format(SPHINX_INDEX, SPHINX_LIMIT)

    cur.execute(qry, (query,))
    rows = cur.fetchall()
    cur.close()
    return {r[0]: r[1] for r in rows}

def search(query):
    res = _search(query)
    res_extended = _search(query + '*')
    for id_, weight in res_extended.items():
        res[id_] = max(weight, res.get(id_, 0))
    return [
        item[0] for item in 
        sorted(
            res.items(),
            key=lambda i: i[1],
            reverse = True
        )
    ][:SPHINX_LIMIT]
