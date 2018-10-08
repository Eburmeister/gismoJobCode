#-------------------------------------------------------------------------------
# Name:        Post_Compress
# Purpose:     Reconciles PRSCL geodatabase, posts to Default & compresses.
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
        print "Started at " + time.strftime("%Y/%m/%d %H.%M.%S", time.localtime())
        xFlag = 0
        import arcpy, os, sys, shutil

        # Get parameters from config file
        sys.path.append("//ccgisfiles01m/gisdata/prdba/crupdates/CCPythonLib/Appl/")
        import getConfig
        dbPrConn = getConfig.main('user','crscl','path','sclAdmin')

    	# Reconcile and Post Final to Admin
    	xStep = 'reconcile and post final to admin'
    	arcpy.ReconcileVersion_management(dbPrConn, "SCLFINAL.Final", "SCLADMIN.Admin", "BY_OBJECT", "FAVOR_TARGET_VERSION", "LOCK_ACQUIRED", "ABORT_CONFLICTS", "POST")

    	# Reconcile and Post Admin to Default
    	xStep = 'reconcile and post admin to default'
    	arcpy.ReconcileVersion_management(dbPrConn, "SCLADMIN.Admin", "sde.DEFAULT", "BY_OBJECT", "FAVOR_TARGET_VERSION", "LOCK_ACQUIRED", "ABORT_CONFLICTS", "POST")

    	# Compress database
    	xStep = 'compress database'
    	arcpy.Compress_management(dbPrConn)
        print "\nCompleted at " + time.strftime("%Y/%m/%d %H.%M.%S", time.localtime())

    except:
    	xFlag = 1
    	ex = sys.exc_info()[1]
    	eMsg = ex.args[0]
    	xStep = '{0}: {1}'.format(xStep, eMsg)
    	print 'Error at the following process: {0}'.format(xStep)

    finally:
        return (xStep, xFlag)


