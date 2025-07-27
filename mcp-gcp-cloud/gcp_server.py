from mcp.server.fastmcp import FastMCP
import json
import sys
import os
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta

# GCP imports
try:
    from google.cloud import compute_v1, storage, functions_v1, monitoring_v3
    from google.cloud import billing_v1, resourcemanager_v3
    from google.oauth2 import service_account
    import google.auth
except ImportError:
    print("Google Cloud libraries not installed. Run: pip install google-cloud-compute google-cloud-storage google-cloud-functions google-cloud-monitoring google-cloud-billing google-cloud-resource-manager")
    sys.exit(1)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP(
    "GCP Cloud Management Agent",
    description="A comprehensive Google Cloud Platform management and monitoring agent",
    version="1.0.0"
)

# GCP Configuration
def get_gcp_credentials():
    """Get GCP credentials and project info"""
    try:
        # Try to get default credentials
        credentials, project_id = google.auth.default()
        logger.info(f"GCP credentials established for project: {project_id}")
        return credentials, project_id
    except Exception as e:
        logger.error(f"Failed to establish GCP credentials: {e}")
        return None, None

# Compute Engine Management Tools
@mcp.tool()
def list_compute_instances(project_id: str = "", zone: str = "us-central1-a") -> Dict[str, Any]:
    """List all Compute Engine instances in a zone
    
    Args:
        project_id: GCP project ID (uses default if empty)
        zone: GCP zone (default: us-central1-a)
    """
    try:
        credentials, default_project = get_gcp_credentials()
        if not credentials:
            return {"error": "Failed to establish GCP credentials"}
        
        project = project_id or default_project
        if not project:
            return {"error": "No project ID specified and no default project found"}
        
        instances_client = compute_v1.InstancesClient(credentials=credentials)
        request = compute_v1.ListInstancesRequest(
            project=project,
            zone=zone
        )
        
        instances = []
        page_result = instances_client.list(request=request)
        
        for instance in page_result:
            instance_info = {
                "name": instance.name,
                "machine_type": instance.machine_type.split('/')[-1],
                "status": instance.status,
                "zone": zone,
                "creation_timestamp": instance.creation_timestamp,
                "internal_ip": instance.network_interfaces[0].network_i_p if instance.network_interfaces else None,
                "external_ip": instance.network_interfaces[0].access_configs[0].nat_i_p if instance.network_interfaces and instance.network_interfaces[0].access_configs else None,
                "tags": list(instance.tags.items) if instance.tags else [],
                "labels": dict(instance.labels) if instance.labels else {}
            }
            instances.append(instance_info)
        
        return {
            "project": project,
            "zone": zone,
            "instance_count": len(instances),
            "instances": instances
        }
    except Exception as e:
        return {"error": f"Failed to list Compute instances: {str(e)}"}

@mcp.tool()
def start_compute_instance(instance_name: str, project_id: str = "", zone: str = "us-central1-a") -> Dict[str, Any]:
    """Start a Compute Engine instance
    
    Args:
        instance_name: Instance name
        project_id: GCP project ID
        zone: GCP zone
    """
    try:
        credentials, default_project = get_gcp_credentials()
        if not credentials:
            return {"error": "Failed to establish GCP credentials"}
        
        project = project_id or default_project
        
        instances_client = compute_v1.InstancesClient(credentials=credentials)
        request = compute_v1.StartInstanceRequest(
            project=project,
            zone=zone,
            instance=instance_name
        )
        
        operation = instances_client.start(request=request)
        
        return {
            "instance_name": instance_name,
            "project": project,
            "zone": zone,
            "action": "start",
            "operation_id": operation.name,
            "status": "starting"
        }
    except Exception as e:
        return {"error": f"Failed to start instance {instance_name}: {str(e)}"}

@mcp.tool()
def stop_compute_instance(instance_name: str, project_id: str = "", zone: str = "us-central1-a") -> Dict[str, Any]:
    """Stop a Compute Engine instance
    
    Args:
        instance_name: Instance name
        project_id: GCP project ID
        zone: GCP zone
    """
    try:
        credentials, default_project = get_gcp_credentials()
        if not credentials:
            return {"error": "Failed to establish GCP credentials"}
        
        project = project_id or default_project
        
        instances_client = compute_v1.InstancesClient(credentials=credentials)
        request = compute_v1.StopInstanceRequest(
            project=project,
            zone=zone,
            instance=instance_name
        )
        
        operation = instances_client.stop(request=request)
        
        return {
            "instance_name": instance_name,
            "project": project,
            "zone": zone,
            "action": "stop",
            "operation_id": operation.name,
            "status": "stopping"
        }
    except Exception as e:
        return {"error": f"Failed to stop instance {instance_name}: {str(e)}"}

