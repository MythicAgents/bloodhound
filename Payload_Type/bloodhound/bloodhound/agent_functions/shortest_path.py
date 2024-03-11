from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
from bloodhound.BloodhoundRequests import BloodhoundAPI


class ShortestPathArguments(TaskArguments):

    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="start_node",
                cli_name="start",
                description="The object id to start from ",
                type=ParameterType.String,
                parameter_group_info=[ParameterGroupInfo(
                    required=True,
                    ui_position=1
                )]
            ),
            CommandParameter(
                name="end_node",
                cli_name="end",
                description="The object id to end",
                type=ParameterType.String,
                default_value="",
                parameter_group_info=[ParameterGroupInfo(
                    required=True,
                    ui_position=2
                )]
            ),
            CommandParameter(
                name="relationships",
                cli_name="relationships",
                description="Only allow certain kinds of edges",
                type=ParameterType.ChooseMultiple,
                choices=[],
                default_value=["Contains", "GetChangesAll", "MemberOf"],
                parameter_group_info=[ParameterGroupInfo(
                    required=False,
                    ui_position=3
                )]
            ),
        ]

    async def parse_arguments(self):
        self.load_args_from_json_string(self.command_line)

    async def parse_dictionary(self, dictionary_arguments):
        self.load_args_from_dictionary(dictionary=dictionary_arguments)


class ShortestPath(CommandBase):
    cmd = "shortest_path"
    needs_admin = False
    help_cmd = "shortest_path -start \"S-1-5-21-909015691-3030120388-2582151266-512\" -end \"S-1-5-21-909015691-3030120388-2582151266-1000\""
    description = "Query Bloodhound CE for the shortest path between two nodes"
    version = 1
    author = "@its_a_feature_"
    argument_class = ShortestPathArguments
    browser_script = BrowserScript(script_name="cypher", author="@its_a_feature_", for_new_ui=True)
    attackmapping = []

    async def create_go_tasking(self,
                                taskData: MythicCommandBase.PTTaskMessageAllData) -> MythicCommandBase.PTTaskCreateTaskingMessageResponse:
        response = MythicCommandBase.PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=False,
            Completed=True,
            DisplayParams=f" for {taskData.args.get_arg('start_node')} to {taskData.args.get_arg('end_node')}"
        )
        uri = f"/api/v2/graphs/shortest-path?start_node={taskData.args.get_arg('start_node')}&end_node={taskData.args.get_arg('end_node')}&relationship_kinds=in%3A{'%2C'.join(taskData.args.get_arg('relationships'))}"
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
