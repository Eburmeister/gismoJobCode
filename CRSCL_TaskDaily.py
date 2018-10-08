"""Runs daily SCL scripts.

Author: Gary Harrison
Modified: 10-1-2018
"""
import sys, os, timeit
from time import gmtime, strftime

# Set path to custom python modules
sys.path.append("//ccgisfiles01m/gisdata/prdba/crupdates/CCPythonLib/Appl/")

import getConfig, mongoJobUpdate

def main():
    """Primary function."""
    try:
        xStep, xFlag = 'Start',0
        startFtime = strftime("%Y-%m-%dT%H:%M:%S")
        startTime = timeit.default_timer()

        # Get parameters from config file (use first line for testing)
        #emailList = getConfig.main('globalEmail','test')
        emailList = getConfig.main('user','crscl','email')
        emailFrom = getConfig.main('globalEmail','from')

        # Import Mailer3 and set arrays
        import Mailer3
        successMsg, failedMsg = [],[]

        # Run Post_Compress process
        xStep = 'Starting Post_Compress...'
        import Post_Compress
        outvar = Post_Compress.main()
        if outvar[1] == 1:
            xStep = outvar[0]
            raise Exception
        successMsg.append('<br>Post_Compress successful')

        # Run Scl_Exports process
        xStep = 'import scl exports'
        import Scl_Exports
        outvar = Scl_Exports.main()
        if outvar[1] == 1:
            xStep = outvar[0]
            raise Exception
        successMsg.append('<br>Scl_Exports successful')

        # Run Crscl_SdeDaily process
        xStep = 'import crscl sde daily'
        import Crscl_SdeDaily
        outvar = Crscl_SdeDaily.main()
        if outvar[1] == 1:
            xStep = outvar[0]
            raise Exception
        successMsg.append('<br>Crscl_SdeDaily successful')
        successMsg.append('<br><br><em>CRSCL Daily processes have run successfully!</em>')

    except:
    	print 'Error at {0}'.format(xStep)
    	failedMsg.append(xStep)

    finally:
        if len(failedMsg) != 0:
            emailSubject = '##--ERROR--## CRSCL_Daily'
            jobStatus = 'error'
        if len(failedMsg) == 0:
            emailSubject = '##--Successful--## CRSCL_Daily'
            jobStatus = 'ok'

        # Call Mailer3 and send email
        Mailer3.mailReport(successMsg, failedMsg, emailList, emailFrom, emailSubject)

        # Call mongoJobUpdate to update mongo
        endFtime = strftime("%Y-%m-%dT%H:%M:%S")
        endTime = timeit.default_timer()
        mongoJobUpdate.mongoUpdate('scl - crscl daily',startTime,endTime,startFtime,endFtime,jobStatus,failedMsg)

if __name__ == '__main__':
    main()