from flask import Flask, request, render_template_string
import boto3

app = Flask(__name__)

ec2 = boto3.client('ec2')

# Fetch all subnets
def get_subnets():
    response = ec2.describe_subnets()
    return response['Subnets']

# Fetch specific subnet details
def get_subnet(subnet_id):
    response = ec2.describe_subnets(SubnetIds=[subnet_id])
    return response['Subnets'][0]


HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>AWS Subnets</title>
    <style>
        body {
            font-family: Arial;
            margin: 20px;
        }

        table {
            border-collapse: collapse;
            width: 100%;
        }

        th, td {
            border: 1px solid #ccc;
            padding: 8px;
            text-align: left;
        }

        th {
            background-color: #232f3e;
            color: white;
        }

        tr:hover {
            background-color: #f2f2f2;
            cursor: pointer;
        }

        .details {
            margin-top: 20px;
            padding: 15px;
            border: 1px solid #ccc;
            background: #fafafa;
        }
    </style>
</head>
<body>

<h2>AWS Subnets</h2>

<table>
<tr>
<th>Subnet ID</th>
<th>Name</th>
<th>VPC ID</th>
<th>CIDR</th>
<th>Availability Zone</th>
<th>Available IPs</th>
</tr>

{% for subnet in subnets %}
<tr onclick="window.location='/?subnet_id={{ subnet.SubnetId }}'">
<td>{{ subnet.SubnetId }}</td>
<td>
{% for tag in subnet.get('Tags', []) %}
    {% if tag['Key']=='Name' %}
        {{ tag['Value'] }}
    {% endif %}
{% endfor %}
</td>
<td>{{ subnet.VpcId }}</td>
<td>{{ subnet.CidrBlock }}</td>
<td>{{ subnet.AvailabilityZone }}</td>
<td>{{ subnet.AvailableIpAddressCount }}</td>
</tr>
{% endfor %}
</table>


{% if selected %}
<div class="details">
<h3>Subnet Details</h3>

<b>Subnet ID:</b> {{ selected.SubnetId }} <br>
<b>VPC ID:</b> {{ selected.VpcId }} <br>
<b>CIDR:</b> {{ selected.CidrBlock }} <br>
<b>Availability Zone:</b> {{ selected.AvailabilityZone }} <br>
<b>Available IPs:</b> {{ selected.AvailableIpAddressCount }} <br>
<b>State:</b> {{ selected.State }} <br>
<b>Default for AZ:</b> {{ selected.DefaultForAz }} <br>

<h4>Tags:</h4>
{% for tag in selected.get('Tags', []) %}
{{ tag['Key'] }} : {{ tag['Value'] }} <br>
{% endfor %}

</div>
{% endif %}

</body>
</html>
"""


@app.route("/")
def index():

    subnets = get_subnets()

    subnet_id = request.args.get("subnet_id")

    selected = None

    if subnet_id:
        selected = get_subnet(subnet_id)

    return render_template_string(
        HTML,
        subnets=subnets,
        selected=selected
    )


if __name__ == "__main__":
    app.run(debug=True)