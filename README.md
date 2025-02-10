# solara-maxar_preprocessing

# Project Overview

This is a data-pre processing pipeline for The Delta Project, an extension study following the development of the Disaster Assessment with VIsion foundation model (DAVI). This involves preprocessing and downloading satellite images from Maxar, as well as handling related CSV files for analysis.

## Files Description

- **pre_post.csv**: CSV file containing data comparing pre- and post-event images.
- **pre_pre.csv**: CSV file containing data comparing pre-event images.
- **download_maxar_images.py**: Script to download Maxar satellite images using the csv files.
  
- **maxar_preprocessing.py**: Preprocessing script for handling Maxar satellite images.
- **preprocessing_utils.py**: Utility functions for preprocessing data.

- **internship_final_progress_report_final.pdf**: Final progress report documenting the internship work.


## Data Collection
The first step in calculating the building recovery rate is detecting damaged buildings after a disaster. The Delta Project uses DAVI to generate binary masks of damaged buildings. To ensure effective training and application of DAVI, the project requires high-quality pre- and post-disaster satellite image pairs and corresponding labeled data.

### Satellite Imagery Sources
The Delta Project primarily utilizes open-source satellite imagery from the **Maxar Open Data Program**, which provides high-resolution pre- and post-event imagery to support emergency planning, risk assessment, damage evaluation, and recovery efforts.

#### Selected Disaster Events:
1. **2023 Turkey Earthquake:**
   - Magnitude: 7.8 (followed by a 7.7 aftershock)
   - Location: Kahramanmaras, Turkey
   - Damage: 280,000 buildings severely damaged or collapsed
   
2. **2023 Morocco Earthquake:**
   - Magnitude: 6.8
   - Location: High Atlas Mountains, near Marrakesh
   - Damage: 19,000 homes completely destroyed

These earthquake events were chosen due to their well-documented impact, the availability of high-resolution imagery, and the clear visibility of structural damage.

## Image Preprocessing
To ensure optimal performance of DAVI, raw satellite images undergo several preprocessing steps:

1. **Image Selection**: Pre- and post-disaster image pairs are selected based on:
   - High resolution (Ground Sample Distance < 0.50m)
   - Minimal cloud coverage (<10%)
   - Low off-nadir angle (<30°)

2. **Downloading Images**:
   - Using GeoJSON files provided by Maxar Open Data, raw satellite imagery is retrieved in TIFF format via the `maxar-open-data` module in the `leafmap` Python package.

3. **Tiling Images**:
   - Images are cropped to 256x256 pixel tiles at zoom level 18 using the `gdal2tiles` Python library.
   - Tiles are generated consistently using the Open Source Geospatial (OSGeo) Tile Map Service Specification and EPSG:4326 projection.

4. **Producing Image Pairs**:
   - Longitude and latitude coordinates from tile metadata are used to match pre- and post-disaster images.
   - Matched image pairs are stored in a separate dataset for further processing.

5. **Image Pruning**:
   - To enhance model performance, images are removed if they:
     - Contain empty pixels due to misaligned base tiles
     - Have excessive cloud coverage
     - Depict only natural landscapes (mountains, plains) without built structures
     - Are distorted or unclear, making building identification difficult
