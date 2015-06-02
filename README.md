## OslcClient for Python

The primary focus of this client is to interface with the Jazz Platform to perform
some basic administrative tasks en masse.

Hence the coverage of what you can do is pretty narrow and is intended to be used
as a base to extend to whatever else you may need.

### Goals

Provide a simple starting point to access Jazz from Python, not to provide client
parity.

Solve the problems that I have, ymmv.

### Functionality limited to RTC

* Login to a Jazz Server via Standard Form Auth
* Submit Workitems
* Get Project Areas
* Get Categories for a Project Area
* Get Enumeration Values

### todo items for work I have pending...

* Query Workitems ( working example being added)
* Edit Workitems
* Batch edit workitems by query