# Cloud Storage Management Tools
@mcp.tool()
def list_storage_buckets(project_id: str = "") -> Dict[str, Any]:
    """List all Cloud Storage buckets
    
    Args:
        project_id: GCP project ID
    """
    try:
        credentials, default_project = get_gcp_credentials()
        if not credentials:
            return {"error": "Failed to establish GCP credentials"}
        
        project = project_id or default_project
        
        storage_client = storage.Client(credentials=credentials, project=project)
        buckets = storage_client.list_buckets()
        
        bucket_list = []
        for bucket in buckets:
            bucket_info = {
                "name": bucket.name,
                "location": bucket.location,
                "storage_class": bucket.storage_class,
                "creation_time": bucket.time_created.isoformat() if bucket.time_created else None,
                "updated_time": bucket.updated.isoformat() if bucket.updated else None,
                "versioning_enabled": bucket.versioning_enabled,
                "labels": dict(bucket.labels) if bucket.labels else {}
            }
            bucket_list.append(bucket_info)
        
        return {
            "project": project,
            "bucket_count": len(bucket_list),
            "buckets": bucket_list
        }
    except Exception as e:
        return {"error": f"Failed to list Storage buckets: {str(e)}"}

@mcp.tool()
def get_storage_bucket_objects(bucket_name: str, prefix: str = "", max_results: int = 10) -> Dict[str, Any]:
    """List objects in a Cloud Storage bucket
    
    Args:
        bucket_name: Bucket name
        prefix: Object name prefix filter
        max_results: Maximum number of objects to return
    """
    try:
        credentials, _ = get_gcp_credentials()
        if not credentials:
            return {"error": "Failed to establish GCP credentials"}
        
        storage_client = storage.Client(credentials=credentials)
        bucket = storage_client.bucket(bucket_name)
        
        blobs = bucket.list_blobs(prefix=prefix, max_results=max_results)
        
        objects = []
        for blob in blobs:
            object_info = {
                "name": blob.name,
                "size": blob.size,
                "content_type": blob.content_type,
                "updated": blob.updated.isoformat() if blob.updated else None,
                "storage_class": blob.storage_class,
                "generation": blob.generation,
                "etag": blob.etag
            }
            objects.append(object_info)
        
        return {
            "bucket": bucket_name,
            "prefix": prefix,
            "object_count": len(objects),
            "objects": objects
        }
    except Exception as e:
        return {"error": f"Failed to list objects in bucket {bucket_name}: {str(e)}"}

# Cloud Functions Management Tools
@mcp.tool()
def list_cloud_functions(project_id: str = "", location: str = "us-central1") -> Dict[str, Any]:
    """List Cloud Functions
    
    Args:
        project_id: GCP project ID
        location: GCP location
    """
    try:
        credentials, default_project = get_gcp_credentials()
        if not credentials:
            return {"error": "Failed to establish GCP credentials"}
        
        project = project_id or default_project
        
        functions_client = functions_v1.CloudFunctionsServiceClient(credentials=credentials)
        parent = f"projects/{project}/locations/{location}"
        
        functions = functions_client.list_functions(parent=parent)
        
        function_list = []
        for function in functions:
            function_info = {
                "name": function.name.split('/')[-1],
                "runtime": function.runtime,
                "entry_point": function.entry_point,
                "memory": function.available_memory_mb,
                "timeout": function.timeout.total_seconds() if function.timeout else None,
                "status": function.status.name,
                "update_time": function.update_time.isoformat() if function.update_time else None,
                "labels": dict(function.labels) if function.labels else {}
            }
            function_list.append(function_info)
        
        return {
            "project": project,
            "location": location,
            "function_count": len(function_list),
            "functions": function_list
        }
    except Exception as e:
        return {"error": f"Failed to list Cloud Functions: {str(e)}"}

