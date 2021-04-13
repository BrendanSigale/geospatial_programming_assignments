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
# Problem 1 (20 points)
# 
# Given an input point feature class (e.g., facilities or hospitals) and a polyline feature class, i.e., bike_routes:
# Calculate the distance of each facility to the closest bike route and append the value to a new field.
#        
###################################################################### 
def calculateDistanceFromPointsToPolylines(input_geodatabase, fcPoint, fcPolyline):
    try:
        ## update workspace
        arcpy.env.workspace = input_geodatabase
        
        ##perform near analysis
        arcpy.analysis.Near(fcPoint, fcPolyline, field_names = ['NEAR_DIST'])

    except:
        # By default any other errors will be caught here
        e = sys.exc_info()[1]
        print(e.args[0])
######################################################################
# Problem 2 (30 points)
# 
# Given an input point feature class, i.e., facilities, with a field name (FACILITY) and a value ('NURSING HOME'), and a polygon feature class, i.e., block_groups:
# Count the number of the given type of point features (NURSING HOME) within each polygon and append the counts as a new field in the polygon feature class
#
######################################################################
def countPointsByTypeWithinPolygon(input_geodatabase, fcPoint, pointFieldName, pointFieldValue, fcPolygon):
    try:
        arcpy.env.workspace = input_geodatabase
        
        ## add the new column
        newColumnName = "objects_in_polygon"
        arcpy.AddField_management(fcPolygon, newColumnName, 'FLOAT')
        
        ## selects polygons where field name matches input
        expression = arcpy.AddFieldDelimiters(arcpy.env.workspace, pointFieldName) + " = '" + str(pointFieldValue) + "'"
        outPoints = fcPoint + "_filtered"
        arcpy.FeatureClassToFeatureClass_conversion(fcPoint, arcpy.env.workspace, outPoints, expression)
        
        ## new feature class which contains information on which polygon a point is in
        arcpy.SpatialJoin_analysis(fcPolygon, fcPoint, outFc, '#', '#', '#', 'CONTAINS')
        
        ## new table with summarized information, grouped by FIPS, for further analysis - note: Function needs FIPS. Change for different object identified
        arcpy.Statistics_analysis(outFc, countTable, 'Join_Count SUM', 'FIPS')
    
        ## assembles counts into a dictionary
        countDict = {}
        with arcpy.da.SearchCursor(countTable, ["FIPS", 'SUM_Join_Count']) as cursor:
            for row in cursor:
                fips = row[0]
                if fips in countDict.keys():
                    countDict[fips] += row[1]
                else:
                    countDict[fips] = row[1]
            del row
        del cursor
        
        ## matches based on FIPS, updates newColumnName
        with arcpy.da.UpdateCursor(fcPolygon, ['FIPS', newColumnName]) as cursor:
            for row in cursor:
                if row[0] in countDict.keys():
                    row[1] = countDict[row[0]]
                else:
                    row[1] = 0
                cursor.updateRow(row)
            del row
        del cursor
    
    except:
        # By default any other errors will be caught here
        e = sys.exc_info()[1]
        print(e.args[0])

######################################################################
# Problem 3 (50 points)
# 
# Given a polygon feature class, i.e., block_groups, and a point feature class, i.e., facilities,
# with a field name within point feature class that can distinguish categories of points (i.e., FACILITY);
# count the number of points for every type of point features (NURSING HOME, LIBRARY, HEALTH CENTER, etc.) within each polygon and
# append the counts to a new field with an abbreviation of the feature type (e.g., nursinghome, healthcenter) into the polygon feature class 

# HINT: If you find an easier solution to the problem than the steps below, feel free to implement.
# Below steps are not necessarily explaining all the code parts, but rather a logical workflow for you to get started.
# Therefore, you may have to write more code in between these steps.

# 1- Extract all distinct values of the attribute (e.g., FACILITY) from the point feature class and save it into a list
# 2- Go through the list of values:
#    a) Generate a shortened name for the point type using the value in the list by removing the white spaces and taking the first 13 characters of the values.
#    b) Create a field in polygon feature class using the shortened name of the point type value.
#    c) Perform a spatial join between polygon features and point features using the specific point type value on the attribute (e.g., FACILITY)
#    d) Join the counts back to the original polygon feature class, then calculate the field for the point type with the value of using the join count field.
#    e) Delete uncessary files and the fields that you generated through the process, including the spatial join outputs.  
######################################################################
######################################################################
# Problem 3 (50 points)
# 
# Given a polygon feature class, i.e., block_groups, and a point feature class, i.e., facilities,
# with a field name within point feature class that can distinguish categories of points (i.e., FACILITY);
# count the number of points for every type of point features (NURSING HOME, LIBRARY, HEALTH CENTER, etc.) within each polygon and
# append the counts to a new field with an abbreviation of the feature type (e.g., nursinghome, healthcenter) into the polygon feature class 

