#-------------------------------------------------------------------------------
# Name:        Crscl_SdeDaily
# Purpose:     Deletes and copies layers to SDE
#
# Author:      Gary Harrison (modified from Jaime McKeown)
#
# Created:     30/06/2017
# Copyright:   (c) Gary Harrison 2017
# Licence:
#-------------------------------------------------------------------------------

def main():
    try:
        import time
        import os, sys
        print "Started at " + time.strftime("%Y/%m/%d %H.%M.%S", time.localtime())
        import arcpy

        xFlag = 0

        # Get parameters from config file
        sys.path.append("//ccgisfiles01m/gisdata/prdba/crupdates/CCPythonLib/Appl/")
        import getConfig

        arcpy.env.workspace = getConfig.main('user','crscl','path','workspace') + 'scl_exports.gdb'
        sdeWorkspace = getConfig.main('globalPath','gismoLoad')

    	outputStep = "start"

    	# List the feature classes in Scl_Exports.gdb
    	xStep = 'list Scl_Exports feature classes'
    	fcList = arcpy.ListFeatureClasses()

        # Loop through the list
    	for featureClass in fcList:
    		# Copy to SDE
    		if featureClass == "scl_l" or featureClass == "sclrte_l" or featureClass == "scl_n":
    			# In order to keep address locators current without recreating them, we need to
    			# delete the features and reload them
    			outputStep = "truncate"
    			arcpy.TruncateTable_management(sdeWorkspace + featureClass)
    			outputStep = "append"
    			arcpy.Append_management(featureClass, sdeWorkspace + featureClass, "TEST", "", "")
    		else:
    			if arcpy.Exists(sdeWorkspace + featureClass):
    				outputStep = "delete sde"
    				arcpy.Delete_management(sdeWorkspace + featureClass)
    			outputStep = "copy to sde"
    			arcpy.FeatureClassToFeatureClass_conversion(featureClass, sdeWorkspace, featureClass)

        print "Completed at " + time.strftime("%Y/%m/%d %H.%M.%S", time.localtime())


    except:
    	xFlag = 1
    	ex = sys.exc_info()[1]
    	eMsg = ex.args[0]
    	xStep = '{0} at {1}: {2}'.format(featureClass,outputStep,eMsg)
    	arcpy.AddMessage("There was a problem deleting or converting " + featureClass + " at step " + outputStep + ".")
    	arcpy.GetMessages()

    finally:
        return(xStep, xFlag)

