from mcp.server.fastmcp import FastMCP
import json
import sys
import os
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP(
    "AWS Cloud Management Agent",
    description="A comprehensive AWS cloud management and monitoring agent",
    version="1.0.0"
)

# Global AWS session variable
_aws_session = None
_aws_available = False

# AWS Configuration
def get_aws_session():
    """Get AWS session with proper error handling"""
    global _aws_session, _aws_available
    
    if _aws_session is not None:
        return _aws_session
    
    try:
        import boto3
        # Try to use environment variables or IAM roles
        session = boto3.Session()
        # Test the session
        sts = session.client('sts')
        identity = sts.get_caller_identity()
        logger.info(f"AWS Session established for: {identity.get('Arn')}")
        _aws_session = session
        _aws_available = True
        return session
    except ImportError:
        logger.warning("boto3 not available. AWS tools will be disabled.")
        _aws_available = False
        return None
    except Exception as e:
        logger.warning(f"AWS credentials not available: {e}")
        logger.info("MCP server will start in demo mode without AWS connectivity")
        _aws_available = False
        return None

def check_aws_available():
    """Check if AWS is available"""
    return _aws_available and get_aws_session() is not None

# Health check tool
@mcp.tool()
def health_check() -> Dict[str, Any]:
    """Health check for the MCP server"""
    aws_session = get_aws_session()
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "server": "AWS MCP Server",
        "version": "1.0.0",
        "aws_available": check_aws_available(),
        "aws_session": aws_session is not None,
        "capabilities": [
            "EC2 Management" if check_aws_available() else "EC2 Management (offline)",
            "S3 Management" if check_aws_available() else "S3 Management (offline)",
            "Lambda Management" if check_aws_available() else "Lambda Management (offline)",
            "CloudWatch Monitoring" if check_aws_available() else "CloudWatch Monitoring (offline)",
            "Cost Analysis" if check_aws_available() else "Cost Analysis (offline)",
            "Help System"
        ]
    }

