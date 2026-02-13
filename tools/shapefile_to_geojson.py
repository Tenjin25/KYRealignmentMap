import geopandas as gpd
import os

def convert_shapefile_to_geojson(shapefile_path, output_path=None):
    """
    Converts a shapefile to GeoJSON format.
    """
    if not os.path.exists(shapefile_path):
        print(f"Error: Shapefile not found at {shapefile_path}")
        return False

    if output_path is None:
        output_path = os.path.splitext(shapefile_path)[0] + ".geojson"

    try:
        print(f"Reading shapefile: {shapefile_path}")
        gdf = gpd.read_file(shapefile_path)
        
        # Ensure CRS is WGS84 (EPSG:4326) for GeoJSON compatibility
        if gdf.crs and gdf.crs.to_epsg() != 4326:
            print(f"Projecting from {gdf.crs} to EPSG:4326")
            gdf = gdf.to_crs(epsg=4326)
        
        print(f"Writing GeoJSON: {output_path}")
        gdf.to_file(output_path, driver='GeoJSON')
        print("Conversion successful!")
        return True
    except Exception as e:
        print(f"Error during conversion: {e}")
        return False

if __name__ == "__main__":
    # Path to the Kentucky county shapefile
    shp_path = os.path.join("data", "tl_2020_21_county20", "tl_2020_21_county20.shp")
    
    # Run conversion
    convert_shapefile_to_geojson(shp_path)
