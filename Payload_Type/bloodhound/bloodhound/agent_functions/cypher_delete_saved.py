from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
from bloodhound.BloodhoundRequests import BloodhoundAPI


class CypherDeleteSavedArguments(TaskArguments):

    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="query_id",
                description="ID for the saved query to delete",
                type=ParameterType.String,
                parameter_group_info=[ParameterGroupInfo(
                    required=True,
                    ui_position=1
                )]
            ),
        ]

    async def parse_arguments(self):
        self.load_args_from_json_string(command_line=self.command_line)

    async def parse_dictionary(self, dictionary_arguments):
        self.load_args_from_dictionary(dictionary=dictionary_arguments)


class CypherDeleteSaved(CommandBase):
    cmd = "cypher_delete_saved"
    needs_admin = False
    help_cmd = "cypher_delete_saved -query_id 4"
    description = "Delete a new saved custom cypher"
    version = 1
    author = "@its_a_feature_"
    argument_class = CypherDeleteSavedArguments
    supported_ui_features = ["bloodhound:cypher_delete_saved"]
    #browser_script = BrowserScript(script_name="cypher_list_saved", author="@its_a_feature_", for_new_ui=True)
    attackmapping = []

    async def create_go_tasking(self,
                                taskData: MythicCommandBase.PTTaskMessageAllData) -> MythicCommandBase.PTTaskCreateTaskingMessageResponse:
        response = MythicCommandBase.PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=False,
            Completed=True,
            DisplayParams=f" for {taskData.args.get_arg('query_id')}"
        )
        uri = f"/api/v2/saved-queries/{taskData.args.get_arg('query_id')}"
        try:
            response_code, response_data = await BloodhoundAPI.query_bloodhound(taskData,
                                                                                method='DELETE',
                                                                                uri=uri)
            if response_code == 204:
                await SendMythicRPCResponseCreate(MythicRPCResponseCreateMessage(
                    TaskID=taskData.Task.ID,
                    Response=f"Successfully deleted query".encode("UTF8"),
                ))
                response.Success = True
                return response
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