# EC2 Management Tools
@mcp.tool()
def list_ec2_instances(region: str = "us-east-1") -> Dict[str, Any]:
    """List all EC2 instances in a region
    
    Args:
        region: AWS region (default: us-east-1)
    """
    if not check_aws_available():
        return {
            "error": "AWS not available", 
            "message": "AWS credentials not configured or boto3 not installed",
            "demo_data": {
                "region": region,
                "instance_count": 2,
                "instances": [
                    {
                        "instance_id": "i-1234567890abcdef0",
                        "instance_type": "t3.micro",
                        "state": "running",
                        "public_ip": "203.0.113.12",
                        "private_ip": "10.0.1.12",
                        "launch_time": "2024-01-01T12:00:00Z",
                        "tags": {"Name": "demo-web-server", "Environment": "demo"}
                    },
                    {
                        "instance_id": "i-0987654321fedcba0",
                        "instance_type": "t3.small",
                        "state": "stopped",
                        "public_ip": "N/A",
                        "private_ip": "10.0.1.13",
                        "launch_time": "2024-01-01T12:00:00Z",
                        "tags": {"Name": "demo-app-server", "Environment": "demo"}
                    }
                ]
            }
        }
    
    try:
        session = get_aws_session()
        ec2 = session.client('ec2', region_name=region)
        response = ec2.describe_instances()
        
        instances = []
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instance_info = {
                    "instance_id": instance['InstanceId'],
                    "instance_type": instance['InstanceType'],
                    "state": instance['State']['Name'],
                    "public_ip": instance.get('PublicIpAddress', 'N/A'),
                    "private_ip": instance.get('PrivateIpAddress', 'N/A'),
                    "launch_time": instance['LaunchTime'].isoformat(),
                    "availability_zone": instance.get('Placement', {}).get('AvailabilityZone', 'N/A'),
                    "tags": {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
                }
                instances.append(instance_info)
        
        return {
            "region": region,
            "instance_count": len(instances),
            "instances": instances
        }
    except Exception as e:
        return {"error": f"Failed to list EC2 instances: {str(e)}"}

@mcp.tool()
def list_all_ec2_instances() -> Dict[str, Any]:
    """List ALL EC2 instances across all AWS regions"""
    if not check_aws_available():
        return {
            "error": "AWS not available",
            "message": "AWS credentials not configured or boto3 not installed"
        }
    
    try:
        session = get_aws_session()
        ec2_client = session.client('ec2', region_name='us-east-1')
        
        # Get all available regions
        regions_response = ec2_client.describe_regions()
        regions = [region['RegionName'] for region in regions_response['Regions']]
        
        all_instances = []
        region_summary = {}
        
        for region in regions:
            try:
                ec2 = session.client('ec2', region_name=region)
                response = ec2.describe_instances()
                
                region_instances = []
                for reservation in response['Reservations']:
                    for instance in reservation['Instances']:
                        instance_info = {
                            "instance_id": instance['InstanceId'],
                            "name": next((tag['Value'] for tag in instance.get('Tags', []) if tag['Key'] == 'Name'), 'N/A'),
                            "instance_type": instance['InstanceType'],
                            "state": instance['State']['Name'],
                            "public_ip": instance.get('PublicIpAddress', 'N/A'),
                            "private_ip": instance.get('PrivateIpAddress', 'N/A'),
                            "launch_time": instance['LaunchTime'].isoformat(),
                            "availability_zone": instance.get('Placement', {}).get('AvailabilityZone', 'N/A'),
                            "region": region,
                            "tags": {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
                        }
                        region_instances.append(instance_info)
                        all_instances.append(instance_info)
                
                if region_instances:
                    region_summary[region] = {
                        "count": len(region_instances),
                        "states": {}
                    }
                    
                    # Count instances by state
                    for instance in region_instances:
                        state = instance['state']
                        region_summary[region]['states'][state] = region_summary[region]['states'].get(state, 0) + 1
                        
            except Exception as e:
                logger.warning(f"Failed to query region {region}: {str(e)}")
                continue
        
        return {
            "total_instances": len(all_instances),
            "regions_checked": len(regions),
            "region_summary": region_summary,
            "instances": all_instances
        }
        
    except Exception as e:
        return {"error": f"Failed to list all EC2 instances: {str(e)}"}

@mcp.tool()
def get_ec2_instances_by_region() -> Dict[str, Any]:
    """Get a summary of EC2 instances grouped by region"""
    if not check_aws_available():
        return {
            "error": "AWS not available",
            "message": "AWS credentials not configured or boto3 not installed"
        }
    
    try:
        session = get_aws_session()
        ec2_client = session.client('ec2', region_name='us-east-1')
        
        # Get all available regions
        regions_response = ec2_client.describe_regions()
        regions = [region['RegionName'] for region in regions_response['Regions']]
        
        regional_data = {}
        total_instances = 0
        
        for region in regions:
            try:
                ec2 = session.client('ec2', region_name=region)
                response = ec2.describe_instances()
                
                instances = []
                state_counts = {}
                
                for reservation in response['Reservations']:
                    for instance in reservation['Instances']:
                        state = instance['State']['Name']
                        state_counts[state] = state_counts.get(state, 0) + 1
                        
                        # Only include running/stopped instances in details
                        if state in ['running', 'stopped', 'pending', 'stopping']:
                            instance_info = {
                                "instance_id": instance['InstanceId'],
                                "name": next((tag['Value'] for tag in instance.get('Tags', []) if tag['Key'] == 'Name'), 'N/A'),
                                "instance_type": instance['InstanceType'],
                                "state": state,
                                "public_ip": instance.get('PublicIpAddress', 'N/A'),
                                "availability_zone": instance.get('Placement', {}).get('AvailabilityZone', 'N/A')
                            }
                            instances.append(instance_info)
                
                if instances or state_counts:
                    regional_data[region] = {
                        "instance_count": len(instances),
                        "state_summary": state_counts,
                        "instances": instances
                    }
                    total_instances += len(instances)
                    
            except Exception as e:
                logger.warning(f"Failed to query region {region}: {str(e)}")
                continue
        
        return {
            "total_instances_across_all_regions": total_instances,
            "regions_with_instances": len(regional_data),
            "regional_breakdown": regional_data
        }
        
    except Exception as e:
        return {"error": f"Failed to get regional EC2 summary: {str(e)}"}

@mcp.tool()
def get_instance_details(instance_id: str, region: str = None) -> Dict[str, Any]:
    """Get detailed information about a specific EC2 instance
    
    Args:
        instance_id: EC2 instance ID
        region: AWS region (if not provided, will search across regions)
    """
    if not check_aws_available():
        return {
            "error": "AWS not available",
            "message": "AWS credentials not configured or boto3 not installed"
        }
    
    try:
        session = get_aws_session()
        
        # If region is provided, search only in that region
        if region:
            regions_to_search = [region]
        else:
            # Search across all regions
            ec2_client = session.client('ec2', region_name='us-east-1')
            regions_response = ec2_client.describe_regions()
            regions_to_search = [r['RegionName'] for r in regions_response['Regions']]
        
        for search_region in regions_to_search:
            try:
                ec2 = session.client('ec2', region_name=search_region)
                response = ec2.describe_instances(InstanceIds=[instance_id])
                
                for reservation in response['Reservations']:
                    for instance in reservation['Instances']:
                        # Found the instance
                        return {
                            "instance_id": instance['InstanceId'],
                            "name": next((tag['Value'] for tag in instance.get('Tags', []) if tag['Key'] == 'Name'), 'N/A'),
                            "instance_type": instance['InstanceType'],
                            "state": instance['State']['Name'],
                            "public_ip": instance.get('PublicIpAddress', 'N/A'),
                            "private_ip": instance.get('PrivateIpAddress', 'N/A'),
                            "public_dns": instance.get('PublicDnsName', 'N/A'),
                            "private_dns": instance.get('PrivateDnsName', 'N/A'),
                            "launch_time": instance['LaunchTime'].isoformat(),
                            "availability_zone": instance.get('Placement', {}).get('AvailabilityZone', 'N/A'),
                            "region": search_region,
                            "vpc_id": instance.get('VpcId', 'N/A'),
                            "subnet_id": instance.get('SubnetId', 'N/A'),
                            "security_groups": [sg['GroupName'] for sg in instance.get('SecurityGroups', [])],
                            "key_name": instance.get('KeyName', 'N/A'),
                            "tags": {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])},
                            "architecture": instance.get('Architecture', 'N/A'),
                            "platform": instance.get('Platform', 'Linux/UNIX'),
                            "monitoring": instance.get('Monitoring', {}).get('State', 'N/A'),
                            "source_dest_check": instance.get('SourceDestCheck', False)
                        }
                        
            except Exception as e:
                if "InvalidInstanceID.NotFound" in str(e):
                    continue  # Instance not in this region, try next
                else:
                    logger.warning(f"Error searching region {search_region}: {str(e)}")
                    continue
        
        return {"error": f"Instance {instance_id} not found in any region"}
        
    except Exception as e:
        return {"error": f"Failed to get instance details: {str(e)}"}

