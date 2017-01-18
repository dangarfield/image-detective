import os
import re
import requests
import urllib3
urllib3.disable_warnings()
import imagehash
import aws_utils

from datetime import datetime
#res = requests.get('http://localhost:9200')
#print(res.content)

from elasticsearch import Elasticsearch

def bonzai_connection():
    url = 'https://1rvw9vpa8m:6hk82xtsuq@first-cluster-1433751595.eu-west-1.bonsaisearch.net'
    auth = re.search('https\:\/\/(.*)\@', url).group(1).split(':')
    host = url.replace('https://%s:%s@' % (auth[0], auth[1]), '')

    # Connect to cluster over SSL using auth for best security:
    es_header = [{
        'host': host,
        'port': 443,
        'use_ssl': True,
        'http_auth': (auth[0],auth[1])
    }]
    return Elasticsearch(es_header)

# es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
es = Elasticsearch([{'host': 'search-content-hackathon-dg-test-pn4ggl2rcwaa5cxsy5ym53qkoa.eu-central-1.es.amazonaws.com', 'port': 443, 'use_ssl': True}])
# es = bonzai_connection()
es.ping()

TYPES = ['ahash', 'phash', 'dhash']#, 'whash', 'whashDb4']

def set_connection(domain, port):
    es = Elasticsearch([{'host': domain, 'port': port}])

def delete_index(index_name='local'):
    es.indices.delete(index=index_name, ignore=[400, 404])
    es.indices.create(index=index_name)


def store_hash(imgPath, data, data_type, imgPathFeature='', index_name='local'):

    # Note - This is a really horrible way of querying in order to use XOR type distances (eg, fuzzy matching / levenshtein distance)

    print "Storing hash for:    " + imgPath + " - " + data_type + " - " + index_name

    baseImage = imgPath

    doc = {
        'timestamp': datetime.now(),
        'imgPath': baseImage,
        #'ahash': str(data['ahash']),
        #'ahashStr': ahashStr,
        #'ahashBinary': ahashBinary,
        #'phash': str(data['phash']),
        #'dhash': str(data['dhash']),
        #'whash': str(data['whash']),
        #'whashDb4': str(data['whashDb4']),
        'data_type': data_type
    }

    specificImage = imgPath
    if imgPathFeature != '':
        specificImage = imgPathFeature
        doc['imgPathFeature'] = specificImage

    for hash_type in TYPES:
        hash = data[hash_type]
        hashStr = str(hash)
        # this won't be right for non 16, need to calculate the zfill
        # dynamically
        hashBinary = bin(int(hashStr, 16))[2:].zfill(16)
        doc[hash_type + "-binary"] = hashBinary
        doc[hash_type + "-string"] = hashStr

        
        count = 0
        for x in hash.hash:
            for y in x:
                doc[hash_type + '-' + str(count)] = bool(y)
                count = count + 1


        #print(doc)

    
    res = es.index(index=index_name, doc_type='hash', id=specificImage, body=doc)
    # print(res['created'])

    #res = es.get(index=index_name, doc_type='hash', id=specificImage)
    # print(res['_source'])

    es.indices.refresh(index=index_name)



def query_with_features(hash_data_full, hash_data_features, hash_type, use_full, use_features, index_name='local'):
    
    # Note - This is a really horrible way of querying in order to use XOR type distances (eg, fuzzy matching / levenshtein distance)

    doc = {
        "query": {
            "bool": {
                "should": []
            }
        }
    }

    if use_full:
        full_query = {
            'bool': {
                'must': {
                    'term': {
                        'data_type': 'full'
                    }
                },
                'minimum_should_match': "75%",
                'should': []
            }
        }
        hash = hash_data_full[hash_type]
        #print str(hash)
        count = 0
        for x in hash.hash:
            for y in x:
                # print str(count) + " - " + str(bool(y))
                term = {'term': {hash_type + '-' + str(count): bool(y)}}
                full_query['bool']['should'].append(term)
                count = count + 1

        doc['query']['bool']['should'].append(full_query)
    
    if use_features:
        for hash_data_feature in hash_data_features:
            feature_query = {
                'bool': {
                    'must': {
                        'term': {
                            'data_type': 'feature'
                        }
                    },
                    'minimum_should_match': "85%",
                    'should': []
                }
            }
            hash = hash_data_feature[hash_type]
            #print str(hash)
            count = 0
            for x in hash.hash:
                for y in x:
                    # print str(count) + " - " + str(bool(y))
                    term = {'term': {hash_type + '-' + str(count): bool(y)}}
                    feature_query['bool']['should'].append(term)
                    count = count + 1
            doc['query']['bool']['should'].append(feature_query)


    res = es.search(index=index_name, doc_type='hash', body=doc,
                    _source_include=['imgPath', 'imgPathFeature', 'data_type'], size=500)

    # There will be a better way of grouping and ordering the results with the search engine itself, but without consulting the API docs and for a quick fix, I'll just do it here

    result_docs = set()
    for result_doc in res['hits']['hits']:
        result_docs.add(result_doc['_source']['imgPath'])
    
    print "Found " + str(len(result_docs)) + " results for query"



    return result_docs