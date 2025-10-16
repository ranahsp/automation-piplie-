import os
import sys
import gc
sys.path.append("C:\\Users\\39351\\.snap\\snap-python")

from esa_snappy import ProductIO, GPF, HashMap, jpy
System = jpy.get_type('java.lang.System')
Runtime = jpy.get_type('java.lang.Runtime')
java_int = jpy.get_type('java.lang.Integer')
GPF.getDefaultInstance().getOperatorSpiRegistry().loadOperatorSpis()
class InterferometryProcessor:
    def __init__(self, subswath, polarization, output_folder, wkt,s1a_bursts, s1b_bursts):
        self.subswath = subswath
        self.polarization = polarization
        self.wkt = wkt
        self.output_folder = output_folder
        self.s1a_bursts = s1a_bursts
        self.s1b_bursts = s1b_bursts
        self.java_int = jpy.get_type('java.lang.Integer')
        GPF.getDefaultInstance().getOperatorSpiRegistry().loadOperatorSpis()

        def _get_bursts_for_product(self, product_name):
            if product_name.startswith("S1A"):
                 return self.s1a_bursts
            elif product_name.startswith("S1B"):
                return self.s1b_bursts
            else:
                 raise ValueError("Unknown Sentinel-1 platform in product name: " + product_name)
            
    def run(self, master_path, slave_path, output_name="final"):
        
        master = ProductIO.readProduct(master_path)
        slave = ProductIO.readProduct(slave_path)

        
        orbit_params = HashMap()
        master_orbit = GPF.createProduct("Apply-Orbit-File", orbit_params, master)
        slave_orbit = GPF.createProduct("Apply-Orbit-File", orbit_params, slave)

        
        split_params = HashMap()
        split_params.put("subswath", self.subswath)  
        split_params.put("selectedPolarisations", self.polarization)
        if "S1A" in master.getName():
            split_params.put('firstBurstIndex', self.java_int(int(self.s1a_bursts[0])))
            split_params.put('lastBurstIndex',self.java_int(int(self.s1a_bursts[1])))
        else:
            split_params.put('firstBurstIndex', self.java_int(int(self.s1b_bursts[0])))
            split_params.put('lastBurstIndex', self.java_int(int(self.s1b_bursts[1])))
        master_split = GPF.createProduct("TOPSAR-Split", split_params, master_orbit)


        split_params = HashMap()
        split_params.put("subswath", self.subswath)  
        split_params.put("selectedPolarisations", self.polarization)
        if "S1A" in slave.getName():
            split_params.put('firstBurstIndex', self.java_int(int(self.s1a_bursts[0])))
            split_params.put('lastBurstIndex', self.java_int(int(self.s1a_bursts[1])))
        else:
            split_params.put('firstBurstIndex', self.java_int(int(self.s1b_bursts[0])))
            split_params.put('lastBurstIndex', self.java_int(int(self.s1b_bursts[1])))
        slave_split = GPF.createProduct("TOPSAR-Split", split_params, slave_orbit)

        
        bg_params = HashMap()
        bg_params.put("demName", "SRTM 3Sec")
        bg_params.put("resamplingType", "BILINEAR_INTERPOLATION")
        bg_params.put("maskOutAreaWithoutElevation", True)
        #bg_params.put("doESD", True)
        bg_input_list = [slave_split, master_split]
        coregistered = GPF.createProduct("Back-Geocoding", bg_params, bg_input_list)

        del master
        del slave
        del master_orbit
        del slave_orbit
        del master_split
        del slave_split
        gc.collect()
        Runtime.getRuntime().gc()

       
        #esd_params = HashMap()
        #esd = GPF.createProduct("Enhanced-Spectral-Diversity", esd_params, coregistered)

        
        interf_params = HashMap()
        interf_params.put("subtractFlatEarthPhase", True)
        interf_params.put("subtractTopographicPhase", True)
        interf_params.put("demName", "SRTM 3Sec")
        interf_params.put("flatEarthPolynomialDegree", 5)
        interf_params.put("includeCoherence", True)
        interf_params.put("cohWinAzimuth", 3)
        interf_params.put("cohWinRange", 10)
        interf_params.put("squarePixel", True)
        interferogram = GPF.createProduct("Interferogram", interf_params, coregistered)

        del coregistered
        gc.collect()
        Runtime.getRuntime().gc()

        
        deburst_params = HashMap()
        deburst = GPF.createProduct("TOPSAR-Deburst", deburst_params, interferogram)

        
        #goldstein_params = HashMap()
        #goldstein_params.put("alpha", 1.0)
        #goldstein_params.put("FFTSize", 64)
        #goldstein_params.put("windowSizeInMeter", 3)
        #goldstein = GPF.createProduct("GoldsteinPhaseFiltering", goldstein_params, deburst)

        
        tc_params = HashMap()
        tc_params.put("demName", "SRTM 3Sec")
        tc_params.put("pixelSpacingInMeter", 90.0)
        tc_params.put("mapProjection", "WGS84(DD)")
        tc_params.put("maskOutAreaWithoutElevation", True)
        tc_params.put("outputComplex", False)
        tc_params.put("outputIntensity", True)
        tc_params.put("demResamplingMethod", "BILINEAR_INTERPOLATION")
        tc_params.put("imgResamplingMethod", "BILINEAR_INTERPOLATION")
        terrain_corrected = GPF.createProduct("Terrain-Correction", tc_params, deburst)


        
        for band_name in list(terrain_corrected.getBandNames()):
            if band_name.startswith('Intensity_ifg_'):
                terrain_corrected.removeBand(terrain_corrected.getBand(band_name))

        coherence_band_name = None
        for band_name in terrain_corrected.getBandNames():
            if "coh_" in band_name or "coh" in band_name.lower():
                coherence_band_name = band_name
                break
        subset_params = HashMap()
        subset_params.put("geoRegion", self.wkt)
        subset_params.put("bandNames", coherence_band_name)
        subset_params.put("copyMetadata", True)
        subset = GPF.createProduct("Subset", subset_params, terrain_corrected)
        output_path = os.path.join(self.output_folder, output_name)
        ProductIO.writeProduct(subset, output_path, "GeoTIFF")
        print(f"Interferogram saved to: {output_path}")


        subset.dispose()
        terrain_corrected.dispose()
        deburst.dispose()
        interferogram.dispose()
        del deburst
        del terrain_corrected
        del subset
        gc.collect()
        Runtime.getRuntime().gc()

        return output_path