@mcp.tool()
def invoke_cloud_function(function_name: str, project_id: str = "", location: str = "us-central1", data: str = "{}") -> Dict[str, Any]:
    """Invoke a Cloud Function
    
    Args:
        function_name: Function name
        project_id: GCP project ID
        location: GCP location
        data: JSON data to send to the function
    """
    try:
        credentials, default_project = get_gcp_credentials()
        if not credentials:
            return {"error": "Failed to establish GCP credentials"}
        
        project = project_id or default_project
        
        functions_client = functions_v1.CloudFunctionsServiceClient(credentials=credentials)
        name = f"projects/{project}/locations/{location}/functions/{function_name}"
        
        request = functions_v1.CallFunctionRequest(
            name=name,
            data=data
        )
        
        response = functions_client.call_function(request=request)
        
        return {
            "function_name": function_name,
            "project": project,
            "location": location,
            "result": response.result,
            "error": response.error if hasattr(response, 'error') else None,
            "execution_id": response.execution_id if hasattr(response, 'execution_id') else None
        }
    except Exception as e:
        return {"error": f"Failed to invoke function {function_name}: {str(e)}"}

# Cloud Monitoring Tools
@mcp.tool()
def get_monitoring_metrics(metric_type: str, project_id: str = "", hours: int = 1) -> Dict[str, Any]:
    """Get Cloud Monitoring metrics
    
    Args:
        metric_type: Metric type (e.g., compute.googleapis.com/instance/cpu/utilization)
        project_id: GCP project ID
        hours: Number of hours to look back
    """
    try:
        credentials, default_project = get_gcp_credentials()
        if not credentials:
            return {"error": "Failed to establish GCP credentials"}
        
        project = project_id or default_project
        
        monitoring_client = monitoring_v3.MetricServiceClient(credentials=credentials)
        project_name = f"projects/{project}"
        
        # Create time interval
        now = datetime.utcnow()
        interval = monitoring_v3.TimeInterval({
            "end_time": {"seconds": int(now.timestamp())},
            "start_time": {"seconds": int((now - timedelta(hours=hours)).timestamp())}
        })
        
        # Create the request
        request = monitoring_v3.ListTimeSeriesRequest({
            "name": project_name,
            "filter": f'metric.type="{metric_type}"',
            "interval": interval,
            "view": monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL
        })
        
        # Get the time series data
        time_series = monitoring_client.list_time_series(request=request)
        
        metrics_data = []
        for ts in time_series:
            for point in ts.points:
                point_data = {
                    "timestamp": point.interval.end_time.isoformat(),
                    "value": point.value.double_value or point.value.int64_value,
                    "resource": dict(ts.resource.labels) if ts.resource.labels else {},
                    "metric_labels": dict(ts.metric.labels) if ts.metric.labels else {}
                }
                metrics_data.append(point_data)
        
        return {
            "project": project,
            "metric_type": metric_type,
            "period_hours": hours,
            "data_points": len(metrics_data),
            "metrics": metrics_data
        }
    except Exception as e:
        return {"error": f"Failed to get monitoring metrics: {str(e)}"}

# Billing and Cost Tools
@mcp.tool()
def get_gcp_billing_info(project_id: str = "", days: int = 30) -> Dict[str, Any]:
    """Get GCP billing and cost information
    
    Args:
        project_id: GCP project ID
        days: Number of days to look back
    """
    try:
        credentials, default_project = get_gcp_credentials()
        if not credentials:
            return {"error": "Failed to establish GCP credentials"}
        
        project = project_id or default_project
        
        # Note: This requires billing account access
        # For now, return placeholder data
        return {
            "project": project,
            "period_days": days,
            "message": "Billing data requires Cloud Billing API access and billing account permissions",
            "recommendation": "Use Cloud Console Billing section or configure Cloud Billing API"
        }
    except Exception as e:
        return {"error": f"Failed to get billing info: {str(e)}"}

