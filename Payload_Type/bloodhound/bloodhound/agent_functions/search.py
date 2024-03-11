from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
from bloodhound.BloodhoundRequests import BloodhoundAPI


class SearchArguments(TaskArguments):

    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="query",
                description="What to query Bloodhound for",
                type=ParameterType.String,
                parameter_group_info=[ParameterGroupInfo(
                    required=True,
                    ui_position=1
                )]
            ),
            CommandParameter(
                name="type",
                description="Filter your search results by Node type",
                type=ParameterType.String,
                default_value="",
                parameter_group_info=[ParameterGroupInfo(
                    required=False,
                    ui_position=2
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
            raise ValueError("Must supply a query")
        self.add_arg("query", self.command_line)

    async def parse_dictionary(self, dictionary_arguments):
        self.load_args_from_dictionary(dictionary=dictionary_arguments)


class Search(CommandBase):
    cmd = "search"
    needs_admin = False
    help_cmd = "search -query \"my query\" -type \"Group\""
    description = "Search Bloodhound Nodes via the /api/v2/search API"
    version = 1
    author = "@its_a_feature_"
    argument_class = SearchArguments
    browser_script = BrowserScript(script_name="search", author="@its_a_feature_", for_new_ui=True)
    attackmapping = []

    async def create_go_tasking(self,
                                taskData: MythicCommandBase.PTTaskMessageAllData) -> MythicCommandBase.PTTaskCreateTaskingMessageResponse:
        response = MythicCommandBase.PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=False,
            Completed=True,
            DisplayParams=f" for {taskData.args.get_arg('query')}"
        )
        uri = f"/api/v2/search?limit=100&q={taskData.args.get_arg('query')}&skip={taskData.args.get_arg('skip')}"
        if taskData.args.get_arg("type") != "":
            uri += f"&type={taskData.args.get_arg('type')}"
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
