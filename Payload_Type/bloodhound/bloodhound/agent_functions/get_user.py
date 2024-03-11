from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
from bloodhound.BloodhoundRequests import BloodhoundAPI


class GetUserArguments(TaskArguments):

    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="object_id",
                description="Which User object_id to query",
                type=ParameterType.String,
                parameter_group_info=[ParameterGroupInfo(
                    required=True,
                    ui_position=1,
                    group_name="object_id"
                )]
            ),
            CommandParameter(
                name="name",
                description="Which User search for",
                type=ParameterType.String,
                parameter_group_info=[ParameterGroupInfo(
                    required=True,
                    ui_position=1,
                    group_name="search"
                )]
            ),

        ]

    async def parse_arguments(self):
        if len(self.command_line) == 0:
            raise ValueError("Must supply an object_id")
        self.add_arg("object_id", self.command_line)

    async def parse_dictionary(self, dictionary_arguments):
        self.load_args_from_dictionary(dictionary=dictionary_arguments)


async def finished_searching(completionMsg: PTTaskCompletionFunctionMessage) -> PTTaskCompletionFunctionMessageResponse:
    response = PTTaskCompletionFunctionMessageResponse(Success=True)
    if "error" in completionMsg.SubtaskData.Task.Status:
        response.TaskStatus = "error: Failed to find object"
        response.Success = False
        response.Completed = True
        return response
    subtaskOutput = await SendMythicRPCResponseSearch(MythicRPCResponseSearchMessage(
        TaskID=completionMsg.SubtaskData.Task.ID
    ))
    if not subtaskOutput.Success:
        response.TaskStatus = "error: Failed to get search output"
        response.Success = False
        response.Completed = True
        return response
    json.loads(subtaskOutput.Responses[0].Response)
    return response


class GetUser(CommandBase):
    cmd = "get_user"
    needs_admin = False
    help_cmd = "get_user -object_id \"S-1-5-21-909015691-3030120388-2582151266-512\""
    description = "Get information about a specific user"
    version = 1
    author = "@its_a_feature_"
    argument_class = GetUserArguments
    supported_ui_features = ["bloodhound:get_user"]
    #browser_script = BrowserScript(script_name="controllables", author="@its_a_feature_", for_new_ui=True)
    attackmapping = []
    completion_functions = {
        "finished_searching": finished_searching
    }

    async def create_go_tasking(self,
                                taskData: MythicCommandBase.PTTaskMessageAllData) -> MythicCommandBase.PTTaskCreateTaskingMessageResponse:
        response = MythicCommandBase.PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=False,
            Completed=True,
            DisplayParams=f" for {taskData.args.get_arg('object_id')}"
        )
        if taskData.args.get_parameter_group_name() == "object_id":
            uri = f"/api/v2/users/{taskData.args.get_arg('object_id')}"
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
        else:
            # we need to search for the user first
            subtask = await SendMythicRPCTaskCreateSubtask(MythicRPCTaskCreateSubtaskMessage(
                TaskID=taskData.Task.ID,
                SubtaskCallbackFunction="finished_searching",
                CommandName="search",
                Params=json.dumps({"query": taskData.args.get_arg("name")})
            ))
            if subtask.Success:
                return MythicCommandBase.PTTaskCreateTaskingMessageResponse(
                    TaskID=taskData.Task.ID,
                    Success=True,
                    Completed=False,
                    DisplayParams=f" for {taskData.args.get_arg('name')}"
                )
            else:
                MythicCommandBase.PTTaskCreateTaskingMessageResponse(
                    TaskID=taskData.Task.ID,
                    Success=False,
                    Completed=True,
                    DisplayParams=f" for {taskData.args.get_arg('object_id')}",
                    Error=subtask.Error
                )

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp
