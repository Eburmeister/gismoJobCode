#-------------------------------------------------------------------------------
# Name:        CRSCL_Weekly
# Purpose:     Fires off the scripts required for SCL weekly processes
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
        import timeit, os, sys, shutil
        from time import gmtime, strftime
        startTime = timeit.default_timer()
        startFtime = strftime("%Y-%m-%dT%H:%M:%S")

        # Set paths
        sys.path.append("//ccgisfiles01m/gisdata/prdba/crupdates/CCPythonLib/Appl/")

        # Import Mailer3 and set arrays
        import Mailer3
        successMsg = []
        failedMsg = []

        # Get parameters from config file
        import getConfig, mongoJobUpdate
        emailList = getConfig.main('user','crscl','email')
        emailFrom = getConfig.main('globalEmail','from')

        ftpUpdateIni = getConfig.main('globalPath','ftpUpdateIniCCGIS1')

        # Run Post_Compress process
        print 'Starting Post_Compress...'
        xStep = 'import post compress'
        import Post_Compress
        outvar = Post_Compress.main()
        if outvar[1] == 1:
            xStep = outvar[0]
            raise Exception
        print 'Completed'
        print ' '
        successMsg.append('<br>Post_Compress successful')

        # Run Scl_Exports process
        print 'Starting Scl_Exports...'
        xStep = 'import scl exports'
        import Scl_Exports
        outvar = Scl_Exports.main()
        if outvar[1] == 1:
            xStep = outvar[0]
            raise Exception
        print 'Completed'
        print ' '
        successMsg.append('<br>Scl_Exports successful')

        # Run rest of weekly processes
        print 'Starting SCL Weekly processes...'
        xStep = 'import weekly processes'
        import CRSCL_Weekly_processes
        outvar = CRSCL_Weekly_processes.main()
        if outvar[1] == 1:
            xStep = outvar[0]
            raise Exception
        print 'Completed'
        print ' '
        successMsg.append('<br>InternetFile successful')
        successMsg.append('<br>ArcXstreet successful')
        successMsg.append('<br>ArcXstreetNinesInternet successful')
        successMsg.append('<br>InternetFile_Xstreet successful')
        successMsg.append('<br>Intdata_SclDimeNew successful')
        successMsg.append('<br>Crscl_Updates successful')

        # SCL Map Updates
        xStep = 'import crscl map updates'
        import CRSCL_Map_Updates
        outvar = CRSCL_Map_Updates.main()
        if outvar[1] == 1:
            xStep = outvar[0]
            failedMsg.append('<br>{0}'.format(xStep))
        if outvar[1] == 2:
            xStep = 'There was an error with CRSCL_Map_Updates.'
            failedMsg.append('<br>{0}'.format(xStep))

        print 'CRSCL Weekly processes completed!'
        print ' '
        if outvar[1] not in [1,2]:
            successMsg.append('<br><br><em>CRSCL Weekly processes have run successfully!</em>')

    except:
        print ' '
        print 'Error at {0}'.format(xStep)
        failedMsg.append(xStep)

    finally:
        if len(failedMsg) != 0:
            emailSubject = '##--ERROR--## CRSCL_Weekly'
            jobStatus = 'error'
        if len(failedMsg) == 0:
            emailSubject = '##--Successful--## CRSCL_Weekly'
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
        mongoJobUpdate.mongoUpdate('scl - crscl weekly',startTime,endTime,startFtime,endFtime,jobStatus,failedMsg)

if __name__ == '__main__':
    main()