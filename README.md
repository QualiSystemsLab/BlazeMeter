BlazeMeter is a JMeter-derived SaaS traffic generation service for testing websites. You create a test, which can be anything from a Selenium test to a simple GET or POST repeated at a certain frequency, and run it. 

Here we show how to run a BlazeMeter test against a dynamic URL determined during Setup and expose the BlazeMeter results page in CloudShell. 

The BlazeMeter test sends a series of identical requests to a given URL. Here we use a simple URL test with a URL dynamically reconfigured based on an attribute. There are other types of test like Selenium. Starting the test, displaying the results page, and polling for completion should work the same, but the BlazeMeter API calls to reconfigure the test would need to be updated.


BlazeMeter test settings:

![](blazemeter%20leads.png)

