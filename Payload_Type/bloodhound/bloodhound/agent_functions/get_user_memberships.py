from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
from bloodhound.BloodhoundRequests import BloodhoundAPI


class GetUserMembershipsArguments(TaskArguments):

    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="object_id",
                description="Which Group object_id to query",
                type=ParameterType.String,
                parameter_group_info=[ParameterGroupInfo(
                    required=True,
                    ui_position=1
                )]
            ),

        ]

    async def parse_arguments(self):
        if len(self.command_line) == 0:
            raise ValueError("Must supply an object_id")
        self.add_arg("object_id", self.command_line)

    async def parse_dictionary(self, dictionary_arguments):
        self.load_args_from_dictionary(dictionary=dictionary_arguments)


class GetUserMemberships(CommandBase):
    cmd = "get_user_memberships"
    needs_admin = False
    help_cmd = "get_user_memberships -object_id \"S-1-5-21-942593832-2479470506-1224757232-1113\""
    description = "Get information about which groups this user belongs to"
    version = 1
    author = "@its_a_feature_"
    argument_class = GetUserMembershipsArguments
    supported_ui_features = ["bloodhound:get_user_memberships"]
    browser_script = BrowserScript(script_name="get_group_members", author="@its_a_feature_", for_new_ui=True)
    attackmapping = []

    async def create_go_tasking(self,
                                taskData: MythicCommandBase.PTTaskMessageAllData) -> MythicCommandBase.PTTaskCreateTaskingMessageResponse:
        response = MythicCommandBase.PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=False,
            Completed=True,
            DisplayParams=f" for {taskData.args.get_arg('object_id')}"
        )
        uri = f"/api/v2/users/{taskData.args.get_arg('object_id')}/memberships?limit=100"
        try:
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
