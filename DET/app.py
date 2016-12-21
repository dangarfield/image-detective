import fnmatch
import os
import argparse

import generate_image_utils
import hash_generator
import hash_store
import feature_identifier


SRC = "images-src/"
QUERY = "images-query/"
QUERY_FEATURES = QUERY + "features/"
INDEX = "images-index/"
INDEX_FEATURES = INDEX + "features/"

def clean_files():
    generate_image_utils.remove_generated_images(INDEX, INDEX_FEATURES)
    generate_image_utils.remove_generated_images(QUERY, QUERY_FEATURES)

def clean_index():
    hash_store.delete_index()

def hash_and_index_full_and_features(filename):
    # Generate hash and index for master image
    hash_data = hash_generator.generate_hashes_for_image(INDEX + filename)
    hash_store.store_hash(INDEX + filename, hash_data, 'full')

    # Identify features and create individual feature images
    generated_feature_files = feature_identifier.generateFeatureImage(INDEX, INDEX_FEATURES, filename)
    for generated_feature_file in generated_feature_files:

        # Generate hash and index for feature image
        hash_data = hash_generator.generate_hashes_for_image(generated_feature_file)
        hash_store.store_hash(INDEX + filename, hash_data, 'feature',generated_feature_file)

def query(filename, hash_type, use_full, use_features):

    query_data = {}
    query_data['hash_data_features'] = []

    # Remove temporary query images
    generate_image_utils.remove_generated_images(QUERY, QUERY_FEATURES)

    # Move image to query folder, and generate hash
    generate_image_utils.generate_detect_image(SRC, QUERY, filename)
    query_data['hash_data_full'] = hash_generator.generate_hashes_for_image(QUERY + filename)
    
    # Identify features, create individual feature images and get their hashes
    generated_feature_files = feature_identifier.generateFeatureImage(QUERY, QUERY_FEATURES, filename)
    for generated_feature_file in generated_feature_files:
        query_data['hash_data_features'].append(hash_generator.generate_hashes_for_image(generated_feature_file))

    # Search for hashes
    results = hash_store.query_with_features(query_data['hash_data_full'], query_data['hash_data_features'], hash_type, use_full, use_features)
    # Print results in a nice format envoked from the parent method
    return results

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
        row.append(result.split("/", 1)[1])
    return row

def write_csv(csv_name, rows):
    import csv

    with open(csv_name, 'wb') as outfile:
        writer = csv.writer(outfile)
        header = ['type', 'file', 'total', 'totalPositive', 'totalNegative', 'files']
        writer.writerow(header)

        for row in rows:
            writer.writerow(row)

    print "Created CSV for results: " + csv_name

def initialise():
    parser = argparse.ArgumentParser()
    parser.add_argument("method", help="The type of method you intend to execute, options are: clean-files, clean-index, generate, index, query")
    parser.add_argument("-i", "--image", help="For indexing or querying, if you only want to run for one specific image, by default, it is all")
    parser.add_argument("-a", "--algo", help="For querying, if you want to run for one hash algorithm type, options are: ahash, phash, dhash. Default is all hash types as separate queries")
    parser.add_argument("-fl", "--full", help="For indexing or querying, if you want to run for just full image hashes, no feature hashes", action='store_true')
    parser.add_argument("-ft", "--feature", help="For querying, if you want to run for just features image hashes, no full hashes", action='store_true')
    args = parser.parse_args()
    # print "   Method > " + args.method
    # print "   Image > " + str(args.image)
    # print "   Algo > " + str(args.algo)
    # print "   Full > " + str(args.full)
    # print "   Feature > " + str(args.feature)


    ####### CLEAN FILES #######
    if args.method == "clean-files":
        clean_files()
        print "Removed all generated files"

    ####### CLEAN INDEX #######
    elif args.method == "clean-index":
        clean_index()
        print "Removed all index data"

    ####### GENERATE #######
    elif args.method == "generate":
        file_filter = "*.*"
        if args.image is None:
            clean_files()
        else:
            file_filter = args.image

        print "Generating test images - " + file_filter

        src_files = fnmatch.filter(os.listdir(SRC), file_filter)
        for src_file in src_files:
            print src_file
            generate_image_utils.generate_image_variants(SRC, INDEX, src_file)

    ####### INDEX #######
    elif args.method == "index":
        file_filter = "*.*"
        if args.image is None:
            clean_index()
        else:
            file_filter = args.image

        print "Create hashes and index, generate feature images, create feature hashes and index features for all - " + file_filter
        index_files = fnmatch.filter(os.listdir(INDEX), file_filter)
        for index_file in index_files:
            print index_file
            hash_and_index_full_and_features(index_file)


    ####### QUERY #######
    elif args.method == "query":

        # Note: I had a first attempt that displayed every match from every feature (eg, very verbose) but I tweaked things and need to add it back in

        file_filter = "*.*"
        if args.image is not None:
            file_filter = args.image

        hash_types = ['phash', 'dhash', 'ahash']
        if args.algo is not None:
            hash_types = [args.algo]
        
        use_full = True
        if args.feature is True:
            use_full = False
        use_feature = True
        if args.full is True:
            use_feature = False

        
        print "Create hashes, generate hash images, create feature hashes and then search full and features for images"

        rows = []
        files = fnmatch.filter(os.listdir(SRC), file_filter)
        for hash_type in hash_types:
            for filename in files:
                print filename + " - " + hash_type + " - " + str(use_full) + " - " + str(use_feature)
                results = query(filename, hash_type, use_full, use_feature)
                rows.append(generate_csv_row(filename, hash_type, results))

        csv_name = "query_"+file_filter.replace("*.*","all-images")+"_"+("-".join(hash_types))+"_full-"+str(use_full)+"_feature-"+str(use_feature)+".csv"
        write_csv(csv_name, rows)


    else:
        parser.print_help()




initialise()
