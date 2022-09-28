# Terrain classification based on satellite (Landsat) images analisis

## Goal of the project
Perform image analysis of satellite images. Based on the developed classification system, recognize and label following areas:
- water
- forest
- desert
- urban

## Used Technologies
- spark
- pyspark
- python
- EMR
- EMR Notebook

## Requirements
### Cluster configuration
To launch program in the cluster on the EMR platform with EMR Notebooks, specified configuration must be set.
Choose **Create Cluster - Advanced Options  -> Software Configuration**. Then, select the following:
- Hadoop 2.10.1
- Hive 2.3.9
- JupyterEnterpriseGateway 2.1.0 
- Spark 2.4.8
- Livy 0.7.1

Next, step into **Hardware** tab and in **Cluster Nodes and Instances** choose:
- 1 m5.xlarge instace for Master node
- 2 m5.xlarge instances for Core node

### Starting the program
To launch the program, connect "main.ipybn" file to the previously created cluster and start it. Installing all of the required dependencies and libraries are included at the start of the notebook file


## Dataset
- https://registry.opendata.aws/usgs-landsat/


## Classification method
Each area (water, desert, city, forest) is calculated on the indicators basis. They are calculated based on the data obtained from the red (red), blue (blue), green (green), near infrared (nir) and shortwave infrared (SWIR1) bands. After calculating the corresponding indices, they are processed into matrices containing binary values, where 1 - indicates a detected given area, and 0 - no detected given area.
### Water
Normalized difference water index (NDWI) and Modified Normalized Difference Water Index (MNDWI) indices were used to detect water areas. When the sum of their values is greater than zero, it means that the area at that point is water.
### Desert
Desert areas are detected based on the Normalized Differential Sand Areas Index (NDSAI) described in *Mapping Sandy Areas and Their Changes Using Remote Sensing. A Case Study at North-East Al-Muthanna Province, South of Iraq*[1]. 
### City
The area of a city is detected using the Normalized Difference Built-up Index (NDBI). The middle values of the index indicate the urban area.
### Forest
The normalized difference vegetation index (NDVI) is used to detect forest. When the values obtained using this index are greater than 0.3, the area is classified as forested.

