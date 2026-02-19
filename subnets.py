from flask import Flask, request, render_template_string
import boto3

app = Flask(__name__)

ec2 = boto3.client('ec2')


def get_subnets():
    return ec2.describe_subnets()['Subnets']


def get_subnet(subnet_id):
    return ec2.describe_subnets(SubnetIds=[subnet_id])['Subnets'][0]


HTML = """
<html>
<head>
<title>AWS Subnets</title>
</head>
<body>

<h2>AWS Subnets</h2>

<table border="1">

<tr>
<th>Subnet ID</th>
<th>Name</th>
<th>VPC ID</th>
<th>CIDR</th>
<th>AZ</th>
<th>Available IPs</th>
</tr>

{% for subnet in subnets %}

<tr>

<td>
<a href="/?subnet_id={{ subnet.SubnetId }}">
{{ subnet.SubnetId }}
</a>
</td>

<td>
{% for tag in subnet.get('Tags', []) %}
{% if tag['Key'] == 'Name' %}
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

<h3>Subnet Details</h3>

<table border="1">

<tr><td>Subnet ID</td><td>{{ selected.SubnetId }}</td></tr>
<tr><td>VPC ID</td><td>{{ selected.VpcId }}</td></tr>
<tr><td>CIDR</td><td>{{ selected.CidrBlock }}</td></tr>
<tr><td>Availability Zone</td><td>{{ selected.AvailabilityZone }}</td></tr>
<tr><td>Available IPs</td><td>{{ selected.AvailableIpAddressCount }}</td></tr>
<tr><td>State</td><td>{{ selected.State }}</td></tr>

</table>

<h4>Tags</h4>

<table border="1">

<tr>
<th>Key</th>
<th>Value</th>
</tr>

{% for tag in selected.get('Tags', []) %}

<tr>
<td>{{ tag['Key'] }}</td>
<td>{{ tag['Value'] }}</td>
</tr>

{% endfor %}

</table>

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
    app.run(host="0.0.0.0", port=5000)