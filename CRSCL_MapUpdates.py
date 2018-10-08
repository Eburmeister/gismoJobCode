# This script fires off the web map updates
def main():
    try:
        xFlag = 0
        import sys
        import arcpy
        import os, shutil
        import Scl_Elections_Basic_Maps
        import Scl_Elections_Valley
        import Scl_Elections_County
        import UrbanRuralMaps

        # Get parameters from config file
        sys.path.append("//ccgisfiles01m/gisdata/prdba/crupdates/CCPythonLib/Appl/")
        import getConfig

        serverName = getConfig.main('globalPath','serverName')
        destinationGISPLOT = getConfig.main('globalPath','GISPlot')
        webplot01 = getConfig.main('globalPath','webplot01')
        webplot02 = getConfig.main('globalPath','webplot02')


        plotDir = getConfig.main('user','crscl','path','crsclPlot')
        destinationCRSCL = serverName + 'gisdata/crscl/plot'

        mapErrors = []

        # SCL GISPlot Maps-------------------------------------------------------------------
        xStep = 'Basic maps'
        print xStep
        Scl_Elections_Basic_Maps.start("CC_Communities","GEN5.3_Clark_County_Communities")
        Scl_Elections_Basic_Maps.start("LV_Valley_Streetmap","GEN5.4_LasVegasValleyStreetMap")
        xStep = 'Valley maps'
        print xStep
        Scl_Elections_Valley.start("MCD Boundaries","#","#","#","Minor Civil Division","Boundaries","GI5.2.1_Minor_Civil_Division_Boundaries")
        Scl_Elections_Valley.start("Zip Code Boundaries","#","#","#","Zip Code","Boundaries","GI5.3.1_Zip_Code_Boundaries")
        Scl_Elections_Valley.start("Tract Boundaries","#","#","#","Census Tract","Boundaries","GI5.4.1_Census_Tract_Boundaries")
        Scl_Elections_Valley.start("Unincorporated Towns","#","#","#","Unincorporated","Towns","GI5.5.1_Unincorporated_Townships")
        Scl_Elections_Valley.start("Cities","#","#","#","Incorporated","Cities","GI5.6.1_Incorporated_Cities")
        Scl_Elections_Valley.start("#","#","#","#","Street","Centerline","GI5.7.1_Street_Centerline")
        xStep = 'County maps'
        print xStep
        Scl_Elections_County.start("MCD Boundaries","#","Minor Civil Division","Boundaries","GI5.2.2_Minor_Civil_Division_Boundaries")
        Scl_Elections_County.start("Zip Code Boundaries","#","Zip Code","Boundaries","GI5.3.2_Zip_Code_Boundaries")
        Scl_Elections_County.start("Tract Boundaries","#","Census Tract","Boundaries","GI5.4.2_Census_Tract_Boundaries")
        Scl_Elections_County.start("Unincorporated Towns","#","Unincorporated","Towns","GI5.5.2_Unincorporated_Townships")
        Scl_Elections_County.start("Cities","#","Incorporated","Cities","GI5.6.2_Incorporated_Cities")
        import UnlawfulFirearmMap

        # SCL Urban Rural Maps --------------------------------------------------------------------------------
        xStep = 'Urban Rural maps'
        print xStep
        UrbanRuralMaps.start("Urban","Enterprise","Enterprise","Enterprise","Town Advisory Board")
        UrbanRuralMaps.start("Urban","LoneMountain","LoneMountain","Lone Mountain","Citizens Advisory Council")
        UrbanRuralMaps.start("Urban","LowerKyleCanyon","LowerKyleCanyon","Lower Kyle Canyon","Citizens Advisory Council")
        UrbanRuralMaps.start("Urban","Paradise","Paradise","Paradise","Town Advisory Board")
        UrbanRuralMaps.start("Urban","SpringValley","SpringValley","Spring Valley","Town Advisory Board")
        UrbanRuralMaps.start("Urban","SunriseManor","SunriseManor","Sunrise Manor","Town Advisory Board")
        UrbanRuralMaps.start("Urban","Whitney","Whitney","Whitney","Town Advisory Board")
        UrbanRuralMaps.start("Urban","Winchester","Winchester","Winchester","Town Advisory Board")
        UrbanRuralMaps.start("Rural","Bunkerville","Bunkerville","Bunkerville","Town Advisory Board")
        UrbanRuralMaps.start("Rural","Goodsprings","Goodsprings","Goodsprings","Citizens Advisory Council")
        UrbanRuralMaps.start("Rural","IndianSprings","IndianSprings","Indian Springs","Town Advisory Board")
        UrbanRuralMaps.start("Rural","Laughlin","Laughlin","Laughlin","Town Advisory Board")
        UrbanRuralMaps.start("Rural","Moapa","Moapa","Moapa","Town Advisory Board")
        UrbanRuralMaps.start("Rural","MoapaValley","MoapaValley","Moapa Valley","Town Advisory Board")
        UrbanRuralMaps.start("Rural","MountainSprings","MountainSprings","Mountain Springs","Citizens Advisory Council")
        UrbanRuralMaps.start("Rural","MountCharleston","MountCharleston","Mount Charleston","Town Advisory Board")
        UrbanRuralMaps.start("Rural","RedRock","RedRock","Red Rock","Citizens Advisory Council")
        UrbanRuralMaps.start("Rural","SandyValley","SandyValley","Sandy Valley","Citizens Advisory Council")
        UrbanRuralMaps.start("Rural","Searchlight","Searchlight","Searchlight","Town Advisory Board")

        print 'All maps created!'

        # Copy PDFs to internet site and crscl\plot ----------------------
        # Copy to internet site
        xStep = 'Copy PDFs to internet site'
        source = os.listdir(plotDir)
        for i in source:
            shutil.copy(plotDir + i, destinationGISPLOT)
##            shutil.copy(plotDir + i, webplot01)
##            shutil.copy(plotDir + i, webplot02)
        print 'Maps copied to internet site'

        # Copy to crscl/plot
        xStep = 'Copy PDFs to crscl/plot'
        source = os.listdir(plotDir)
        for i in source:
            shutil.copy(plotDir + i, destinationCRSCL)
        print 'Maps copied to crscl/plot'

    except:
        xFlag = 2
        print 'Error in CRSCL Map Update script: {0}'.format(xStep)
        print sys.exc_info()

    finally:
        return(xStep, xFlag)

if __name__ == '__main__':
    main()