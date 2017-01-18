import sys
import fnmatch
import os
import pprint

import generate_image_utils
import hash_generator
import hash_store
import feature_identifier

###  Just a starter for ten, changed my approach ###


def index_all(folder, files, data_type):
    for file in files:
        # print file
        data = hash_generator.generate_hashes_for_image(folder + file)
        # print data
        hash_store.store_hash(data, data_type)


def detect_all(image, hash_type='ahash', data_type='full'):
    print "here - " + data_type
    path = 'images-src/gen/'
    if data_type == 'feature':
        path = path + 'features/'
    data = hash_generator.generate_hashes_for_image(path + image)
    result = hash_store.find_duplicates(data, hash_type=hash_type, data_type=data_type)
    #print (result['total'])
    return result


def compare_different_hashes(files, hash_types, files_to_detect, data_type='full'):
    compare_results = []
    for hash_type in hash_types:
        print hash_type

        for file_to_detect in files_to_detect:
            print " " + file_to_detect
            result = detect_all(file_to_detect, hash_type=hash_type, data_type=data_type)
            total = result['total']
            totalPositive = 0
            totalNegative = 0
            compare_result = {'type': hash_type,
                                'file': file_to_detect, 'total': total}

            for possible_file in files:
                possible_file_name = os.path.basename(possible_file)
                compare_result[possible_file_name] = False

            file_to_detect_no_ext = os.path.splitext((file_to_detect))[0].split('-')[0]
            if data_type == 'feature':
                file_to_detect_no_ext = os.path.splitext((file_to_detect))[0].split('_feature_')[0]
            #print("****** " + file_to_detect_no_ext + " *** ")

            for doc in result['docs']:
                matched_filename = os.path.basename(
                    doc['_source']['imgPath'])
                matched_filename_ext = os.path.splitext((matched_filename))[1]
                matched_filename_no_ext = os.path.splitext((matched_filename))[0]
                if data_type == 'feature':
                    matched_filename_no_ext = os.path.splitext((matched_filename))[0].split('_feature_')[0]
                #print("    ******" + matched_filename_no_ext + "***" + file_to_detect_no_ext + "***")
                if(matched_filename_no_ext.startswith(file_to_detect_no_ext+"-")):
                    #print "MATCH A - full"
                    totalPositive = totalPositive + 1
                elif(matched_filename_no_ext == file_to_detect_no_ext):
                    #print "MATCH B - full"
                    totalPositive = totalPositive + 1
                else:
                    totalNegative = totalNegative + 1
                # print matched_filename
                compare_result[matched_filename_no_ext + matched_filename_ext] = True

            compare_result['totalPositive'] = totalPositive
            compare_result['totalNegative'] = totalNegative
            # pprint.PrettyPrinter(indent=4).pprint(compare_result)
            compare_results.append(compare_result)
    # pprint.PrettyPrinter(indent=4).pprint(compare_results)
    return compare_results
        
def write_comparison_result(filename, files, compare_results):
    import csv
    with open(filename, 'wb') as outfile:
        writer = csv.writer(outfile)
        header = ['type', 'file', 'total', 'totalPositive', 'totalNegative']
        for possible_file in files:
            possible_file_name = os.path.basename(possible_file)
            header.append(possible_file_name)

        writer.writerow(header)
        for i in compare_results:
            row = [i['type'], i['file'], i['total'], i['totalPositive'], i['totalNegative']]
            for possible_file in files:
                possible_file_name = os.path.basename(possible_file)
                value = i[possible_file_name]
                row.append(value)
            writer.writerow(row)

def aggregate_results(compare_results):
    # nasty nasty way of quickly aggregating results
    key_list = {}
    for result in compare_results:
        total = result['total']
        data_type = result['type']
        totalNegative = result['totalNegative']
        totalPositive = result['totalPositive']
        file_feature = result['file']
        file_full = file_feature.split('_')[0] + "." + file_feature.split('.')[1]
        result['file'] = file_full
        key = data_type + "-" + file_full

        #print "Key - " + key
        if key_list.__contains__(key) == False:
            #print "Not in key list - adding"
            key_list[key] = result
        else:
            #print 'adding each of the fields'
            for k, v in result.items():
                #print k + " - " + str(v)
                if v == True:
                    key_list[key][k] = True
        

    aggregate_results = []
    for rk, rv in key_list.items():

        positive = 0
        negative = 0
        for k, v in rv.items():
            if v == True:
                k_full = k
                if '-' in k:
                    k_full = k.split('-')[0] + "." + k.split('.')[1]
                #else :
                    #print 'Get rid of me in a sec'
                if k_full.split('.')[0] == file_full.split('.')[0]:
                    #print "positive"
                    positive = positive + 1
                else:
                    #print "negative"
                    negative = negative + 1

        rv['totalNegative'] = negative
        rv['totalPositive'] = positive
        rv['total'] = negative + positive
        aggregate_results.append(rv)

    return aggregate_results

