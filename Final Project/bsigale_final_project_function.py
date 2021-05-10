

################################################################################################################################################
# The purpose of this function is to calculate statistics about the relationship between census block groups, emergency evacuation routes,
# and where flood damage occurs. This dataset was tested and developed using data from Hurricane Harvey, and specifically how it affected
# Texas. However, the function is universal, provided the user defines polygons, roads, evacuation routes, and points for analysis.
#
# Pseudocode:
#     - Create new database in defined workspace.
#     - Check input feature data types.
#     - Reproject any unmatching feature classes to that of the roads input.
#     - Clip point data into the polygon feature class boundaries.
#     - Centroids are calculated for the input polygons to estimate distance to roads.
#     - Intersect analysis is performed between roads and evac inputs to estimate evacuation route access points.
#     - Distance between polygon centroids and the nearest intersection is calculated.
#     - Specified summary statistics are computed for the provided inputs, keeping only polygons which intersect with points.
#     - Data is joined together using the input polygon's unique identifier.
#     - Data is exported to a feature class, then to a shapefile, using the user-defined output information and field mappings.
#
# This function was created for GEOG:5055 Geospatial Programming at the University of Iowa by Brendan Sigale.
# Email brendan.sigale@gmail.com with any questions.
################################################################################################################################################

def evacuationAccessibilityandPSVI(svi, evac, roads, hwm, workspace, joinField, statField, statType, output_path, output_name, fieldmap=None):
    # Input definitions:
    # svi - Path to polygons, in this analysis representing census block groups.
    # evac - Path to polylines, in this case representing TxDOT's emergency evacuation routes.
    # roads - Path to roads, in this case using TxDOT's road inventory database.
    # hwm - Path to points, in this case representing USGS high water marks from Hurricane Harvey. Can be any points.
    # workspace - Path to folder where new analysis gdb should be created.
    # statField - Field which summary statistics will be crreated from. Must be in hwm.
    # statType - Summary statistic type. Must be 'SUM', 'MEAN', 'MIN', 'MAX', or 'STDDEV'.
    # joinField - Unique field in svi which will be used to join the analyses back together.
    # output_path - Path of desired output shapefile.
    # output_name - Name out output shapefile.

    # fieldmap - To export only specific columns, this analysis must essentially be run twice. After the first run, in which a shapefile with all data
    # will be created, the user should use Arc's FeatureClasstoFeatureClass tool to remove unwanted columns. Once this is complete,
    # copy the program's field mappings from the results pane into a fieldmappings string, which can then be passed into the function.

    ## intialize useful variables names
    svi_cent = 'svi_centroids'
    intersect = 'intersection_points'
    clipped_svi_hwm = 'svi_clipped_hwm'
    hwm_clip = 'hwm_clipped'
    hwm_summary = 'hwm_summary'

    arcpy.env.overwriteOutput = True
    arcpy.CreateFileGDB_management(workspace, 'SVI_Analysis.gdb')
    arcpy.env.workspace = 'SVI_Analysis.gdb'

    ## get spatial references for matching to roads
    ## Check input feature class spatial reference
    roads_desc = arcpy.Describe(roads)
    roads_desc_name = roads_desc.spatialReference.name
    svi_desc = arcpy.Describe(svi)
    svi_desc_name = svi_desc.spatialReference.name
    evac_desc = arcpy.Describe(evac)
    evac_desc_name = evac_desc.spatialReference.name
    hwm_desc = arcpy.Describe(hwm)
    hwm_desc_name = hwm_desc.spatialReference.name

    ## Checking shapefile types
    if roads_desc.shapeType != 'Polyline':
        raise TypeError('Roads must be a Polyline!')
    if svi_desc.shapeType != 'Polygon':
        raise TypeError('SVI must be a Polygon!')
    if evac_desc.shapeType != 'Polyline':
        raise TypeError('Evacuation Routes must be a Polyline!')
    if hwm_desc.shapeType != 'Point':
        raise TypeError('High Water marks must be Points!')
    else:
        print("Input feature class types accepted.")

    ## Ensure projections all match, using roads as the defining piece.

    if roads_desc_name != svi_desc_name:
        print("Roads and SVI do not match, updating svi in svi_reprojected to match roads: " + roads_desc_name)
        arcpy.management.Project(svi, 'svi_reprojected', roads_desc.spatialReference)
        svi = arcpy.env.workspace + '/svi_reprojected'
        print("Projection updated, both svi and roads are projected in: " + roads_desc_name)
    else:
        print("SVI feature class spatial reference matches.")

    if roads_desc_name != evac_desc_name:
        print("Roads and Evac do not match, updating evac in evac_reprojected to match roads: " + roads_desc_name)
        arcpy.management.Project(evac, 'evac_reprojected', roads_desc.spatialReference)
        evac = arcpy.env.workspace + '/evac_reprojected'
        print("Projection updated, both evac and roads are projected in: " + roads_desc_name)
    else:
        print("Evac feature class spatial reference matches.")

    if roads_desc_name != hwm_desc_name:
        print("Roads and HWM do not match, updating HWM in hwm_reprojected to match roads: " + roads_desc_name)
        arcpy.management.Project(hwm, 'hwm_reprojected', roads_desc.spatialReference)
        hwm = arcpy.env.workspace + '/hwm_reprojected'
        print("Projection updated, both hwm and roads are projected in: " + roads_desc_name)
    else:
        print("High Water Marks feature class spatial reference matches.")

    ## clip high water marks to be within possible svi regions (Must be done first, as the svi is clipped after using these points)
    arcpy.analysis.Clip(hwm, svi, hwm_clip)
    print("Points clipped successfully.")


    ## Convert census block groups to centroids for point to point distance analysis.
    arcpy.management.FeatureToPoint(svi, svi_cent, "CENTROID")

    ## intersect analysis between roads and evacuation routes
    print("Calculating evacuation route access points...")
    intersect_features = [roads, evac]
    arcpy.analysis.Intersect(intersect_features, intersect, 'ONLY_FID', output_type='POINT')
    print("Evacuation route entrances generated successfully.")

    ## Distance from census block group centroid to nearest road and evacuation route intersection (on ramp estimation)
    arcpy.analysis.Near(svi_cent, intersect, method="GEODESIC")
    print("Near analysis complete.")

    field_names_hwm_clip = [f.name for f in arcpy.ListFields(hwm_clip)]
    if statField not in field_names_hwm_clip:
        raise NameError("Input summary statistic not in High Water Marks feature class")

    numFields = []
    for field in arcpy.ListFields(hwm_clip):
        if field.type == 'Integer' or field.type == 'Double' or field.type == 'SmallInteger':
            numFields.append(field.name)
    if statField not in numFields:
        raise TypeError("Input summary statistic must be a numeric type.")

    statOptions = ['SUM', 'MEAN', 'MIN', 'MAX', 'STDDEV']
    if statType not in statOptions:
        raise NameError("Input summary statistic type not an available option")

    try:
        ## Summarize high water mark points into high water summary feature class, summary stat of input variable
        arcpy.analysis.SummarizeWithin(svi, hwm_clip, hwm_summary, 'ONLY_INTERSECTING', [[statField, statType]])
        print("Summary statistics computer successfully.")
    except:
        print("Could not compute. Likely possibility is statField is not numeric.")

    field_names_join = [f.name for f in arcpy.ListFields(hwm_summary)]
    if joinField not in field_names_join:
        raise NameError("Join Field is not in the input SVI feature class")

    ## Joining with census block group centroids to add nearest on ramp to table
    arcpy.management.AddJoin(hwm_summary, joinField, svi_cent, joinField)
    print("Join complete.")

    if fieldmap is None:
        arcpy.FeatureClassToFeatureClass_conversion(hwm_summary, output_path, output_name)
    else:
        ## Make a feature class with the specified names. This is the default.
        arcpy.FeatureClassToFeatureClass_conversion(hwm_summary, output_path, output_name, field_mapping=fieldmap)
    print("Feature class with specified columns created successfully.")

    ## to output to a new, filtered shapefile using the above field mappings.
    arcpy.conversion.FeatureClassToShapefile(output_name, output_path)
    print("Shapefile created successfully.")

    ## delete newly created tables
    fc_Delete = [hwm_clip, svi_cent, clipped_svi_hwm, intersect, hwm, 'hwm_reprojected', 'svi_reprojected', 'evac_reprojected']

    for fc in fc_Delete:
        fc_path = os.path.join(arcpy.env.workspace, fc)
        if arcpy.Exists(fc_path):
            arcpy.Delete_management(fc_path)

    print("Created analysis layers deleted.")