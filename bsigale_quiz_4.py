## Brendan Sigale
## Geospatial Programming - Quiz 4


## imports and set working environment
import arcpy
from arcpy import env
arcpy.env.workspace = <YOUR DATA FOLDER>
arcpy.env.overwriteOutput = True

## set the targeted feature class and define the field to be looked at, in this case 'FEATURE' 
fc = 'airports'
delimitedField = arcpy.AddFieldDelimiters(fc, "FEATURE")

## add a buffer field for use in the update cursor.
arcpy.AddField_management(fc, "buffer", "STRING")


## go through the feature class table and update the buffer field based on the feature field.
with arcpy.da.UpdateCursor(fc, ['FEATURE', 'buffer']) as cursor:
    for row in cursor:
        if row[0] == 'Seaplane Base':
            row[1] = "7500 METERS"
        elif row[0] == 'Airport':
            row[1] = "1500 METERS"
        else:
            print("Error: Feature Type Not Supported")
        cursor.updateRow(row)

## create the buffer name for the new shapefile        
bufferFcName = "buffer_" + fc + ".shp"

## perform buffer analysis on the buffer field, output to the name created above.
arcpy.Buffer_analysis(fc, bufferFcName, "buffer")