import os, glob
import shutil
import argparse
import csv

import gdal2tiles
import cv2
import numpy as np
from osgeo import gdal

from download_maxar_images import *
from preprocessing_utils import *


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--z', type=int, default=18, help='Zoom levels to render (format:\'2-5\', \'10-\' or \'10\')') 
    parser.add_argument('--p', type=int, default=4, help='Number of parallel processes to use for tiling, to speed-up the computation')
    parser.add_argument('--size', type=int, default=256, help='Width and height in pixel of a tile') 
    parser.add_argument('--threshold', type=int, default=500, help='Maximum number of white pixels allowed in cropped images') 
    
    parser.add_argument('--src', type=str, default='./images/', help='Source path for original image tiff files - TIFF files should be located in {src}/{imageID}/*.tiff')
    parser.add_argument('--des', type=str, default='../../data/delta/maxar/', help='Destination path for processed images')
    
    parser.add_argument('--d', type=str, required=True, help='Name of the disaster')
    
    parser.add_argument('--pre_post', type=str, default='./pre_post.csv', help='CSV file containing pre and post image id pairs')
    parser.add_argument('--pre_pre', type=str, default='./pre_pre.csv', help='CSV file containing pre1 and pre2 image id pairs')
    
    parser.add_argument('--download', type=bool, default=True, help='Option to download TIFF files from solara-maxar catalogue')
    
    args = parser.parse_args()
    return args


def create_tiles(z, p, size, source_path, destination_path):
    
    options = {'zoom':z,
        'nb_processes': p,
        'tile_size': size,
        'srs':'EPSG:4326'
        }
    
    gdal2tiles.generate_tiles(source_path, destination_path, **options)
    
    
def crop_images(z, p, size, src, des, all_img_ids):
    
    condition = '/*.tif'

    for img_id_folder in glob.glob(src + "*"):
        img_id = img_id_folder.split("/")[-1]
        if img_id in all_img_ids:
            img_id_des = os.path.join(des, img_id)
            zoom_level_des = os.path.join(img_id_des, str(z))
            if os.path.exists(zoom_level_des):
                print("Skipping: " + img_id + " - already cropped")
            else:
                if not os.path.exists(img_id_des):
                    os.mkdir(img_id_des)
                print("Processing: " + img_id)
                for file in glob.glob(img_id_folder + condition):
                    file_id = file.split("/")[-1].split(".")[-2]
                    converted_file = convert_srs(file)

                    save_cropped = os.path.join(des, img_id, file_id)
                    os.makedirs(save_cropped, exist_ok=True)

                    create_tiles(z, p, size, converted_file, save_cropped)

                    xfolderlist = glob.glob(save_cropped + '/{}/*'.format(str(z)))

                    for onexfolder in xfolderlist:
                        xylist = glob.glob(onexfolder+'/*.png')
                        for onepic in xylist:

                            onepicx = onepic.split('/')[-2]
                            onepicy = onepic.split('/')[-1][:-4]

                            aa1, aa2, _, _ = TileLatLonBounds(z, size, int(onepicx),int(onepicy))
                            mm1, mm2 = LatLonToMeters(z, size, aa1, aa2)
                            _, ans2 = MetersToTile(z, size, mm1, mm2)

                            new_y_x = str(ans2-1)+'_'+onepicx

                            newpath = os.path.join(des, img_id, str(z)) + "/"
                            os.makedirs(newpath, exist_ok=True)

                            newonepic = newpath+new_y_x+'.png'
                            shutil.move(onepic, newonepic)
                    shutil.rmtree(save_cropped)
            
    print("Completed cropping images")
    
    
def pair_images(z, src, des, disaster, pre_id, post_id, n):
    if not os.path.exists(des):
        os.mkdir(des)
        
    post_src_cond = src + post_id + "/{}/*.png".format(str(z))
    
    i = 0
    for img_path in glob.glob(post_src_cond):
        img = img_path.split("/")[-1]
        pre_src = src + pre_id + "/{}/".format(str(z)) + img
        if os.path.exists(pre_src):
            post_src = src + post_id + "/{}/".format(str(z)) + img
            
            pre_des = des + disaster + "_" + str(n).zfill(8) + "_pre_disaster_" + str(i) + ".png"
            post_des = des + disaster + "_" + str(n).zfill(8) + "_post_disaster_" + str(i) + ".png"

            shutil.copy2(pre_src, pre_des)
            shutil.copy2(post_src, post_des)
                        
            i += 1
    return i


