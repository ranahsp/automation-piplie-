
import sys
import os ,json
import requests
import zipfile
import gc
import asf_search as asf
from datetime import datetime
import numpy as np
sys.path.append("C:\\Users\\39351\\.snap\\snap-python")
import esa_snappy
print("ESA SNAPPY is installed correctly!")
from esa_snappy import ProductIO, GPF , HashMap, jpy
ProductUtils = jpy.get_type('org.esa.snap.core.util.ProductUtils')

class SentinelDownloader:
    def __init__(self, start_date, end_date, aoi, download_dir, netrc_path):
        self.start_date = start_date
        self.end_date = end_date
        self.aoi = aoi
        self.download_dir = download_dir
        self.safe_paths = {}
        os.environ["NETRC"] = netrc_path

        if not os.path.exists(download_dir):
            os.makedirs(download_dir)


    def search_products(self):
        print("\nSearching for Sentinel-1 SLC products...")
        results = asf.search(
            platform="SENTINEL-1",
            processingLevel="SLC",
            start=self.start_date.strftime("%Y-%m-%dT00:00:00Z"),
            end=self.end_date.strftime("%Y-%m-%dT23:59:59Z"),
            intersectsWith=self.aoi
        )
        print(f"Found {len(results)} results between {self.start_date.date()} and {self.end_date.date()}")
        return results

    def download_and_extract(self, results):
        for idx, result in enumerate(results):
            filename = result.properties['fileName']
            zip_path = os.path.join(self.download_dir, filename)
            expected_safe_folder = os.path.join(self.download_dir, filename[:60] + ".SAFE")

            print(f"\n[{idx + 1}/{len(results)}] Processing: {filename}")


            if not os.path.exists(zip_path):
                try:
                    result.download(path=self.download_dir)
                    print(" Downloaded:", filename)
                except Exception as e:
                    print(f"Failed to download {filename}: {e}")
                    continue
            else:
                print(" Already downloaded:", filename)

            if not os.path.exists(expected_safe_folder):
                if zipfile.is_zipfile(zip_path):
                    try:
                        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                            zip_ref.extractall(self.download_dir)
                            print(" Unzipped successfully")
                    except Exception as e:
                        print(f" Failed to unzip {filename}: {e}")
                        continue
                else:
                    print(f" Not a valid zip file: {zip_path}")
                    continue

            found_safe = False
            for root, dirs, _ in os.walk(self.download_dir):
                for dir_name in dirs:
                    if dir_name.endswith('.SAFE') and filename[:60] in dir_name:
                        safe_folder = os.path.join(root, dir_name)
                        self.safe_paths[filename] = safe_folder
                        print(" Found .SAFE folder:", safe_folder)
                        found_safe = True
                        break
                if found_safe:
                    break

            gc.collect()
            jpy.get_type('java.lang.System').gc()
            print(" Released from memory (ZIP and SAFE folder still on disk)")

    def save_safe_paths(self):
        safe_paths_file = os.path.join(self.download_dir, "safe_paths.json")
        with open(safe_paths_file, "w") as f:
            json.dump(self.safe_paths, f, indent=4)
        print("\nAll SAFE paths saved to:", safe_paths_file)
        return self.safe_paths

    def run(self):
        results = self.search_products()
        self.download_and_extract(results)
        return self.save_safe_paths()
