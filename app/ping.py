import json
import platform
import subprocess
from re import compile                as    re_compile

datacenters = {
    'DO': {
        'nyc1': 'speedtest-nyc1.digitalocean.com',
        'nyc2': 'speedtest-nyc2.digitalocean.com',
        'nyc3': 'speedtest-nyc3.digitalocean.com',
        'ams2': 'speedtest-ams2.digitalocean.com',
        'ams3': 'speedtest-ams3.digitalocean.com',
        'sfo1': 'speedtest-sfo1.digitalocean.com',
        'sfo2': 'speedtest-sfo2.digitalocean.com',
        'sfo3': 'speedtest-sfo3.digitalocean.com',
        'sgp1': 'speedtest-sgp1.digitalocean.com',
        'lon1': 'speedtest-lon1.digitalocean.com',
        'fra1': 'speedtest-fra1.digitalocean.com',
        'tor1': 'speedtest-tor1.digitalocean.com',
        'blr1': 'speedtest-blr1.digitalocean.com',
    },
    'AWS': {
        'eu-north-1': 'ec2.eu-north-1.amazonaws.com',
        'ap-south-1': 'ec2.ap-south-1.amazonaws.com',
        'eu-west-3': 'ec2.eu-west-3.amazonaws.com',
        'eu-west-2': 'ec2.eu-west-2.amazonaws.com',
        'eu-west-1': 'ec2.eu-west-1.amazonaws.com',
        'ap-northeast-3': 'ec2.ap-northeast-3.amazonaws.com',
        'ap-northeast-2': 'ec2.ap-northeast-2.amazonaws.com',
        'ap-northeast-1': 'ec2.ap-northeast-1.amazonaws.com',
        'sa-east-1': 'ec2.sa-east-1.amazonaws.com',
        'ca-central-1': 'ec2.ca-central-1.amazonaws.com',
        'ap-southeast-1': 'ec2.ap-southeast-1.amazonaws.com',
        'ap-southeast-2': 'ec2.ap-southeast-2.amazonaws.com',
        'eu-central-1': 'ec2.eu-central-1.amazonaws.com',
        'us-east-1': 'ec2.us-east-1.amazonaws.com',
        'us-east-2': 'ec2.us-east-2.amazonaws.com',
        'us-west-1': 'ec2.us-west-1.amazonaws.com',
        'us-west-2': 'ec2.us-west-2.amazonaws.com',
    }
}


def ping(host, tries=1):
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, str(tries), host]
    out = subprocess.run(command, capture_output=True, text=True)
    return out.stdout


def ping_servers(datacenter='DO', tries=1, output='ping.json'):
    if datacenter == 'all':
        servers = {f'{dc}-{region}': dict(host=host) for dc, region_hosts in datacenters.items() for
                   region, host in region_hosts.items()}
    else:
        servers = {f'{datacenter}-{region}': dict(host=host) for region, host in
                   datacenters[datacenter].items()}

    expression = re_compile('(\d+.\d+)/(\d+.\d+)/(\d+.\d+)/(\d+.\d+) ms')

    for key, server in servers.items():
        ping_result = ping(server['host'], tries=tries)
        print(f'{server["host"]}, {ping_result=}')
        ping_ms = float(expression.search(ping_result).group(2))
        server['ping'] = ping_ms

    print("\n\nLowest latency region: ")
    sorted_servers = list(sorted(servers.items(), key=lambda key_server: key_server[1]['ping']))
    for i, (key, server) in enumerate(sorted_servers):
        print(f'{i}) {key}: {server["ping"]} ms')
    with open(output, 'w') as f:
        json.dump(servers, f)

    return sorted_servers