@mcp.tool()
def start_ec2_instance(instance_id: str, region: str = "us-east-1") -> Dict[str, Any]:
    """Start an EC2 instance
    
    Args:
        instance_id: EC2 instance ID
        region: AWS region (default: us-east-1)
    """
    if not check_aws_available():
        return {
            "error": "AWS not available",
            "message": "This is a demo response",
            "demo_result": {
                "instance_id": instance_id,
                "action": "start",
                "current_state": "pending",
                "previous_state": "stopped"
            }
        }
    
    try:
        session = get_aws_session()
        ec2 = session.client('ec2', region_name=region)
        response = ec2.start_instances(InstanceIds=[instance_id])
        
        return {
            "instance_id": instance_id,
            "action": "start",
            "current_state": response['StartingInstances'][0]['CurrentState']['Name'],
            "previous_state": response['StartingInstances'][0]['PreviousState']['Name']
        }
    except Exception as e:
        return {"error": f"Failed to start instance {instance_id}: {str(e)}"}

@mcp.tool()
def stop_ec2_instance(instance_id: str, region: str = "us-east-1") -> Dict[str, Any]:
    """Stop an EC2 instance
    
    Args:
        instance_id: EC2 instance ID
        region: AWS region (default: us-east-1)
    """
    if not check_aws_available():
        return {
            "error": "AWS not available",
            "message": "This is a demo response",
            "demo_result": {
                "instance_id": instance_id,
                "action": "stop",
                "current_state": "stopping",
                "previous_state": "running"
            }
        }
    
    try:
        session = get_aws_session()
        ec2 = session.client('ec2', region_name=region)
        response = ec2.stop_instances(InstanceIds=[instance_id])
        
        return {
            "instance_id": instance_id,
            "action": "stop",
            "current_state": response['StoppingInstances'][0]['CurrentState']['Name'],
            "previous_state": response['StoppingInstances'][0]['PreviousState']['Name']
        }
    except Exception as e:
        return {"error": f"Failed to stop instance {instance_id}: {str(e)}"}

