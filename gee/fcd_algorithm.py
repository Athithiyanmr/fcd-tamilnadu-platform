"""Core Pseudo-FCD algorithm (Sentinel-2 SR Harmonized)."""
import ee

CONFIG = {
    "detect_water": True,
    "ndwi_hi":      0.2,
    "bi_hi":        2.0,
    "ndvi_lo":      0.25,
    "ndvi_hi":      0.45,
    "si_lo":        0.92,
    "si_hi":        0.95,
    "cloud_pct":    1,
    "scale":        10,
    "crs":          "EPSG:4326",
}

CLASS_CODES  = [0, 1, 2, 3, 4, 5]
CLASS_NAMES  = ["Other", "Water", "High forest", "Low forest", "Grassland", "Bare land"]
CLASS_COLORS = ["#000000", "#3380cc", "#006837", "#3ea540", "#baf096", "#ad8855"]
SEQ_COEF     = {"Other": 0, "Water": 0, "High forest": 104.58,
                "Low forest": 90.18, "Grassland": 60.64, "Bare land": 0}


def mask_s2_clouds(img):
    qa   = img.select("QA60")
    mask = qa.bitwiseAnd(1 << 10).eq(0).And(qa.bitwiseAnd(1 << 11).eq(0))
    return (img.updateMask(mask)
               .divide(10000)
               .copyProperties(img, ["system:time_start", "system:index"]))


def build_fcd(geom, start_date, end_date, label, cloud_pct=None):
    """Build an FCD image for the given geometry and date window."""
    if cloud_pct is None:
        cloud_pct = CONFIG["cloud_pct"]

    s2 = (ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
            .filterBounds(geom)
            .filterDate(start_date, end_date)
            .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", cloud_pct))
            .map(mask_s2_clouds))

    img  = s2.median().clip(geom)
    ndvi = img.normalizedDifference(["B8", "B4"]).rename("NDVI")
    ndwi = img.normalizedDifference(["B3", "B8"]).rename("NDWI")
    bi   = img.expression(
        "(NIR+GREEN+RED)/(NIR+GREEN-RED)",
        {"NIR": img.select("B8"), "GREEN": img.select("B3"), "RED": img.select("B4")}
    ).rename("BI")
    si   = img.expression(
        "sqrt((1-GREEN)*(1-RED))",
        {"GREEN": img.select("B3"), "RED": img.select("B4")}
    ).rename("SI")

    water_mask      = ndwi.gt(CONFIG["ndwi_hi"])
    hi_forest_mask  = ndvi.gt(CONFIG["ndvi_hi"]).And(bi.lt(CONFIG["bi_hi"])).And(si.gt(CONFIG["si_hi"]))
    low_forest_mask = (ndvi.gt(CONFIG["ndvi_lo"]).And(ndvi.lte(CONFIG["ndvi_hi"]))
                           .And(bi.lt(CONFIG["bi_hi"])).And(si.gt(CONFIG["si_lo"])).And(si.lte(CONFIG["si_hi"])))
    grass_mask      = ndvi.gt(CONFIG["ndvi_lo"])
    bare_mask       = ndvi.lt(CONFIG["ndvi_lo"]).And(bi.gt(CONFIG["bi_hi"])).And(si.lt(CONFIG["si_lo"]))

    fcd = (ee.Image(0).rename("FCD")
             .where(bare_mask,        5)
             .where(grass_mask,       4)
             .where(low_forest_mask,  3)
             .where(hi_forest_mask,   2))

    if CONFIG["detect_water"]:
        fcd = fcd.where(water_mask, 1)

    return fcd.toByte().clip(geom).set({
        "label":         label,
        "start_date":    start_date,
        "end_date":      end_date,
        "scene_count":   s2.size(),
        "source_scenes": s2.aggregate_array("system:index"),
    })


def class_area_dict(fcd_img, geom, scale=10):
    """Return a dict of {class_code_str: area_ha} for all FCD classes."""
    grouped = (ee.Image.pixelArea().divide(10000).addBands(fcd_img)
               .reduceRegion(
                   reducer=ee.Reducer.sum().group(groupField=1, groupName="class"),
                   geometry=geom, scale=scale, maxPixels=1e13, bestEffort=True
               ))
    groups = ee.List(grouped.get("groups"))
    return ee.Dictionary(groups.iterate(
        lambda g, acc: ee.Dictionary(acc).set(
            ee.Number(ee.Dictionary(g).get("class")).format("%d"),
            ee.Dictionary(g).get("sum")
        ),
        ee.Dictionary({})
    ))
