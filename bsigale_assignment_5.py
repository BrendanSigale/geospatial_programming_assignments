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
# Problem 1 (30 Points)
#
# Given a polygon feature class in a geodatabase, a count attribute of the feature class(e.g., population, disease count):
# this function calculates and appends a new density column to the input feature class in a geodatabase.

# Given any polygon feature class in the geodatabase and a count variable:
# - Calculate the area of each polygon in square miles and append to a new column
# - Create a field (e.g., density_sqm) and calculate the density of the selected count variable
#   using the area of each polygon and its count variable(e.g., population)
#
# 1- Check whether the input variables are correct(e.g., the shape type, attribute name)
# 2- Make sure overwrite is enabled if the field name already exists.
# 3- Identify the input coordinate systems unit of measurement (e.g., meters, feet) for an accurate area calculation and conversion
# 4- Give a warning message if the projection is a geographic projection(e.g., WGS84, NAD83).
#    Remember that area calculations are not accurate in geographic coordinate systems.
#
######################################################################
def calculateDensity(fcpolygon, attribute, geodatabase = "assignment2.gdb"):
    ## overwrite enabled, update gdb
    arcpy.env.overwriteOutput = True
    arcpy.env.workspace = folder + geodatabase
    print("overwrite enabled and gdb updated")

    area_field = 'area_sqmi'
    density_field = 'density_sqm'
    fieldList = [f.name for f in arcpy.ListFields(fcpolygon)]
    inputUnit = arcpy.Describe(fcpolygon).spatialReference.angularUnitName

    if attribute not in fieldList:
        raise ValueError('Chosen attribute not in field class')
    if inputUnit == 'Degree':
            print("WARNING: This layer uses a geographic coordinate system. Results may not be 100% accurate.")

    try:
        ## adding new fields
        arcpy.AddField_management(fcpolygon, area_field, "DOUBLE")
        arcpy.AddField_management(fcpolygon, density_field, "DOUBLE")
        print("new columns created")

        ## format the expression
        expression = '"!'+ attribute + '!/!' + area_field + '!"'
        print('Expression in use: ' + expression)

        ## calculate area in sqmi
        arcpy.CalculateGeometryAttributes_management(fcpolygon, [[area_field, "AREA_GEODESIC"]], 'MILES_US', "SQUARE_MILES_US")
        print('area calculated')

        ## calculate density
        arcpy.CalculateField_management(fcpolygon, density_field, "!" + attribute + "!/!area_sqmi!", "PYTHON3")
        print('density calcaulated')

    except:
        # By default any other errors will be caught here
        e = sys.exc_info()[1]
        print(e.args[0])

######################################################################
# Problem 2 (40 Points)
#
# Given a line feature class (e.g.,river_network.shp) and a polygon feature class (e.g.,states.shp) in a geodatabase,
# id or name field that could uniquely identify a feature in the polygon feature class
# and the value of the id field to select a polygon (e.g., Iowa) for using as a clip feature:
# this function clips the linear feature class by the selected polygon boundary,
# and then calculates and returns the total length of the line features (e.g., rivers) in miles for the selected polygon.
#
# 1- Check whether the input variables are correct (e.g., the shape types and the name or id of the selected polygon)
# 2- Transform the projection of one to other if the line and polygon shapefiles have different projections
# 3- Identify the input coordinate systems unit of measurement (e.g., meters, feet) for an accurate distance calculation and conversion
#
######################################################################
def estimateTotalLineLengthInPolygons(fcLine, fcClipPolygon, polygonIDFieldName, clipPolygonID, geodatabase = "assignment2.gdb"):
    ## overwrite enabled, update gdb
    arcpy.env.overwriteOutput = True
    arcpy.env.workspace = folder + geodatabase
    print("overwrite enabled and gdb updated")

    lengthField = 'length_mi'
    lengthTotal = 'length_total'
    outName = 'line_overlap'
    outProject = 'fcClipPolygon_projected'
    fieldListPolygon = [f.name for f in arcpy.ListFields(fcClipPolygon)]
    inputUnitLine = arcpy.Describe(fcLine).spatialReference.angularUnitName
    inputUnitPolygon = arcpy.Describe(fcClipPolygon).spatialReference.angularUnitName
    spatialRefLine = arcpy.Describe(fcLine).spatialReference.factoryCode
    spatialRefLine_object = arcpy.Describe(fcLine).spatialReference
    spatialRefPolygon = arcpy.Describe(fcClipPolygon).spatialReference.factoryCode

    if polygonIDFieldName not in fieldListPolygon:
        raise ValueError('Chosen attribute not in polygon field class')
    if clipPolygonID not in fieldListPolygon:
        raise ValueError('Chosen attribute not in polygon field class')
    if inputUnitLine or inputUnitPolygon == 'Degree':
            print("WARNING: A layer is using a geographic coordinate system. Results may not be 100% accurate.")

    if spatialRefLine != spatialRefPolygon:
        arcpy.management.Project(fcClipPolygon, outProject, spatialRefLine_object)

        try:
            ## add length field to polyogn
            arcpy.AddField_management(fcClipPolygon, lengthField, "DOUBLE")
            print("Length Field added")

            ## Intersect Analysis
            arcpy.Intersect_analysis([outProject, fcLine], outName)
            print('Intersect Analysis complete.')

            ## Length in each
            arcpy.CalculateGeometryAttributes_management(outName, [[lengthField, "LENGTH_GEODESIC"]], "MILES_US")
            print('Length calculated')

            polyDict = dict()
            with arcpy.da.SearchCursor(outName, [clipPolygonID, lengthField]) as cursor:
                for row in cursor:
                    id = row[0]
                    if polygonIDFieldName in polyDict.keys():
                        polyDict[id] += row[1]
                    else:
                        polyDict[id] = row[1]

            with arcpy.da.UpdateCursor(fcClipPolygon, [polygonIDFieldName, lengthField]) as cursor:
                for row in cursor:
                    if row[0] in polyDict.keys():
                        row[1] = polyDict[row[0]]
                    else:
                        row[1] = 0
                    cursor.updateRow(row)
        except:
            # By default any other errors will be caught here
            e = sys.exc_info()[1]
            print(e.args[0])

        arcpy.management.Delete(outProject)

    else:
        try:
            ## add length field to polyogn
            arcpy.AddField_management(fcClipPolygon, lengthField, "DOUBLE")
            print("Length Field added")

            ## Intersect Analysis
            arcpy.Intersect_analysis([fcClipPolygon, fcLine], outName)
            print('Intersect Analysis complete.')

            ## Length in each
            arcpy.CalculateGeometryAttributes_management(outName, [[lengthField, "LENGTH_GEODESIC"]], "MILES_US")
            print('Length calculated')

            polyDict = dict()
            with arcpy.da.SearchCursor(outName, [clipPolygonID, lengthField]) as cursor:
                for row in cursor:
                    id = row[0]
                    if polygonIDFieldName in polyDict.keys():
                        polyDict[id] += row[1]
                    else:
                        polyDict[id] = row[1]

            with arcpy.da.UpdateCursor(fcClipPolygon, [polygonIDFieldName, lengthField]) as cursor:
                for row in cursor:
                    if row[0] in polyDict.keys():
                        row[1] = polyDict[row[0]]
                    else:
                        row[1] = 0
                    cursor.updateRow(row)
        except:
            # By default any other errors will be caught here
            e = sys.exc_info()[1]
            print(e.args[0])

    arcpy.management.Delete(outName)

