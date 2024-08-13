import geopandas as gpd
import requests
import os, glob
import argparse
import leafmap


def download_all_images(des, disaster):
    collections = leafmap.maxar_child_collections(disaster)
    url = f'https://raw.githubusercontent.com/opengeos/maxar-open-data/master/datasets/{disaster}_union.geojson'
    gdf = leafmap.geojson_to_gdf(url)
    image_id_lst = gdf["catalog_id"].tolist()
    print(image_id_lst)
    assert(0)
    
    if not os.path.exists(des):
        os.mkdir(des)

    for image_id in image_id_lst:
        if not os.path.exists(os.path.join(des, image_id)):
            print("Downloading: " + image_id)
            gdf = leafmap.maxar_items(collection_id=disaster,
                                      child_id=image_id,
                                      return_gdf=True,
                                      assets=['visual'])
            images = gdf['visual'].tolist()

            leafmap.maxar_download(images, out_dir=des)

    print("Completed Downloading Images for: " + disaster)


def download_image_ids(des, disaster, img_ids):
    if not os.path.exists(des):
        os.mkdir(des)

    for image_id in img_ids:
        if not os.path.exists(os.path.join(des, image_id)):
            print("Downloading: " + image_id)
            gdf = leafmap.maxar_items(collection_id=disaster,
                                      child_id=image_id,
                                      return_gdf=True,
                                      assets=['visual'])
            images = gdf['visual'].tolist()

            leafmap.maxar_download(images, out_dir=des)

    print("Completed Downloading Images for: " + disaster)