import geopandas as gpd
import requests
import os, glob
import argparse

def parse_arguments(notebook=False):
    parser = argparse.ArgumentParser()
    parser.add_argument('--src', type=str, default='./datasets', help='Source path')
    parser.add_argument('--imgdes', type=str, default='./images', help='Destination path for csv files')
    parser.add_argument('--d', type=str, required=True, help='Disaster name')

        
    return parser.parse_args()

def download_img(df, disaster, imgdes):
    if not os.path.exists(imgdes):
        os.mkdir(imgdes)

    url_list = list(df["visual"])

    for url in url_list:    
        data = requests.get(url).content
        fname = url.split('/')[-1]

        directory = os.path.join(imgdes, disaster)
        if not os.path.exists(directory):
            os.mkdir(directory)

        path = os.path.join(directory, fname)

        f = open(path, 'wb')
        f.write(data)
        f.close()
        print("Completed downloading: " + url)

if __name__=='__main__':
    
    args = parse_arguments()
    print(args)
    
    src = args.src
    imgdes = args.imgdes
    disaster = args.d

    condition = "/*.geojson"

    # create csv file with latitude and longitude for each disaster
    for filepath in glob.glob(src + condition):
        disaster = filepath.split('/')[-1].split('.')[0].split('_')[0]
        if disaster in disaster_list:
            df = gpd.read_file(filepath)
            print("Downloading image files for: " + disaster)
            download_img(df, disaster, imgdes)

#             print("Completed: " + disaster)

    print("Finished")