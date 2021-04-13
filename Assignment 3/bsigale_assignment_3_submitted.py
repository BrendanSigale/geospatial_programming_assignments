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
	except:
		print("Workspace format invalid.")
	
	## get list of feature classes in the workspace.
	try:
		fcList = arcpy.ListFeatureClasses()
	except:
		print("Feature Class error.")
    
	## loop through the feature classes in fcList, describe the object, and print the shapetype
	## using .format for ease of use.
    for fc in fcList:
        geom_type = arcpy.Describe(fc).shapeType
        print("{0} is a {1} feature class".format(fc, geom_type))

###################################################################### 
# Problem 2 (20 Points)
#
# This function reads all the attribute names in a feature class or shape file and
# prints the name of each attribute name and its type (e.g., integer, float, double)
# only if it is a numerical type

###################################################################### 
def printNumericalFieldNames(inputFc, workspace):
    
	## updates the workspace to the workspace given by the user
	try:
		arcpy.env.workspace = workspace
	except:
		print("Workspace invalid.")
	
	## lists fields for the user-specified feature class in the workspace.
    try:
		fieldlist = arcpy.ListFields(inputFc)
	except:
		print("Feature Class input is invalid")

    numberList = ['Double', 'Integer', 'SmallInteger', 'Single']
    for field in fieldlist:
        if field.type in numberList:
            print(field.name, field.type)

###################################################################### 
# Problem 3 (30 Points)
#
# Given a geodatabase with feature classes, and shape type (point, line or polygon) and an output geodatabase:
# this function creates a new geodatabase and copying only the feature classes with the given shape type into the new geodatabase

###################################################################### 
def exportFeatureClassesByShapeType(input_geodatabase, shapeType, output_geodatabase):
    
	##store the current environment so it can be reset later
    original_env = str(arcpy.env.workspace)
    print("Current Workspace: " + arcpy.env.workspace)
    print("Beginning Database Creation")
    
	##try to create the new geodatabase
    try:
		arcpy.management.CreateFileGDB(arcpy.env.workspace, output_geodatabase)
	except:
		print("Database creation error!")

	##try to update the current geodatabase using the user input
    try:
		arcpy.env.workspace = input_geodatabase
	except:
		print("Workspace update error")
		
    print("Current Workspace: " + arcpy.env.workspace)

	## get list of feature classes in the workspace.
	try:
		fcList = arcpy.ListFeatureClasses()
	except:
		print("Feature Class error.")
		
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

###################################################################### 
# Problem 4 (40 Points)
#
# Given an input feature class or a shape file and a table in a geodatabase or a folder workspace,
# join the table to the feature class using one-to-one and export to a new feature class.
# Print the results of the joined output to show how many records matched and unmatched in the join operation. 

###################################################################### 
def exportAttributeJoin(inputFc, idFieldInputFc, inputTable, idFieldTable, workspace):
    
	## updates the workspace to the workspace given by the user
	try:
		arcpy.env.workspace = workspace
	except:
		print("Workspace invalid.")
		
	##sets the output table name.
    outName = inputFc + "_" + inputTable + "_JoinOn_" + idFieldInputFc
    
	##tries to creat a table with the join
    try:
		joined = arcpy.AddJoin_management(inputFc, idFieldInputFc, inputTable, idFieldTable)
    except:
		print("Issue with join. Check table names and field names.")
	
	##tries to copy the newly joined table into the workspace.
    arcpy.CopyFeatures_management(joined, outName)
    
	##prints the number of records successfully joined into the 
	##table as well as the number of rows in the original tables..
    print("Rows Matched: " + str(arcpy.management.GetCount(joined)))
	print("Input Feature Class Rows: " + str(arcpy.management.GetCount(inputFc)))
    print("Input Table Rows: " + str(arcpy.management.GetCount(inputTable)))


######################################################################
# MAKE NO CHANGES BEYOND THIS POINT.
######################################################################
if __name__ == '__main__' and hawkid()[1] == "hawkid":
    print('### Error: YOU MUST provide your hawkid in the hawkid() function.')
