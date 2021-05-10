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
# Problem 1 (10 Points)
#
# This function reads all the feature classes in a workspace (folder or geodatabase) and
# prints the name of each feature class and the geometry type of that feature class in the following format:
# 'states is a point feature class'

###################################################################### 
def printFeatureClassNames(workspace):
	
    ## updates the workspace to the workspace given by the user
    try:
        arcpy.env.workspace = workspace
        ## get list of feature classes in the workspace.
    arcpy.env.overwriteOutput = True

	fcList = arcpy.ListFeatureClasses()
	## loop through the feature classes in fcList, describe the object, and print the shapetype
	## using .format for ease of use.
	for fc in fcList:
            geom_type = arcpy.Describe(fc).shapeType
            print("{0} is a {1} feature class".format(fc, geom_type))

    ## Return geoprocessing specific errors
    except arcpy.ExecuteError:
        arcpy.AddError(arcpy.GetMessages(2))

    # Return any other type of error
    except:
        # By default any other errors will be caught here
        e = sys.exc_info()[1]
        print(e.args[0])

###################################################################### 
# Problem 2 (20 Points)
#
# This function reads all the attribute names in a feature class or shape file and
# prints the name of each attribute name and its type (e.g., integer, float, double)
# only if it is a numerical type

###################################################################### 
def printNumericalFieldNames(inputFc, workspace):
    try:
        ## updates the workspace to the workspace given by the user
        arcpy.env.workspace = workspace
    except:
        raise NameError('Input workspace does not exist!')
    
    arcpy.env.overwriteOutput = True

    try:
        ## lists fields for the user-specified feature class in the workspace.
        fieldlist = arcpy.ListFields(inputFc)

        numberList = ['Double', 'Integer', 'SmallInteger', 'Single']
        for field in fieldlist:
            if field.type in numberList:
                print(field.name, field.type)

    # Return geoprocessing specific errors
    except arcpy.ExecuteError:
        arcpy.AddError(arcpy.GetMessages(2))

    # Return any other type of error
    except:
        # By default any other errors will be caught here
        e = sys.exc_info()[1]
        print(e.args[0])

###################################################################### 
# Problem 3 (30 Points)
#
# Given a geodatabase with feature classes, and shape type (point, line or polygon) and an output geodatabase:
# this function creates a new geodatabase and copying only the feature classes with the given shape type into the new geodatabase

###################################################################### 
def exportFeatureClassesByShapeType(input_geodatabase, shapeType, output_geodatabase):
    
    arcpy.env.overwriteOutput = True

    try:
        ##store the current environment so it can be reset later
        original_env = str(arcpy.env.workspace)
        print("Current Workspace: " + arcpy.env.workspace)
        print("Beginning Database Creation")
	##create the new geodatabase
        arcpy.management.CreateFileGDB(arcpy.env.workspace, output_geodatabase)

        ##try to update the current geodatabase using the user input
        arcpy.env.workspace = input_geodatabase
        print("Current Workspace: " + arcpy.env.workspace)

        ## get list of feature classes in the workspace.
        fcList = arcpy.ListFeatureClasses()

	##loop through the list of feature classes and describe each one. If it matches
	##the user-specified shape type, copy it into the newly created database.
        for fc in fcList:
            geom_type = arcpy.Describe(fc).shapeType
            if geom_type == shapeType:
                outFeatureClass = os.path.join(output_geodatabase, fc.strip(".shp"))
                arcpy.CopyFeatures_management(fc, outFeatureClass)
                print("--- Created copy of: " + fc + " located at: " + outFeatureClass)

        ##resets the workspace
	arcpy.env.workspace = original_env
        print("Copy Complete")
        print("Current Workspace: " + arcpy.env.workspace)

    # Return geoprocessing specific errors
    except arcpy.ExecuteError:
        arcpy.AddError(arcpy.GetMessages(2))

    # Return any other type of error
    except:
        # By default any other errors will be caught here
        e = sys.exc_info()[1]
        print(e.args[0])


###################################################################### 
# Problem 4 (40 Points)
#
# Given an input feature class or a shape file and a table in a geodatabase or a folder workspace,
# join the table to the feature class using one-to-one and export to a new feature class.
# Print the results of the joined output to show how many records matched and unmatched in the join operation. 

###################################################################### 
def exportAttributeJoin(inputFc, idFieldInputFc, inputTable, idFieldTable, workspace):
    try:
        ## updates the workspace to the workspace given by the user
        arcpy.env.workspace = workspace
    except:
        raise NameError('Input workspace does not exist!')
    
    arcpy.env.overwriteOutput = True

    try:
        ##sets the output table name.
        outName = inputFc + "_" + inputTable + "_JoinOn_" + idFieldInputFc

        ##creates a table with the join
        joined = arcpy.AddJoin_management(inputFc, idFieldInputFc, inputTable, idFieldTable, 'KEEP_COMMON')

        ##copies the newly joined table into the workspace.
        arcpy.CopyFeatures_management(joined, outName)

        ## Get Row Counts
        joinedCount = int(arcpy.management.GetCount('joined').getOutput(0))
        unJoinedCount = int(arcpy.management.GetCount('inputFc').getOutput(0)) - joinedCount

        ##prints the number of records successfully joined into the
        ##table as well as the number of rows in the original tables.
        print("Rows Matched: " + joinedCount)
        print("Rows Unmatched: " + unJoinedCount)

	# Return geoprocessing specific errors
        except arcpy.ExecuteError:
            arcpy.AddError(arcpy.GetMessages(2))

        # Return any other type of error
        except:
            # By default any other errors will be caught here
            e = sys.exc_info()[1]
            print(e.args[0])

######################################################################
# MAKE NO CHANGES BEYOND THIS POINT.
######################################################################
if __name__ == '__main__' and hawkid()[1] == "hawkid":
    print('### Error: YOU MUST provide your hawkid in the hawkid() function.')