# S3 Management Tools
@mcp.tool()
def list_s3_buckets() -> Dict[str, Any]:
    """List all S3 buckets"""
    if not check_aws_available():
        return {
            "error": "AWS not available",
            "message": "This is demo data",
            "demo_data": {
                "bucket_count": 3,
                "buckets": [
                    {
                        "name": "demo-data-bucket-12345",
                        "creation_date": "2024-01-01T12:00:00Z",
                        "region": "us-east-1"
                    },
                    {
                        "name": "demo-logs-bucket-12345",
                        "creation_date": "2024-01-01T12:01:00Z", 
                        "region": "us-east-1"
                    },
                    {
                        "name": "demo-backups-bucket-12345",
                        "creation_date": "2024-01-01T12:02:00Z",
                        "region": "us-west-2"
                    }
                ]
            }
        }
    
    try:
        session = get_aws_session()
        s3 = session.client('s3')
        response = s3.list_buckets()
        
        buckets = []
        for bucket in response['Buckets']:
            # Get bucket region
            try:
                location = s3.get_bucket_location(Bucket=bucket['Name'])
                region = location['LocationConstraint'] or 'us-east-1'
            except:
                region = 'unknown'
            
            bucket_info = {
                "name": bucket['Name'],
                "creation_date": bucket['CreationDate'].isoformat(),
                "region": region
            }
            buckets.append(bucket_info)
        
        return {
            "bucket_count": len(buckets),
            "buckets": buckets
        }
    except Exception as e:
        return {"error": f"Failed to list S3 buckets: {str(e)}"}

@mcp.tool()
def get_s3_bucket_objects(bucket_name: str, prefix: str = "", max_keys: int = 10) -> Dict[str, Any]:
    """List objects in an S3 bucket
    
    Args:
        bucket_name: S3 bucket name
        prefix: Object key prefix filter
        max_keys: Maximum number of objects to return
    """
    try:
        session = get_aws_session()
        if not session:
            return {"error": "Failed to establish AWS session"}
        
        s3 = session.client('s3')
        kwargs = {
            'Bucket': bucket_name,
            'MaxKeys': max_keys
        }
        if prefix:
            kwargs['Prefix'] = prefix
        
        response = s3.list_objects_v2(**kwargs)
        
        objects = []
        if 'Contents' in response:
            for obj in response['Contents']:
                object_info = {
                    "key": obj['Key'],
                    "size": obj['Size'],
                    "last_modified": obj['LastModified'].isoformat(),
                    "storage_class": obj.get('StorageClass', 'STANDARD')
                }
                objects.append(object_info)
        
        return {
            "bucket": bucket_name,
            "prefix": prefix,
            "object_count": len(objects),
            "objects": objects,
            "is_truncated": response.get('IsTruncated', False)
        }
    except Exception as e:
        return {"error": f"Failed to list objects in bucket {bucket_name}: {str(e)}"}

# CloudWatch Monitoring Tools
@mcp.tool()
def get_cloudwatch_metrics(metric_name: str, namespace: str, region: str = "us-east-1", hours: int = 1) -> Dict[str, Any]:
    """Get CloudWatch metrics
    
    Args:
        metric_name: CloudWatch metric name (e.g., CPUUtilization)
        namespace: AWS namespace (e.g., AWS/EC2)
        region: AWS region
        hours: Number of hours to look back
    """
    try:
        session = get_aws_session()
        if not session:
            return {"error": "Failed to establish AWS session"}
        
        cloudwatch = session.client('cloudwatch', region_name=region)
        
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        response = cloudwatch.get_metric_statistics(
            Namespace=namespace,
            MetricName=metric_name,
            StartTime=start_time,
            EndTime=end_time,
            Period=300,  # 5 minute periods
            Statistics=['Average', 'Maximum']
        )
        
        datapoints = []
        for point in response['Datapoints']:
            datapoints.append({
                "timestamp": point['Timestamp'].isoformat(),
                "average": point.get('Average'),
                "maximum": point.get('Maximum')
            })
        
        # Sort by timestamp
        datapoints.sort(key=lambda x: x['timestamp'])
        
        return {
            "metric_name": metric_name,
            "namespace": namespace,
            "region": region,
            "datapoints": datapoints,
            "period_hours": hours
        }
    except Exception as e:
        return {"error": f"Failed to get CloudWatch metrics: {str(e)}"}

