
# 1
# Grab the root services catalog
# => /ccm/rootservices

# 2
# Find the CM Service Provides section and get the WorkItem catalog url
# Xpath ::= /oslc_cm:cmServiceProviders@rdf:resource
#
# <oslc_cm:cmServiceProviders
#	      xmlns:oslc_cm="http://open-services.net/xmlns/cm/1.0/"
#	      rdf:resource="https://anzclm.rationalanz.com.au/ccm/oslc/workitems/catalog" />
# Extract WI catalog url and follow
# => https://anzclm.rationalanz.com.au/ccm/oslc/workitems/catalog

# 3
# Find the specific service provider for your project
# Xpath ::= //oslc_disc:ServiceProvider[dc:title="JKE Banking"]/oslc_disc:services@rdf:resource
#
# <oslc_disc:ServiceProvider>
#  <dc:title>JKE Banking (Change Management)</dc:title>
#  <oslc_disc:details rdf:resource="https://anzclm.rationalanz.com.au/ccm/process/project-areas/_6qIDcEKpEeSi3pe7jBZL6Q"/>
#  <oslc_disc:services rdf:resource="https://anzclm.rationalanz.com.au/ccm/oslc/contexts/_6qIDcEKpEeSi3pe7jBZL6Q/workitems/services.xml"/>
#  <jfs_proc:consumerRegistry rdf:resource="https://anzclm.rationalanz.com.au/ccm/process/project-areas/_6qIDcEKpEeSi3pe7jBZL6Q/links"/>
# </oslc_disc:ServiceProvider>
#
# Extract the workitems services url and follow
# => https://anzclm.rationalanz.com.au/ccm/oslc/contexts/_6qIDcEKpEeSi3pe7jBZL6Q/workitems/services.xml

# 4
# We are now in the service catalog for a specific project, find the WI creation factory URL
# xpath ::= /oslc_cm:ServiceDescriptor/oslc_cm:changeRequests/oslc_cm:factory/oslc_cm:url
#
# <oslc_cm:factory>
#   <dc:title>Location for creation of change requests</dc:title>
#   <oslc_cm:url>https://anzclm.rationalanz.com.au/ccm/oslc/contexts/_6qIDcEKpEeSi3pe7jBZL6Q/workitems</oslc_cm:url>
# </oslc_cm:factory>
#
#
