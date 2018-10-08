#-------------------------------------------------------------------------------
# Name:        Scl_Intersections
# Purpose:     Creates the scl intersections file
#
# Author:      Gary Harrison
#
# Created:     30/06/2017
# Copyright:   (c) Gary Harrison 2017
# Licence:
#-------------------------------------------------------------------------------

def main():
    try:
        xFlag = 0
        import time, timeit
        from time import gmtime, strftime

        startTime = timeit.default_timer()
        startFtime = strftime("%Y-%m-%dT%H:%M:%S")
        print "Started at " + time.strftime("%m/%d/%Y %H.%M.%S", time.localtime())
        import arcpy
        from collections import defaultdict
        import operator
        import itertools

        arcpy.env.qualifiedFieldNames = False
        arcpy.env.overwriteOutput = True

        # Get parameters from config file
        sys.path.append("//ccgisfiles01m/gisdata/prdba/crupdates/CCPythonLib/Appl/")
        import getConfig, mongoJobUpdate
        emailList = getConfig.main('user','crscl','email')
        emailFrom = getConfig.main('globalEmail','from')

        # Import Mailer3 and set arrays
        import Mailer3
        successMsg = []
        failedMsg = []

        # Set variables for workspace and data
        workspace = getConfig.main('user','crscl','path','workspace')
        sdeWorkspace = getConfig.main('globalPath','gismoLoad')
        sclIntGdb = workspace + "SclIntersections.gdb\\"
        nodeArcImport = workspace + "InternetFile.gdb\\Data\\node_arc"
        nodeArc = sclIntGdb + "node_arc"
        nodeArcFreq = sclIntGdb + "node_arc_freq"
        nodeArcCopy = sclIntGdb + "node_arc_copy"

        # Prepare data for SCL_INTERSECTIONS table

        # Delete old GDB and create new GDB
        xStep = 'Delete old GDB and create new GDB'
        if arcpy.Exists(sclIntGdb):
            arcpy.Delete_management(sclIntGdb, "")
            print "\n", arcpy.GetMessages()
        arcpy.CreateFileGDB_management(workspace, "SclIntersections", "CURRENT")
        print "\n", arcpy.GetMessages()

        # Import node_arc, delete fields, and add X,Y
        xStep = 'Import node_arc, delete fields, and add X,Y'
        arcpy.FeatureClassToFeatureClass_conversion(nodeArcImport, sclIntGdb, "node_arc", "NSCODE = 0", "", "")
        print "\n", arcpy.GetMessages()
        arcpy.DeleteField_management(nodeArc, "LTADD;CENSUSID;FNODE;TNODE;FELEV;TELEV;NSCODE;LEFT_PREC;RIGHT_PREC;LEFT_BOOKSEC;RIGHT_BOOKSEC")
        print "\n", arcpy.GetMessages()
        arcpy.AddXY_management(nodeArc)
        print "\n", arcpy.GetMessages()

        # Delete Identical records in node_arc based on STRDIR, STRNAME, STRTYPE, UNQNODENO
        xStep = 'Delete Identical records in node_arc based on STRDIR, STRNAME, STRTYPE, UNQNODENO'
        arcpy.DeleteIdentical_management(nodeArc, ["STRDIR", "STRNAME", "STRTYPE", "UNQNODENO"], "", "")
        print "\n", arcpy.GetMessages()

        # Make Feature Layer for node_arc
        xStep = 'Make Feature Layer for node_arc'
        arcpy.MakeFeatureLayer_management(nodeArc, "nodeArcLyr")
        print "\n", arcpy.GetMessages()

        # Select Layer by Attribute and delete selected features
        xStep = 'Select Layer by Attribute and delete selected features'
        arcpy.SelectLayerByAttribute_management("nodeArcLyr", "NEW_SELECTION", "STRNAME LIKE 'Ramp %' OR STRNAME LIKE 'Acc %'")
        print "\n", arcpy.GetMessages()
        arcpy.DeleteFeatures_management("nodeArcLyr")
        print "\n", arcpy.GetMessages()

        # Frequency on node_arc UNQNODENO field to find nodes with no intersections
        xStep = 'Frequency on node_arc UNQNODENO field to find nodes with no intersections'
        arcpy.Frequency_analysis(nodeArc, nodeArcFreq, ["UNQNODENO"], "")
        print "\n", arcpy.GetMessages()

        # Make Table View for node_arc_freq
        xStep = 'Make Table View for node_arc_freq'
        arcpy.MakeTableView_management(nodeArcFreq, "nodeArcFreqLyr")
        print "\n", arcpy.GetMessages()

        # Add Join between node_arc and node_arc_freq
        xStep = 'Add Join between node_arc and node_arc_freq'
        arcpy.AddJoin_management("nodeArcLyr", "UNQNODENO", "nodeArcFreqLyr", "UNQNODENO", "KEEP_ALL")
        print "\n", arcpy.GetMessages()

        # Select Layer by Attribute where FREQUENCY > 1
        xStep = 'Select Layer by Attribute where FREQUENCY > 1'
        arcpy.SelectLayerByAttribute_management("nodeArcLyr", "NEW_SELECTION", "FREQUENCY > 1")
        print "\n", arcpy.GetMessages()

        # Remove Join between node_arc and node_arc_freq
        xStep = 'Remove Join between node_arc and node_arc_freq'
        arcpy.RemoveJoin_management("nodeArcLyr", "")
        print "\n", arcpy.GetMessages()

        # Copy selected features to new feature class
        xStep = 'Copy selected features to new feature class'
        arcpy.CopyFeatures_management("nodeArcLyr", nodeArcCopy)
        print "\n", arcpy.GetMessages()

        # Create SCL_INTERSECTIONS table

        # Set variables for node_arc_copy fields
        strdirField = "STRDIR"
        strnameField = "STRNAME"
        strtypeField = "STRTYPE"
        unqField = "UNQNODENO"
        xField = "POINT_X"
        yField = "POINT_Y"

        # Set variables for fields used in Search Cursor for node_arc_copy layer
        xStep = 'Set variables for fields used in Search Cursor for node_arc_copy layer'
        nodeArcFields = (strdirField, strnameField, strtypeField, unqField, xField, yField)

        # Create an empty list to save intersection information to based on UNQNODENO
        nodeArcList = []

        # Load node_arc_copy to nodeArcList
        xStep = 'Load node_arc_copy to nodeArcList'
        with arcpy.da.SearchCursor(nodeArcCopy, nodeArcFields) as nodeArcCopyCursor:
            for nodeArcCopyRow in nodeArcCopyCursor:
                nodeArcList.append([nodeArcCopyRow[3],[nodeArcCopyRow[0],nodeArcCopyRow[1],nodeArcCopyRow[2],nodeArcCopyRow[4],nodeArcCopyRow[5]]])

        # Load nodeArcList into nodeArcDict, iteritems to merge all identical keys into one key with many values
        xStep = 'Load nodeArcList into nodeArcDict, iteritems to merge all identical keys into one key with many values'
        nodeArcDictTemp = defaultdict(list)

        for k, v in nodeArcList:
            nodeArcDictTemp[k].append(v)

        nodeArcDict = dict((k,v) for k,v in nodeArcDictTemp.iteritems())
        del nodeArcDictTemp
        del nodeArcList

        # Set variables for GDB tables
        xStep = 'Set variables for GDB tables'
        sclIntTemplate = workspace + "InternetFile_Template.gdb\\sclIntersections"
        sclIntTable = sclIntGdb + "SCL_INTERSECTIONS"
        sclIntSort = sclIntGdb + "SCL_INTERSECTIONS_SORT"

        # Import SCL_INTERSECTIONS Template
        xStep = 'Import SCL_INTERSECTIONS Template'
        arcpy.TableToTable_conversion(sclIntTemplate, sclIntGdb, "SCL_INTERSECTIONS", "", "", "")
        print "\n", arcpy.GetMessages()

        # Loop through dictionary and create SCL_INTERSECTIONS table
        xStep = 'Loop through dictionary and create SCL_INTERSECTIONS table'
        for k, v in nodeArcDict.iteritems():
            # Sort street items by STRNAME, STRTYPE, then STRDIR
            v.sort(key = operator.itemgetter(1,2,0))
            # Use combinations to create a list of all 2 pair combinations that are possible for each intersection
            streetList = list(itertools.combinations(v,2))
            # Loop through the streetList, inserting a new row into SCL_INTERSECTIONS for each record
            for item in streetList:
                tempItem = "{3},{4},{0},{1},{2},".format(*item[0])
                tempItem += "{0},{1},{2}".format(*item[1])
                xCoord = item[0][3]
                yCoord = item[0][4]
                dir1 = item[0][0]
                name1 = item[0][1]
                type1 = item[0][2]
                dir2 = item[1][0]
                name2 = item[1][1]
                type2 = item[1][2]

                fieldsToUpdate = ("X","Y","PREDIR1","STRNAME1","STRTYPE1","PREDIR2","STRNAME2","STRTYPE2")
                with arcpy.da.InsertCursor(sclIntTable, fieldsToUpdate) as cursor:
                    cursor.insertRow((xCoord, yCoord, dir1, name1,type1, dir2, name2, type2))
                del cursor

        # Sort SCL_INTERSECTIONS table (STRNAME1,STRTYPE1,PREDIR1,STRNAME2,STRTYPE2,PREDIR2)
        xStep = 'Sort SCL_INTERSECTIONS table (STRNAME1,STRTYPE1,PREDIR1,STRNAME2,STRTYPE2,PREDIR2)'
        sortFields = [["STRNAME1", "ASCENDING"], ["STRTYPE1", "ASCENDING"], ["PREDIR1"], ["STRNAME2", "ASCENDING"], ["STRTYPE2", "ASCENDING"], ["PREDIR2", "ASCENDING"]]
        arcpy.Sort_management(sclIntTable, sclIntSort, sortFields)
        print "\n", arcpy.GetMessages()

        # Delete existing and copy new table to SDE Load
        xStep = 'Delete existing and copy new table to SDE Load'
        if arcpy.Exists(sdeWorkspace + "SCL_INTERSECTIONS"):
            arcpy.Delete_management(sdeWorkspace + "SCL_INTERSECTIONS","")
            print "\n", arcpy.GetMessages()
        arcpy.Copy_management(sclIntSort, sdeWorkspace + "SCL_INTERSECTIONS")
        print "\n", arcpy.GetMessages()

        successMsg.append('<br><br><em>SCL Intersections successfully completed!</em>')


    except:
        xFlag = 1
        ex = sys.exc_info()[1]
        eMsg = ex.args[0]
        xStep = '{0}: {1}'.format(xStep,eMsg)
        failedMsg.append('Error at the following process: {0}'.format(xStep))

    finally:
        if xFlag == 1:
            emailSubject = '##--ERROR--## CRSCL_Intersections'
            jobStatus = 'error'
        if xFlag == 0:
            emailSubject = '##--Successful--## CRSCL_Intersections'
            jobStatus = 'ok'

        # Call Mailer3 and send email
        Mailer3.mailReport(successMsg, failedMsg, emailList, emailFrom, emailSubject)

        endTime = timeit.default_timer()
        seconds = endTime - startTime
        minutes = seconds/60
        endFtime = strftime("%Y-%m-%dT%H:%M:%S")
        print '\nRuntime {0} seconds ({1} minutes)'.format(round(seconds,2),round(minutes,2))
        print ' '
        # Call mongoJobUpdate to update mongo
        mongoJobUpdate.mongoUpdate('scl - crscl intersections',startTime,endTime,startFtime,endFtime,jobStatus,failedMsg)

if __name__ == '__main__':
    main()


