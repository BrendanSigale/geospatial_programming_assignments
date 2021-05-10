## Brendan Sigale | 20210331 0714

def calculatePercentAreaOfPolygonAInPolygonB(input_geodatabase, fcPolygon1, fcPolygon2):
    try:
        ## Update workspace
        arcpy.env.workspace = input_geodatabase
        
        ## Create field name objects
        cbg_area_field = 'cbg_area'
        park_area_field = 'park_area'
        park_pct_field = 'park_pct'
        fcOverlap = 'park_overlap'
        
        ## Add new fields used in calculations to fcPolygon2
        arcpy.AddField_management(fcPolygon2, cbg_area_field, "DOUBLE")
        arcpy.AddField_management(fcPolygon2, park_area_field, "DOUBLE")
        arcpy.AddField_management(fcPolygon2, park_pct_field, 'DOUBLE')
        
        ## Calculate area of block groups, perform an intersect analysis, and then calculate area of intersect.
        arcpy.CalculateGeometryAttributes_management(fcPolygon2, [[cbg_area_field, "AREA_GEODESIC"]], "MILES_US")
        arcpy.Intersect_analysis([fcPolygon2, fcPolygon1], fcOverlap)
        arcpy.CalculateGeometryAttributes_management(fcOverlap, [[park_area_field, "AREA_GEODESIC"]], "MILES_US")

        ## Create dictionary of area of Polygon1 by FIPS code, used for combining with Polygon2
        cbg_dict = {}
        with arcpy.da.SearchCursor(fcParkOverlap, ["FIPS", park_area_field]) as cursor:
            for row in cursor:
                geoid = row[0]
                if geoid in cbg_dict.keys():
                    cbg_dict[geoid] += row[1]
                else:
                    cbg_dict[geoid] = row[1]
            del row
        del cursor
        
        ## Match park area from fcParkOverlap with FIPS in Polygon2
        with arcpy.da.UpdateCursor(fcPolygon2, ["FIPS", park_area_field]) as cursor:
            for row in cursor:
                if row[0] in cbg_dict.keys():
                    row[1] = cbg_dict[row[0]]
                else:
                    row[1] = 0
                cursor.updateRow(row)
            del row
        del cursor
        
        ## Calculate percent overlap and input into park_pct_field     
        arcpy.CalculateField_management(fcPolygon2, park_pct_field, "!park_area!/!cbg_area!", "PYTHON3")

    except:
        # By default any other errors will be caught here
        e = sys.exc_info()[1]
        print(e.args[0])
