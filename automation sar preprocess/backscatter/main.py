import json
from datetime import datetime
from sentinel_downloader import SentinelDownloader
from preprocess_sentinel import PreprocessSentinel1
from filter_sar import Filter_sar

with open("C:/polimi/geoinformatic project/test/config_input.json", 'r') as file:
    parameters = json.load(file)

downloader = SentinelDownloader(
    start_date=datetime.strptime(parameters["start_date"], "%Y-%m-%d"),
    end_date=datetime.strptime(parameters["end_date"], "%Y-%m-%d"),
    aoi=parameters["subset_wkt"],
    download_dir=parameters["download_dir"],
    netrc_path=parameters["netrc_path"]
)

safe_paths = downloader.run()

filtered_safe_paths = Filter_sar.filter_images(safe_paths, parameters["subset_wkt"], parameters["subswath"])


processor = PreprocessSentinel1(
    wkt_st=parameters["subset_wkt"],
    output_folder_path=parameters["output_folder_path"],
    export_intermediate=parameters["export_intermediate"],
    print_operators=parameters["print_operators"],
    subswath=parameters["subswath"]
)


for filename, safe_path in filtered_safe_paths.items():
    processor.run(label=filename, safe_path=safe_path)

print("All done.")
