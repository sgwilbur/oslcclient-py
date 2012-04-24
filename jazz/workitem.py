
class WorkItem(object):
    
    def __init__(self):
        self.xmlContent
        print('New WorkItem')
        
    def createXML(self, attribs):
        wiXML = '<oslc_cm:ChangeRequest xmlns:rtc_cm="http://jazz.net/xmlns/prod/jazz/rtc/cm/1.0/" xmlns:dc="http://purl.org/dc/terms/" xmlns:oslc_cm="http://open-services.net/xmlns/cm/1.0/" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:calm="http://jazz.net/xmlns/prod/jazz/calm/1.0/"'
        
        # Existing WI will have this about piece
        # wiXML += ' rdf:about="https://wincqserver:9445/rtc/resource/itemName/com.ibm.team.workitem.WorkItem/2772"'
        
        wiXML == '>'
# <rtc_cm:projectArea rdf:resource="https://wincqserver:9445/rtc/oslc/projectareas/_v-iPIIO2Ed-ec4_ZoGHE4w"/>
# <rtc_cm:filedAgainst rdf:resource="https://wincqserver:9445/rtc/resource/itemOid/com.ibm.team.workitem.Category/_YehX8IVXEd-0pPi2nnFPlA"/>
# <rtc_cm:teamArea rdf:resource="https://wincqserver:9445/rtc/oslc/teamareas/_9j3cYIO2Ed-ec4_ZoGHE4w"/>
        
        wiXML += '</oslc_cm:ChangeRequest>'