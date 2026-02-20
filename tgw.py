import boto3
import argparse
from prettytable import PrettyTable

# ----------------------------------------
# CONFIG - Change these
# ----------------------------------------
TGW_ID = "tgw-xxxxxxxxxxxxxxxxx"  # Your Transit Gateway ID
REGION = "us-east-1"              # Your region
# ----------------------------------------

ec2 = boto3.client("ec2", region_name=REGION)

def get_all_attachments():
    """Get all TGW attachments"""
    attachments = []
    paginator = ec2.get_paginator("describe_transit_gateway_attachments")
    for page in paginator.paginate(
        Filters=[{"Name": "transit-gateway-id", "Values": [TGW_ID]}]
    ):
        attachments.extend(page["TransitGatewayAttachments"])
    return attachments

def get_all_route_tables():
    """Get all TGW route tables"""
    route_tables = []
    paginator = ec2.get_paginator("describe_transit_gateway_route_tables")
    for page in paginator.paginate(
        Filters=[{"Name": "transit-gateway-id", "Values": [TGW_ID]}]
    ):
        route_tables.extend(page["TransitGatewayRouteTables"])
    return route_tables

def get_routes_for_route_table(route_table_id):
    """Get all routes in a specific TGW route table"""
    routes = []
    paginator = ec2.get_paginator("search_transit_gateway_routes")
    for page in paginator.paginate(
        TransitGatewayRouteTableId=route_table_id,
        Filters=[{"Name": "state", "Values": ["active", "blackhole"]}]
    ):
        routes.extend(page["Routes"])
    return routes

def get_route_table_associations(route_table_id):
    """Get attachments associated with a route table"""
    associations = []
    paginator = ec2.get_paginator("get_transit_gateway_route_table_associations")
    for page in paginator.paginate(TransitGatewayRouteTableId=route_table_id):
        associations.extend(page["Associations"])
    return associations

def get_route_table_propagations(route_table_id):
    """Get attachments propagating into a route table"""
    propagations = []
    paginator = ec2.get_paginator("get_transit_gateway_route_table_propagations")
    for page in paginator.paginate(TransitGatewayRouteTableId=route_table_id):
        propagations.extend(page["TransitGatewayRoutePropagations"])
    return propagations

def get_name_tag(tags):
    """Extract Name tag from tag list"""
    if not tags:
        return "N/A"
    for tag in tags:
        if tag["Key"] == "Name":
            return tag["Value"]
    return "N/A"

def search_attachment(search_term):
    """
    Search for a TGW attachment by:
    - VPC ID
    - VPN Connection ID
    - Direct Connect Gateway ID
    - Attachment ID
    - Account ID
    - Name tag
    """
    print(f"\n🔍 Searching for: {search_term}\n")
    attachments = get_all_attachments()
    matched = []

    for att in attachments:
        name = get_name_tag(att.get("Tags", []))
        resource_id = att.get("ResourceId", "")
        att_id = att.get("TransitGatewayAttachmentId", "")
        account_id = att.get("ResourceOwnerId", "")
        att_type = att.get("ResourceType", "")

        if (search_term.lower() in resource_id.lower() or
            search_term.lower() in att_id.lower() or
            search_term.lower() in account_id.lower() or
            search_term.lower() in name.lower()):
            matched.append(att)

    if not matched:
        print("❌ No attachment found matching your search term.")
        return

    for att in matched:
        print_attachment_details(att)

def print_attachment_details(att):
    """Print full details of an attachment and its route table"""
    att_id = att["TransitGatewayAttachmentId"]
    att_type = att["ResourceType"]
    resource_id = att["ResourceId"]
    account_id = att["ResourceOwnerId"]
    state = att["State"]
    name = get_name_tag(att.get("Tags", []))

    print("=" * 70)
    print(f"✅ ATTACHMENT FOUND")
    print("=" * 70)
    print(f"  Name          : {name}")
    print(f"  Attachment ID : {att_id}")
    print(f"  Type          : {att_type}")
    print(f"  Resource ID   : {resource_id}")
    print(f"  Account ID    : {account_id}")
    print(f"  State         : {state}")

    # Find which route table this attachment is ASSOCIATED with
    print(f"\n📋 Finding Route Table Association...")
    route_tables = get_all_route_tables()
    associated_rt = None

    for rt in route_tables:
        rt_id = rt["TransitGatewayRouteTableId"]
        associations = get_route_table_associations(rt_id)
        for assoc in associations:
            if assoc["TransitGatewayAttachmentId"] == att_id:
                associated_rt = rt
                break

    if associated_rt:
        rt_id = associated_rt["TransitGatewayRouteTableId"]
        rt_name = get_name_tag(associated_rt.get("Tags", []))
        print(f"  Associated Route Table : {rt_name} ({rt_id})")

        # Show routes in that route table
        print(f"\n🗺️  Routes in this Route Table:")
        routes = get_routes_for_route_table(rt_id)
        table = PrettyTable()
        table.field_names = ["Prefix", "Type", "State", "Next Hop Attachment", "Next Hop Type"]
        table.align = "l"

        for route in routes:
            prefix = route.get("DestinationCidrBlock", "N/A")
            route_type = route.get("Type", "N/A")
            route_state = route.get("State", "N/A")
            next_hop_att = "N/A"
            next_hop_type = "N/A"

            if "TransitGatewayAttachments" in route:
                for hop in route["TransitGatewayAttachments"]:
                    next_hop_att = hop.get("TransitGatewayAttachmentId", "N/A")
                    next_hop_type = hop.get("ResourceType", "N/A")

            table.add_row([prefix, route_type, route_state, next_hop_att, next_hop_type])

        print(table)

        # Show what is propagating INTO this route table
        print(f"\n📡 Attachments PROPAGATING into this Route Table:")
        propagations = get_route_table_propagations(rt_id)
        prop_table = PrettyTable()
        prop_table.field_names = ["Attachment ID", "Resource Type", "Resource ID", "State"]
        prop_table.align = "l"
        for prop in propagations:
            prop_table.add_row([
                prop.get("TransitGatewayAttachmentId", "N/A"),
                prop.get("ResourceType", "N/A"),
                prop.get("ResourceId", "N/A"),
                prop.get("State", "N/A")
            ])
        print(prop_table)
    else:
        print("  ⚠️  No route table association found for this attachment.")

# ----------------------------------------
# MAIN
# ----------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TGW Route Tracer")
    parser.add_argument("search", help="Search by VPC ID, VPN ID, Attachment ID, Account ID, or Name")
    args = parser.parse_args()
    search_attachment(args.search)
