#!/usr/bin/env python3

import boto3
import time
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

# --- Configuration ---
DOMAIN_NAME = 'your-es-domain-name'
REGION = 'your-aws-region'
HOST = 'search-your-es-domain-name-xxxxxx.your-aws-region.es.amazonaws.com' # The domain endpoint

# --- Clients Setup ---
# Use boto3 for AWS service interactions (e.g., node reboot command)
opensearch_client = boto3.client('opensearch', region_name=REGION)
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, REGION, 'es', session_token=credentials.token)

# Use opensearch-py for direct cluster API calls (e.g., health checks)
es_client = OpenSearch(
    hosts=[{'host': HOST, 'port': 443}],
    http_auth=awsauth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)

def check_cluster_health(wait_for_status='yellow', timeout_seconds=300):
    """Waits for the cluster to reach a specific health status."""
    print(f"Waiting for cluster status to be '{wait_for_status}' or better (timeout: {timeout_seconds}s)...")
    try:
        response = es_client.cluster.health(
            wait_for_status=wait_for_status,
            timeout=f"{timeout_seconds}s"
        )
        if response['timed_out']:
            print(f"ERROR: Cluster health check timed out. Current status: {response['status']}")
            return False
        print(f"Cluster status is now '{response['status']}'")
        return True
    except Exception as e:
        print(f"ERROR: Failed to check cluster health: {e}")
        return False

def manage_shard_allocation(enable=True):
    """Enables or disables shard allocation."""
    setting_value = "all" if enable else "primaries" # Disable replicas, keep primaries
    try:
        es_client.cluster.put_settings(
            body={
                "transient": {
                    "cluster.routing.allocation.enable": setting_value
                }
            }
        )
        print(f"Shard allocation set to: {setting_value}")
        return True
    except Exception as e:
        print(f"ERROR: Failed to change shard allocation settings: {e}")
        return False

def restart_node(node_id):
    """Restarts a specific OpenSearch data node process via the AWS API."""
    print(f"Initiating restart for node {node_id} via AWS API...")
    try:
        # Note: AWS API performs a restart of the OpenSearch process, not the instance reboot.
        # Use 'REBOOT_NODE' for a full instance reboot.
        response = opensearch_client.start_domain_maintenance(
            DomainName=DOMAIN_NAME,
            Action='RESTART_SEARCH_PROCESS',
            NodeId=node_id
        )
        print(f"Restart command issued. Request ID: {response['MaintenanceId']}")
    except Exception as e:
        print(f"ERROR: Failed to restart node {node_id} via AWS API: {e}")
        return False
    return True

def get_data_node_ids():
    """Retrieves current data node IDs from the cluster."""
    try:
        response = es_client.cat.nodes(h='id,r', format='json')
        data_nodes = [node['id'] for node in response if 'data' in node['r']]
        return data_nodes
    except Exception as e:
        print(f"ERROR: Failed to retrieve node list: {e}")
        return []

def main():
    print("--- Starting Rolling Restart Process ---")

    # 1. Initial sanity check
    if not check_cluster_health(wait_for_status='green'):
        print("Cluster is unhealthy. Aborting restart.")
        return

    nodes_to_restart = get_data_node_ids()
    if not nodes_to_restart:
        print("No data nodes found. Aborting.")
        return

    print(f"Found data nodes: {nodes_to_restart}")

    for node_id in nodes_to_restart:
        print(f"\n--- Processing Node: {node_id} ---")

        # 2. Disable shard allocation (optional, but safer)
        # manage_shard_allocation(enable=False) # Skip in this simplified example as AWS handles some of this during managed operations

        # 3. Restart the node process
        if not restart_node(node_id):
            print(f"Could not restart node {node_id}. Aborting process.")
            break
        
        # Note: When using AWS managed maintenance APIs, AWS handles the cluster coordination
        # and re-enabling allocation automatically after the node rejoins and is healthy.
        # We just need to wait for the cluster to stabilize before proceeding to the next node.

        # 4. Verify node rejoins and cluster is healthy (yellow status is sufficient to proceed)
        # This will block until the status is yellow or green, ensuring the cluster is stable.
        if not check_cluster_health(wait_for_status='yellow', timeout_seconds=600):
            print(f"Cluster did not return to healthy state after restarting node {node_id}. Intervention required.")
            break
        
        print(f"Node {node_id} successfully rejoined and cluster is stable.")

    print("\n--- Rolling Restart Process Complete ---")
    # Final check for green status after all nodes are done
    check_cluster_health(wait_for_status='green')

if __name__ == "__main__":
    main()
