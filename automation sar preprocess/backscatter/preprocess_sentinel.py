import os
import sys
sys.path.append("C:\\Users\\39351\\.snap\\snap-python")
import esa_snappy
from esa_snappy import ProductIO, GPF, HashMap, jpy

class PreprocessSentinel1:
    def __init__(self, wkt_st, subswath, output_folder_path, export_intermediate=False, print_operators=False):
        self.ProductIO = ProductIO
        self.GPF = GPF
        self.HashMap = HashMap
        self.jpy = jpy
        self.ProductUtils = jpy.get_type('org.esa.snap.core.util.ProductUtils')
        self.wkt_st = wkt_st
        self.subswath = subswath
        self.output_folder_path = output_folder_path
        self.export_intermediate = export_intermediate
        self.print_operators = print_operators

    def run(self, label, safe_path):  # Keep as positional arguments for now
        label_clean = os.path.splitext(label)[0].replace(" ", "_")
        slc_product = self.ProductIO.readProduct(safe_path)

        if self.print_operators:
            operator_registry = self.GPF.getDefaultInstance().getOperatorSpiRegistry()
            for operator in operator_registry.getOperatorSpis().toArray():
                print(operator.getOperatorAlias())

        parameters = self.HashMap()
        parameters.put("Apply-Orbit-File", True)
        parameters.put("outputComplex", True)
        orbit_corrected = self.GPF.createProduct("Apply-Orbit-File", parameters, slc_product)

        parameters1 = self.HashMap()
        parameters1.put("removeThermalNoise", True)
        parameters1.put("outputComplex", True)
        parameters1.put("retainComplexBands", True)
        thermal_removed = self.GPF.createProduct("ThermalNoiseRemoval", parameters1, orbit_corrected)

        for band_name in [b for b in orbit_corrected.getBandNames() if "i_" in b or "q_" in b]:
            self.ProductUtils.copyBand(band_name, orbit_corrected, thermal_removed, True)

        parameters2 = self.HashMap()
        parameters2.put("subswath", self.subswath)
        parameters2.put("polarization", "VH,VV")
        parameters2.put("outputComplex", True)
        split_product = self.GPF.createProduct("TOPSAR-Split", parameters2, thermal_removed)

        parameters3 = self.HashMap()
        parameters3.put("outputBetaBand", True)
        parameters3.put("outputSigmaBand", False)
        parameters3.put("sourceBands", f"Intensity_{self.subswath}_VH ,Intensity_{self.subswath}_VV")
        parameters3.put("selectedPolarisations", "VH,VV")
        parameters3.put("outputImageScaleInDb", False)
        parameters3.put("outputComplex", True)
        calibrated_product = self.GPF.createProduct("Calibration", parameters3, split_product)

        for band_name in [b for b in split_product.getBandNames() if "i_" in b or "q_" in b]:
            self.ProductUtils.copyBand(band_name, split_product, calibrated_product, True)

        parameters4 = self.HashMap()
        parameters4.put("outputComplex", True)
        debursted_product = self.GPF.createProduct("TOPSAR-Deburst", parameters4, calibrated_product)

        java_int = self.jpy.get_type('java.lang.Integer')
        parameters5 = self.HashMap()
        parameters5.put("nRgLooks", java_int(3))
        parameters5.put("nAzLooks", java_int(3))
        parameters5.put("sourceBands", f"Beta0_{self.subswath}_VH,Beta0_{self.subswath}_VV")
        parameters5.put("outputComplex", False)
        parameters5.put("saveAsComplex", False)
        multilooked_product = self.GPF.createProduct("Multilook", parameters5, debursted_product)

        parameters6 = self.HashMap()
        parameters6.put("filter", "Lee")
        speckle_filtered_product = self.GPF.createProduct("Speckle-Filter", parameters6, multilooked_product)

        parameters7 = self.HashMap()
        parameters7.put("sourceBands", f"Beta0_{self.subswath}_VH, Beta0_{self.subswath}_VV")
        parameters7.put("demName", "SRTM 3Sec")
        parameters7.put("externalDEMNoDataValue", 0.0)
        parameters7.put("externalDEMApplyEGM", True)
        flattened_product = self.GPF.createProduct("Terrain-Flattening", parameters7, speckle_filtered_product)

        for band_name in [b for b in debursted_product.getBandNames() if "i_" in b or "q_" in b]:
            self.ProductUtils.copyBand(band_name, debursted_product, flattened_product, True)

        parameter8 = self.HashMap()
        parameter8.put("demName", "SRTM 3Sec")
        parameter8.put("pixelSpacingInMeter", 10.0)
        parameter8.put("mapProjection", "WGS84(DD)")
        parameter8.put("sourceBands", f"Gamma0_{self.subswath}_VH , Gamma0_{self.subswath}_VV")
        parameter8.put('demResamplingMethod', 'BILINEAR_INTERPOLATION')
        parameter8.put('imgResamplingMethod', 'BILINEAR_INTERPOLATION')
        parameter8.put("outputComplex", True)
        terrain_corrected_product = self.GPF.createProduct("Terrain-Correction", parameter8, flattened_product)

        parameters9 = self.HashMap()
        parameters9.put("geoRegion", self.wkt_st)
        parameters9.put("sourceBands", f"Gamma0_{self.subswath}_VH, Gamma0_{self.subswath}_VV")
        terrain_corrected_product_subset = self.GPF.createProduct("Subset", parameters9, terrain_corrected_product)


        parameters10= self.HashMap()
        parameters10.put("sourceBands", f"Gamma0_{self.subswath}_VH , Gamma0_{self.subswath}_VV")
        dB_converted_product = self.GPF.createProduct("LinearToFromdB", parameters10, terrain_corrected_product_subset)

        output_path2 = os.path.join(self.output_folder_path, f"{label_clean}_dB.tif")
        self.ProductIO.writeProduct(dB_converted_product, output_path2,  "GeoTIFF")
        print(f" Final product exported: {output_path2}")
        return output_path2