# Lambda Management Tools
@mcp.tool()
def list_lambda_functions(region: str = "us-east-1") -> Dict[str, Any]:
    """List all Lambda functions in a region
    
    Args:
        region: AWS region
    """
    if not check_aws_available():
        return {
            "error": "AWS not available",
            "message": "This is demo data",
            "demo_data": {
                "region": region,
                "function_count": 2,
                "functions": [
                    {
                        "function_name": "demo-mcp-test",
                        "runtime": "python3.9",
                        "memory_size": 128,
                        "timeout": 30,
                        "last_modified": "2024-01-01T12:00:00Z",
                        "code_size": 1024
                    },
                    {
                        "function_name": "demo-data-processor",
                        "runtime": "python3.9",
                        "memory_size": 256,
                        "timeout": 60,
                        "last_modified": "2024-01-01T12:01:00Z",
                        "code_size": 2048
                    }
                ]
            }
        }
    
    try:
        session = get_aws_session()
        lambda_client = session.client('lambda', region_name=region)
        response = lambda_client.list_functions()
        
        functions = []
        for func in response['Functions']:
            function_info = {
                "function_name": func['FunctionName'],
                "runtime": func['Runtime'],
                "memory_size": func['MemorySize'],
                "timeout": func['Timeout'],
                "last_modified": func['LastModified'],
                "code_size": func['CodeSize']
            }
            functions.append(function_info)
        
        return {
            "region": region,
            "function_count": len(functions),
            "functions": functions
        }
    except Exception as e:
        return {"error": f"Failed to list Lambda functions: {str(e)}"}

# Help and Information Tools
@mcp.tool()
def get_aws_help() -> str:
    """Get help information about AWS MCP tools"""
    aws_status = "✅ Connected" if check_aws_available() else "❌ Not Connected (Demo Mode)"
    
    return f"""
🌩️ AWS CLOUD MANAGEMENT HELP GUIDE

📊 CONNECTION STATUS: {aws_status}

🔍 AVAILABLE OPERATIONS:

📊 EC2 MANAGEMENT:
• "List EC2 instances in us-west-2"
• "List all EC2 instances" (across all regions)
• "Get EC2 instances by region" (regional summary)
• "Get instance details i-1234567890abcdef0"
• "Start EC2 instance i-1234567890abcdef0"
• "Stop EC2 instance i-1234567890abcdef0"

🪣 S3 MANAGEMENT:
• "List all S3 buckets"
• "Show objects in bucket my-bucket"
• "List files in bucket my-bucket with prefix logs/"

⚡ LAMBDA MANAGEMENT:
• "List Lambda functions in us-east-1"
• "Invoke function my-lambda with payload {{}}"

🎯 EXAMPLE QUERIES:
• "What EC2 instances are running in us-west-2?"
• "Show me all my EC2 instances across all regions"
• "Start instance i-abc123 and show me the result"
• "List my Lambda functions and their runtimes"
• "Health check"

⚠️ SETUP NOTES:
{"• ✅ AWS credentials configured" if check_aws_available() else "• ❌ AWS credentials not configured - showing demo data"}
• Default region is us-east-1 unless specified
• Some operations require appropriate IAM permissions

🔑 TO CONFIGURE AWS:
1. Install AWS CLI: pip install awscli
2. Configure credentials: aws configure
3. Test connection: aws sts get-caller-identity
4. Restart MCP server
"""

# Resource definitions for configuration and status
@mcp.resource("aws://server/status")
def get_server_status() -> str:
    """Get MCP server status"""
    status = {
        "server": "AWS MCP Server",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "aws_available": check_aws_available(),
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "working_directory": os.getcwd()
    }
    
    if check_aws_available():
        try:
            session = get_aws_session()
            sts = session.client('sts')
            identity = sts.get_caller_identity()
            status["aws_account"] = identity.get('Account')
            status["aws_user"] = identity.get('Arn')
        except:
            pass
    
    return json.dumps(status, indent=2)

if __name__ == "__main__":
    logger.info("Starting AWS Cloud Management MCP Server...")
    
    # Check AWS credentials (but don't fail if not available)
    session = get_aws_session()
    if session:
        logger.info("✅ AWS credentials available - full functionality enabled")
    else:
        logger.warning("⚠️ AWS credentials not available - running in demo mode")
        logger.info("Configure AWS credentials with: aws configure")
    
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
        import traceback
        traceback.print_exc()
        sys.exit(1)