# HINT: If you find an easier solution to the problem than the steps below, feel free to implement.
# Below steps are not necessarily explaining all the code parts, but rather a logical workflow for you to get started.
# Therefore, you may have to write more code in between these steps.

# 1- Extract all distinct values of the attribute (e.g., FACILITY) from the point feature class and save it into a list
# 2- Go through the list of values:
#    a) Generate a shortened name for the point type using the value in the list by removing the white spaces and taking the first 13 characters of the values.
#    b) Create a field in polygon feature class using the shortened name of the point type value.
#    c) Perform a spatial join between polygon features and point features using the specific point type value on the attribute (e.g., FACILITY)
#    d) Join the counts back to the original polygon feature class, then calculate the field for the point type with the value of using the join count field.
#    e) Delete uncessary files and the fields that you generated through the process, including the spatial join outputs.  
######################################################################
def countCategoricalPointTypesWithinPolygons(fcPoint, pointFieldName, fcPolygon, workspace):
    try:
        ## updates the workspace
        arcpy.env.workspace = workspace
        
        ## gets unique values of the provided fields
        fc_search = fcPoint
        fields = [pointFieldName]
        uniqueNames = []

        search_cursor = arcpy.da.SearchCursor(fc_search, fields)

        for row in search_cursor:
            if row[0] not in uniqueNames:
                uniqueNames.append(row[0])
            else:
                pass
        print(uniqueNames)

        ## creates temporary feature classes for analysis
        outFc = 'facilities_in_cbg'
        countTable = 'counts'
        outPoints = fcPoint + "_filtered"

        ## begins analysis loop through each value and for each column
        for name in range(len(uniqueNames)):
            ##creates new columns based on uniqueNames
            inputName = uniqueNames[name].replace(" ", "_").lower()
            newColumnName = inputName + "_in_fcpolygon"
            arcpy.AddField_management(fcPolygon, newColumnName, 'FLOAT')

            print("column " + newColumnName + " created")

            ## selects polygons where field name matches input
            expression = arcpy.AddFieldDelimiters(arcpy.env.workspace, pointFieldName) + " = '" + str(uniqueNames[name]) + "'"
            outPoints = fcPoint + "_filtered"
            arcpy.FeatureClassToFeatureClass_conversion(fcPoint, arcpy.env.workspace, outPoints, expression)

            ## new feature class which contains information on which polygon a point is in
            arcpy.SpatialJoin_analysis(fcPolygon, fcPoint, outFc, '#', '#', '#', 'CONTAINS')

            print("spatial join complete")

            ## new table with summarized information, grouped by FIPS, for further analysis - note: Function needs FIPS. Change for different object identified
            arcpy.Statistics_analysis(outFc, countTable, 'Join_Count SUM', 'FIPS')

            print("Statistic Analysis complete")

            ## assembles counts into a dictionary
            countDict = {}
            with arcpy.da.SearchCursor(countTable, ["FIPS", 'SUM_Join_Count']) as cursor:
                for row in cursor:
                    fips = row[0]
                    if fips in countDict.keys():
                        countDict[fips] += row[1]
                    else:
                        countDict[fips] = row[1]
                del row
            del cursor

            ## matches based on FIPS, updates newColumnName
            with arcpy.da.UpdateCursor(fcPolygon, ['FIPS', newColumnName]) as cursor:
                for row in cursor:
                    if row[0] in countDict.keys():
                        row[1] = countDict[row[0]]
                    else:
                        row[1] = 0
                    print(row[1])
                    cursor.updateRow(row)
                del row
            del cursor

            ## deletes temporarily used feature classes
            arcpy.management.DeleteFeatures(outFc)
            arcpy.management.Delete(countTable)
            arcpy.management.DeleteFeatures(outPoints)

            print("Additional features deleted")
            
    except:
        # By default any other errors will be caught here
        e = sys.exc_info()[1]
        print(e.args[0])

######################################################################
# MAKE NO CHANGES BEYOND THIS POINT.
######################################################################
if __name__ == '__main__' and hawkid()[1] == "hawkid":
    print('### Error: YOU MUST provide your hawkid in the hawkid() function.')