def prune_images(z, path, threshold, all_image_ids):
    for img_id in glob.glob(path + "*"):
        img_id = img_id_folder.split("/")[-1]
        if img_id in all_img_ids:
            print("Pruning images for: " + img_id.split("/")[-1])
            allimagepaths = glob.glob(img_id + "/{}/*.png".format(str(z)))
            for imagepath in allimagepaths:

                img = cv2.imread(imagepath)
                num_white_pix = np.sum(img == 0)
                if num_white_pix > threshold:
                    os.remove(imagepath)
    print("Completed pruning images")
    
    
def convert_srs(src):
    des = src[:-11] + ".tif"
    options = {"dstSRS": "EPSG:4326", 
                "format": "GTiff"}
    gdal.Warp(des, src, **options)
    os.remove(src)
    return des


def get_img_pairs(args):
    pre_post_pair = []
    with open(args.pre_post, mode='r') as file:
        f = csv.reader(file)
        for line in f:
            tup = (line[0], line[1])
            pre_post_pair.append(tup)
            
    pre_pre_pair = []
    with open(args.pre_pre, mode='r') as file:
        f = csv.reader(file)
        for line in f:
            tup = (line[0], line[1])
            pre_pre_pair.append(tup)
            
    all_img_ids = set(())

    for pair in pre_post_pair:
        all_img_ids.add(pair[0])
        all_img_ids.add(pair[1])

    for pair in pre_pre_pair:
        all_img_ids.add(pair[0])
        all_img_ids.add(pair[1])
    
    return pre_post_pair, pre_pre_pair, all_img_ids


def produce_image_pairs(z, disaster, des, cropped_des, pre_post_pair, pre_pre_pair):
    pair_des = des + "images_256/" + disaster + "/"
    if not os.path.exists(pair_des):
        os.mkdir(pair_des)

    pair_count = 0

    pre_post_des = pair_des + "pre_post/"
    if not os.path.exists(pre_post_des):
        os.mkdir(pre_post_des)

    n = 1
    for pair in pre_post_pair:
        pre_post_des = pair_des + "pre_post/" + str(n).zfill(8) + "/"
        if not os.path.exists(pre_post_des):
            os.mkdir(pre_post_des)
        pre_id = pair[0]
        post_id = pair[1]
        pair_count += pair_images(z, cropped_des, pre_post_des, disaster, pre_id, post_id, n)
        n += 1

    pre_pre_des = pair_des + "pre_pre/"
    if not os.path.exists(pre_pre_des):
        os.mkdir(pre_pre_des)

    for pair in pre_pre_pair:
        pre_pore_des = pair_des + "pre_pre/" + str(n).zfill(8) + "/"
        if not os.path.exists(pre_pre_des):
            os.mkdir(pre_post_des)
        pre_id = pair[0]
        post_id = pair[1]
        pair_count += pair_images(z, cropped_des, pre_pre_des, disaster, pre_id, post_id, n)
        n += 1

    print("Finished producing " + str(pair_count) + " image pairs")


if __name__ == '__main__':
    
    args = parse_arguments()
    
    z = args.z
    p = args.p
    size = args.size
    threshold = args.threshold
    disaster = args.d
    
    src = os.path.join(args.src, disaster) + "/"
    des = args.des
    cropped_des = os.path.join(des, "cropped", disaster) + "/"n
    if not os.path.exists(cropped_des):
        os.mkdir(cropped_des)
    
    pre_post_pair, pre_pre_pair, all_img_ids = get_img_pairs(args)
    
    if args.download:
        download_image_ids(src, disaster, all_img_ids)
    
    crop_images(z, p, size, src, cropped_des, all_img_ids)
    prune_images(z, cropped_des, threshold, all_img_ids)
    produce_image_pairs(z, disaster, des, cropped_des, pre_post_pair, pre_pre_pair)
    
    print("Finished preprocessing images for: " + disaster)
