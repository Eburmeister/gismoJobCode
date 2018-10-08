#------------------------------
# ChangeReport.py
# Creates the SCL Change Report for users
# Created by: Jaime McKeown
# Modified by: GMH on 10-23-2017
# - Combined SCL and Nine change reports into same script
# - Added FTP update to fix some timing issues with the weekly processes
#------------------------------
def main():
    try:
        xStep = 'Starting script...'
        import os, sys, timeit, time, csv, shutil
        import datetime
        from time import gmtime, strftime
        from shutil import copyfile
        startTime = timeit.default_timer()
        startFtime = strftime("%Y-%m-%dT%H:%M:%S")
        print 'Started at {0}'.format(time.ctime())
        xFlag = 0
        import arcpy
        from openpyxl import Workbook
        # Set paths
        sys.path.append("//ccgisfiles01m/gisdata/prdba/crupdates/CCPythonLib/Appl/")

        # Get parameters from config file
        import getConfig, mongoJobUpdate
        emailList = getConfig.main('user','crscl','email')
        emailFrom = getConfig.main('globalEmail','from')

        # Import Mailer3 and set arrays
        import Mailer3
        successMsg = []
        failedMsg = []

        arcpy.env.overwriteOutput = True
        arcpy.env.qualifiedFieldNames = True

        #-----------------------------------------------------------------------
        # This is temporary just until zip'n'ship is ready on new server
        # Copy ccgisfiles01m-crscl files back to ccgis1-crscl
        xStep = "copy files from ccgisfiles01m back to ccgis1 for zip'n'ship"
        print xStep
        dirSource = getConfig.main('user','crscl','path','outWorkspace')
        dirTarget = getConfig.main('user','crscl','path','outWorkspaceCCGIS1')

        source = os.listdir(dirSource)
        for i in source:
            shutil.copy(dirSource + i, dirTarget + i)

        successMsg.append('<br>Shapefiles copied back to CCGIS1')
        #-----------------------------------------------------------------------

        # Update FTP site
        ftpUpdateIni = getConfig.main('globalPath','ftpUpdateIniCCGIS1')
        xStep = 'write to crupdates FTP file'
        ftpUpdateFile = open(ftpUpdateIni,'a')
        ftpUpdateFile.write('#crscl#\n')
        ftpUpdateFile.close()
        successMsg.append('<br>FTP site set to update')

        #-----------------------------------------------------------------------
        # Get current date for file name
        today = (str(datetime.datetime.now())).split()[0]

        #-----------------------------------------------------------------------
        # Start SCL Change Report
        #-----------------------------------------------------------------------

        # Set variables for the environment
        workspace = getConfig.main('user','crscl','path','workspace')[:-1]
        prsclGdbWorkspace = getConfig.main('user','crscl','path','workspace')[:-1]
        newIntFileGdb = prsclGdbWorkspace + "\\InternetFile.gdb"
        newIntFile = newIntFileGdb + "\\internetFile"
        oldIntFileGdb = prsclGdbWorkspace + "\\InternetFile_LastMonth.gdb"
        oldIntFile = oldIntFileGdb + "\\internetFile"
        chgrepGdb = workspace + "\\ChangeReport.gdb"
        intFileNew = chgrepGdb + "\\internetFileNew"
        intFileOld = chgrepGdb + "\\internetFileOld"
        delete = chgrepGdb + "\\deletes"
        change = chgrepGdb + "\\changes"
        changeOld = chgrepGdb + "\\changes_old"
        changeReport = chgrepGdb + "\\change_report"
        changeReportSort = chgrepGdb + "\\change_report_sort"
        changeFreq = chgrepGdb + "\\changes_freq"
        deleteFreq = chgrepGdb + "\\deletes_freq"
        changeReportWkspace = getConfig.main('user','crscl','path','changeReportWkspace')

        xStep = 'Delete last months GDB and add layers and tables from Internet Files'
        if arcpy.Exists(chgrepGdb):
            arcpy.Delete_management(chgrepGdb, "")
            print "\n", arcpy.GetMessages()
        arcpy.CreateFileGDB_management(workspace, "ChangeReport.gdb", "CURRENT")
        print "\n", arcpy.GetMessages()
        arcpy.TableToTable_conversion(newIntFile, chgrepGdb, "internetFileNew")
        print "\n", arcpy.GetMessages()
        arcpy.DeleteField_management(intFileNew, "FNODE;TNODE;FELEV;TELEV;LMailZip;RMailZip;STRSUF;LEFT_COUNTY;RIGHT_COUNTY;LEFT_STATE;RIGHT_STATE;LEFT_TRACT;RIGHT_TRACT;LEFT_BLOCK;RIGHT_BLOCK;LEFT_ZIP;RIGHT_ZIP;LEFT_LOC;RIGHT_LOC;LEFT_MCD;RIGHT_MCD;LEFT_TRACTBLKGRP;RIGHT_TRACTBLKGRP;FR_X;FR_LAT;FR_Y;FR_LONG;FMAPBASIC;FMAPSUF;TO_X;TO_LAT;TO_Y;TO_LONG;TMAPBASIC;TMAPSUF;STRCLASS;FFDAD;TFDAD")
        print "\n", arcpy.GetMessages()
        arcpy.TableToTable_conversion(oldIntFile, chgrepGdb, "internetFileOld")
        print "\n", arcpy.GetMessages()
        arcpy.DeleteField_management(intFileOld, "FNODE;TNODE;FELEV;TELEV;LMailZip;RMailZip;STRSUF;LEFT_COUNTY;RIGHT_COUNTY;LEFT_STATE;RIGHT_STATE;LEFT_TRACT;RIGHT_TRACT;LEFT_BLOCK;RIGHT_BLOCK;LEFT_ZIP;RIGHT_ZIP;LEFT_LOC;RIGHT_LOC;LEFT_MCD;RIGHT_MCD;LEFT_TRACTBLKGRP;RIGHT_TRACTBLKGRP;FR_X;FR_LAT;FR_Y;FR_LONG;FMAPBASIC;FMAPSUF;TO_X;TO_LAT;TO_Y;TO_LONG;TMAPBASIC;TMAPSUF;STRCLASS;FFDAD;TFDAD")
        print "\n", arcpy.GetMessages()

        xStep = 'Remove domains from fields'
        arcpy.RemoveDomainFromField_management(intFileNew, "STRDIR")
        print "\n", arcpy.GetMessages()
        arcpy.RemoveDomainFromField_management(intFileNew,"STRTYPE")
        print "\n", arcpy.GetMessages()
        arcpy.RemoveDomainFromField_management(intFileNew, "LEFT_PLACE")
        print "\n", arcpy.GetMessages()
        arcpy.RemoveDomainFromField_management(intFileNew, "RIGHT_PLACE")
        print "\n", arcpy.GetMessages()
        arcpy.RemoveDomainFromField_management(intFileNew, "FSTRDIR")
        print "\n", arcpy.GetMessages()
        arcpy.RemoveDomainFromField_management(intFileNew, "TSTRDIR")
        print "\n", arcpy.GetMessages()
        arcpy.RemoveDomainFromField_management(intFileOld, "STRDIR")
        print "\n", arcpy.GetMessages()
        arcpy.RemoveDomainFromField_management(intFileOld,"STRTYPE")
        print "\n", arcpy.GetMessages()
        arcpy.RemoveDomainFromField_management(intFileOld, "LEFT_PLACE")
        print "\n", arcpy.GetMessages()
        arcpy.RemoveDomainFromField_management(intFileOld, "RIGHT_PLACE")
        print "\n", arcpy.GetMessages()

        xStep = 'Remove extra spaces from STRNAME fields on new and old internetFile'
        arcpy.CalculateField_management(intFileNew, "STRDIR", "!strdir!.strip()", "PYTHON_9.3", "")
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management(intFileNew, "STRNAME", "!strname!.strip()", "PYTHON_9.3", "")
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management(intFileNew, "STRTYPE", "!strtype!.strip()", "PYTHON_9.3", "")
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management(intFileNew, "FSTRNAME", "!fstrname!.strip()", "PYTHON_9.3", "")
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management(intFileNew, "F2STRNAME", "!f2strname!.strip()", "PYTHON_9.3", "")
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management(intFileNew, "F3STRNAME", "!f3strname!.strip()", "PYTHON_9.3", "")
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management(intFileNew, "TSTRNAME", "!tstrname!.strip()", "PYTHON_9.3", "")
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management(intFileNew, "T2STRNAME", "!t2strname!.strip()", "PYTHON_9.3", "")
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management(intFileNew, "T3STRNAME", "!t3strname!.strip()", "PYTHON_9.3", "")
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management(intFileOld, "STRDIR", "!strdir!.strip()", "PYTHON_9.3", "")
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management(intFileOld, "STRNAME", "!strname!.strip()", "PYTHON_9.3", "")
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management(intFileOld, "STRTYPE", "!strtype!.strip()", "PYTHON_9.3", "")
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management(intFileOld, "FSTRNAME", "!fstrname!.strip()", "PYTHON_9.3", "")
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management(intFileOld, "F2STRNAME", "!f2strname!.strip()", "PYTHON_9.3", "")
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management(intFileOld, "F3STRNAME", "!f3strname!.strip()", "PYTHON_9.3", "")
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management(intFileOld, "TSTRNAME", "!tstrname!.strip()", "PYTHON_9.3", "")
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management(intFileOld, "T2STRNAME", "!t2strname!.strip()", "PYTHON_9.3", "")
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management(intFileOld, "T3STRNAME", "!t3strname!.strip()", "PYTHON_9.3", "")
        print "\n", arcpy.GetMessages()

        xStep = 'Add attribute indexes based on CENSUSID field'
        arcpy.AddIndex_management(intFileNew, "CENSUSID", "ArcNewIndex", "UNIQUE", "ASCENDING")
        print "\n", arcpy.GetMessages()
        arcpy.AddIndex_management(intFileOld, "CENSUSID", "ArcOldIndex", "UNIQUE", "ASCENDING")
        print "\n", arcpy.GetMessages()

        xStep = 'Add new fields for change report'
        arcpy.AddField_management(intFileNew, "A", "TEXT", "", "", "1", "", "NULLABLE", "NON_REQUIRED")
        print "\n", arcpy.GetMessages()
        arcpy.AddField_management(intFileNew, "S", "TEXT", "", "", "1", "", "NULLABLE", "NON_REQUIRED")
        print "\n", arcpy.GetMessages()
        arcpy.AddField_management(intFileNew, "R", "TEXT", "", "", "1", "", "NULLABLE", "NON_REQUIRED")
        print "\n", arcpy.GetMessages()
        arcpy.AddField_management(intFileNew, "NINE", "TEXT", "", "", "1", "", "NULLABLE", "NON_REQUIRED")
        print "\n", arcpy.GetMessages()
        arcpy.AddField_management(intFileNew, "J", "TEXT", "", "", "1", "", "NULLABLE", "NON_REQUIRED")
        print "\n", arcpy.GetMessages()
        arcpy.AddField_management(intFileNew, "T", "TEXT", "", "", "1", "", "NULLABLE", "NON_REQUIRED")
        print "\n", arcpy.GetMessages()
        arcpy.AddField_management(intFileNew, "M", "TEXT", "", "", "1", "", "NULLABLE", "NON_REQUIRED")
        print "\n", arcpy.GetMessages()
        arcpy.AddField_management(intFileOld, "NINE", "TEXT", "", "", "1", "", "NULLABLE", "NON_REQUIRED")
        print "\n", arcpy.GetMessages()
        arcpy.AddField_management(intFileOld, "D", "TEXT", "", "", "1", "", "NULLABLE", "NON_REQUIRED")
        print "\n", arcpy.GetMessages()

        xStep = 'Make Table View for internetFileNew for Add Join'
        arcpy.MakeTableView_management(intFileNew, "intFileNew_view")
        print "\n", arcpy.GetMessages()

        xStep = 'Add Join between new and old internetFile to calculate A, S, R, NINE, and J fields'
        arcpy.AddJoin_management("intFileNew_view", "CENSUSID", intFileOld, "CENSUSID", "KEEP_ALL")
        print "\n", arcpy.GetMessages()

        xStep = 'Set variable for codeblock to calculate A field'
        aCodeblock = """def CalcField(CidOld):
            if str(CidOld) == 'None':
                return 'A'
            else:
                return ''"""

        xStep = 'Calculate A field on internetFileNew'
        arcpy.CalculateField_management("intFileNew_view", "A", "CalcField(!internetFileOld.CENSUSID!)", "PYTHON_9.3", aCodeblock)
        print "\n", arcpy.GetMessages()

        # Set variable for codeblock to calculate S field
        sCodeblock = """def CalcField(StrDirNew,StrNameNew,StrTypeNew,StrDirOld,StrNameOld,StrTypeOld,Afield):
            if ((StrDirNew != StrDirOld) or (StrNameNew != StrNameOld) or (StrTypeNew != StrTypeOld)) and (Afield != 'A'):
                return 'S'
            else:
                return ''"""

        xStep = 'Calculate S field on internetFileNew'
        arcpy.CalculateField_management("intFileNew_view", "S", "CalcField(!internetFileNew.STRDIR!,!internetFileNew.STRNAME!,!internetFileNew.STRTYPE!,!internetFileOld.STRDIR!,!internetFileOld.STRNAME!,!internetFileOld.STRTYPE!,!internetFileNew.A!)", "PYTHON_9.3", sCodeblock)
        print "\n", arcpy.GetMessages()

        xStep = 'Set variable for codeblock to calculate R field'
        rCodeblock = """def CalcField(LfaddNew,LtaddNew,RfaddNew,RtaddNew,LfaddOld,LtaddOld,RfaddOld,RtaddOld,Afield):
            if ((LfaddNew != LfaddOld) or (LtaddNew != LtaddOld) or (RfaddNew != RfaddOld) or (RtaddNew != RtaddOld)) and (Afield != 'A'):
                return 'R'
            else:
                return ''"""

        xStep = 'Calcuate R field on internetFileNew'
        arcpy.CalculateField_management("intFileNew_view", "R", "CalcField(!internetFileNew.LFADD!,!internetFileNew.LTADD!,!internetFileNew.RFADD!,!internetFileNew.RTADD!,!internetFileOld.LFADD!,!internetFileOld.LTADD!,!internetFileOld.RFADD!,!internetFileOld.RTADD!,!internetFileNew.A!)", "PYTHON_9.3", rCodeblock)
        print "\n", arcpy.GetMessages()

        # Set variable for codeblock to calculate J field
        jCodeblock = """def CalcField(LplaceNew,RplaceNew,LplaceOld,RplaceOld,nscodeNew,nscodeOld,Afield):
            if ((LplaceNew != LplaceOld) or (RplaceNew != RplaceOld) or (nscodeNew != nscodeOld)) and (Afield != 'A'):
                return 'J'
            else:
                return ''"""

        xStep = 'Calculate J field on internetFileNew'
        arcpy.CalculateField_management("intFileNew_view", "J", "CalcField(!internetFileNew.LEFT_PLACE!,!internetFileNew.RIGHT_PLACE!,!internetFileOld.LEFT_PLACE!,!internetFileOld.RIGHT_PLACE!,!internetFileNew.NSCODE!,!internetFileOld.NSCODE!,!internetFileNew.A!)", "PYTHON_9.3", jCodeblock)
        print "\n", arcpy.GetMessages()

        xStep = 'Set variable for codeblock to calculate T field'
        tCodeblock = """def CalcField(fNew,f2New,f3New,tNew,t2New,t3New,fOld,f2Old,f3Old,tOld,t2Old,t3Old):
            if (fNew == fOld or fNew == f2Old or fNew == f3Old) and (f2New == f2Old or f2New == fOld or f2New == f3Old) and (f3New == f3Old or f3New == f2Old or f3New == fOld) and (fOld == fNew or fOld == f2New or fOld == f3New) and (f2Old == f2New or f2Old == fNew or f2Old == f3New) and (f3Old ==f3New or f3Old == fNew or f3Old == f2New) and (tNew == tOld or tNew == t2Old or tNew == t3Old) and (t2New == t2Old or t2New == tOld or t2New == t3Old) and (t3New == t3Old or t3New == t2Old or t3New == tOld) and (tOld == tNew or tOld == t2New or tOld == t3New) and (t2Old == t2New or t2Old == tNew or t2Old == t3New) and (t3Old == t3New or t3Old == tNew or t3Old == t2New):
                return ''
            else:
                return 'T'"""

        xStep = 'Calculate T field on internetFileNew'
        arcpy.CalculateField_management("intFileNew_view", "T", "CalcField(!internetFileNew.FSTRNAME!,!internetFileNew.F2STRNAME!,!internetFileNew.F3STRNAME!,!internetFileNew.TSTRNAME!,!internetFileNew.T2STRNAME!,!internetFileNew.T3STRNAME!,!internetFileOld.FSTRNAME!,!internetFileOld.F2STRNAME!,!internetFileOld.F3STRNAME!,!internetFileOld.TSTRNAME!,!internetFileOld.T2STRNAME!,!internetFileOld.T3STRNAME!)", "PYTHON_9.3", tCodeblock)
        print "\n", arcpy.GetMessages()

        xStep = 'Set variable for codeblock to calculate M field'
        mCodeblock = """def CalcField(fstrnameNew,f2strnameNew,f3strnameNew,tstrnameNew,t2strnameNew,t3strnameNew,tfield):
            if (tfield == 'T' and fstrnameNew != f2strnameNew and str(f2strnameNew) != 'None') or (tfield == 'T' and tstrnameNew != t2strnameNew and str(t2strnameNew) != 'None'):
                return 'M'
            elif (tfield == 'T' and fstrnameNew != f3strnameNew and str(f3strnameNew) != 'None') or (tfield == 'T' and tstrnameNew != t3strnameNew and str(t3strnameNew) != 'None'):
                return 'M'
            else:
                return ''"""

        xStep = 'Calculate M field on internetFileNew'
        arcpy.CalculateField_management("intFileNew_view", "M", "CalcField(!internetFileNew.FSTRNAME!,!internetFileNew.F2STRNAME!,!internetFileNew.F3STRNAME!,!internetFileNew.TSTRNAME!,!internetFileNew.T2STRNAME!,!internetFileNew.T3STRNAME!,!internetFileNew.T!)", "PYTHON_9.3", mCodeblock)
        print "\n", arcpy.GetMessages()

        xStep = 'Set variable for codeblock to recalculate T field'
        t2Codeblock = """def CalcField(Afield,Tfield):
            if (Afield == 'A'):
                return ''
            else:
                return Tfield"""

        xStep = 'Recalculate T field on internetFileNew'
        arcpy.CalculateField_management("intFileNew_view", "T", "CalcField(!internetFileNew.A!,!internetFileNew.T!)", "PYTHON_9.3", t2Codeblock)
        print "\n", arcpy.GetMessages()

        xStep = 'Remove Join between new and old internetFile'
        arcpy.RemoveJoin_management("intFileNew_view")
        print "\n", arcpy.GetMessages()

        xStep = 'Make Table View for internetFileOld for Add Join'
        arcpy.MakeTableView_management(intFileOld, "intFileOld_view")
        print "\n", arcpy.GetMessages()

        xStep = 'Add Join between internetFileOld and internetFileNew to calculate D field'
        arcpy.AddJoin_management("intFileOld_view", "CENSUSID", intFileNew, "CENSUSID", "KEEP_ALL")
        print "\n", arcpy.GetMessages()

        xStep = 'Set variable for codeblock to calculate D field'
        dCodeblock = """def CalcField(CidNew):
            if str(CidNew) == 'None':
                return 'D'
            else:
                return ''"""

        xStep = 'Calculate D field on internetFileOld'
        arcpy.CalculateField_management("intFileOld_view", "D", "CalcField(!internetFileNew.CENSUSID!)", "PYTHON_9.3", dCodeblock)
        print "\n", arcpy.GetMessages()

        xStep = 'Remove Join between internetFileOld and internetFileNew'
        arcpy.RemoveJoin_management("intFileOld_view")
        print "\n", arcpy.GetMessages()

        xStep = 'Export deletes to new feature class'
        arcpy.TableToTable_conversion(intFileOld, chgrepGdb, "deletes", """ "D" = 'D'""")
        print "\n", arcpy.GetMessages()

        xStep = 'Export fields with changes to new feature class'
        arcpy.TableToTable_conversion(intFileNew, chgrepGdb, "changes", """ "A" = 'A' or "S" = 'S' or "R" = 'R' or "J" = 'J' or "T" = 'T' or "M" = 'M' """)
        print "\n", arcpy.GetMessages()

        xStep = 'Set variable for codeblock to calculate NINE field'
        nineCodeblock = """def CalcField(nscodeBoth):
            if (nscodeBoth == 9 ):
                return '9'
            else:
                return ''"""

        xStep = 'Calculate NINE field on changes and deletes'
        arcpy.CalculateField_management(change, "NINE", "CalcField(!nscode!)", "PYTHON_9.3", nineCodeblock)
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management(delete, "NINE", "CalcField(!nscode!)", "PYTHON_9.3", nineCodeblock)
        print "\n", arcpy.GetMessages()

        xStep = 'Add Attribute Index on change table for CENSUSID field'
        arcpy.AddIndex_management(change, "CENSUSID", "cidIndex", "UNIQUE", "ASCENDING")
        print "\n", arcpy.GetMessages()

        xStep = 'Add Join between internetFileOld and changes, Select records when CENSUSID is equal, Remove Join, and Copy Rows to new table'
        arcpy.AddJoin_management("intFileOld_view", "CENSUSID", change, "CENSUSID", "KEEP_COMMON")
        print "\n", arcpy.GetMessages()
        arcpy.SelectLayerByAttribute_management("intFileOld_view", "NEW_SELECTION", "internetFileOld.CENSUSID = changes.CENSUSID")
        print "\n", arcpy.GetMessages()
        arcpy.RemoveJoin_management("intFileOld_view")
        print "\n", arcpy.GetMessages()
        arcpy.CopyRows_management("intFileOld_view", changeOld)
        print "\n", arcpy.GetMessages()

        xStep = 'Merge changes and deletes'
        arcpy.Merge_management([change, changeOld, delete], changeReport)
        print "\n", arcpy.GetMessages()

        xStep = 'Set variable for codeblock to remove nulls from fields'
        nullCodeblock = """def CalcField(Record):
            if str(Record) == 'None':
                return ''
            else:
                return Record"""

        xStep = 'Remove null records in A, S, R, NINE, J, T, M, D'
        arcpy.CalculateField_management(changeReport, "A", "CalcField(!a!)", "PYTHON_9.3", nullCodeblock)
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management(changeReport, "S", "CalcField(!s!)", "PYTHON_9.3", nullCodeblock)
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management(changeReport, "R", "CalcField(!r!)", "PYTHON_9.3", nullCodeblock)
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management(changeReport, "NINE", "CalcField(!nine!)", "PYTHON_9.3", nullCodeblock)
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management(changeReport, "J", "CalcField(!j!)", "PYTHON_9.3", nullCodeblock)
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management(changeReport, "T", "CalcField(!t!)", "PYTHON_9.3", nullCodeblock)
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management(changeReport, "M", "CalcField(!m!)", "PYTHON_9.3", nullCodeblock)
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management(changeReport, "D", "CalcField(!d!)", "PYTHON_9.3", nullCodeblock)
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management(changeReport, "FSTRDIR", "CalcField(!fstrdir!)", "PYTHON_9.3", nullCodeblock)
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management(changeReport, "FSTRTYPE", "CalcField(!fstrtype!)", "PYTHON_9.3", nullCodeblock)
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management(changeReport, "TSTRDIR", "CalcField(!tstrdir!)", "PYTHON_9.3", nullCodeblock)
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management(changeReport, "TSTRTYPE", "CalcField(!tstrtype!)", "PYTHON_9.3", nullCodeblock)
        print "\n", arcpy.GetMessages()

        xStep = 'Add new field and concantenate all change fields'
        arcpy.AddField_management(changeReport, "ACTION", "TEXT", "", "", "8", "", "NULLABLE", "NON_REQUIRED")
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management(changeReport, "ACTION", "\"{0}{1}{2}{3}{4}{5}{6}{7}\".format(!a!,!d!,!s!,!r!,!t!,!m!,!nine!,!j!)", "PYTHON_9.3", "")
        print "\n", arcpy.GetMessages()

        xStep = 'Delete fields not needed in final output'
        arcpy.DeleteField_management(changeReport, "A;S;R;NINE;J;T;M;D")
        print "\n", arcpy.GetMessages()

        xStep = 'Sort the fields'
        arcpy.Sort_management(changeReport, changeReportSort, [("STRNAME", "ASCENDING"),("CENSUSID", "ASCENDING"),("ACTION", "ASCENDING")])
        print "\n", arcpy.GetMessages()

        result = arcpy.GetCount_management(changeReportSort)
        count = int(result.getOutput(0))
        successMsg.append('<br><br>There were {0} SCL changes last week'.format(count))

        if count == 0:
            print 'no changes'
            xStep = 'Copy no changes file to excel'
            copyfile(changeReportWkspace + 'no_changes.xls', changeReportWkspace + 'change_reports_for_users/{0}_scl_change_report.xls'.format(today))

        else:
            xStep = 'Export change_report_sort to Excel'
            arcpy.TableToExcel_conversion(changeReportSort,changeReportWkspace + 'change_reports_for_users/{0}_scl_change_report.xls'.format(today))
            print 'Report exported to Excel'

        successMsg.append('<br><br>SCL Change Code Descriptions:')
        successMsg.append('<br>A - Add')
        successMsg.append('<br>D - Delete')
        successMsg.append('<br>S - Street Attribute Change')
        successMsg.append('<br>R - Address Range Change')
        successMsg.append('<br>T - Cross Street Change')
        successMsg.append('<br>M - Multiple Cross Streets')
        successMsg.append('<br>9 - Nine Record')
        successMsg.append('<br>J - Jurisdiction Change')

        #-----------------------------------------------------------------------
        # Start 9 Record Change Report
        #-----------------------------------------------------------------------

        # Script variables
        workspace = getConfig.main('user','crscl','path','workspace')
        reportWorkspace = getConfig.main('user','crscl','path','reportsWkspace')
        nineChangeGdb = workspace + "Nine_Change.gdb/"
        newNine = workspace + 'InternetFile.gdb/Data/sclnine'
        oldNine = workspace + 'InternetFile_LastMonth.gdb/Data/sclnine'
        nineNew = nineChangeGdb + "sclnine_new"
        nineOld = nineChangeGdb + "sclnine_old"
        nineAdds = nineChangeGdb + "additions"
        nineDeletes = nineChangeGdb + "deletes"
        nineChange = nineChangeGdb + "nine_change"
        changeReportWkspace = getConfig.main('user','crscl','path','changeReportWkspace')

        xStep = 'Delete and recreate output GDB and add sclnine layers'
        if arcpy.Exists(nineChangeGdb):
            arcpy.Delete_management(nineChangeGdb, "")
            print "\n", arcpy.GetMessages()
        arcpy.CreateFileGDB_management(workspace, "Nine_Change", "CURRENT")
        print "\n", arcpy.GetMessages()
        arcpy.FeatureClassToFeatureClass_conversion(newNine, nineChangeGdb, "sclnine_new")
        print "\n", arcpy.GetMessages()
        arcpy.FeatureClassToFeatureClass_conversion(oldNine, nineChangeGdb, "sclnine_old")
        print "\n", arcpy.GetMessages()

        xStep = 'Join field between sclnine_new and sclnine_old to find additions'
        arcpy.JoinField_management(nineNew, "ALIASID", nineOld, "ALIASID")
        print "\n", arcpy.GetMessages()
        arcpy.Select_analysis(nineNew, nineChangeGdb + "additions", "ALIASID_1 IS NULL")
        print "\n", arcpy.GetMessages()
        arcpy.DeleteField_management(nineAdds, "PARCEL;STRPRETYPE;PARCEL_1;CENSUSID_1;ALIASID_1;ADDR_1;SIDE_1;STRDIR_1;STRPRETYPE_1;STRNAME_1;STRTYPE_1")
        print "\n", arcpy.GetMessages()
        arcpy.AddField_management(nineAdds, "CHANGE", "TEXT", "", "", "10", "", "NULLABLE")
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management(nineAdds, "CHANGE", "'Add'", "PYTHON_9.3")
        print "\n", arcpy.GetMessages()
        arcpy.DeleteField_management(nineNew, "PARCEL_1;CENSUSID_1;ALIASID_1;ADDR_1;SIDE_1;STRDIR_1;STRPRETYPE_1;STRNAME_1;STRTYPE_1")
        print "\n", arcpy.GetMessages()

        xStep = 'Join field between sclnine_old and sclnine_new to find deletes'
        arcpy.JoinField_management(nineOld, "ALIASID", nineNew, "ALIASID")
        print "\n", arcpy.GetMessages()
        arcpy.Select_analysis(nineOld, nineChangeGdb + "deletes", "ALIASID_1 IS NULL")
        print "\n", arcpy.GetMessages()
        arcpy.DeleteField_management(nineDeletes, "PARCEL;STRPRETYPE;PARCEL_1;CENSUSID_1;ALIASID_1;ADDR_1;SIDE_1;STRDIR_1;STRPRETYPE_1;STRNAME_1;STRTYPE_1")
        print "\n", arcpy.GetMessages()
        arcpy.AddField_management(nineDeletes, "CHANGE", "TEXT", "", "", "10", "", "NULLABLE")
        print "\n", arcpy.GetMessages()
        arcpy.CalculateField_management(nineDeletes, "CHANGE", "'Delete'", "PYTHON_9.3")
        print "\n", arcpy.GetMessages()

        xStep = 'Merge Additions and Deletes to create new output layer'
        arcpy.Merge_management([nineAdds, nineDeletes], nineChangeGdb + "nine_change")
        print "\n", arcpy.GetMessages()

        xStep = 'Only do report if there were changes'
        fc = getConfig.main('user','crscl','path','workspace') + 'Nine_Change.gdb/nine_change'

        if arcpy.management.GetCount(fc)[0] == "0":
            print 'No changes'
            successMsg.append('<br><br>No nine record changes last week.')

            xStep = 'Copy no changes file to excel'
            copyfile(changeReportWkspace + 'no_changes.xls', changeReportWkspace + 'change_reports_for_users/{0}_nine_change_report.xls'.format(today))

        else:
            xStep = 'Create a variable to remove null values from fields'
            nullCodeblock = """def CalcField(Record):
                if str(Record) == 'None':
                    return ''
                else:
                    return Record"""

            xStep = 'Calculate fields to remove null values'
            arcpy.CalculateField_management(nineChange, "STRDIR", "CalcField(!strdir!)", "PYTHON_9.3", nullCodeblock)
            print "\n", arcpy.GetMessages()
            arcpy.CalculateField_management(nineChange, "STRTYPE", "CalcField(!strtype!)", "PYTHON_9.3", nullCodeblock)
            print "\n", arcpy.GetMessages()

            xStep = 'Export to table to create report'
            arcpy.TableToTable_conversion(nineChange, nineChangeGdb, "nine_change_table")
            print "\n", arcpy.GetMessages()

            xStep = 'Create CSV'
            result = arcpy.GetCount_management(nineChangeGdb + 'nine_change_table')
            count = int(result.getOutput(0))
            successMsg.append('<br><br>There were {0} SCL_Nine changes last week.'.format(count))

            xStep = 'Export change_report_sort to Excel'
            arcpy.TableToExcel_conversion(nineChangeGdb + 'nine_change_table',changeReportWkspace + 'change_reports_for_users/{0}_nine_change_report.xls'.format(today))
            print 'Report exported to Excel'

        #-----------------------------------------------------------------------
        print '\nSucceeded at ' + time.ctime()
        successMsg.append('<br><br>Change reports successfully created!')


    except:
        xFlag = 1
        err = sys.exc_info()[1]
        xStep = '{0} {1}'.format(err, xStep)
        print 'Error occured: {0}'.format(xStep)
        failedMsg.append(xStep)

    finally:
        if len(failedMsg) != 0:
            emailSubject = '##--ERROR--## SCL Weekly Change Report'
            jobStatus = 'error'
        if len(failedMsg) == 0:
            emailSubject = 'SCL Weekly Change Report'
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
        mongoJobUpdate.mongoUpdate('scl - crscl change report',startTime,endTime,startFtime,endFtime,jobStatus,failedMsg)

if __name__ == '__main__':
    main()