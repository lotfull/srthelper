import time

# import boto3



def create_instance(
    token: str,
    name: str,
    region: str = 'eu-central-1',
    image: str = 'ubuntu-20-04-x64',
    cpu_type: str = 'c-2',
    ssh_keys=None,
):
    raise NotImplementedError()
    client = boto3.client('ec2', region_name=region)

    response = client.run_instances(
        BlockDeviceMappings=[
            {
                'DeviceName': '/dev/xvda',
                'Ebs': {

                    'DeleteOnTermination': True,
                    'VolumeSize': 8,
                    'VolumeType': 'gp2'
                },
            },
        ],
        ImageId='ami-6cd6f714',
        InstanceType='t3.micro',
        MaxCount=1,
        MinCount=1,
        Monitoring={
            'Enabled': False
        },
        SecurityGroupIds=[
            'sg-1f39854x',
        ],
    )
    #
    # ssh_keys = ssh_keys or digitalocean.Manager(token=token).get_all_sshkeys()
    # droplet = digitalocean.Droplet(token=token,
    #                                name=name,
    #                                region=region,
    #                                image=image,
    #                                size_slug=cpu_type,
    #                                backups=False,
    #                                ssh_keys=ssh_keys)
    # droplet.create()
    # while get_droplet_status(droplet) != "completed":
    #     time.sleep(5)
    # time.sleep(5)
    # droplet.load()
    # return droplet


def shutdown_droplet(token: str, droplet_id: str):
    droplet = digitalocean.Droplet(token=token, id=droplet_id)
    droplet.shutdown()
    while get_droplet_status(droplet) != "completed":
        time.sleep(15)
    droplet.load()
    return droplet


def resize_droplet(token: str, droplet_id: str, cpu_type: str):
    droplet = digitalocean.Droplet(token=token, id=droplet_id)
    droplet.resize(new_size_slug=cpu_type)
    while get_droplet_status(droplet) != "completed":
        time.sleep(20)
    droplet.load()
    return droplet


def turn_on_droplet(token: str, droplet_id: str):
    droplet = digitalocean.Droplet(token=token, id=droplet_id)
    droplet.power_on()
    while get_droplet_status(droplet) != "completed":
        time.sleep(15)
    droplet.load()
    return droplet


def get_droplet_status(droplet):
    actions = droplet.get_actions()
    for action in actions:
        action.load()
        return action.status


def delete_droplet(token: str, droplet_id):
    droplet = digitalocean.Droplet(token=token, id=droplet_id)
    droplet.destroy()


DROPLET_REGIONS = [
    ('FRA1', 'Frankfurt, Germany'),
    ('NYC1', 'New York City, United States'),
    ('SFO2', 'San Francisco, United States'),
    ('AMS3', 'Amsterdam, the Netherlands'),
    ('LON1', 'London, United Kingdom'),
    ('TOR1', 'Toronto, Canada'),
    ('BLR1', 'Bangalore, India'),
    ('SGP1', 'Singapore')
]

DROPLET_CPU_TYPES = [
    ('c-2', '2 dedicated vCPUs'),
    ('c-4', '4 dedicated vCPUs'),
    ('c-8', '8 dedicated vCPUs'),
    ('c-16', '16 dedicated vCPUs'),
    ('c-32', '32 dedicated vCPUs'),
]
