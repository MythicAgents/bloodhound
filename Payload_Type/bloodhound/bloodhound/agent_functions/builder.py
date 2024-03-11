from mythic_container.PayloadBuilder import *
from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *


class Bloodhound(PayloadType):
    name = "bloodhound"
    file_extension = ""
    author = "@its_a_feature_"
    supported_os = [
        SupportedOS("bloodhound")
    ]
    wrapper = False
    wrapped_payloads = []
    note = """
    This payload communicates with an existing Bloodhound Community Edition instance
    """
    supports_dynamic_loading = False
    mythic_encrypts = True
    translation_container = None
    agent_type = "service"
    agent_path = pathlib.Path(".") / "bloodhound"
    agent_icon_path = agent_path / "agent_functions" / "bloodhound.svg"
    agent_code_path = agent_path / "agent_code"
    build_parameters = [
        BuildParameter(name="URL",
                       description="Bloodhound URL",
                       parameter_type=BuildParameterType.String,
                       default_value="https://127.0.0.1:8080"),
    ]
    c2_profiles = []

    async def build(self) -> BuildResponse:
        # this function gets called to create an instance of your payload
        resp = BuildResponse(status=BuildStatus.Success)
        ip = "127.0.0.1"
        create_callback = await SendMythicRPCCallbackCreate(MythicRPCCallbackCreateMessage(
            PayloadUUID=self.uuid,
            C2ProfileName="",
            User="Bloodhound",
            Host="Bloodhound",
            Ip=ip,
            IntegrityLevel=3,
        ))
        if not create_callback.Success:
            logger.info(create_callback.Error)
        else:
            logger.info(create_callback.CallbackUUID)
        return resp
