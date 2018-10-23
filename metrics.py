from __future__ import division

import xmltodict
import json
import math

PATH_RESULT = '/home/berg/PycharmProjects/metrics/vector_model_metrics/result2.txt'
PATH_XML = '/home/berg/PycharmProjects/metrics/vector_model_metrics/cfquery.xml'

result = []


class DocPayload:
    def __init__(self, id, similarity):
        self.id = id
        self.similarity = similarity

    def m_print(self):
        print(self.id + '|' + self.similarity)


class Query:
    def __init__(self, id, query, result_list):
        self.id = id
        self.query = query
        self.result_list = result_list

    def m_print(self):
        print('QID|' + self.id + '|' + self.query)

        for doc_payload in self.result_list:
            doc_payload.m_print()


with open(PATH_RESULT) as file:
    query_id = 0
    query = ''
    doc_payload = []

    for line in file:
        if 'QID' in line:
            if len(doc_payload) > 0:
                query = Query(query_id, query, doc_payload)
                result.append(query)
                doc_payload = []
                payload = None

            line = line.split('|')
            query_id = line[1]
            query = line[2]
        else:
            line = line.split('|')
            doc_payload.append(DocPayload(line[0], line[1]))


with open(PATH_XML) as fd:
    doc = xmltodict.parse(fd.read())

queryJson = json.dumps(doc)
queryJson = json.loads(queryJson)

items = queryJson['items']['QUERY']

mrr = 0
for query in result: # Pra cada query
    result_list = query.result_list

    scores = []
    for item in items:  # Busca os documentos relevantes da query
        if int(query.id) == int(item['QueryNumber']):
            scores = item['Records']['Item']
            break

    position = 21
    for i, doc_payload in enumerate(result_list): # Pega os documentos relevantes
        founded = False

        for score in scores:
            if doc_payload.id == score['#text']:
                position = i + 1
                founded = True
                break

        if founded:
            break

    mrr += (1 / position)

mrr = mrr / len(items)
print('mrr @ 20:', mrr)

p = 10
precision = 0
for query in result: # Pra cada query
    result_list = query.result_list

    scores = []
    for item in items:  # Busca os documentos relevantes da query
        if int(query.id) == int(item['QueryNumber']):
            scores = item['Records']['Item']
            break

    result_list = result_list[0:p]
    count = 0
    for i, doc_payload in enumerate(result_list): # Pega os documentos relevantes
        for score in scores:
            if doc_payload.id == score['#text']:
                count += 1
                break

    precision += count / p

print('precision @ 10:', precision / len(items))

map = 0
for query in result: # Pra cada query
    result_list = query.result_list

    scores = []
    for item in items:  # Busca os documentos relevantes da query
        if int(query.id) == int(item['QueryNumber']):
            scores = item['Records']['Item']
            break

    relevance = 0
    precision = 0
    for i, doc_payload in enumerate(result_list): # Pega os documentos relevantes
        for score in scores:
            if doc_payload.id == score['#text']:
                relevance += 1
                precision += relevance / (i + 1)
                break

    if precision > 0 and relevance > 0:
        map += precision / relevance

map = map / len(items)

print('Map not interpolated @ 20:', map)

ndcg = 0
for query in result: # Pra cada query
    result_list = query.result_list

    scores = []
    for item in items:  # Busca os documentos relevantes da query
        if int(query.id) == int(item['QueryNumber']):
            scores = item['Records']['Item']
            break

    relevances = []
    for i, doc_payload in enumerate(result_list): # Pega os documentos relevantes
        founded = False

        for score in scores:
            if doc_payload.id == score['#text']:
                founded = True
                temp = 0
                for t in score['@score']:
                    temp += int(t)

                temp /= 8
                relevances.append(temp)
                break
        if not founded:
            relevances.append(0)

    relevance_great = sorted(relevances, reverse=True)

    for i, value in enumerate(relevances):
        if i > 0 and value != 0:
            relevances[i] = value / math.log(i + 1)

    for i, value in enumerate(relevance_great):
        if i > 0 and value != 0:
            relevance_great[i] = value / math.log(i + 1)

    r = []
    for i in range(len(relevances)):
        if relevances[i] != 0 and relevance_great[i] != 0:
            r.append(relevances[i] / relevance_great[i])
        else:
            r.append(0)

    ndcg += r[5]

print('NDCG at k=5:', ndcg / len(items))
