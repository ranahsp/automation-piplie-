import sys
sys.path.append("C:\\Users\\39351\\.snap\\snap-python")
from esa_snappy import ProductIO
import os 
from esa_snappy import ProductIO, GPF, HashMap, jpy

class Filter_sar:
    @staticmethod
    def aoi_orbit(safe_path, aoi_wkt, subswath):
        try:
            product = ProductIO.readProduct(safe_path)
            metadata = product.getMetadataRoot().getElement('Abstracted_Metadata')
            rel_orbit = metadata.getAttribute('rel_orbit').getData().getElemString()

            split_params = HashMap()
            split_params.put("subswath", subswath)
            split_params.put("selectedPolarisations", "VV,VH")
            iw1_product = GPF.createProduct("TOPSAR-Split", split_params, product)

            subset_params = HashMap()
            subset_params.put("geoRegion", aoi_wkt)
            subset_product = GPF.createProduct("Subset", subset_params, iw1_product)

            width = subset_product.getSceneRasterWidth()
            height = subset_product.getSceneRasterHeight()

            print(f" {os.path.basename(safe_path)} → Orbit: {rel_orbit} | Subset size: {width}x{height}")

            if width > 0 and height > 0:
                return rel_orbit 
            else:
                return None

        except Exception as e:
            print(f" Error processing {os.path.basename(safe_path)}: {e}")
            return None

    @staticmethod
    def filter_images(safe_paths, aoi_wkt, subswath):
        filtered = {}
        target_orbit = None

        for filename, path in safe_paths.items():
            
            rel_orbit = Filter_sar.aoi_orbit(path, aoi_wkt, subswath) 

            if rel_orbit:
                if not target_orbit:
                    target_orbit = rel_orbit
                    print(f"Reference Orbit Selected: {target_orbit}")
                if rel_orbit == target_orbit:
                    filtered[filename] = path
                    print(f" Accepted: {filename}")
                else:
                    print(f" Skipped: Orbit mismatch ({rel_orbit})")

        print(f"\n Final selected images: {len(filtered)} in Orbit {target_orbit}")
        return filtered
