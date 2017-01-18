import fnmatch
import os
import argparse

import app_services
import generate_image_utils
import hash_store
import aws_utils


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
        app_services.clean_files()
        print "Removed all generated files"

    ####### CLEAN INDEX #######
    elif args.method == "clean-index":
        app_services.clean_index()
        print "Removed all index data"

    ####### GENERATE #######
    elif args.method == "generate":
        file_filter = "*.*"
        if args.image is None:
            app_services.clean_files()
        else:
            file_filter = args.image

        print "Generating test images - " + file_filter

        src_files = []
        for root, dirs, files in os.walk(app_services.SRC, topdown=False):
            for name in files:
                folder = root.replace(app_services.SRC, "") + "/"
                # print folder + name
                src_files.append({'folder':folder,'file': name})

        for i, src_file in enumerate(src_files):
            folder = src_file['folder']
            file = src_file['file']
            print str(i+1) + " of " + str(len(src_files)) + " - " + folder + file
            generate_image_utils.generate_image_variants(app_services.SRC, app_services.INDEX, folder, file)

    ####### UPLOAD INDEX IMAGES TO S3 #######
    elif args.method == "upload-index":
        print "Uploading all generated index files to s3"
        # index_files = fnmatch.filter(os.listdir(app_services.INDEX), "*.*")
        # aws_utils.upload_index_files_to_s3(app_services.INDEX, index_files)

        aws_utils.delete_s3_bucket_contents(aws_utils.INDEX_BUCKET_NAME)
        index_files = []
        for root, dirs, files in os.walk(app_services.INDEX, topdown=False):
            for name in files:
                folder = root.replace(app_services.INDEX, "") + "/"
                # print folder + name
                index_files.append({'folder':folder,'file': name})

        for i, index_file in enumerate(index_files):
            folder = index_file['folder']
            file = index_file['file']
            print str(i+1) + " of " + str(len(index_files)) + " - " + folder + file
            aws_utils.upload_file_to_s3(aws_utils.INDEX_BUCKET_NAME, app_services.INDEX, folder, file)
    
    ####### UPLOAD QUERY (IMAGES) TO S3 #######
    elif args.method == "upload-query":
        print "Uploading all src query files to s3"
        aws_utils.delete_s3_bucket_contents(aws_utils.QUERY_BUCKET_NAME)
        index_files = []
        for root, dirs, files in os.walk(app_services.SRC, topdown=False):
            for name in files:
                folder = root.replace(app_services.SRC, "") + "/"
                # print folder + name
                index_files.append({'folder':folder,'file': name})

        for i, index_file in enumerate(index_files):
            folder = index_file['folder']
            file = index_file['file']
            print str(i+1) + " of " + str(len(index_files)) + " - " + folder + file
            aws_utils.upload_file_to_s3(aws_utils.QUERY_BUCKET_NAME, app_services.SRC, folder, file)


    ####### INDEX #######
    elif args.method == "index":
        file_filter = "*.*"
        if args.image is None:
            hash_store.delete_index()
        else:
            file_filter = args.image

        print "Create hashes and index, generate feature images, create feature hashes and index features for all - " + file_filter
        index_files = fnmatch.filter(os.listdir(app_services.INDEX), file_filter)
        for index_file in index_files:
            print index_file
            app_services.hash_and_index_full_and_features(app_services.INDEX, app_services.INDEX_FEATURES, index_file)

    ####### INDEX AWS #######
    elif args.method == "index-aws":
        
        index_name = aws_utils.INDEX_BUCKET_NAME

        print "Download images from S3, create hashes and index, generate feature images, create feature hashes and index features"

        files = []
        if args.image is None:
            hash_store.delete_index(index_name=index_name)
            app_services.clean_files()
            files = aws_utils.get_all_files_in_index_bucket()
        else:
            files.append(args.image)

        for file in files:
            aws_utils.download_index_file(app_services.INDEX, file)
            app_services.hash_and_index_full_and_features(app_services.INDEX, app_services.INDEX_FEATURES, file, index_name=index_name)
        

    ####### QUERY #######
    elif args.method == "query":

        # Note: I had a first attempt that displayed every match from every feature (eg, very verbose) but I tweaked things and need to add it back in

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

        from timeit import default_timer as timer
        start = timer()
        rows = []

        files = []
        csv_search_type = ''
        if args.image is None:
            files = fnmatch.filter(os.listdir(app_services.SRC), "*.*")
            csv_search_type = 'all-images'
        else:
            files.append(args.image)
            csv_search_type = args.image

        for hash_type in hash_types:
            for filename in files:
                print filename + " - " + hash_type + " - " + str(use_full) + " - " + str(use_feature)
                # Move to query folder
                generate_image_utils.generate_detect_image(app_services.SRC, app_services.QUERY, filename)
                # Execute query from query folder
                results = app_services.query(filename, hash_type, use_full, use_feature)
                rows.append(app_services.generate_csv_row(filename, hash_type, results))

        end = timer()
        print "Took: " + str(int((1000 * (end - start)))) + "ms"
        csv_name = "query_"+csv_search_type+"_"+("-".join(hash_types))+"_full-"+str(use_full)+"_feature-"+str(use_feature)+".csv"
        app_services.write_csv(csv_name, rows)


    ####### QUERY AWS #######
    elif args.method == "query-aws":

        # Note: I had a first attempt that displayed every match from every feature (eg, very verbose) but I tweaked things and need to add it back in

        index_name = aws_utils.INDEX_BUCKET_NAME

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

        from timeit import default_timer as timer
        start = timer()
        rows = []

        files = []
        csv_search_type = ''
        if args.image is None:
            files = aws_utils.get_all_files_in_query_bucket()
            csv_search_type = 'all-images'
        else:
            files.append(args.image)
            csv_search_type = args.image

        for hash_type in hash_types:
            for filename in files:
                print filename + " - " + hash_type + " - " + str(use_full) + " - " + str(use_feature)
                # Download to query folder
                dl_start = timer()
                aws_utils.download_query_file(app_services.QUERY, filename)
                dl_stop = timer()
                # Execute query from query folder
                results = app_services.query(filename, hash_type, use_full, use_feature, index_name=index_name)
                after_query = timer()
                rows.append(app_services.generate_csv_row(filename, hash_type, results))
        end = timer()
        
        print "Pre:   " + str(int((1000 * (dl_start - start)))) + "ms"
        print "DL:    " + str(int((1000 * (dl_stop - dl_start)))) + "ms"
        print "Query: " + str(int((1000 * (after_query - dl_stop)))) + "ms"
        print "CSV:   " + str(int((1000 * (end - after_query)))) + "ms"
        print "TOTAL: " + str(int((1000 * (end - start)))) + "ms"
        
        csv_name = "query-aws_"+csv_search_type+"_"+("-".join(hash_types))+"_full-"+str(use_full)+"_feature-"+str(use_feature)+".csv"
        app_services.write_csv(csv_name, rows)


    else:
        parser.print_help()




initialise()