# Help and Information Tools
@mcp.tool()
def get_gcp_help() -> str:
    """Get help information about GCP MCP tools"""
    return """
☁️ GCP CLOUD MANAGEMENT HELP GUIDE

🔍 AVAILABLE OPERATIONS:

🖥️ COMPUTE ENGINE:
• "List compute instances in us-central1-a"
• "Start instance my-vm"
• "Stop instance my-vm"
• "Show instances in us-west1-b"

🪣 CLOUD STORAGE:
• "List all storage buckets"
• "Show objects in bucket my-bucket"
• "List files in bucket my-bucket with prefix logs/"

⚡ CLOUD FUNCTIONS:
• "List Cloud Functions in us-central1"
• "Invoke function my-function"
• "Show functions in my-project"

📊 CLOUD MONITORING:
• "Get CPU metrics for the last 2 hours"
• "Show memory metrics for compute instances"
• "Monitor disk utilization"

💰 BILLING:
• "Get billing information"
• "Show costs for the last week"

🎯 EXAMPLE QUERIES:
• "What Compute instances are running in us-west1-a?"
• "Start instance web-server-1 in us-central1-a"
• "How many storage buckets do I have?"
• "List my Cloud Functions and their runtimes"
• "Show CPU usage for the last hour"

⚠️ IMPORTANT NOTES:
• Requires GCP credentials (service account or gcloud auth)
• Some operations require appropriate IAM permissions
• Default project is used if not specified
• Default zone is us-central1-a unless specified

🔑 SETUP REQUIREMENTS:
• GCP credentials configured (gcloud CLI or service account)
• Required IAM permissions for each service
• Internet connectivity to GCP APIs

📋 METRIC TYPES FOR MONITORING:
• compute.googleapis.com/instance/cpu/utilization
• compute.googleapis.com/instance/memory/utilization
• storage.googleapis.com/api/request_count
• cloudfunctions.googleapis.com/function/execution_count

🌍 GCP REGIONS:
• us-central1, us-east1, us-west1, us-west2
• europe-west1, europe-west2, europe-west3
• asia-east1, asia-northeast1, asia-southeast1
"""

# Resource definitions
@mcp.resource("gcp://project/info")
def get_project_info() -> str:
    """Get GCP project information"""
    try:
        credentials, project_id = get_gcp_credentials()
        if not credentials or not project_id:
            return "GCP credentials not available"
        
        return json.dumps({
            "project_id": project_id,
            "credentials_type": type(credentials).__name__,
            "scopes": getattr(credentials, 'scopes', 'Not available')
        }, indent=2)
    except Exception as e:
        return f"Failed to get project info: {str(e)}"

@mcp.resource("gcp://zones")
def get_gcp_zones() -> str:
    """Get list of GCP zones"""
    try:
        credentials, project_id = get_gcp_credentials()
        if not credentials:
            return "GCP credentials not available"
        
        zones_client = compute_v1.ZonesClient(credentials=credentials)
        request = compute_v1.ListZonesRequest(project=project_id)
        
        zones = []
        for zone in zones_client.list(request=request):
            zones.append({
                "name": zone.name,
                "region": zone.region.split('/')[-1],
                "status": zone.status
            })
        
        return json.dumps(zones, indent=2)
    except Exception as e:
        return f"Failed to get zones: {str(e)}"

@mcp.resource("gcp://regions")
def get_gcp_regions() -> str:
    """Get list of GCP regions"""
    try:
        credentials, project_id = get_gcp_credentials()
        if not credentials:
            return "GCP credentials not available"
        
        regions_client = compute_v1.RegionsClient(credentials=credentials)
        request = compute_v1.ListRegionsRequest(project=project_id)
        
        regions = []
        for region in regions_client.list(request=request):
            regions.append({
                "name": region.name,
                "status": region.status,
                "zones": [zone.split('/')[-1] for zone in region.zones]
            })
        
        return json.dumps(regions, indent=2)
    except Exception as e:
        return f"Failed to get regions: {str(e)}"

if __name__ == "__main__":
    logger.info("Starting GCP Cloud Management MCP Server...")
    
    # Check GCP credentials
    credentials, project_id = get_gcp_credentials()
    if not credentials:
        logger.error("GCP credentials not configured. Please set up gcloud CLI or service account.")
        logger.error("Run: gcloud auth application-default login")
        sys.exit(1)
    
    logger.info(f"Using GCP project: {project_id}")
    
    # Run the server
    transport = "stdio"
    if len(sys.argv) > 1 and sys.argv[1] == "--http":
        transport = "http"
        logger.info("Server will use HTTP transport on port 8080")
    else:
        logger.info("Server will use STDIO transport for MCP client")
    
    try:
        if transport == "http":
            mcp.run(transport="http", port=8080)
        else:
            mcp.run(transport="stdio")
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        sys.exit(1)
