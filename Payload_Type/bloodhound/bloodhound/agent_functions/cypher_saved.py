from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
from bloodhound.BloodhoundRequests import BloodhoundAPI


class CypherSavedArguments(TaskArguments):

    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="query_name",
                cli_name="query-name",
                description="Run a custom saved cypher query from Bloodhound CE",
                type=ParameterType.ChooseOne,
                dynamic_query_function=self.get_saved_queries,
                parameter_group_info=[ParameterGroupInfo(
                    required=True,
                    group_name="selected"
                )]
            )
        ]

    async def get_saved_queries(self, callback: PTRPCDynamicQueryFunctionMessage) -> PTRPCDynamicQueryFunctionMessageResponse:
        response = PTRPCDynamicQueryFunctionMessageResponse()
        payload_resp = await SendMythicRPCPayloadSearch(MythicRPCPayloadSearchMessage(
            PayloadUUID=callback.PayloadUUID
        ))
        if payload_resp.Success:
            if len(payload_resp.Payloads) == 0:
                await SendMythicRPCOperationEventLogCreate(MythicRPCOperationEventLogCreateMessage(
                    CallbackId=callback.Callback,
                    Message=f"Failed to get payload: {payload_resp.Error}",
                    MessageLevel="warning"
                ))
                response.Error = f"Failed to get payload: {payload_resp.Error}"
                return response
            payload = payload_resp.Payloads[0]
            fakeTaskData = PTTaskMessageAllData()
            fakeTaskData.BuildParameters = payload.BuildParameters
            fakeTaskData.Secrets = callback.Secrets
            choices = await BloodhoundAPI.get_saved_queries(taskData=fakeTaskData)
            response.Choices = [x["name"] for x in choices]
            response.Success = True
            return response
        else:
            await SendMythicRPCOperationEventLogCreate(MythicRPCOperationEventLogCreateMessage(
                CallbackId=callback.Callback,
                Message=f"Failed to get payload: {payload_resp.Error}",
                MessageLevel="warning"
            ))
            response.Error = f"Failed to get payload: {payload_resp.Error}"
            return response

    async def parse_arguments(self):
        return self.load_args_from_json_string(self.command_line)

    async def parse_dictionary(self, dictionary_arguments):
        return self.load_args_from_dictionary(dictionary=dictionary_arguments)


class CypherSaved(CommandBase):
    cmd = "cypher_saved"
    needs_admin = False
    help_cmd = cmd
    description = "Run one of your saved queries from Bloodhound"
    version = 1
    author = "@its_a_feature_"
    argument_class = CypherSavedArguments
    browser_script = BrowserScript(script_name="cypher", author="@its_a_feature_", for_new_ui=True)
    attackmapping = []

    async def create_go_tasking(self,
                                taskData: MythicCommandBase.PTTaskMessageAllData) -> MythicCommandBase.PTTaskCreateTaskingMessageResponse:
        response = MythicCommandBase.PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=False,
            Completed=True,
            DisplayParams=f"{taskData.args.get_arg('query_name')}"
        )
        saved_queries = await BloodhoundAPI.get_saved_queries(taskData=taskData)
        matched_query = [x["query"] for x in saved_queries if x["name"] == taskData.args.get_arg("query_name")]
        if len(matched_query) == 0:
            response.TaskStatus = "error: Saved Query Not Found"
            return response
        uri = f"/api/v2/graphs/cypher"
        body = json.dumps({
            "include_properties": True,
            "query": matched_query[0]
        }).encode()
        response.Stdout = matched_query[0]
        try:
            response_code, response_data = await BloodhoundAPI.query_bloodhound(taskData,
                                                                                method='POST',
                                                                                body=body,
                                                                                uri=uri)
            return await BloodhoundAPI.process_standard_response(response_code=response_code,
                                                                 response_data=response_data,
                                                                 taskData=taskData,
                                                                 response=response)

        except Exception as e:
            await SendMythicRPCResponseCreate(MythicRPCResponseCreateMessage(
                TaskID=taskData.Task.ID,
                Response=f"{e}".encode("UTF8"),
            ))
            response.TaskStatus = "Error: Bloodhound Access Error"
        return response

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp
