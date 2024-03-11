from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
from bloodhound.BloodhoundRequests import BloodhoundAPI


class CypherPredefinedArguments(TaskArguments):

    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="query_name",
                cli_name="query-name",
                description="Run a predefined cypher query from Bloodhound CE",
                type=ParameterType.ChooseOne,
                default_value="All Domain Admins",
                choices=[
                    "All Domain Admins",
                    "Map domain trusts",
                    "Computers with unsupported operating systems",
                    "Locations of high value/Tier Zero objects",
                    "Principals with DCSync privileges",
                    "Users with foreign domain group membership",
                    "Groups with foreign domain group membership",
                    "Computers where Domain Users are local administrators",
                    "Computers where Domain Users can read LAPS passwords",
                    "Paths from Domain Users to high value/Tier Zero targets",
                    "Workstations where Domain Users can RDP",
                    "Servers where Domain Users can RDP",
                    "Dangerous privileges for Domain Users groups",
                    "Domain Admins logons to non-Domain Controllers",
                    "Kerberoastable members of high value/Tier Zero groups",
                    "All Kerberoastable users",
                    "Kerberoastable users with most privileges",
                    "AS-REP Roastable users (DontReqPreAuth)",
                    "Shortest paths to systems trusted for unconstrained delegation",
                    "Shortest paths from Kerberoastable users",
                    "Shortest paths to Domain Admins from Kerberoastable users",
                    "Shortest paths to high value/Tier Zero targets",
                    "Shortest paths from Domain Users to high value/Tier Zero targets",
                    "Shortest paths to Domain Admins",
                    "PKI hierarchy",
                    "Public Key Services container",
                    "Enrollment rights on published certificate templates",
                    "Enrollment rights on published ESC1 certificate templates",
                    "Enrollment rights on published enrollment agent certificate templates",
                    "Enrollment rights on published certificate templates with no security extension",
                    "Enrollment rights on certificate templates published to Enterprise CA with User Specified SAN enabled",
                    "CA administrators and CA managers",
                    "Domain controllers with weak certificate binding enabled",
                    "Domain controllers with UPN certificate mapping enabled"
                ],
                parameter_group_info=[ParameterGroupInfo(
                    required=True
                )]
            )
        ]

    async def parse_arguments(self):
        return self.load_args_from_json_string(self.command_line)

    async def parse_dictionary(self, dictionary_arguments):
        return self.load_args_from_dictionary(dictionary=dictionary_arguments)