if __name__ == '__main__':

    sys.argv = []
    sys.argv.append('app.py')
    sys.argv.append('indexfeatures')

    if len(sys.argv) < 2:
        print "Must add methods"

    elif sys.argv[1] == 'generate':
        print "Generate test images"

        files = fnmatch.filter(os.listdir("images-src"), '*.*')

        generate_image_utils.remove_generated_images()

        for file in files:
            print file
            generate_image_utils.generate_image_variants(file)
        print "Generate test images: COMPLETE"

        
    elif sys.argv[1] == 'generatefeatures':
        print "Generate test images - features"

        files = fnmatch.filter(os.listdir("images-gen"), '*.*')

        #generate_image_utils.remove_generated_images()

        for file in files:
            print file
            feature_identifier.generateFeatureImage(file)
        print "Generate test images - features: COMPLETE"

        

    elif sys.argv[1] == 'index':
        print "Create hashes and add to index"

        files = fnmatch.filter(os.listdir("images-gen"), '*.*')
        hash_store.delete_index()
        for file in files:
            print file
        index_all("images-gen/", files, "full")
        print "Create hashes and add to index: COMPLETE"

    elif sys.argv[1] == 'indexfeatures':
        print "Create hashes and add to index - features"

        files = fnmatch.filter(os.listdir("images-gen/features"), '*.*')
        
        for file in files:
            print file
        index_all("images-gen/features/", files, "feature")
        print "Create hashes and add to index - features: COMPLETE"

    elif sys.argv[1] == 'detect':
        image = "1.jpg"
        print "Detecting duplicates for " + image
        result = detect_all(image)
        total = result['total']
        docs = result['docs']
        files = []
        for doc in docs:
            path = doc['_source']['imgPath']
            files.append(os.path.basename(path))
        files.sort()
        print(files)

    elif sys.argv[1] == 'compare':

        files = fnmatch.filter(os.listdir("images-gen"), '*.*')

        hash_types = ['ahash', 'phash', 'dhash']#, 'whash']
        
        files_to_detect = fnmatch.filter(os.listdir("images-src"), '*.*')
        generate_image_utils.generate_detect_images(files_to_detect)

        compare_results = compare_different_hashes(files, hash_types, files_to_detect)

        write_comparison_result("compare.csv", files, compare_results)

        print "Comparison complete, import compare.csv to test"
    
    elif sys.argv[1] == 'comparerotate':
        
        files = fnmatch.filter(os.listdir("images-gen"), '*.*')

        generate_image_utils.generate_detect_images_rotation("1.jpg")

        hash_types = ['ahash', 'phash', 'dhash']#, 'whash']
        files_to_detect = fnmatch.filter(os.listdir("images-src/gen"), '*.*')

        compare_results = compare_different_hashes(files, hash_types, files_to_detect)

        write_comparison_result("comparerotate.csv", files, compare_results)

        print "Comparison complete, import comparerotate.csv to test"


    elif sys.argv[1] == 'comparefeatures':
        
        files = fnmatch.filter(os.listdir("images-gen"), '*.*')

        hash_types = ['ahash', 'phash', 'dhash']#, 'whash']
        
        files_to_detect = fnmatch.filter(os.listdir("images-src/"), '*.*')
        generate_image_utils.generate_detect_images(files_to_detect)

        files_to_detect = fnmatch.filter(os.listdir("images-src/gen/features"), '*.*')
        compare_results = compare_different_hashes(files, hash_types, files_to_detect, data_type='feature')

        write_comparison_result("comparefeatures-individual.csv", files, compare_results)

        compare_results = aggregate_results(compare_results)
        write_comparison_result("comparefeatures-aggregated.csv", files, compare_results)

        print "Comparison complete, import comparefeatures-individual.csv and comparefeatures-individual.csv to test"

    else:
        print "No method called: " + sys.argv[1]