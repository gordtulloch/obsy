import pandas

colSpecs = [(1,2), (3,6), (7,7), (8,17), (18,18), (20,21),(22,23),(24, 28),(30,30),(31,32), (33,34), (35,38), (39,39),(41,50),(52,52),
            (53,58), (59,59), (62,63), (64,69), (70,70), (71,72),(73,73),(75,76),(77,82), (83,83), (84,85), (86,86), (88,89), (91,101),
            (102,102),(104,107),(108,108), (110,110), (111,126), (129,129), (131,133), (134,134),(135,135),(137,153),
            (155,159), (161,165), (167,177), (179,184), (186,191), (193,200),(202,202),(204,212),(214,223),(225,235)]
nameSpecs = ['constCode', 'starNo', 'compNo', 'gvcsNo', 'noteFlag', 'RAh2000','RAm2000','RAs2000','DECdeg2000','DECmin2000','DECsec2000',
             'posnAccuracyFlag','varType','lMagMax','magMax','magMaxUncertainty','magMin1BrightLimit','magMin1','magMin1Uncertainty','magMin1AltPhot',
             'magMin1AmplitudeFlag','magMin2BrightLimit','magMin2','magMin2Uncertainty','magMin2AltPhot','magMin2AmplitudeFlag','photSystem',
             'epochForMaxLight','epochQualityFlag','yearOfOutburst','yearOfOutburstQualityFlag','upperLowerLimitCode','period','periodUncertaintyFlag',
             'nPeriod','nPeriodUncertaintyFlag','risingTimeOrDuration','risingTimeOrDurationUncertaintyFlag','eclipsingVarNote','spectralType','ref1'
             ,'ref2','exists','properMotionRA','properMotionDEC','coordEpoch','identUncertaintyFlag','astrometrySource','varType2','gvcs2No']
constellationCodes = [(1,'And'),(23,'Cir'),(45,'Lac'),(67,'PsA'),(2,'Ant'),(24,'Col'),(46,'Leo'),(68,'Pup'),
                      (3,'Aps'),(25,'Com'),(47,'LMi'),(69,'Pyx'),(4,'Aqr'),(26,'CrA'),(48,'Lep'),(70,'Ret'),
                      (5,'Aql'),(27,'CrB'),(49,'Lib'),(71,'Sge'),(6,'Ara'),(28,'Crv'),(50,'Lup'),(72,'Sgr'),
                      (7,'Ari'),(29,'Crt'),(51,'Lyn'),(73,'Sco'),(8,'Aur'),(30,'Cru'),(52,'Lyr'),(74,'Scl'),
                      (9,'Boo'),(31,'Cyg'),(53,'Men'),(75,'Sct'),(10,'Cae'),(32,'Del'),(54,'Mic'),(76,'Ser'),
                      (11,'Cam'),(33,'Dor'),(55,'Mon'),(77,'Sex'),(12,'Cnc'),(34,'Dra'),(56,'Mus'),(78,'Tau'),
                      (13,'CVn'),(35,'Equ'),(57,'Nor'),(79,'Tel'),(14,'CMa'),(36,'Eri'),(58,'Oct'),(80,'Tri'),
                      (15,'CMi'),(37,'For'),(59,'Oph'),(81,'TrA'),(16,'Cap'),(38,'Gem'),(60,'Ori'),(82,'Tuc'),(17,'Car'),
                      (39,'Gru'),(61,'Pav'),(83,'UMa'),(18,'Cas'),(40,'Her'),(62,'Peg'),(84,'UMi'),(19,'Cen'),
                      (41,'Hor'),(63,'Per'),(85,'Vel'),(20,'Cep'),(42,'Hya'),(64,'Phe'),(86,'Vir'),(21,'Cet'),
                      (43,'Hyi'),(65,'Pic'),(87,'Vol'),(22,'Cha'),(44,'Ind'),(66,'Psc'),(88,'Vul')]
gcvsDF  =pandas.read_fwf('catalogs/gcvs/gcvs5.txt',colspecs=colSpecs,names=nameSpecs)
print(list(gcvsDF.columns.values))
#starNoDF=pandas.read_fwf('catalogs/gcvs/starno.txt',colspecs=[(0,5),(6,10)],names=['starName','starNo'])
#print(starNoDF)
#print(list(starNoDF.columns.values))
#remarksDF=pandas.read_fwf('catalogs/gcvs/remarks.txt',colspecs=[(0,5),(6,8),(9,80)],names=['starName','const','remark'])
#print(list(remarksDF.columns.values))