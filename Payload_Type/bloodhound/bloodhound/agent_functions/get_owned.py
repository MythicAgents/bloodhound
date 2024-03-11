from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
from bloodhound.BloodhoundRequests import BloodhoundAPI


class GetOwnedArguments(TaskArguments):

    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [

        ]

    async def parse_arguments(self):
        #self.load_args_from_json_string(self.command_line)
        pass

    async def parse_dictionary(self, dictionary_arguments):
        self.load_args_from_dictionary(dictionary=dictionary_arguments)


class GetOwned(CommandBase):
    cmd = "get_owned"
    needs_admin = False
    help_cmd = "get_owned"
    description = "Get information about owned objects"
    version = 1
    author = "@its_a_feature_"
    argument_class = GetOwnedArguments
    supported_ui_features = []
    browser_script = BrowserScript(script_name="get_owned", author="@its_a_feature_", for_new_ui=True)
    attackmapping = []

    async def create_go_tasking(self,
                                taskData: MythicCommandBase.PTTaskMessageAllData) -> MythicCommandBase.PTTaskCreateTaskingMessageResponse:
        response = MythicCommandBase.PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=False,
            Completed=True,
            DisplayParams=f""
        )

        try:
            owned_id = await BloodhoundAPI.get_owned_id(taskData)
            uri = f"/api/v2/asset-groups/{owned_id}/members?limit=100"
            response_code, response_data = await BloodhoundAPI.query_bloodhound(taskData,
                                                                                method='GET',
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
