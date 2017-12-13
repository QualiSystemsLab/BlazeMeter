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
- Load the release package which includes the Service and its driver
- Update the BlazeMeterKey and BlazeMeterSecret default values and remove the 'User Input' from them
- Create a test in BlazeMeter with some name, e.g. "Flex Load Balancer" 
- Add the BlazeMeter service to a blueprint
- Add a resource/app with a name containing the test name, e.g. "Flex Load Balancer", and a URL stored in an
attribute Web Interface; add a visual connector between this resource and the BlazeMeter service
- Run the Start Test command. The command will then look for any resource/app that is connected to the BlazeMeter service, which also has the 'Web Interface' attribute, and will try to find a matching test to execute for that resource/app.
- You can also provide a test name to the Start Test command, and a test with that specific name will get executed for each of the connected resources/apps

Creating a BlazeMeter test:

![](blazemeter%20leads.png)


Output of Start_Traffic - URL of live BlazeMeter result page:

![](blazemeter%20output%20url.png)

Live BlazeMeter result page:
![](blazemeter%20result.png)
