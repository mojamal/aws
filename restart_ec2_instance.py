#!/usr/bin/env python3

import boto3
import sys
from botocore.exceptions import ClientError

def reboot_ec2_instance(instance_ids, region_name):
    """
    Reboots specified EC2 instances and waits for them to be running.

    :param instance_ids: A list of instance IDs to reboot.
    :param region_name: The AWS region where the instances are located.
    """
    client = boto3.client('ec2', region_name=region_name)
    
    try:
        # Request a reboot of the instances
        print(f"Initiating reboot for instance(s): {', '.join(instance_ids)} in {region_name} region.")
        client.reboot_instances(InstanceIds=instance_ids)
        print("Reboot request sent successfully.")

        # Use a waiter to wait until the instance status is 'ok' (running and passed health checks)
        print("Waiting for instance(s) to be running and pass status checks...")
        waiter = client.get_waiter('instance_status_ok')
        waiter.wait(InstanceIds=instance_ids, WaiterConfig={'Delay': 15, 'MaxAttempts': 40})
        print(f"Instance(s) {', '.join(instance_ids)} are now running and healthy.")

    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code")
        if error_code == 'InvalidInstanceID.NotFound':
            print(f"Error: One or more instance IDs are invalid or not found. {e.response['Error']['Message']}")
        elif error_code == 'UnauthorizedOperation':
            print(f"Error: You do not have the required permissions to reboot instances. Check your IAM policies. {e.response['Error']['Message']}")
        else:
            print(f"An AWS client error occurred: {e.response['Error']['Message']}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    # --- Configuration 
