import fnmatch
import os
import argparse

import generate_image_utils
import hash_generator
import hash_store
import feature_identifier
import aws_utils

#HOME = "/tmp"
HOME = "/Users/DanGarfield/code/image-detective/assets"
SRC = HOME+"/images-src/"
QUERY = HOME+"/images-query/"
QUERY_FEATURES = QUERY + "features/"
INDEX = HOME+"/images-index/"
INDEX_FEATURES = INDEX + "features/"
REPORT = HOME+"/reports/"

def clean_files():
    generate_image_utils.remove_generated_images(INDEX, INDEX_FEATURES)
    generate_image_utils.remove_generated_images(QUERY, QUERY_FEATURES)

def clean_index():
    hash_store.delete_index()
    hash_store.delete_index(aws_utils.INDEX_BUCKET_NAME)

def hash_and_index_full_and_features(index_folder, feature_folder, filename, index_name='local'):

    indexed_images = []
    # Generate hash and index for master image
    hash_data = hash_generator.generate_hashes_for_image(index_folder + filename)
    hash_store.store_hash(filename, hash_data, 'full', index_name=index_name)
    indexed_images.append(filename)

    # Identify features and create individual feature images
    generated_feature_files = feature_identifier.generateFeatureImage(index_folder, feature_folder, filename)
    print generated_feature_files
    for generated_feature_file in generated_feature_files:

        # Generate hash and index for feature image
        hash_data = hash_generator.generate_hashes_for_image(feature_folder + generated_feature_file)
        hash_store.store_hash(filename, hash_data, 'feature',generated_feature_file, index_name=index_name)
        indexed_images.append(generated_feature_file)
    return indexed_images

def query(filename, hash_type, use_full, use_features, index_name='local'):

    query_data = {}
    query_data['hash_data_features'] = []

    # Generate hash
    query_data['hash_data_full'] = hash_generator.generate_hashes_for_image(QUERY + filename)

    if use_features:
        # Identify features, create individual feature images and get their hashes
        generated_feature_files = feature_identifier.generateFeatureImage(QUERY, QUERY_FEATURES, filename)
        for generated_feature_file in generated_feature_files:
            query_data['hash_data_features'].append(hash_generator.generate_hashes_for_image(QUERY_FEATURES + generated_feature_file))

    # Search for hashes
    results = hash_store.query_with_features_fuzzy(query_data['hash_data_full'], query_data['hash_data_features'], hash_type, use_full, use_features, index_name=index_name)
    
    # Remove temporary query images
    #TODO - Improve this, we shouldn't really need to clean up the lambda storage
    generate_image_utils.remove_generated_images(QUERY, QUERY_FEATURES)

    # Print results in a nice format envoked from the parent method
    return list(results)

def isPositiveMatch(src_file, trg_file):
    # Just so I can tell if there it is matching the correct source images

    matchA = src_file
    matchB = trg_file
    
    if ("/" in src_file):
        matchA = matchA.split("/", 1)[1]
    if ("/" in trg_file):
        matchB = matchB.split("/", 1)[1]

    for sym in ["-", "_", "."]:
        if (sym in src_file):
            matchA = matchA.split(sym, 1)[0]
        if (sym in trg_file):
            matchB = matchB.split(sym, 1)[0]
        
    if matchA == matchB :
        return True
    else:
        return False

def generate_csv_row(filename, hash_type, results):
    results = sorted(results)
    pos = 0
    neg = 0
    for result in results:
        if isPositiveMatch(result, filename):
            pos = pos + 1
        else:
            neg = neg + 1

    #print ", ".join(results)
    #print str(pos) + " + " + str(neg) + " = " + str(len(results))
    row = [hash_type, filename, len(results), pos, neg]
    for result in results:
        row.append(result)
    return row

def write_csv(csv_name, rows):
    import csv

    if not os.path.exists(REPORT):
        os.makedirs(REPORT)

    with open(REPORT + csv_name, 'wb') as outfile:
        writer = csv.writer(outfile)
        header = ['type', 'file', 'total', 'totalPositive', 'totalNegative', 'files']
        writer.writerow(header)

        for row in rows:
            writer.writerow(row)

    print "Created CSV for results: " + REPORT + csv_name