######################################################################
# Problem 3 (30 points)
#
# Given an input point feature class, (i.e., eu_cities.shp) and a distance threshold and unit:
# Calculate the number of points within the distance threshold from each point (e.g., city),
# and append the count to a new field (attribute).
#
# 1- Identify the input coordinate systems unit of measurement (e.g., meters, feet, degrees) for an accurate distance calculation and conversion
# 2- If the coordinate system is geographic (latitude and longitude degrees) then calculate bearing (great circle) distance
#
######################################################################
def countObservationsWithinDistance(fcPoint, distance, distanceUnit, geodatabase = "assignment2.gdb"):

    ## overwrite enabled, update gdb
    arcpy.arcpy.env.overwriteOutput = True
    arcpy.env.workspace = folder + "/" + geodatabase

    ## output feature class with Count
    outName = 'bufferOverlap'
    overlapField = 'Points_in_Distance'
    countCol = 'Point_Count'
    joinField = 'OBJECTID_1'
    inputUnit = arcpy.Describe(fcPoint).spatialReference.angularUnitName
    inputType = arcpy.Describe(fcPoint).shapeType

    try:
        if inputType != 'Point':
            raise ValueError("Please use a point feature class to use this tool.")

        if inputUnit == 'Degree':
            print("WARNING: This layer uses a geographic coordinate system. Results may not be 100% accurate.")

        ## calculate count
        arcpy.analysis.SummarizeNearby(fcPoint, fcPoint, outName, 'STRAIGHT_LINE', distance, distanceUnit)

        ## add new field for count to fcPoint
        arcpy.AddField_management(fcPoint, overlapField, "DOUBLE")

        ## Create the dictionary and update it
        countDict = dict()
        with arcpy.da.SearchCursor(outName, [joinField, countCol]) as cursor:
            for row in cursor:
                id = row[0]
                if joinField in countDict.keys():
                    countDiiict[id] += row[1]
                else:
                    countDict[id] = row[1]

        with arcpy.da.UpdateCursor(fcPoint, [joinField, overlapField]) as cursor:
            for row in cursor:
                if row[0] in countDict.keys():
                    row[1] = countDict[row[0]]
                else:
                    row[1] = 0
                cursor.updateRow(row)

        ## Delete New Feature Class
        arcpy.management.Delete(outName)

    except Exception:
        e = sys.exc_info()[1]
        print(e.args[0])

######################################################################
# MAKE NO CHANGES BEYOND THIS POINT.
######################################################################
if __name__ == '__main__' and hawkid()[1] == "hawkid":
    print('### Error: YOU MUST provide your hawkid in the hawkid() function.')
    print('### Otherwise, the Autograder will assign 0 points.')
