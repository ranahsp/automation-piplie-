# Automated pipeline to derive tthe analysis-ready sentinel-1 SAR backscatter and coherence products
This project provides fully automated pipelines for preprocessing SAR SLC time series imagery and generate the analysis ready backscatter and interferometric coherence products suitable for geospatial analusis.  
There are two dedicated pipelines: one for backscatter preprocessing and the other for interferometric coherence preprocesssing.  
Each pipeline is composed of three core classes:  
    1-  Downlaoding the sentinel-1 images: Automates the retrieval of sentinel-1 SLC scences from ASF website.  
    2-  Image filter: selects the appropriate acquisitions based on user-defined criteria and ensure the complete coverage of are of interest and uniform geometry.  
    3-  Preprocessing class: applies SNAP-based opertors to generate analysis-ready outputs.  
The code is implemented using ESA SNAP toolbax via esa-snappy python interface.  
# User setup
To run the pipelines, users only need to:  
1- configure SNAP and Python integration by following https://senbox.atlassian.net/wiki/spaces/SNAP/pages/2499051521/Configure+Python+to+use+the+SNAP-Python+esa_snappy+interface+SNAP+version+10  
2-Edite the corresponding config.json file for each pipeline to define the processing parameters and output settings.  
Here's a sample configuration:  

{    
  "subswath": "IW2",  
  "polarization": "VV",  
  "start_date": "2021-07-18",  
  "end_date": "2021-08-18",  
  "subset_wkt": "POLYGON((8.771000155000024 40.10317950000007, 8.771000155000024 40.33213643700003, 8.462286404000054 40.33213643700003, 8.462286404000054 40.10317950000007, 8.771000155000024 40.10317950000007))",  
  "download_dir": "C:/Users/39351/Downloads/S1_Batch2",  
  "netrc_path": "C:/Users/39351/.netrc" (this is the credentials for nasa earth website for downloading the images),    
  "output_folder_path": "C:\\polimi\\thesis\\motiferru analysis\\S1-coherence",  
  "export_intermediate": false,  
  "print_operators": false  
}  
3-Execute the main script to lunch the pipeline.
