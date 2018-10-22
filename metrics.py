import xmltodict
import pprint
import json

PATH_RESULT = '/home/vdberg/PycharmProjects/vector_model_metrics/result.txt'
PATH_XML = '/home/vdberg/PycharmProjects/vector_model_metrics/cfquery.xml'

result = []


class DocPayload:
    def __init__(self, id, similarity):
        self.id = id
        self.similarity = similarity

    def m_print(self):
        print(self.id + '|' + self.similarity)


class QueryPayload:
    def __init__(self, id, query):
        self.id = id
        self.query = query

    def m_print(self):
        print('QID|' + self.id + '|' + self.query)


class Query:
    def __init__(self, query_payload, result_list):
        self.query_payload = query_payload
        self.result_list = result_list

    def m_print(self):
        self.query_payload.m_print()

        for doc_payload in self.result_list:
            doc_payload.m_print()


with open(PATH_RESULT) as file:
    payload = None
    doc_payload = []

    for line in file:
        if 'QID' in line:
            if len(doc_payload) > 0:
                query = Query(payload, doc_payload)
                result.append(query)
                doc_payload = []
                payload = None

            line = line.split('|')
            payload = QueryPayload(line[1], line[2])
        else:
            line = line.split('|')
            doc_payload.append(DocPayload(line[0], line[1]))


with open(PATH_XML) as fd:
    doc = xmltodict.parse(fd.read())

queryJson = json.dumps(doc)
queryJson = json.loads(queryJson)
print(queryJson['items']['QUERY'])

# for item in queryJson:
#     print(item)
