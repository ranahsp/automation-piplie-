import json
from datetime import datetime
from sentinel_downloader import SentinelDownloader
from interferometry import InterferometryProcessor
from filter_sar import Filter_sar

with open("C:/polimi/thesis/motiferru analysis/S1-coherence/config_input.json", 'r') as file:
    parameters = json.load(file)

#downloader = SentinelDownloader(
 #   start_date=datetime.strptime(parameters["start_date"], "%Y-%m-%d"),
  #  end_date=datetime.strptime(parameters["end_date"], "%Y-%m-%d"),
  #  aoi=parameters["subset_wkt"],
  #  download_dir=parameters["download_dir"],
  #  netrc_path=parameters["netrc_path"]
#) 

#safe_paths = downloader.run()
with open("C:/Users/39351/Downloads/S1_Batch2/safe_paths.json", 'r') as file2:
    safe_paths = json.load(file2)
filtered_safe_paths = Filter_sar.filter_images(safe_paths, parameters["subset_wkt"], parameters["subswath"])
filtered_safe_paths  = list(filtered_safe_paths.items())[::-1]

filtered_json_path = "C:/Users/39351/Downloads/S1_Batch2/filtered_safe_paths.json"
with open(filtered_json_path, 'w') as outfile:
    json.dump(filtered_safe_paths, outfile, indent=4)


pairs = [(filtered_safe_paths[i], filtered_safe_paths[i+1]) for i in range(len(filtered_safe_paths)-1)]
print (pairs)

interf_processor = InterferometryProcessor(
    subswath=parameters["subswath"],
    output_folder=parameters["output_folder_path"],
    polarization=parameters["polarization"],
    wkt=parameters["subset_wkt"],
    s1a_bursts=parameters["s1a_bursts"],
    s1b_bursts=parameters["s1b_bursts"]

)

for idx, (master, slave) in enumerate(pairs, start=1):
    master_name, master_path = master
    slave_name, slave_path = slave
    
    master_date = master_path.split('_')[4][:8]
    slave_date = slave_path.split('_')[4][:8]
    
    output_name = f"interferogramVV_{idx}_{master_date}_vs_{slave_date}"

    interf_processor.run(
        master_path=master_path,
        slave_path=slave_path,
        output_name=output_name
        


    )



    
    print(f"Processed pair {idx}: {master_date} & {slave_date}")

print("All done.")