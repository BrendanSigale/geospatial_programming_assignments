###################################################################### 
# Edit the following function definition, replacing the words
# 'name' with your name and 'hawkid' with your hawkid.
# 
# Note: Your hawkid is the login name you use to access ICON, and not
# your firsname-lastname@uiowa.edu email address.
# 
# def hawkid():
#     return(["Caglar Koylu", "ckoylu"])
###################################################################### 
def hawkid():
    return(["Brendan Sigale", "bsigale"])

##################################################################################################### 
# 100 Points Total
#
# Given a linear shapefile (roads) and a point shapefile representing facilities(schools),
# this function should generate either a time-based (1-,2-,3- minute) or road network distance-based (200-, 400-, 600-, .. -2000 meters)
# concentric service areas around facilities and save the results to a layer file on an output geodatabase.
# Although you are not required to map the result, make sure to check your output service layer feature.
# The service area polygons can be used to visualize the areas that do not have adequate coverage from the schools. 

# Each parameter is described below:

# inFacilities: The name of point shapefile (schools)     
# roads: The name of the roads shapefile
# workspace: The workspace folder where the shapefiles are located. 

# Below are suggested steps for your program. More code may be needed for exception handling
# and checking the accuracy of the input values.

# 1- Do not hardcode any parameters or filenames in your code.
#    Name your parameters and output files based on inputs. 
# 2- Check all possible cases where inputs can be in wrong type, different projections, etc. 
# 3- Create a geodatabase using arcpy and import all initial shapefiles into feature classes. All your processes and final output should be saved into
#    the geodatabase you created. Therefore, set the workspace parameter to the geodatabase once it is created.
# 4- Using the roads linear feature class, create and build a network dataset. Check the Jupyter notebook shared on ICON,
#    which covers the basics of how to create and build a network dataset from scratch. 
# 5- Use arcpy's MakeServiceAreaLayer function in the link below:
#    https://pro.arcgis.com/en/pro-app/tool-reference/network-analyst/make-service-area-layer.htm
#    Specify the following options while creating the new service area layer. Please make sure to read all the parameters needed for the function. 
#       If you use "length" as impedance_attribute, you can calculate concentric service areas using 200, 400, 600, .. 2000 meters for break values.
#       Feel free to describe your own break values, however, make sure to include at least three of them. 
#       Generate the service area polygons as rings, so that anyone can easily visualize the coverage for any given location if needed.
#       Use overlapping polygons to determine the number of facilities (schools) that cover a given location.
#       Use hierarchy to speed up the time taken to create the polygons.
#       Use the following values for the other parameters:
#       "TRAVEL_FROM", "DETAILED_POLYS", "MERGE"
#################################################################################################################### 
def calculateNetworkServiceArea(inFacilities, roads, workspace):
    import arcpy
    import sys

    arcpy.env.overwriteOutput = True

    try:
        ##Create new gdb
        arcpy.CreateFileGDB_management(workspace, 'serviceArea.gdb')
        arcpy.env.workspace = 'serviceArea.gdb'
    except:
        raise NameError('Input workspace does not exist!')
    try:
        arcpy.CheckOutExtension("network")
    except:
        print("Network Analyst Extension not available")

    ## Check input feature class spatial reference
    roads_desc = arcpy.Describe(roads)
    roads_desc_name = roads_desc.spatialReference.name
    facilities_desc = arcpy.Describe(inFacilities)
    facilities_desc_name = facilities_desc.spatialReference.name

    if roads_desc.shapeType != 'Polyline':
        raise TypeError('Roads must be a Polyline!')

    if facilities_desc.shapeType != 'Point':
        raise TypeError('Facilities must be a Point!')

    if roads_desc_name != facilities_desc_name:
        print(
            "Projections do not match, updating inFacilities in inFacilities_reprojected to match roads: " + roads_desc_name)
        arcpy.management.Project(inFacilities, 'inFacilities_reprojected', roads_desc.spatialReference)
        inFacilities = arcpy.env.workspace + '/inFacilities_reprojected'
        print("Projection updated, both inFacilities and roads are projected in: " + roads_desc_name)
    else:
        print("Input feature class spatial references match.")

    ## Create feature dataset
    arcpy.CreateFeatureDataset_management(arcpy.env.workspace, 'featuredataset', roads_desc.spatialReference)

    ## Copy input feature classes to featuredataset
    arcpy.CopyFeatures_management(roads, 'featuredataset/roads')
    arcpy.CopyFeatures_management(inFacilities, 'featuredataset/inFacilities')

    ## Create network dataset and build the network
    arcpy.na.CreateNetworkDataset('featuredataset', 'roads_ND', ['roads'])
    arcpy.BuildNetwork_na('featuredataset/roads_ND')

    ## Generating the Service Area Layer with service areas from 200 - 2000 meters, increasing at 200m intervals.
    routeLy = arcpy.na.MakeServiceAreaLayer('featuredataset/roads_ND', 'myRoute', 'Length',
                                            "TRAVEL_FROM", '200 400 600 800 1000 1200 1400 1600 1800 2000',
                                            'DETAILED_POLYS', 'MERGE',
                                            'RINGS', overlap="OVERLAP", hierarchy="USE_HIERARCHY")

    ## Standard processing features
    routeLayer = routeLy.getOutput(0)
    na_classes = arcpy.na.GetNAClassNames(routeLayer, 'INPUT')
    field_mappings = arcpy.na.NAClassFieldMappings(routeLayer, na_classes['Facilities'])
    field_mappings['Attr_Length'].defaultValue = 0
    arcpy.na.AddLocations(routeLayer, na_classes["Facilities"], "featuredataset/inFacilities", field_mappings)

    ## Compute the service areas
    arcpy.na.Solve(routeLayer)

######################################################################
# MAKE NO CHANGES BEYOND THIS POINT.
######################################################################
if __name__ == '__main__' and hawkid()[1] == "hawkid":
    print('### Error: YOU MUST provide your hawkid in the hawkid() function.')
