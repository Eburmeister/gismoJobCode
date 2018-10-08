#-------------------------------------------------------------------------------
# Name:        CRSCL_Weekly_processes
# Purpose:     Creates various products of the SCL and uploads to FTP/SDE
#
# Author:      Gary Harrison (original modifled from Robert Vega/Jaime Mckeown)
#
# Created:     30/06/2017
# Copyright:   (c) Gary Harrison 2017
# Licence:
#-------------------------------------------------------------------------------

def main():
    try:
        # Import modules
        import arcpy
        import time
        from datetime import datetime
        from collections import defaultdict
        import operator
        import itertools
        import os, sys
        xFlag = 0
        xStep = 'starting crscl weekly processes'

        # -------------------------------------------------------------------------
        # InternetFile ------------------------------------------------------------
        # -------------------------------------------------------------------------
        startTime = datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")
        arcpy.env.overwriteOutput = True
        arcpy.env.qualifiedFieldNames = True

        # Get parameters from config file
        sys.path.append("//ccgisfiles01m/gisdata/prdba/crupdates/CCPythonLib/Appl/")
        import getConfig

        # Set variables for the environment
        workspace = getConfig.main('user','crscl','path','workspace')
        sdeWorkspace = getConfig.main('user','crscl','path','sclAdmin') + 'prscl.SCLADMIN.'
        gismoWorkspace = getConfig.main('globalPath','gismo') + '/GISMO.GISMO.'
        sdeLoad = getConfig.main('globalPath','gismoLoad')
        internetFileGdb = workspace + "InternetFile_work.gdb"
        templateGdb = workspace + "InternetFile_Template.gdb/"
        xstreetTemplate = workspace + "InternetFile_Template.gdb/Xstreet"
        nineInternetTemplate = workspace + "InternetFile_Template.gdb/nineInternet"
        outTableWorkspace = getConfig.main('user','crscl','path','outTableWorkspace')
        outFtpWorkspace = getConfig.main('user','crscl','path','outFtpWorkspaceCCGIS1')
        outWorkspace = getConfig.main('user','crscl','path','outWorkspace')
        CRSCLUpdateWorkspace = getConfig.main('user','crscl','path','CRSCLUpdateWorkspace')

        # Set variable for layer imported from sde
        sclDimemap = gismoWorkspace + "SCLDimeMap"
        bookSec = gismoWorkspace + "CLARKTRS_P"

        # Set variables for dataset and layers in GDB
        dataset = internetFileGdb + "/Data"
        sclarc = dataset + "/sclarc"
        sclnode = dataset + "/sclnode"
        sclnine = dataset + "/sclnine"
        blkgrp = dataset + "/sclblkgrp"
        place = dataset + "/sclplace"

        # Set variables for polygon layers
        blkptBooksec = dataset + "/blkpt_booksec"
        cntyStateArc = dataset + "/cntystate_arc"
        cntyState = dataset + "/cntystate"
        cntyStateTract = dataset + "/cntystate_tract"
        tractBlock = dataset + "/tract_block"
        blockZip = dataset + "/block_zip"
        zipPlace = dataset + "/zip_place"
        placeMcd = dataset + "/place_mcd"
        mcdBlkgrp = dataset + "/mcd_blkgrp"
        blkgrpPrec = dataset + "/blkgrp_prec"
        precBooksec = dataset + "/prec_booksec"
        sclarcPolys = dataset + "/sclarc_polys"

        # Set variable for sclarc identity to polygons
        sclarcId = dataset + "/sclarc_id"

        # Set variables for node layers
        sclnodeProj = internetFileGdb + "/sclnode_proj"
        sclnodeDime = dataset + "/sclnode_dime"
        sclnodeAllXy = dataset + "/sclnode_allxy"
        intersect = dataset + "/node_arc"

        # Set variable for a spatial reference object for the dataset
        spatRef = arcpy.CreateSpatialReference_management("", sdeWorkspace + "sclarc", "", "", "", "")
        print "\n", arcpy.GetMessages()

        xStep = 'delete last month GDB'
        # Delete last months old GDB, rename new GDB to last months, create new GDB for this month, create feature dataset, and add working layers to new GDB deleting unnecessary fields
        if arcpy.Exists(internetFileGdb):
            arcpy.Delete_management(internetFileGdb, "")
            print "\n", arcpy.GetMessages()
        arcpy.CreateFileGDB_management(workspace, "InternetFile_work", "CURRENT")
        print "\n", arcpy.GetMessages()
        arcpy.CreateFeatureDataset_management(internetFileGdb, "Data", spatRef)
        print "\n", arcpy.GetMessages()
        arcpy.FeatureClassToFeatureClass_conversion(sdeWorkspace + "sclarc", dataset, "sclarc")
        print "\n", arcpy.GetMessages()
        arcpy.AddField_management(sclarc, "STRCLASSI", "SHORT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management(sclarc, "STRCLASSI", "!STRCLASS!", "PYTHON_9.3", "")
        print "\n", arcpy.GetMessages()
        arcpy.DeleteField_management(sclarc, "SCLQA;SCLUPD;ATTUPD;SPEED;LANES;ONEWAY;STRCLASS")
        print "\n", arcpy.GetMessages()
        arcpy.FeatureClassToFeatureClass_conversion(sdeWorkspace + "sclnode", dataset, "sclnode")
        print "\n", arcpy.GetMessages()
        arcpy.DeleteField_management(sclnode, "SCLUPD;ATTUPD;STRLIGHT")
        print "\n", arcpy.GetMessages()
        arcpy.FeatureClassToFeatureClass_conversion(sdeWorkspace + "sclnine", dataset, "sclnine")
        print "\n", arcpy.GetMessages()
        arcpy.DeleteField_management(sclnine, "PTUPD;ATTUPD")
        print "\n", arcpy.GetMessages()
        arcpy.FeatureClassToFeatureClass_conversion(sdeWorkspace + "sclplace", dataset, "sclplace")
        print "\n", arcpy.GetMessages()
        arcpy.AddField_management(place, "LOC", "TEXT", "", "", "2", "", "NULLABLE", "NON_REQUIRED", "")
        print "\n", arcpy.GetMessages()

        xStep = 'Set variable for codeblock to calculate LOC field'
        # Set variable for codeblock to calculate LOC field
        placeCodeblock = """def CalcField(PlaceField):
            if (PlaceField == 77):
                return 'AF'
            elif (PlaceField == 10):
                return 'BC'
            elif (PlaceField == 15):
                return 'BU'
            elif (PlaceField == 205):
                return 'GS'
            elif (PlaceField == 60):
                return 'HN'
            elif (PlaceField == 43):
                return 'IS'
            elif (PlaceField == 65):
                return 'LV'
            elif (PlaceField == 67):
                return 'LA'
            elif (PlaceField == 71):
                return 'ME'
            elif (PlaceField == 74):
                return 'MO'
            elif (PlaceField == 206):
                return 'MS'
            elif (PlaceField == 75):
                return 'MV'
            elif (PlaceField == 79):
                return 'MC'
            elif (PlaceField == 80):
                return 'NL'
            elif (PlaceField == 99):
                return 'SL'
            elif (PlaceField ==203):
                return 'SV'
            elif (PlaceField == 905):
                return 'VF'
            else:
                return 'CC'"""

        # Calculate LOC field
        xStep = 'Calculate LOC field'
        arcpy.CalculateField_management(place, "LOC", "CalcField(!place!)", "PYTHON_9.3", placeCodeblock)
        print "\n", arcpy.GetMessages()

        # Add sclblkgrp and delete fields
        xStep = 'Add sclblkgrp and delete fields'
        arcpy.FeatureClassToFeatureClass_conversion(sdeWorkspace + "sclblkgrp", dataset, "sclblkgrp")
        print "\n", arcpy.GetMessages()

        #Set variable for codeblock to calculate TRACTBLKGRP field
        xStep = 'Set variable for codeblock to calculate TRACTBLKGRP field'
        blkgrpCodeblock = """def CalcField(BlockGroup):
            return BlockGroup[-1]"""

        # Calculate TRACTBLKGRP field
        xStep = 'Calculate TRACTBLKGRP field'
        arcpy.CalculateField_management(blkgrp, "TRACTBLKGRP", "CalcField(str(!tractblkgrp!))", "PYTHON_9.3", blkgrpCodeblock)
        print "\n", arcpy.GetMessages()

        # Select County Boundary arcs from sclarc in prscl.sde and create a polygon layer
        xStep = 'Select County Boundary arcs from sclarc in prscl.sde and create a polygon layer'
        arcpy.Select_analysis(sclarc, cntyStateArc, "STRCLASSI = 16")
        print "\n", arcpy.GetMessages()
        arcpy.FeatureToPolygon_management(cntyStateArc, cntyState, "", "NO_ATTRIBUTES", "")
        print "\n", arcpy.GetMessages()

        # Add COUNTY and STATE fields and calculate
        xStep = 'Add COUNTY and STATE fields and calculate'
        arcpy.AddField_management(cntyState, "COUNTY", "TEXT", "", "", "5", "", "NULLABLE", "NON_REQUIRED", "")
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management(cntyState, "COUNTY", "32003", "PYTHON_9.3", "")
        print "\n", arcpy.GetMessages()
        arcpy.AddField_management(cntyState, "STATE", "TEXT", "", "", "3", "", "NULLABLE", "NON_REQUIRED", "")
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management(cntyState, "STATE", "32", "PYTHON_9.3", "")
        print "\n", arcpy.GetMessages()

        # Identity between sclblkpt and CLARKTRS for BOOKSEC field info
        xStep = 'Identity between sclblkpt and CLARKTRS for BOOKSEC field info'
        arcpy.Identity_analysis(sdeWorkspace + "sclblkpt", bookSec, blkptBooksec, "NO_FID", "", "NO_RELATIONSHIPS")
        print "\n", arcpy.GetMessages()
        arcpy.DeleteField_management(blkptBooksec, "ATTUPD;TRACT;BLKGRP;PLACE;MCD;BLOCK;ZIP;BKNO;SECTNO;TOWNSHIP;RANGE;HALFTR;EXTENT;ZNMAP;FIREAREA;FIRENS;FIREEW;ZNKEY;FRONTBOY;BOOKQUAD;BATTALION;FIREMPNO;FLAG;BKNOC;SECTNOC")
        print "\n", arcpy.GetMessages()

        # Identity all polygon layers to create one polygon layer
        xStep = 'Identity all polygon layers to create one polygon layer'
        arcpy.Identity_analysis(cntyState, sdeWorkspace + "scltract", cntyStateTract, "NO_FID", "", "NO_RELATIONSHIPS")
        print "\n", arcpy.GetMessages()
        arcpy.Identity_analysis(cntyStateTract, sdeWorkspace + "sclblock", tractBlock, "NO_FID", "", "NO_RELATIONSHIPS")
        print "\n", arcpy.GetMessages()
        arcpy.Identity_analysis(tractBlock, sdeWorkspace + "sclzip", blockZip, "NO_FID", "", "NO_RELATIONSHIPS")
        print "\n", arcpy.GetMessages()
        arcpy.Identity_analysis(blockZip, place, zipPlace, "NO_FID", "", "NO_RELATIONSHIPS")
        print "\n", arcpy.GetMessages()
        arcpy.Identity_analysis(zipPlace, sdeWorkspace + "sclmcd", placeMcd, "NO_FID", "", "NO_RELATIONSHIPS")
        print "\n", arcpy.GetMessages()
        arcpy.Identity_analysis(placeMcd, blkgrp, mcdBlkgrp, "NO_FID", "", "NO_RELATIONSHIPS")
        print "\n", arcpy.GetMessages()
        arcpy.Identity_analysis(mcdBlkgrp, sdeWorkspace + "precinct", blkgrpPrec, "NO_FID", "", "NO_RELATIONSHIPS")
        print "\n", arcpy.GetMessages()
        arcpy.SpatialJoin_analysis(blkgrpPrec, blkptBooksec, sclarcPolys, "JOIN_ONE_TO_ONE", "KEEP_ALL", "", "CONTAINS")
        print "\n", arcpy.GetMessages()
        arcpy.DeleteField_management(sclarcPolys, "Join_Count;TARGET_FID;ATTUPD;WARD;COMMISSION;ASSEMBLY;SENATE;EDUCATION;REGENT;SCHOOL;CONGRESS;TOWNSHIP;POLLING")
        print "\n", arcpy.GetMessages()

        # -------------------------------
        # sclnine, sclarc and sclarc_id processing
        #--------------------------------

        # Set variable for codeblock to calculate null values to blanks
        xStep = 'Set variable for codeblock to calculate null values to blanks'
        nullCodeblock = """def CalcField(Record):
                if str(Record) == 'None':
                    return ''
                else:
                    return Record"""

        # Calculate STRDIR to account for null values on sclarc and sclnine
        xStep = 'Calculate STRDIR to account for null values on sclarc and sclnine'
        arcpy.CalculateField_management(sclarc, "STRDIR", "CalcField(!strdir!).strip()", "PYTHON_9.3", nullCodeblock)
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management(sclnine, "STRDIR", "CalcField(!strdir!).strip()", "PYTHON_9.3", nullCodeblock)
        print "\n", arcpy.GetMessages()

        # Calculate STRPRETYPE to account for null values on sclarc and sclnine
        xStep = 'Calculate STRPRETYPE to account for null values on sclarc and sclnine'
        arcpy.CalculateField_management(sclarc, "STRPRETYPE", "CalcField(!strpretype!)", "PYTHON_9.3", nullCodeblock)
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management(sclnine, "STRPRETYPE", "CalcField(!strpretype!)", "PYTHON_9.3", nullCodeblock)
        print "\n", arcpy.GetMessages()

        # Calculate STRNAME field to ensure there are no extra spaces in the field on sclarc and sclnine
        xStep = 'Calculate STRNAME field to ensure there are no extra spaces in the field on sclarc and sclnine'
        arcpy.CalculateField_management(sclarc, "STRNAME", "!strname!.strip()", "PYTHON_9.3", "")
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management(sclnine, "STRNAME", "!strname!.strip()", "PYTHON_9.3", "")
        print "\n", arcpy.GetMessages()

        # Set variable for codeblock to calculate STRNAME field
        xStep = 'Set variable for codeblock to calculate STRNAME field'
        strnameCodeblock = """def CalcField(StreetPreType, StreetName):
                if (StreetPreType == 'CC') or (StreetPreType =='I') or (StreetPreType == 'SR') or (StreetPreType == 'US'):
                    return (StreetPreType + ' ' + StreetName)
                else:
                    return StreetName"""

        # Concatenate STRNAME field to include STRPRETYPE where STRPRETYPE is not blank
        xStep = 'Concatenate STRNAME field to include STRPRETYPE where STRPRETYPE is not blank'
        arcpy.CalculateField_management(sclarc, "STRNAME", "CalcField(!strpretype!,!strname!)", "PYTHON_9.3", strnameCodeblock)
        print "\n", arcpy.GetMessages()

        # Delete STRPRETYPE field
        xStep = 'Delete STRPRETYPE field'
        arcpy.DeleteField_management(sclarc, "STRPRETYPE")
        print "\n", arcpy.GetMessages()

        # Calculate STRTYPE to account for null values on sclarc and sclnine
        xStep = 'Calculate STRTYPE to account for null values on sclarc and sclnine'
        arcpy.CalculateField_management(sclarc, "STRTYPE", "CalcField(!strtype!).strip()", "PYTHON_9.3", nullCodeblock)
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management(sclnine, "STRTYPE", "CalcField(!strtype!).strip()", "PYTHON_9.3", nullCodeblock)
        print "\n", arcpy.GetMessages()

        # Add STRSUF and NSCODE fields to sclarc, remove nulls from STRSUF field
        xStep = 'Add STRSUF and NSCODE fields to sclarc, remove nulls from STRSUF field'
        arcpy.AddField_management(sclarc, "STRSUF", "TEXT", "", "", "2", "", "NULLABLE", "NON_REQUIRED", "")
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management(sclarc, "STRSUF", "CalcField(!strsuf!)", "PYTHON_9.3", nullCodeblock)
        print "\n", arcpy.GetMessages()
        arcpy.AddField_management(sclarc, "NSCODE", "SHORT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
        print "\n", arcpy.GetMessages()

        # Set variable for codeblock to calculate NSCODE field
        xStep = 'Set variable for codeblock to calculate NSCODE field'
        nscodeCodeblock = """def CalcField(StreetClass):
            if (StreetClass < 11) or (StreetClass == 12) or (StreetClass == 18):
                return 0
            elif (StreetClass == 11):
                return 1
            elif (StreetClass == 19):
                return 2
            elif (StreetClass > 12) and (StreetClass < 18):
                return 3"""

        # Calculate NSCODE field
        xStep = 'Calculate NSCODE field'
        arcpy.CalculateField_management(sclarc, "NSCODE", "CalcField(!strclassi!)", "PYTHON_9.3", nscodeCodeblock)
        print "\n", arcpy.GetMessages()

        # Identity sclarc to sclarc_polys, keeping relationships to create sclarc_id
        xStep = 'Identity sclarc to sclarc_polys, keeping relationships to create sclarc_id'
        arcpy.Identity_analysis(sclarc, sclarcPolys, sclarcId, "NO_FID", "", "KEEP_RELATIONSHIPS")
        print "\n", arcpy.GetMessages()

        # Add new fields to sclarc_id
        xStep = 'Add new fields to sclarc_id'
        arcpy.AddField_management(sclarcId, "FR_X", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
        print "\n", arcpy.GetMessages()
        arcpy.AddField_management(sclarcId, "FR_LAT", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
        print "\n", arcpy.GetMessages()
        arcpy.AddField_management(sclarcId, "FR_Y", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
        print "\n", arcpy.GetMessages()
        arcpy.AddField_management(sclarcId, "FR_LONG", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
        print "\n", arcpy.GetMessages()
        arcpy.AddField_management(sclarcId, "FMAPBASIC", "LONG", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
        print "\n", arcpy.GetMessages()
        arcpy.AddField_management(sclarcId, "FMAPSUF", "TEXT", "", "", "2", "", "NULLABLE", "NON_REQUIRED", "")
        print "\n", arcpy.GetMessages()
        arcpy.AddField_management(sclarcId, "TO_X", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
        print "\n", arcpy.GetMessages()
        arcpy.AddField_management(sclarcId, "TO_LAT", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
        print "\n", arcpy.GetMessages()
        arcpy.AddField_management(sclarcId, "TO_Y", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
        print "\n", arcpy.GetMessages()
        arcpy.AddField_management(sclarcId, "TO_LONG", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
        print "\n", arcpy.GetMessages()
        arcpy.AddField_management(sclarcId, "TMAPBASIC", "LONG", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
        print "\n", arcpy.GetMessages()
        arcpy.AddField_management(sclarcId, "TMAPSUF", "TEXT", "", "", "2", "", "NULLABLE", "NON_REQUIRED", "")
        print "\n", arcpy.GetMessages()
        arcpy.AddField_management(sclarcId, "STRCLASS", "TEXT", "", "", "20", "", "NULLABLE", "NON_REQUIRED", "")
        print "\n", arcpy.GetMessages()
        arcpy.AddField_management(sclarcId, "FFDAD", "TEXT", "", "", "4", "", "NULLABLE", "NON_REQUIRED", "")
        print "\n", arcpy.GetMessages()
        arcpy.AddField_management(sclarcId, "TFDAD", "TEXT", "", "", "4", "", "NULLABLE", "NON_REQUIRED", "")
        print "\n", arcpy.GetMessages()

        # Remove null value from non-coded fields
        xStep = 'Remove null value from non-coded fields'
        arcpy.CalculateField_management(sclarcId, "FMAPSUF", "CalcField(!fmapsuf!)", "PYTHON_9.3", nullCodeblock)
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management(sclarcId, "TMAPSUF", "CalcField(!tmapsuf!)", "PYTHON_9.3", nullCodeblock)
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management(sclarcId, "FFDAD", "CalcField(!ffdad!)", "PYTHON_9.3", nullCodeblock)
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management(sclarcId, "TFDAD", "CalcField(!tfdad!)", "PYTHON_9.3", nullCodeblock)
        print "\n", arcpy.GetMessages()

        # Add attribute indexes to sclarc_id
        xStep = 'Add attribute indexes to sclarc_id'
        arcpy.AddIndex_management(sclarcId, "STRNAME", "StrnameArcIndex", "NON_UNIQUE", "ASCENDING")
        print "\n", arcpy.GetMessages()
        arcpy.AddIndex_management(sclarcId, "CENSUSID", "CensusidArcIndex", "UNIQUE", "ASCENDING")
        print "\n", arcpy.GetMessages()
        arcpy.AddIndex_management(sclarcId, "FNODE", "FnodeArcIndex", "NON_UNIQUE", "ASCENDING")
        print "\n", arcpy.GetMessages()
        arcpy.AddIndex_management(sclarcId, "TNODE", "TnodeArcIndex", "NON_UNIQUE", "ASCENDING")
        print "\n", arcpy.GetMessages()
        arcpy.AddIndex_management(sclarcId, "FELEV", "FelevArcIndex", "NON_UNIQUE", "ASCENDING")
        print "\n", arcpy.GetMessages()
        arcpy.AddIndex_management(sclarcId, "TELEV", "TelevArcIndex", "NON_UNIQUE", "ASCENDING")
        print "\n", arcpy.GetMessages()

        #--------------------------------------------
        # Sclnode processing to code sclarc_id fields
        #--------------------------------------------

        # Add attribute index to sclnode for UNQNODENO
        xStep = 'Add attribute index to sclnode for UNQNODENO'
        arcpy.AddIndex_management(sclnode, "UNQNODENO", "NodeIndex", "UNIQUE", "ASCENDING")
        print "\n", arcpy.GetMessages()

        # Project sclnode to WGS84 and add XY (Lat/Long) coordinates
        xStep = 'Project sclnode to WGS84 and add XY (Lat/Long) coordinates'
        arcpy.Project_management(sclnode, sclnodeProj, "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]", "NAD_1983_To_WGS_1984_1", "PROJCS['NAD_1983_StatePlane_Nevada_East_FIPS_2701_Feet',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',656166.6666666665],PARAMETER['False_Northing',26246666.66666666],PARAMETER['Central_Meridian',-115.5833333333333],PARAMETER['Scale_Factor',0.9999],PARAMETER['Latitude_Of_Origin',34.75],UNIT['Foot_US',0.3048006096012192]]")
        print "\n", arcpy.GetMessages()
        arcpy.AddXY_management(sclnodeProj)
        print "\n", arcpy.GetMessages()

        # Add XY coordinates to sclnode
        xStep = 'Add XY coordinates to sclnode'
        arcpy.AddXY_management(sclnode)
        print "\n", arcpy.GetMessages()

        # Spatial join between sclnode to dimemap to create sclnode_dime
        xStep = 'Spatial join between sclnode to dimemap to create sclnode_dime'
        arcpy.SpatialJoin_analysis(sclnode, sclDimemap, sclnodeDime, "JOIN_ONE_TO_ONE", "KEEP_ALL", "", "INTERSECT")
        print "\n", arcpy.GetMessages()
        arcpy.DeleteField_management(sclnodeDime, "Join_Count;TARGET_FID;PERIMETER;DIMEMAP_;DIMEMAP_ID;AREA")
        print "\n", arcpy.GetMessages()

        # Identity between sclnode_dime and sclnode_proj
        xStep = 'Identity between sclnode_dime and sclnode_proj'
        arcpy.Identity_analysis(sclnodeDime, sclnodeProj, sclnodeAllXy, "NO_FID", "", "NO_RELATIONSHIPS")
        print "\n", arcpy.GetMessages()
        arcpy.DeleteField_management(sclnodeAllXy, "UNQNODENO_1")
        print "\n", arcpy.GetMessages()

        # Add index on sclnode_allxy on UNQNODENO field
        xStep = 'Add index on sclnode_allxy on UNQNODENO field'
        arcpy.AddIndex_management(sclnodeAllXy, "UNQNODENO", "sclnodeAllXyIndex", "UNIQUE", "ASCENDING")
        print "\n", arcpy.GetMessages()

        # Make Feature Layer for sclarc_id and sclnode_allxy
        xStep = 'Make Feature Layer for sclarc_id and sclnode_allxy'
        arcpy.MakeFeatureLayer_management(sclarcId, "sclarc_id_lyr")
        print "\n", arcpy.GetMessages()
        arcpy.MakeFeatureLayer_management(sclnodeAllXy, "sclnodeAllXy_lyr")
        print "\n", arcpy.GetMessages()

        # Add Join between sclarc_id_lyr and sclnode_allxy on FNODE, calculate fields, and remove join
        xStep = 'Add Join between sclarc_id_lyr and sclnode_allxy on FNODE, calculate fields, and remove join'
        arcpy.AddJoin_management("sclarc_id_lyr", "FNODE", "sclnodeAllXy_lyr", "UNQNODENO", "KEEP_COMMON")
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management("sclarc_id_lyr", "sclarc_id.FR_X", "!sclnode_allxy.POINT_X!", "PYTHON_9.3", "")
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management("sclarc_id_lyr", "sclarc_id.FR_LAT", "!sclnode_allxy.POINT_Y_1!", "PYTHON_9.3", "")
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management("sclarc_id_lyr", "sclarc_id.FR_Y", "!sclnode_allxy.POINT_Y!", "PYTHON_9.3", "")
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management("sclarc_id_lyr", "sclarc_id.FR_LONG", "!sclnode_allxy.POINT_X_1!", "PYTHON_9.3", "")
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management("sclarc_id_lyr", "sclarc_id.FMAPBASIC", "!sclnode_allxy.MAPNO!", "PYTHON_9.3", "")
        print "\n", arcpy.GetMessages()
        arcpy.RemoveJoin_management("sclarc_id_lyr")
        print "\n", arcpy.GetMessages()

        # Add Join between sclarc_id and sclnode_allxy on TNODE, calculate fields, and remove join
        xStep = 'Add Join between sclarc_id and sclnode_allxy on TNODE, calculate fields, and remove join'
        arcpy.AddJoin_management("sclarc_id_lyr", "TNODE", "sclnodeAllXy_lyr", "UNQNODENO", "KEEP_COMMON")
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management("sclarc_id_lyr", "sclarc_id.TO_X", "!sclnode_allxy.POINT_X!", "PYTHON_9.3", "")
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management("sclarc_id_lyr", "sclarc_id.TO_LAT", "!sclnode_allxy.POINT_Y_1!", "PYTHON_9.3", "")
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management("sclarc_id_lyr", "sclarc_id.TO_Y", "!sclnode_allxy.POINT_Y!", "PYTHON_9.3", "")
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management("sclarc_id_lyr", "sclarc_id.TO_LONG", "!sclnode_allxy.POINT_X_1!", "PYTHON_9.3", "")
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management("sclarc_id_lyr", "sclarc_id.TMAPBASIC", "!sclnode_allxy.MAPNO!", "PYTHON_9.3", "")
        print "\n", arcpy.GetMessages()
        arcpy.RemoveJoin_management("sclarc_id_lyr")
        print "\n", arcpy.GetMessages()

        #-----------------------------------
        # continue with sclarc_id processing
        #-----------------------------------

        # Set variable for codeblock to calculate STRCLASS field
        xStep = 'Set variable for codeblock to calculate STRCLASS field'
        strclassCodeblock = """def CalcField(StreetClass):
            if (StreetClass == 0):
                return 'Local'
            elif (StreetClass == 1):
                return 'Tributary'
            elif (StreetClass == 2):
                return 'Access'
            elif (StreetClass == 3):
                return 'Collector'
            elif (StreetClass == 4):
                return 'Major Street'
            elif (StreetClass == 5):
                return 'Ramp'
            elif (StreetClass == 6):
                return 'County Highway'
            elif (StreetClass == 7):
                return 'US Highway'
            elif (StreetClass == 8):
                return 'State Highway'
            elif (StreetClass == 9):
                return 'Interstate'
            elif (StreetClass == 10):
                return 'Rural Travel'
            elif (StreetClass == 11):
                return 'Railroad'
            elif (StreetClass == 12):
                return '4WD High Clearance'
            elif (StreetClass == 13):
                return 'Corp Limit'
            elif (StreetClass == 14):
                return 'Precinct Bdry'
            elif (StreetClass == 15):
                return 'Miscellaneous Bdry'
            elif (StreetClass == 16):
                return 'County Boundary'
            elif (StreetClass == 17):
                return 'Feature Bdry'
            elif (StreetClass == 18):
                return 'Emerg Vehicles Only'
            elif (StreetClass == 19):
                return 'Planned Road'"""

        # Calculate STRCLASS field and delete STRCLASSI field
        xStep = 'Calculate STRCLASS field and delete STRCLASSI field'
        arcpy.CalculateField_management(sclarcId, "STRCLASS", "CalcField(!STRCLASSI!)", "PYTHON_9.3", strclassCodeblock)
        print "\n", arcpy.GetMessages()
        arcpy.DeleteField_management(sclarcId, "STRCLASSI")
        print "\n", arcpy.GetMessages()

        #--------------------------------------------------------------------
        # Create point feature class to calculate cross street fields for sclarc_id
        #--------------------------------------------------------------------

        xStep = 'Create point feature class to calculate cross street fields for sclarc_id'
        # Intersect sclnode and sclarc_id, and delete unnecessary fields
        arcpy.Intersect_analysis([sclarcId,sclnode], intersect, "NO_FID", "", "POINT")
        print "\n", arcpy.GetMessages()
        arcpy.DeleteField_management(intersect, "POINT_X;POINT_Y;LFADD;RFADD;RTADD;LMailZip;RMailZip;STRSUF;LEFT_COUNTY;RIGHT_COUNTY;LEFT_STATE;RIGHT_STATE;LEFT_TRACT;RIGHT_TRACT;LEFT_BLOCK;RIGHT_BLOCK;LEFT_ZIP;RIGHT_ZIP;LEFT_PLACE;RIGHT_PLACE;LEFT_LOC;RIGHT_LOC;LEFT_MCD;RIGHT_MCD;LEFT_TRACTBLKGRP;RIGHT_TRACTBLKGRP;FR_X;FR_LAT;FR_Y;FR_LONG;FMAPBASIC;FMAPSUF;TO_X;TO_LAT;TO_Y;TO_LONG;TMAPBASIC;TMAPSUF;STRCLASS;FFDAD;TFDAD")
        print "\n", arcpy.GetMessages()

        # Add attribute index to node_arc for all fields used in queries
        xStep = 'Add attribute index to node_arc for all fields used in queries'
        arcpy.AddIndex_management(intersect, "STRNAME", "StrnameNodeIndex", "NON_UNIQUE", "ASCENDING")
        print "\n", arcpy.GetMessages()
        arcpy.AddIndex_management(intersect, "CENSUSID", "CensusidNodeIndex", "NON_UNIQUE", "ASCENDING")
        print "\n", arcpy.GetMessages()
        arcpy.AddIndex_management(intersect, "FNODE", "FnodeNodeIndex", "NON_UNIQUE", "ASCENDING")
        print "\n", arcpy.GetMessages()
        arcpy.AddIndex_management(intersect, "TNODE", "TnodeNodeIndex", "NON_UNIQUE", "ASCENDING")
        print "\n", arcpy.GetMessages()
        arcpy.AddIndex_management(intersect, "FELEV", "FelevNodeIndex", "NON_UNIQUE", "NON_ASCENDING")
        print "\n", arcpy.GetMessages()
        arcpy.AddIndex_management(intersect, "TELEV", "TelevNodeIndex", "NON_UNIQUE", "NON_ASCENDING")
        print "\n", arcpy.GetMessages()
        arcpy.AddIndex_management(intersect, "NSCODE", "NscodeIndex", "NON_UNIQUE", "NON_ASCENDING")
        print "\n", arcpy.GetMessages()
        arcpy.AddIndex_management(intersect, "UNQNODENO", "UnqNodeIndex", "NON_UNIQUE", "ASCENDING")
        print "\n", arcpy.GetMessages()

        # -------------------------------------------------------------------------
        # ArcXstreet --------------------------------------------------------------
        # -------------------------------------------------------------------------

        # Set additional variables for the environment
        arcSelect = dataset + "/sclarc_id"
        nodeSelect = dataset + "/node_arc"
        xstreetTable = internetFileGdb + "/Xstreet"

        xStep = 'delete xstreetTable'
        if arcpy.Exists(xstreetTable):
            arcpy.Delete_management(xstreetTable)

        xStep = 'set arc field variables'
        # Set variables for arc fields
        arcCensusidField = "CENSUSID"
        arcFnodeField = "FNODE"
        arcTnodeField = "TNODE"
        arcFelevField = "FELEV"
        arcTelevField = "TELEV"
        arcStrnameField = "STRNAME"
        arcFltaddField = "FLTADD"
        arcFstrnameField = "FSTRNAME"
        arcFstrtypeField = "FSTRTYPE"
        arcFstrdirField = "FSTRDIR"
        arcFcensusidField = "FCENSUSID"
        arcF2ltaddField = "F2LTADD"
        arcF2strnameField = "F2STRNAME"
        arcF2strtypeField = "F2STRTYPE"
        arcF2strdirField = "F2STRDIR"
        arcF2censusidField = "F2CENSUSID"
        arcF3ltaddField = "F3LTADD"
        arcF3strnameField = "F3STRNAME"
        arcF3strtypeField = "F3STRTYPE"
        arcF3strdirField = "F3STRDIR"
        arcF3censusidField = "F3CENSUSID"
        arcTltaddField = "TLTADD"
        arcTstrnameField = "TSTRNAME"
        arcTstrtypeField = "TSTRTYPE"
        arcTstrdirField = "TSTRDIR"
        arcTcensusidField = "TCENSUSID"
        arcT2ltaddField = "T2LTADD"
        arcT2strnameField = "T2STRNAME"
        arcT2strtypeField = "T2STRTYPE"
        arcT2strdirField = "T2STRDIR"
        arcT2censusidField = "T2CENSUSID"
        arcT3ltaddField = "T3LTADD"
        arcT3strnameField = "T3STRNAME"
        arcT3strtypeField = "T3STRTYPE"
        arcT3strdirField = "T3STRDIR"
        arcT3censusidField = "T3CENSUSID"

        # Set variables for node fields
        xStep = 'set node field variables'
        nodeLtaddField = "LTADD"
        nodeStrnameField = "STRNAME"
        nodeStrtypeField = "STRTYPE"
        nodeStrdirField = "STRDIR"
        nodeCensusidField = "CENSUSID"
        nodeUnqField = "UNQNODENO"
        nodeFnodeField = "FNODE"
        nodeTnodeField = "TNODE"
        nodeFelevField = "FELEV"
        nodeTelevField = "TELEV"
        nodeNscodeField = "NSCODE"

        # Make a feature layer of the node layer
        #arcpy.MakeFeatureLayer_management(nodeSelect, "NodeSelectLayer")

        # Create a new table to code with xstreet information
        xStep = 'Create a new table to code with xstreet information'
        arcpy.CreateTable_management(internetFileGdb, "xstreet", xstreetTemplate, "")

        # Set variable for fields used in Update Cursor for arc layer
        xStep = 'et variable for fields used in Update Cursor for arc layer'
        xStreetFields = (arcCensusidField,arcFltaddField, arcFstrnameField, arcFstrtypeField, arcFstrdirField, arcFcensusidField, arcF2ltaddField, arcF2strnameField, arcF2strtypeField, arcF2strdirField, arcF2censusidField, arcF3ltaddField, arcF3strnameField, arcF3strtypeField, arcF3strdirField, arcF3censusidField, arcTltaddField, arcTstrnameField, arcTstrtypeField, arcTstrdirField, arcTcensusidField, arcT2ltaddField, arcT2strnameField, arcT2strtypeField, arcT2strdirField, arcT2censusidField, arcT3ltaddField, arcT3strnameField, arcT3strtypeField, arcT3strdirField, arcT3censusidField)
        arcFields = (arcCensusidField, arcFnodeField, arcTnodeField, arcFelevField, arcTelevField, arcStrnameField)

        # Set variables for fields used in Search Cursor for node layer
        xStep = 'Set variables for fields used in Search Cursor for node layer'
        nodeFields = (nodeLtaddField, nodeStrnameField, nodeStrtypeField, nodeStrdirField, nodeCensusidField, nodeUnqField, nodeFnodeField, nodeTnodeField, nodeFelevField, nodeTelevField, nodeNscodeField)

        # Create an empty list to save the from xstreet information to in order to code the arc layer
        selectedFnodeList = []
        selectedTnodeList = []
        node_arcList = []
        firstNodeList = []
        fullArcList = []
        arcList = []

        xStep = 'load node_arc list'
        print "Start loading node_arc list " + datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")
        with arcpy.da.SearchCursor(nodeSelect,nodeFields) as nodeSelectCursor:
            for nodeSelectRow in nodeSelectCursor:
                #node_arcList.append([nodeSelectRow[0],str(nodeSelectRow[1]),str(nodeSelectRow[2]),str(nodeSelectRow[3]),nodeSelectRow[4],nodeSelectRow[5],nodeSelectRow[6],nodeSelectRow[7],nodeSelectRow[8],nodeSelectRow[9]])
                node_arcList.append([nodeSelectRow[5],[nodeSelectRow[0],str(nodeSelectRow[1]),str(nodeSelectRow[2]),str(nodeSelectRow[3]),nodeSelectRow[4],nodeSelectRow[5],nodeSelectRow[6],nodeSelectRow[7],nodeSelectRow[8],nodeSelectRow[9],nodeSelectRow[10]]])
        print "Finished loading node_arc list " + datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")
        print ""

        #nodeDict = {k:v for k, v in zip(tuple(node_keys), tuple(node_arcList))}
        #nodeDict = dict(itertools.izip(tuple(node_keys), tuple(node_arcList)))
        xStep = 'create temporary node dictionary'
        nodeDictTemp = defaultdict(list)

        for k, v in node_arcList:
            nodeDictTemp[k].append(v)

        xStep = 'create node dictionary'
        nodeDict = dict((k,v) for k,v in nodeDictTemp.iteritems())
        del nodeDictTemp
        del node_arcList

        xStep = 'load sclarc_id list'
        print "Start loading sclarc_id list " + datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")
        with arcpy.da.SearchCursor(arcSelect, arcFields) as arcCursor:
            for aRow in arcCursor:
                fullArcList.append([aRow[0],aRow[1],aRow[2],aRow[3],aRow[4],str(aRow[5])])

        print "Finished loading sclarc_id list " + datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")
        print ""

        # Create an insert cursor to code the xstreet table
        xStep = 'Code xstreet table'
        xStreetCursor = arcpy.da.InsertCursor(xstreetTable, xStreetFields)
        startUpdateTime = datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")
        # Start looping through the arc layer
        # Many, MANY comments were taken out here.  See archive version for them.
        for arcListRow in fullArcList:
            xRow = [None] * 31
            xRow[0] = arcListRow[0]
            filteredNodes = [arcListRow[1],arcListRow[2]]
            firstNodeListTemp = [nodeDict[k] for k in filteredNodes]
            firstNodeList = [item for sublist in firstNodeListTemp for item in sublist]
            del firstNodeListTemp

            # FROM XSTREET SECTION----------------------------------------------------------------------------
            counterFromNoMatch = 0
            counterFromMatch = 0
            counterToNoMatch = 0
            counterToMatch = 0
            selectedFnodeList[:] = []
            selectedTnodeList[:] = []
            for nodeRow in firstNodeList:
                nodeLtadd = nodeRow[0]
                nodeStrname = nodeRow[1]
                nodeStrtype = nodeRow[2]
                nodeStrdir = nodeRow[3]
                nodeCensusid = nodeRow[4]
                if nodeRow[5] == arcListRow[1] and nodeRow[4] != arcListRow[0] and nodeRow[10] == 0:
                    if nodeRow[1] != arcListRow[5]:
                        if nodeRow[5] == nodeRow[7] and arcListRow[3] == nodeRow[9]:
                            selectedFnodeList.append([nodeLtadd,str(nodeStrname),str(nodeStrtype),str(nodeStrdir),nodeCensusid])
                            counterFromMatch += 1
                        elif nodeRow[5] == nodeRow[6] and arcListRow[3] == nodeRow[8]:
                            selectedFnodeList.append([nodeLtadd,str(nodeStrname),str(nodeStrtype),str(nodeStrdir),nodeCensusid])
                            counterFromMatch += 1
                else:
                    counterFromNoMatch += 1
                if nodeRow[5] == arcListRow[2] and nodeRow[4] != arcListRow[0] and nodeRow[10] == 0:
                    if nodeRow[1] != arcListRow[5]:
                        if nodeRow[5] == nodeRow[7] and arcListRow[4] == nodeRow[9]:
                            selectedTnodeList.append([nodeLtadd,str(nodeStrname),str(nodeStrtype),str(nodeStrdir),nodeCensusid])
                            counterToMatch += 1
                        elif nodeRow[5] == nodeRow[6] and arcListRow[4] == nodeRow[8]:
                            selectedTnodeList.append([nodeLtadd,str(nodeStrname),str(nodeStrtype),str(nodeStrdir),nodeCensusid])
                            counterToMatch += 1
                else:
                    counterToNoMatch += 1

            lineFromCounter = 0
            for line in selectedFnodeList:
                lineFromCounter += 1
                if lineFromCounter == 1:
                    xRow[1] = line[0]
                    xRow[2] = line[1]
                    xRow[3] = line[2]
                    xRow[4] = line[3]
                    xRow[5] = line[4]
                elif lineFromCounter == 2:
                    xRow[6] = line[0]
                    xRow[7] = line[1]
                    xRow[8] = line[2]
                    xRow[9] = line[3]
                    xRow[10] = line[4]
                elif lineFromCounter == 3:
                    xRow[11] = line[0]
                    xRow[12] = line[1]
                    xRow[13] = line[2]
                    xRow[14] = line[3]
                    xRow[15] = line[4]

            lineToCounter = 0
            for line in selectedTnodeList:
                lineToCounter += 1
                if lineToCounter == 1:
                    xRow[16] = line[0]
                    xRow[17] = line[1]
                    xRow[18] = line[2]
                    xRow[19] = line[3]
                    xRow[20] = line[4]
                elif lineToCounter == 2:
                    xRow[21] = line[0]
                    xRow[22] = line[1]
                    xRow[23] = line[2]
                    xRow[24] = line[3]
                    xRow[25] = line[4]
                elif lineToCounter == 3:
                    xRow[26] = line[0]
                    xRow[27] = line[1]
                    xRow[28] = line[2]
                    xRow[29] = line[3]
                    xRow[30] = line[4]

            for nodeEOSRow in firstNodeList:
              if counterFromMatch == 0:
                  if nodeEOSRow[5] == arcListRow[1] and arcListRow[0] == nodeEOSRow[4] and nodeEOSRow[5] != nodeEOSRow[7]:
                      selectedFnodeList.append(["End of Street"])
                  if nodeEOSRow[5] == arcListRow[1] and nodeEOSRow[5] == nodeEOSRow[7] and arcListRow[3] == nodeEOSRow[9]:
                      selectedFnodeList.append(["Continues"])
                      xRow[2] = "*Continues"
              if counterToMatch == 0:
                  if nodeEOSRow[5] == arcListRow[2] and arcListRow[0] == nodeEOSRow[4] and nodeEOSRow[5] != nodeEOSRow[6]:
                      selectedTnodeList.append(["End of Street"])
                  if nodeEOSRow[5] == arcListRow[2] and nodeEOSRow[5] == nodeEOSRow[6] and arcListRow[4] == nodeEOSRow[8]:
                      selectedTnodeList.append(["Continues"])
                      xRow[17] = "*Continues"

            conCounter = 0
            eosCounter = 0
            for line in selectedFnodeList:
                if str(line[0]) == "Continues":
                    conCounter +=1
                elif str(line[0]) == "End of Street":
                    eosCounter +=1

            if conCounter == 0 and eosCounter == 1:
                xRow[2] = "*End-Of-Str"

            # TO XSTREET SECTION------------------------------------------------------------------------------------------

            contToCounter = 0
            eosToCounter = 0
            for line in selectedTnodeList:
                if str(line[0]) == "Continues":
                    contToCounter +=1
                elif str(line[0]) == "End of Street":
                    eosToCounter +=1
            if contToCounter == 0 and eosToCounter == 1:
                xRow[17] = "*End-Of-Str"

            xStreetCursor.insertRow(xRow)

            counterFromNoMatch = 0
            counterFromMatch = 0
            counterToNoMatch = 0
            counterToMatch = 0

            xRow[:] = []
            firstNodeList[:] = []

        # ------------------------------------------------------------------------
        # ArcXstreetNinesInternet ------------------------------------------------
        # ------------------------------------------------------------------------

        # Set additional variables for the environment
        xStep = 'ArcXstreetNinesInternet'
        nineSelect = dataset + "/sclnine"
        nineInternetTable = internetFileGdb + "/nineInternet"

        if arcpy.Exists(nineInternetTable):
            arcpy.Delete_management(nineInternetTable)

        # Set variables for arc fields
        descArcs = arcpy.Describe(arcSelect)
        arcFieldList = []
        for field in descArcs.fields:
            arcFieldList.append(str(field.name))

        arcFieldList.remove("Shape")
        arcFieldList.remove("Shape_Length")
        arcFieldList.remove("OBJECTID")

        # xstreet Fields
        descXStreets = arcpy.Describe(xstreetTable)
        xStreetsFieldList = []
        for field in descXStreets.fields:
            xStreetsFieldList.append(str(field.name))
        xStreetsFieldList.remove("OBJECTID")

        # Set variables for nine fields
        nineCensusID = "censusid"
        nineAliasID = "aliasid"
        nineAddr = "addr"
        nineSide = "side"
        nineStrDir = "strdir"
        nineStrPreType = "strpretype"
        nineStrName = "strname"
        nineStrType = "strtype"

        # Start Nine Record insertion process

        # set nine field list
        xStep = 'set nine field list'
        nineList = []
        descNine = arcpy.Describe(nineSelect)
        nineFieldList = []
        for field in descNine.fields:
            nineFieldList.append(str(field.name))
        nineFieldList.remove("OBJECTID")
        nineFieldList.remove("Shape")
        nineFieldList.remove("PARCEL")

        print "Start loading sclnine list" + datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")
        with arcpy.da.SearchCursor(nineSelect, nineFieldList) as nineCursor:
            for nRow in nineCursor:
                nineList.append([nRow[0],nRow[1],nRow[2],nRow[3],nRow[4],nRow[5],nRow[6],nRow[7]])

        #load xStreetTable into list
        xStep = 'load xStreetTable into list'
        xStreetList = []
        print "Start loading xstreet list " + datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")
        with arcpy.da.SearchCursor(xstreetTable,xStreetsFieldList) as xStreetCursor:
            for xRow in xStreetCursor:
                xStreetList.append([xRow[0],[xRow]])

        xStep = 'create xStreet dictionary'
        xStreetDictTemp = defaultdict(list)
        for k, v in xStreetList:
            xStreetDictTemp[k].append(v)
        xStreetDict = dict((k,v) for k,v in xStreetDictTemp.iteritems())
        del xStreetDictTemp
        del xStreetList

        #load arcs into list
        arcList = []
        print "Start loading arcs list " + datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")
        with arcpy.da.SearchCursor(arcSelect,arcFieldList) as arcCursor:
            for aRow in arcCursor:
                arcList.append([aRow[7],[aRow]])

        arcDictTemp = defaultdict(list)
        for k, v in arcList:
            arcDictTemp[k].append(v)
        arcDict = dict((k,v) for k,v in arcDictTemp.iteritems())
        del arcDictTemp
        del arcList

        # Create a new table to code with nines information
        xStep = 'Create a new table to code with nines information'
        arcpy.CreateTable_management(internetFileGdb, "nineInternet", nineInternetTemplate, "")
        descNineInternet = arcpy.Describe(nineInternetTable)
        nineInternetFieldList = []
        for field in descNineInternet.fields:
            nineInternetFieldList.append(str(field.name))

        nineInternetFieldList.remove("OBJECTID")

        print "Processing files... at " + datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")

        nineInternetCursor = arcpy.da.InsertCursor(nineInternetTable, nineInternetFieldList)

        # Create temporary list for insertion purposes
        xRow = []

        xStep = 'iterate through nineList'
        for row in nineList:
            key = row[0]
            if key in arcDict:
                arcTemp = list(*(itertools.chain(*arcDict[key])))
                xStreetTemp = list(*(itertools.chain(*xStreetDict[key])))
                xRow = arcTemp + xStreetTemp
                # Switch CensusID to AliasID
                xRow[7] = row[1]
                # Calc NSCODE = 9
                xRow[15] = 9
                # Switch street name information
                xRow[0] = str(row[4])
                xRow[1] = str(row[6])
                xRow[2] = str(row[7])
                if row[3] == 'L':
                    # Calc Left address info
                    xRow[3] = row[2]
                    xRow[4] = row[2]
                    # Zero out Right Address INfo
                    xRow[5] = 0
                    xRow[6] = 0
                else:
                    # Zero Left address info
                    xRow[3] = 0
                    xRow[4] = 0
                    # Calc Right Address INfo
                    xRow[5] = row[2]
                    xRow[6] = row[2]

                nineInternetCursor.insertRow(xRow)
                # Reset temporary list
                xRow[:] = []

        del nineInternetCursor

        #--------------------------------------------------------------------------
        # InternetFile_Xstreet ----------------------------------------------------
        #--------------------------------------------------------------------------
        arcpy.env.qualifiedFieldNames = False

        xStep = 'InternetFile_Xstreet'
        # Set additional variables for the environment
        sclarcId = internetFileGdb + "/Data/sclarc_id"
        sclarcIdXstreet = internetFileGdb + "/Data/sclarc_id_xstreet"
        nineTable = internetFileGdb + "/nineInternet"
        xstreetTable = internetFileGdb + "/xstreet"
        internetFile = internetFileGdb + "/internetFile"

        # Create the complete Internet File
        xStep = 'Create the complete Internet File'
        arcpy.AddIndex_management(xstreetTable, "CENSUSID", "CID_Index", "UNIQUE", "ASCENDING")
        print "\n", arcpy.GetMessages()
        arcpy.MakeFeatureLayer_management(sclarcId, "sclarc_id_lyr")
        print "\n", arcpy.GetMessages()
        arcpy.AddJoin_management("sclarc_id_lyr", "CENSUSID", xstreetTable, "CENSUSID", "KEEP_ALL")
        print "\n", arcpy.GetMessages()
        arcpy.CopyFeatures_management("sclarc_id_lyr", sclarcIdXstreet)
        print "\n", arcpy.GetMessages()
        arcpy.TableToTable_conversion(sclarcIdXstreet, internetFileGdb, "internetFile")
        print "\n", arcpy.GetMessages()
        arcpy.RemoveJoin_management("sclarc_id_lyr")
        print "\n", arcpy.GetMessages()
        arcpy.DeleteField_management(internetFile, "OBJECTID_1;CENSUSID_1;Shape_Length")
        print "\n", arcpy.GetMessages()
        arcpy.DeleteField_management(nineTable, "CENSUSID_1")
        print "\n", arcpy.GetMessages()
        arcpy.Append_management(nineTable, internetFile)
        print "\n", arcpy.GetMessages()

        # Set variable for codeblock to calculate null values to blanks
        xStep = 'Set variable for codeblock to calculate null values to blanks'
        nullCodeblock = """def CalcField(Record):
            if str(Record) == 'None':
                return ''
            else:
                return Record"""

        # Set variable for codeblock to calculate null values for number fields
        xStep = 'Set variable for codeblock to calculate null values for number fields'
        nullnumCodeblock = """def CalcField(Record):
            if (Record) is None:
                return 0
            else:
                return Record"""

        # Remove null values from fields
        xStep = 'Remove null values from fields'
        arcpy.CalculateField_management(internetFile, "FLTADD", "CalcField(!fltadd!)", "PYTHON_9.3", nullnumCodeblock)
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management(internetFile, "FSTRTYPE", "CalcField(!fstrtype!).strip()", "PYTHON_9.3", nullCodeblock)
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management(internetFile, "FSTRDIR", "CalcField(!fstrdir!).strip()", "PYTHON_9.3", nullCodeblock)
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management(internetFile, "FCENSUSID", "CalcField(!fcensusid!)", "PYTHON_9.3", nullnumCodeblock)
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management(internetFile, "F2LTADD", "CalcField(!f2ltadd!)", "PYTHON_9.3", nullnumCodeblock)
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management(internetFile, "F2STRNAME", "CalcField(!f2strname!)", "PYTHON_9.3", nullCodeblock)
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management(internetFile, "F2STRTYPE", "CalcField(!f2strtype!).strip()", "PYTHON_9.3", nullCodeblock)
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management(internetFile, "F2STRDIR", "CalcField(!f2strdir!).strip()", "PYTHON_9.3", nullCodeblock)
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management(internetFile, "F2CENSUSID", "CalcField(!f2censusid!)", "PYTHON_9.3", nullnumCodeblock)
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management(internetFile, "F3LTADD", "CalcField(!f3ltadd!)", "PYTHON_9.3", nullnumCodeblock)
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management(internetFile, "F3STRNAME", "CalcField(!f3strname!)", "PYTHON_9.3", nullCodeblock)
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management(internetFile, "F3STRTYPE", "CalcField(!f3strtype!).strip()", "PYTHON_9.3", nullCodeblock)
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management(internetFile, "F3STRDIR", "CalcField(!f3strdir!).strip()", "PYTHON_9.3", nullCodeblock)
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management(internetFile, "F3CENSUSID", "CalcField(!f3censusid!)", "PYTHON_9.3", nullnumCodeblock)
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management(internetFile, "TLTADD", "CalcField(!tltadd!)", "PYTHON_9.3", nullnumCodeblock)
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management(internetFile, "TSTRTYPE", "CalcField(!tstrtype!).strip()", "PYTHON_9.3", nullCodeblock)
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management(internetFile, "TSTRDIR", "CalcField(!tstrdir!).strip()", "PYTHON_9.3", nullCodeblock)
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management(internetFile, "TCENSUSID", "CalcField(!tcensusid!)", "PYTHON_9.3", nullnumCodeblock)
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management(internetFile, "T2LTADD", "CalcField(!t2ltadd!)", "PYTHON_9.3", nullnumCodeblock)
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management(internetFile, "T2STRNAME", "CalcField(!t2strname!)", "PYTHON_9.3", nullCodeblock)
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management(internetFile, "T2STRTYPE", "CalcField(!t2strtype!).strip()", "PYTHON_9.3", nullCodeblock)
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management(internetFile, "T2STRDIR", "CalcField(!t2strdir!).strip()", "PYTHON_9.3", nullCodeblock)
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management(internetFile, "T2CENSUSID", "CalcField(!t2censusid!)", "PYTHON_9.3", nullnumCodeblock)
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management(internetFile, "T3LTADD", "CalcField(!t3ltadd!)", "PYTHON_9.3", nullnumCodeblock)
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management(internetFile, "T3STRNAME", "CalcField(!t3strname!)", "PYTHON_9.3", nullCodeblock)
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management(internetFile, "T3STRTYPE", "CalcField(!t3strtype!).strip()", "PYTHON_9.3", nullCodeblock)
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management(internetFile, "T3STRDIR", "CalcField(!t3strdir!).strip()", "PYTHON_9.3", nullCodeblock)
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management(internetFile, "T3CENSUSID", "CalcField(!t3censusid!)", "PYTHON_9.3", nullnumCodeblock)
        print "\n", arcpy.GetMessages()

        #---------------------------------------------------------------------------
        # IntData_SclDimeNew -------------------------------------------------------
        #---------------------------------------------------------------------------

        # Set variables for the working environment
        xStep = 'IntData_SclDimeNew'
        intFileGdb = workspace + "/InternetFile_work.gdb/"
        intFileTable = intFileGdb + "internetFile"
        outTable = intFileGdb + "SclDimeNew"
        tableSort = intFileGdb + "SclDimeNew_Sort"

        # Set variables for output environments
        inTemplate = workspace + "/InternetFile_Template.gdb/SclDimeNew"
        prsclGdb = workspace + "/InternetFile.gdb"
        prsclOldGdb = workspace + "/InternetFile_LastMonth.gdb"

        # Copy SclDimeNew Template to InternetFile.gdb to create SclDimeNew table
        xStep = 'Copy SclDimeNew Template to InternetFile.gdb to create SclDimeNew table'
        arcpy.Copy_management(inTemplate, outTable)
        print "\n", arcpy.GetMessages()
        arcpy.Append_management(intFileTable, outTable, "NO_TEST")
        print "\n", arcpy.GetMessages()

        # Sort table
        xStep = 'Sort table'
        arcpy.Sort_management(outTable, tableSort,[["CENSUSID", "ASCENDING"]])
        print "\n", arcpy.GetMessages()

        # Create list from table and delete OID field
        xStep = 'Create list from table and delete OID field'
        fieldList = arcpy.ListFields(tableSort)
        del fieldList[0]

        # Create variable for Internet table and open text file
        xStep = 'Create variable for Internet table and open text file'
        outputIntFile = outTableWorkspace + "intdata.txt"
        table = open(outputIntFile, 'w')

        # Create cursor to iterate through the sorted SclDimeNew table
        xStep = 'Create cursor to iterate through the sorted SclDimeNew table'
        searchRows = arcpy.SearchCursor(tableSort)
        for searchRow in searchRows:
            table.write(",".join([str(searchRow.getValue(field.name)) for field in fieldList]) + "\n")

        del searchRow, searchRows
        table.close()

        # Copy text files to ftp site
        xStep = 'Copy text files to ftp site'
        arcpy.Copy_management(outputIntFile, outFtpWorkspace + "intdata.txt")
        print "\n", arcpy.GetMessages()

        # Create new InternetFile_LastMonth and InternetFile GDBs

        # This is a workaround since arcpy is placing a lock on the internetFile_work
        #   gdb and won't let me rename it.  So, I'm copying it out to a new one.  The
        #   internetFile_work gdb will be deleted at the beginning of the initial process.
        xStep = 'Create new InternetFile_LastMonth and InternetFile GDBs'
        if arcpy.Exists(prsclOldGdb):
            arcpy.Delete_management(prsclOldGdb, "")
            print "\n", arcpy.GetMessages()
        if arcpy.Exists(prsclGdb):
            arcpy.Rename_management(prsclGdb, "InternetFile_LastMonth.gdb")
            print "\n", arcpy.GetMessages()
        # This kept breaking.  Would not release schema lock.
        #arcpy.Rename_management(intFileGdb, "InternetFile.gdb")

        # Delete the previous internet file gdb
        if arcpy.Exists(workspace + '/InternetFile.gdb'):
            arcpy.Delete_management(workspace + '/InternetFile.gdb', "")
            print "\n", arcpy.GetMessages()

        arcpy.Copy_management(workspace + '/InternetFile_work.gdb',workspace + '/InternetFile.gdb')

        #---------------------------------------------------------------------------
        # CRSCL Updates ------------------------------------------------------------
        #---------------------------------------------------------------------------

        xStep = 'CRSCL_Updates'

        arcpy.env.workspace = CRSCLUpdateWorkspace

        # List the feature classes in Scl_Exports.gdb
        xStep = 'List the feature classes in Scl_Exports.gdb'
        fcList = arcpy.ListFeatureClasses()

        # Loop through the list
        for featureClass in fcList:
            # Convert to shapefiles
            if arcpy.Exists(outWorkspace + featureClass + ".shp"):
                xStep = 'delete {0}'.format(featureClass)
                arcpy.Delete_management(outWorkspace + featureClass + ".shp", "")
                print arcpy.GetMessages()
                print
            xStep = 'create {0}'.format(featureClass)
            arcpy.FeatureClassToFeatureClass_conversion(featureClass, outWorkspace, featureClass + ".shp")
            print arcpy.GetMessages()
            print
            # Copy to SDE
            if featureClass == "scl_l" or featureClass == "sclrte_l" or featureClass == "scl_n":
                # In order to keep address locators current without recreating them, we need to
                # delete the features and reload them
                xStep = 'truncate {0}'.format(featureClass)
                arcpy.TruncateTable_management(sdeLoad + featureClass)
                print arcpy.GetMessages()
                print
                xStep = 'append {0}'.format(featureClass)
                arcpy.Append_management(featureClass, sdeLoad + featureClass, "TEST", "", "")
                print arcpy.GetMessages()
                print
            else:
                if arcpy.Exists(sdeLoad + featureClass):
                    xStep = "delete sde"
                    arcpy.Delete_management(sdeLoad + featureClass)
                    print arcpy.GetMessages()
                    print
                xStep = "copy to sde"
                arcpy.FeatureClassToFeatureClass_conversion(featureClass, sdeLoad, featureClass)
                print arcpy.GetMessages()
                print
            print


    except:
        xFlag = 1
        ex = sys.exc_info()[1]
        eMsg = ex.args[0]
        xStep = '{0}: {1}'.format(xStep,eMsg)
        print 'Error at the following process: {0}'.format(xStep)

    finally:
        return(xStep, xFlag)