predefined_queries = {
    "All Domain Admins": """
MATCH p=(n:Group)<-[:MemberOf*1..]-(m)
WHERE n.objectid ENDS WITH "-512"
RETURN p
    """,
    "Map domain trusts": """
MATCH p=(n:Domain)-[]->(m:Domain)
RETURN p
    """,
    "Computers with unsupported operating systems": """
MATCH (n:Computer)
WHERE n.operatingsystem =~ "(?i).*Windows.* (2000|2003|2008|2012|xp|vista|7|8|me|nt).*"
RETURN n 
    """,
    "Locations of high value/Tier Zero objects": """
MATCH p = (:Domain)-[:Contains*1..]->(n:Base)
WHERE "admin_tier_0" IN split(n.system_tags, ' ')
RETURN p
    """,
    "Principals with DCSync privileges": """
MATCH p=()-[:DCSync|AllExtendedRights|GenericAll]->(:Domain)
RETURN p
    """,
    "Users with foreign domain group membership": """
MATCH p=(n:User)-[:MemberOf]->(m:Group)
WHERE m.domainsid<>n.domainsid
RETURN p
    """,
    "Groups with foreign domain group membership": """
MATCH p=(n:Group)-[:MemberOf]->(m:Group)
WHERE m.domainsid<>n.domainsid AND n.name<>m.name
RETURN p    
    """,
    "Computers where Domain Users are local administrators": """
MATCH p=(m:Group)-[:AdminTo]->(n:Computer)
WHERE m.objectid ENDS WITH "-513"
RETURN p    
    """,
    "Computers where Domain Users can read LAPS passwords": """
MATCH p=(m:Group)-[:AllExtendedRights|ReadLAPSPassword]->(n:Computer)
WHERE m.objectid ENDS WITH "-513"
RETURN p    
    """,
    "Paths from Domain Users to high value/Tier Zero targets": """
MATCH p=shortestPath((m:Group)-[:Owns|GenericAll|GenericWrite|WriteOwner|WriteDacl|MemberOf|ForceChangePassword|AllExtendedRights|AddMember|HasSession|Contains|GPLink|AllowedToDelegate|TrustedBy|AllowedToAct|AdminTo|CanPSRemote|CanRDP|ExecuteDCOM|HasSIDHistory|AddSelf|DCSync|ReadLAPSPassword|ReadGMSAPassword|DumpSMSAPassword|SQLAdmin|AddAllowedToAct|WriteSPN|AddKeyCredentialLink|SyncLAPSPassword|WriteAccountRestrictions|GoldenCert|ADCSESC1|ADCSESC3|ADCSESC4|ADCSESC5|ADCSESC6a|ADCSESC6b|ADCSESC7|ADCSESC9a|ADCSESC9b|ADCSESC10a|ADCSESC10b|DCFor*1..]->(n))
WHERE "admin_tier_0" IN split(n.system_tags, ' ') AND m.objectid ENDS WITH "-513" AND m<>n
RETURN p    
    """,
    "Workstations where Domain Users can RDP": """
MATCH p=(m:Group)-[:CanRDP]->(c:Computer)
WHERE m.objectid ENDS WITH "-513" AND NOT toUpper(c.operatingsystem) CONTAINS "SERVER"
RETURN p    
    """,
    "Servers where Domain Users can RDP": """
MATCH p=(m:Group)-[:CanRDP]->(c:Computer)
WHERE m.objectid ENDS WITH "-513" AND toUpper(c.operatingsystem) CONTAINS "SERVER"
RETURN p    
    """,
    "Dangerous privileges for Domain Users groups": """
MATCH p=(m:Group)-[:Owns|WriteDacl|GenericAll|WriteOwner|ExecuteDCOM|GenericWrite|AllowedToDelegate|ForceChangePassword]->(n:Computer)
WHERE m.objectid ENDS WITH "-513"
RETURN p    
    """,
    "Domain Admins logons to non-Domain Controllers": """
MATCH (dc)-[r:MemberOf*0..]->(g:Group)
WHERE g.objectid ENDS WITH '-516'
WITH COLLECT(dc) AS exclude
MATCH p = (c:Computer)-[n:HasSession]->(u:User)-[r2:MemberOf*1..]->(g:Group)
WHERE g.objectid ENDS WITH '-512' AND NOT c IN exclude
RETURN p   
    """,
    "Kerberoastable members of high value/Tier Zero groups": """
MATCH p=shortestPath((n:User)-[:MemberOf]->(g:Group))
WHERE "admin_tier_0" IN split(g.system_tags, ' ') AND n.hasspn=true
RETURN p    
    """,
    "All Kerberoastable users": """
MATCH (n:User)
WHERE n.hasspn=true
RETURN n    
    """,
    "Kerberoastable users with most privileges": """
MATCH (u:User {hasspn:true})
OPTIONAL MATCH (u)-[:AdminTo]->(c1:Computer)
OPTIONAL MATCH (u)-[:MemberOf*1..]->(:Group)-[:AdminTo]->(c2:Computer)
WITH u,COLLECT(c1) + COLLECT(c2) AS tempVar
UNWIND tempVar AS comps
RETURN u    
    """,
    "AS-REP Roastable users (DontReqPreAuth)": """
MATCH (u:User)
WHERE u.dontreqpreauth = true
RETURN u    
    """,
    "Shortest paths to systems trusted for unconstrained delegation": """
MATCH p=shortestPath((n)-[:Owns|GenericAll|GenericWrite|WriteOwner|WriteDacl|MemberOf|ForceChangePassword|AllExtendedRights|AddMember|HasSession|Contains|GPLink|AllowedToDelegate|TrustedBy|AllowedToAct|AdminTo|CanPSRemote|CanRDP|ExecuteDCOM|HasSIDHistory|AddSelf|DCSync|ReadLAPSPassword|ReadGMSAPassword|DumpSMSAPassword|SQLAdmin|AddAllowedToAct|WriteSPN|AddKeyCredentialLink|SyncLAPSPassword|WriteAccountRestrictions|GoldenCert|ADCSESC1|ADCSESC3|ADCSESC4|ADCSESC5|ADCSESC6a|ADCSESC6b|ADCSESC7|ADCSESC9a|ADCSESC9b|ADCSESC10a|ADCSESC10b|DCFor*1..]->(m:Computer))
WHERE m.unconstraineddelegation = true AND n<>m
RETURN p    
    """,
    "Shortest paths from Kerberoastable users": """
MATCH p=shortestPath((n:User)-[:Owns|GenericAll|GenericWrite|WriteOwner|WriteDacl|MemberOf|ForceChangePassword|AllExtendedRights|AddMember|HasSession|Contains|GPLink|AllowedToDelegate|TrustedBy|AllowedToAct|AdminTo|CanPSRemote|CanRDP|ExecuteDCOM|HasSIDHistory|AddSelf|DCSync|ReadLAPSPassword|ReadGMSAPassword|DumpSMSAPassword|SQLAdmin|AddAllowedToAct|WriteSPN|AddKeyCredentialLink|SyncLAPSPassword|WriteAccountRestrictions|GoldenCert|ADCSESC1|ADCSESC3|ADCSESC4|ADCSESC5|ADCSESC6a|ADCSESC6b|ADCSESC7|ADCSESC9a|ADCSESC9b|ADCSESC10a|ADCSESC10b|DCFor*1..]->(m:Computer))
WHERE n.hasspn = true AND n<>m
RETURN p    
    """,
    "Shortest paths to Domain Admins from Kerberoastable users": """
MATCH p=shortestPath((n:User)-[:Owns|GenericAll|GenericWrite|WriteOwner|WriteDacl|MemberOf|ForceChangePassword|AllExtendedRights|AddMember|HasSession|Contains|GPLink|AllowedToDelegate|TrustedBy|AllowedToAct|AdminTo|CanPSRemote|CanRDP|ExecuteDCOM|HasSIDHistory|AddSelf|DCSync|ReadLAPSPassword|ReadGMSAPassword|DumpSMSAPassword|SQLAdmin|AddAllowedToAct|WriteSPN|AddKeyCredentialLink|SyncLAPSPassword|WriteAccountRestrictions|GoldenCert|ADCSESC1|ADCSESC3|ADCSESC4|ADCSESC5|ADCSESC6a|ADCSESC6b|ADCSESC7|ADCSESC9a|ADCSESC9b|ADCSESC10a|ADCSESC10b|DCFor*1..]->(m:Group))
WHERE n.hasspn = true AND m.objectid ENDS WITH "-512"
RETURN p    
    """,
    "Shortest paths to high value/Tier Zero targets": """
MATCH p=shortestPath((n)-[:Owns|GenericAll|GenericWrite|WriteOwner|WriteDacl|MemberOf|ForceChangePassword|AllExtendedRights|AddMember|HasSession|Contains|GPLink|AllowedToDelegate|TrustedBy|AllowedToAct|AdminTo|CanPSRemote|CanRDP|ExecuteDCOM|HasSIDHistory|AddSelf|DCSync|ReadLAPSPassword|ReadGMSAPassword|DumpSMSAPassword|SQLAdmin|AddAllowedToAct|WriteSPN|AddKeyCredentialLink|SyncLAPSPassword|WriteAccountRestrictions|GoldenCert|ADCSESC1|ADCSESC3|ADCSESC4|ADCSESC5|ADCSESC6a|ADCSESC6b|ADCSESC7|ADCSESC9a|ADCSESC9b|ADCSESC10a|ADCSESC10b|DCFor*1..]->(m))
WHERE "admin_tier_0" IN split(m.system_tags, ' ') AND n<>m
RETURN p    
    """,
    "Shortest paths from Domain Users to high value/Tier Zero targets": """
MATCH p=shortestPath((n:Group)-[:Owns|GenericAll|GenericWrite|WriteOwner|WriteDacl|MemberOf|ForceChangePassword|AllExtendedRights|AddMember|HasSession|Contains|GPLink|AllowedToDelegate|TrustedBy|AllowedToAct|AdminTo|CanPSRemote|CanRDP|ExecuteDCOM|HasSIDHistory|AddSelf|DCSync|ReadLAPSPassword|ReadGMSAPassword|DumpSMSAPassword|SQLAdmin|AddAllowedToAct|WriteSPN|AddKeyCredentialLink|SyncLAPSPassword|WriteAccountRestrictions|GoldenCert|ADCSESC1|ADCSESC3|ADCSESC4|ADCSESC5|ADCSESC6a|ADCSESC6b|ADCSESC7|ADCSESC9a|ADCSESC9b|ADCSESC10a|ADCSESC10b|DCFor*1..]->(m))
WHERE "admin_tier_0" IN split(m.system_tags, ' ') AND n.objectid ENDS WITH "-513" AND n<>m
RETURN p    
    """,
    "Shortest paths to Domain Admins": """
MATCH p=shortestPath((n)-[:Owns|GenericAll|GenericWrite|WriteOwner|WriteDacl|MemberOf|ForceChangePassword|AllExtendedRights|AddMember|HasSession|Contains|GPLink|AllowedToDelegate|TrustedBy|AllowedToAct|AdminTo|CanPSRemote|CanRDP|ExecuteDCOM|HasSIDHistory|AddSelf|DCSync|ReadLAPSPassword|ReadGMSAPassword|DumpSMSAPassword|SQLAdmin|AddAllowedToAct|WriteSPN|AddKeyCredentialLink|SyncLAPSPassword|WriteAccountRestrictions|GoldenCert|ADCSESC1|ADCSESC3|ADCSESC4|ADCSESC5|ADCSESC6a|ADCSESC6b|ADCSESC7|ADCSESC9a|ADCSESC9b|ADCSESC10a|ADCSESC10b|DCFor*1..]->(g:Group))
WHERE g.objectid ENDS WITH "-512" AND n<>g
RETURN p    
    """,
    "PKI hierarchy": """
MATCH p=()-[:HostsCAService|IssuedSignedBy|EnterpriseCAFor|RootCAFor|TrustedForNTAuth|NTAuthStoreFor*..]->()
RETURN p    
    """,
    "Public Key Services container": """
MATCH p = (c:Container)-[:Contains*..]->()
WHERE c.distinguishedname starts with "CN=PUBLIC KEY SERVICES,CN=SERVICES,CN=CONFIGURATION,DC="
RETURN p    
    """,
    "Enrollment rights on published certificate templates": """
MATCH p = ()-[:Enroll|GenericAll|AllExtendedRights]->(ct:CertTemplate)-[:PublishedTo]->(:EnterpriseCA)
RETURN p    
    """,
    "Enrollment rights on published ESC1 certificate templates": """
MATCH p = ()-[:Enroll|GenericAll|AllExtendedRights]->(ct:CertTemplate)-[:PublishedTo]->(:EnterpriseCA)
WHERE ct.enrolleesuppliessubject = True
AND ct.authenticationenabled = True
AND ct.requiresmanagerapproval = False
RETURN p    
    """,
    "Enrollment rights on published enrollment agent certificate templates": """
MATCH p = ()-[:Enroll|GenericAll|AllExtendedRights]->(ct:CertTemplate)-[:PublishedTo]->(:EnterpriseCA)
WHERE ct.effectiveekus CONTAINS "1.3.6.1.4.1.311.20.2.1"
OR ct.effectiveekus CONTAINS "2.5.29.37.0"
OR SIZE(ct.effectiveekus) = 0
RETURN p    
    """,
    "Enrollment rights on published certificate templates with no security extension": """
MATCH p = ()-[:Enroll|GenericAll|AllExtendedRights]->(ct:CertTemplate)-[:PublishedTo]->(:EnterpriseCA)
WHERE ct.nosecurityextension = true
RETURN p    
    """,
    "Enrollment rights on certificate templates published to Enterprise CA with User Specified SAN enabled": """
MATCH p = ()-[:Enroll|GenericAll|AllExtendedRights]->(ct:CertTemplate)-[:PublishedTo]->(eca:EnterpriseCA)
WHERE eca.isuserspecifiessanenabled = True
RETURN p    
    """,
    "CA administrators and CA managers": """
MATCH p = ()-[:ManageCertificates|ManageCA]->(:EnterpriseCA)
RETURN p    
    """,
    "Domain controllers with weak certificate binding enabled": """
MATCH p = (dc:Computer)-[:DCFor]->(d)
WHERE dc.strongcertificatebindingenforcementraw = 0 OR dc.strongcertificatebindingenforcementraw = 1
RETURN p    
    """,
    "Domain controllers with UPN certificate mapping enabled": """
MATCH p = (dc:Computer)-[:DCFor]->(d)
WHERE dc.certificatemappingmethodsraw IN [4, 5, 6, 7, 12, 13, 14, 15, 20, 21, 22, 23, 28, 29, 30, 31]
RETURN p    
    """
}


class CypherPredefined(CommandBase):
    cmd = "cypher_predefined"
    needs_admin = False
    help_cmd = cmd
    description = "Run one of Bloodhound's predefined queries"
    version = 1
    author = "@its_a_feature_"
    argument_class = CypherPredefinedArguments
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
        uri = f"/api/v2/graphs/cypher"
        body = json.dumps({
            "include_properties": True,
            "query": predefined_queries[taskData.args.get_arg("query_name")]
        }).encode()
        response.Stdout = predefined_queries[taskData.args.get_arg("query_name")]
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
