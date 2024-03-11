+++
title = "Creating a New Task"
chapter = false
weight = 25
+++

## Creating a New Task

Creating a new task means creating a new Python file to define what parameters users should define and which API endpoint(s) for Bloodhound to utilize.

New command functionality is placed in the `bloodhound/bloodhound/agent_functions` folder with an appropriately named .py file.

### Examples

Here's a basic example of making a request to a static URI in bloodhound:

```python
uri = '/api/v2/available-domains'

response_code, response_data = await BloodhoundAPI.query_bloodhound(taskData, method='GET', uri=uri)
```

The taskData comes from the `create_go_tasking` function for the command as a parameter, so you can just pass that along.
That `taskData` data specifically has the backing payload's build parameters and the issuing user's secrets. 
These two things together allow the BloodhoundAPI.query_bloodhound to lookup and properly authenticate for requests.

`response_code` will vary depending on the specific bloodhound API that you're using, so I recommend checking their documentation first.

`response_data` will vary depending on the specific bloodhound API that you're using, but it'll either be JSON if things were successful or a string if there was an error.

### Default Response Processing

To make things easier, there is a `process_standard_response` functionality provided as part of BloodhoundAPI:

```python
await BloodhoundAPI.process_standard_response(response_code=response_code,
    response_data=response_data, taskData=taskData, response=response)
```

This function uses the `taskData` from your `create_go_tasking` and the basic `response` you created at the beginning of your `create_go_tasking` to perform some basic checks.
This will return either success or error to Mythic based on the `response_code` and display the `response_data` to the user as standard output. 

If you want to do something special with the response from bloodhound first, then you can either manipulate the data and then call this function, or you can perform these functions yourself.

