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

###################################################################### 
# Problem 1: 20 Points
#
# Given a csv file import it into the database passed as in the second parameter
# Each parameter is described below:

# csvFile: The absolute path of the file should be included (e.g., C:/users/ckoylu/test.csv)
# geodatabase: The workspace geodatabase
######################################################################
def importCSVIntoGeodatabase(csvFile, geodatabase):
    
    import arcpy
    import sys
    
    arcpy.env.overwriteOutput = True

    outTable = 'csvImport'
    try:
        arcpy.env.workspace = geodatabase
        arcpy.TableToTable_conversion(csvFile, arcpy.env.workspace, outTable)
    except:
        # By default any other errors will be caught here
        e = sys.exc_info()[1]
        print(e.args[0])

##################################################################################################### 
# Problem 2: 80 Points Total
#
# Given a csv table with point coordinates, this function should create an interpolated
# raster surface, clip it by a polygon shapefile boundary, and generate an isarithmic map

# You can organize your code using multiple functions. For example,
# you can first do the interpolation, then clip then equal interval classification
# to generate an isarithmic map

# Each parameter is described below:

# inTable: The name of the table that contain point observations for interpolation       
# valueField: The name of the field to be used in interpolation
# xField: The field that contains the longitude values
# yField: The field that contains the latitude values
# inClipFc: The input feature class for clipping the interpolated raster
# workspace: The geodatabase workspace

# Below are suggested steps for your program. More code may be needed for exception handling
#    and checking the accuracy of the input values.

# 1- Do not hardcode any parameters or filenames in your code.
#    Name your parameters and output files based on inputs. For example,
#    interpolated raster can be named after the field value field name 
# 2- You can assume the input table should have the coordinates in latitude and longitude (WGS84)
# 3- Generate an input feature later using inTable
# 4- Convert the projection of the input feature layer
#    to match the coordinate system of the clip feature class. Do not clip the features yet.
# 5- Check and enable the spatial analyst extension for kriging
# 6- Use KrigingModelOrdinary function and interpolate the projected feature class
#    that was created from the point feature layer.
# 7- Clip the interpolated kriging raster, and delete the original kriging result
#    after successful clipping. 
#################################################################################################################### 
def krigingFromPointCSV(inTable, valueField, xField, yField, inClipFc, workspace = "assignment3.gdb"):
    
    import arcpy
    import sys

    try:
        ## update workspace
        arcpy.env.workspace = workspace
    except:
        raise NameError('Input Geodatabase does not exist.')
    
    arcpy.env.overwriteOutput = True
    
    ## Create variables used throughout the function
    outTable = 'csvImport'
    outFc = 'tableAsFc' ## Points as feature class layer name
    outProject = 'pointsToClipConversion' ## Reprojected points if necessary
    krigName = 'K' + valueField ## Kriging name
    clipFc = 'imported_clipping_fc' ## Clipping feature class imported to the gdb
    inputFcClip = 'input_fc_clipped' ## Clipped kriging map
    inputFcClipInt = inputFcClip + '_int' ## Integer clipping kriging map
    outKiriging = 'KClass' 
    finalOutput = 'R_' + valueField ## Final output layer
    
    ## Input the inTable
    importCSVIntoGeodatabase(inTable, workspace)
    
    ## Generate table point feature class from xField and yField
    arcpy.management.XYTableToPoint(outTable, outFc, xField, yField)
    
    ## Imported feature class to gdb
    arcpy.FeatureClassToFeatureClass_conversion(inClipFc, arcpy.env.workspace, clipFc)
    
    
    ## Spatial References
    spatialRefTable = arcpy.Describe(outFc).spatialReference.factoryCode
    spatialRefClip = arcpy.Describe(inClipFc).spatialReference.factoryCode
    spatialRefClip_object = arcpy.Describe(inClipFc).spatialReference
    
    ##check if srids match, if not update clip table points to match clipping feature class
    if spatialRefClip != spatialRefTable:
        arcpy.management.Project(outFc, outProject, spatialRefClip_object)
        
    ## Check to make sure Spatial Analyst license is available, raise error if not
    try:
        arcpy.CheckExtension("Spatial") == 'Available'
        arcpy.CheckOutExtension("Spatial")
    except LicenseError("Spatial Analyst License is not available")
    
    ## Calculate cell size for Kriging
    descTable = arcpy.Describe(outFc)
    width = descTable.extent.width
    height = descTable.extent.height
    cellSize = min(width, height) / 1000

    ## Generate kriging layer
    outKriging = Kriging(outFc, valueField, '#', cellSize)
    outKriging.save(krigName)

    ## Generate clipping extent
    descClip = arcpy.Describe(clipFc)
    rectangle = str(descClip.extent.XMin) + " " + str(descClip.extent.YMin) + " " + str(descClip.extent.XMax) + " " + str(descClip.extent.YMax)

    ## Create clipped kriging map
    arcpy.Clip_management(krigName, rectangle, inputFcClip, clipFc, '#', 'ClippingGeometry', 'MAINTAIN_EXTENT')

    ## Convert clipping kriging map to integer values for classification
    outInt = Int(inputFcClip)
    outInt.save(inputFcClipInt)

    ## Variables for establishing equal interval values (assumes 5 classes, can be changed using numofClasses variable)
    min_int = int(arcpy.management.GetRasterProperties(outInt, "MINIMUM").getOutput(0))
    max_int = int(arcpy.management.GetRasterProperties(outInt, "MAXIMUM").getOutput(0))
    numofClasses = 5
    eqInterval = (max_int - min_int) / numofClasses
    myremapRange = []
    myBreak = min_int

    ## Generate equal interval ranges
    for i in range(0, numofClasses):
        classCode = i + 1
        lowerBound = myBreak
        upperBound = myBreak + eqInterval
        remap = [lowerBound, upperBound, classCode]
        myremapRange.append(remap)
        myBreak += eqInterval

    ## Classified based on Integer kriging values
    outReclassRR = Reclassify(inputFcClipInt, "Value", RemapRange(myremapRange), "NODATA")
    outReclassRR.save("krig_c_out")

    ## Save classified raster as polygon for final output
    arcpy.RasterToPolygon_conversion(outReclassRR, finalOutput, "NO_SIMPLIFY", "Value")

    ## Delete extra feature classes and layers which were generated
    arcpy.management.Delete(outFc)
    arcpy.management.Delete(clipFc)
    arcpy.management.Delete(outKriging)
    arcpy.management.Delete(outInt)
    arcpy.management.Delete(inputFcClip)
    arcpy.management.Delete(outReclassRR)

######################################################################
# MAKE NO CHANGES BEYOND THIS POINT.
######################################################################
if __name__ == '__main__' and hawkid()[1] == "hawkid":
    print('### Error: YOU MUST provide your hawkid in the hawkid() function.')
