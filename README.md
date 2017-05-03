BlazeMeter is a JMeter-derived SaaS traffic generation service for testing websites. 
You create a test, which can be anything from a Selenium test to a simple GET or POST 
repeated at a certain frequency, and run it. 

Here we show how to run a BlazeMeter test against a dynamic URL determined during 
Setup and expose the BlazeMeter results page in CloudShell. 

The BlazeMeter test sends a series of identical requests to a given URL. 
Here we use a simple URL test with a URL dynamically reconfigured based on an attribute. 
There are other types of test like Selenium. 
Starting the test, displaying the results page, and polling for completion should work the same, 
but the BlazeMeter API calls to reconfigure the test would need to be updated.

In order to use this plugin:
- Create a test in BlazeMeter with some name, e.g. "Flex Load Balancer" 
- Create a resource model representing a BlazeMeter resource and attach relevant attributes
- Attach Start_Traffic and Wait_For_Traffic to the model
- Create a BlazeMeter resource and fill in the attributes
- Add a BlazeMeter resource to a reservation
- Add a resource with a name containing the test name, e.g. "Flex Load Balancer", and a URL stored in an 
attribute Web Interface; add a visual connector between this resource and the BlazeMeter resource 
- Run Start_Traffic

For your setup, you will most likely want to update the scripts:
 - Read BlazeMeter key and secret from resource attributes instead of hard-coding them in the script
 - Change the way the test is located (currently using visual connectors and the connected resource name)
 - Change the way the test target URL is determined and the attribute name -- currently hard-coded in the blueprint
 
In the example blueprint in this repo, the BlazeMeter and target resource are both represented as apps because they
came from CloudShell Live, but ordinary resources or services can be used instead. Attach the scripts to the appropriate
resource or service model.


Creating a BlazeMeter test:

![](blazemeter%20leads.png)


Output of Start_Traffic - URL of live BlazeMeter result page:

![](blazemeter%20output%20url.png)

Live BlazeMeter result page:
![](blazemeter%20result.png)
