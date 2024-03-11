from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
from bloodhound.BloodhoundRequests import BloodhoundAPI


class ControllablesArguments(TaskArguments):

    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="object_id",
                description="Which Object to query",
                type=ParameterType.String,
                parameter_group_info=[ParameterGroupInfo(
                    required=True,
                    ui_position=1
                )]
            ),
            CommandParameter(
                name="skip",
                type=ParameterType.Number,
                default_value=0,
                parameter_group_info=[ParameterGroupInfo(
                    required=False,
                    ui_position=3
                )]
            ),

        ]

    async def parse_arguments(self):
        if len(self.command_line) == 0:
            raise ValueError("Must supply an object_id")
        self.add_arg("object_id", self.command_line)

    async def parse_dictionary(self, dictionary_arguments):
        self.load_args_from_dictionary(dictionary=dictionary_arguments)


class Controllables(CommandBase):
    cmd = "controllables"
    needs_admin = False
    help_cmd = "controllables -object_id \"S-1-5-21-909015691-3030120388-2582151266-512\""
    description = "Search for Nodes that the specified object has control over"
    version = 1
    author = "@its_a_feature_"
    argument_class = ControllablesArguments
    supported_ui_features = ["bloodhound:controllables"]
    browser_script = BrowserScript(script_name="controllables", author="@its_a_feature_", for_new_ui=True)
    attackmapping = []

    async def create_go_tasking(self,
                                taskData: MythicCommandBase.PTTaskMessageAllData) -> MythicCommandBase.PTTaskCreateTaskingMessageResponse:
        response = MythicCommandBase.PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=False,
            Completed=True,
            DisplayParams=f" for {taskData.args.get_arg('object_id')}"
        )
        uri = f"/api/v2/base/{taskData.args.get_arg('object_id')}/controllables?skip={taskData.args.get_arg('skip')}&limit=100"
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