## Implementation 
Using a specified function, we mark the areas bounded by a certain longitude and latitude, which are ~1° (111 km) in width and height. This guarantees that the classified areas will be clearly visible on the image. Using the client, we connect to the server (https://landsatlook.usgs.gov/stac-server), which, based on a query with information about the area of interest and other parameters, provides a link to the s3 bucket, which contains a .TIF file for each band. 
We use the ***rasterio*** library to process .TIF files for each of the four bands in the study area. It allows us to obtain a dataset on which we are able to perform operations to classify the four areas. 
After obtaining the dataset, we reduce the data to a list of tuples, where ***red, green, blue, nir, swir*** are the matrices read from the .TIF files. **bbox** contains a list of ordinates of a given area. 
``sh
bands_values = [(red, blue, green, nir, swir, bbox),...,...,...].
``
### RDD
We used RDD (Resilient Distributed Datasets), in order to distribute the computing used on images/matrices operations. Following actions were taken: 
- operations on the matrices in order to create an image (mask) which marks the classified areas.
- scaling down images so that the RAM memory wont be too heavily overloaded when the data is downloaded back to the driver program
- flitration of bad images
- loading back the data

We wanted to also use RDD to read .TIF files, which would remarkably increase overall time of the program execution, but it seemed that access to s3 bucket, where the .TIF files were stored, required a session variable, which couldnt be serialized by RDD. 
We also stumbled upon a problem with saving files with RDD, which was also an access problem.


Result image is obtained by putting multiple **rgb** binary masks over the image and assigning a appropriate collor for each of them. Masks are superimposed on an image in an order based on the effectiveness of the terrain classification. Mask corresponding to the least effective classification was imposed first, and the best - last. Said effectiveness was defined based on our observations.
Terrains sorted by the effectiveness of their classification (from least to best):
1. desert
2. urban
3. forest
4. water
Result image can be either dowloaded or be shown in the program.
Image presented down below is on of the many analised photos in northern Poland. All in all, classification comes down to the pixel analisis so areas like fields without plants or bare ground may be "counted" as a desert. Either way, we think that the classification is correct, and clearly, one can see the relation between "normal" image on the right, and the image with classified terrains.
![landsat](https://user-images.githubusercontent.com/67193178/190922691-9cb4b7e7-1489-4dae-add5-50a1d545473b.png)
Sometimes, among the output images, there can be some "unclean" images that eveded filtering. For examle, image of the Niijama island on the Phillipine sea has some black stripes, but the overall black pixel area sums up to less than 10% of the image, so we still consider it an okay image. 
![Niijama](https://user-images.githubusercontent.com/67193178/190924338-ce215ec1-de20-4c29-9a71-7bee6408a98a.png)
Another photo of northern Poland (areas of Łeba):
![łęba](https://user-images.githubusercontent.com/67193178/190925557-4ab68c3d-06ba-4074-b142-1e254fd02a30.png)
To sum up, we are happy with our current classification system. Nevertheless many areas are assigned to "desert" class when they are de facto not a desert. There are seen as a desert because areas like dry soil or some other types of grounds are no different to a desert for indicators like NDSAI. The system can still be upgraded by experimenting with variables and parameters used in operations on images.

## Result and data visualisation
Result image is obtained by putting multiple **rgb** binary masks over the image and assigning a appropriate collor for each of them. Masks are superimposed on an image in an order based on the effectiveness of the terrain classification. Mask corresponding to the least effective classification was imposed first, and the best - last. Said effectiveness was defined based on our observations.
Terrains sorted by the effectiveness of their classification (from least to best):
1. desert
2. urban
3. forest
4. water
Result image can be either dowloaded or be shown in the program.
Image presented down below is on of the many analised photos in northern Poland. All in all, classification comes down to the pixel analisis so areas like fields without plants or bare ground may be "counted" as a desert. Either way, we think that the classification is correct, and clearly, one can see the relation between "normal" image on the right, and the image with classified terrains.
![landsat](https://user-images.githubusercontent.com/67193178/190922691-9cb4b7e7-1489-4dae-add5-50a1d545473b.png)
Sometimes, among the output images, there can be some "unclean" images that eveded filtering. For examle, image of the Niijama island on the Phillipine sea has some black stripes, but the overall black pixel area sums up to less than 10% of the image, so we still consider it an okay image. 
![Niijama](https://user-images.githubusercontent.com/67193178/190924338-ce215ec1-de20-4c29-9a71-7bee6408a98a.png)
Another photo of northern Poland (areas of Łeba):
![łęba](https://user-images.githubusercontent.com/67193178/190925557-4ab68c3d-06ba-4074-b142-1e254fd02a30.png)
To sum up, we are happy with our current classification system. Nevertheless many areas are assigned to "desert" class when they are de facto not a desert. There are seen as a desert because areas like dry soil or some other types of grounds are no different to a desert for indicators like NDSAI. The system can still be upgraded by experimenting with variables and parameters used in operations on images.


## Bibliography
[1] Awad A. Sahar, Muaid J. Rasheed2, Dhia A. A.-H. Uaid3, Ammar A. Jasim4. 2021. Mapping Sandy Areas and their changes using remote sensing. A Case Study at North-East Al-Muthanna Province, South of Iraq. *Revista de Teledeteccion* 2021(58):39-52.
https://polipapers.upv.es/index.php/raet/article/view/13622/14158
https://doi.org/10.4995/raet.2021.13622

## Sources
- https://web.pdx.edu/~nauna/resources/10_BandCombinations.htm
- https://gisgeography.com/landsat-8-bands-combinations/

## Authors
- Fryderyk Róg
- Piotr Łyczko
