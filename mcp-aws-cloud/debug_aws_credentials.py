#!/usr/bin/env python3
"""
Debug script to check AWS credentials configuration
Run this to see exactly what's wrong with your setup
"""

import os
import sys
import boto3
from pathlib import Path

def check_environment_variables():
    """Check AWS environment variables"""
    print("🔍 CHECKING ENVIRONMENT VARIABLES")
    print("=" * 40)
    
    env_vars = [
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY', 
        'AWS_SESSION_TOKEN',
        'AWS_DEFAULT_REGION',
        'AWS_PROFILE'
    ]
    
    found_vars = False
    for var in env_vars:
        value = os.environ.get(var)
        if value:
            if 'KEY' in var:
                print(f"✅ {var}: {value[:8]}... (hidden)")
            else:
                print(f"✅ {var}: {value}")
            found_vars = True
        else:
            print(f"❌ {var}: Not set")
    
    if not found_vars:
        print("⚠️  No AWS environment variables found")
    
    return found_vars

def check_credentials_file():
    """Check ~/.aws/credentials file"""
    print("\n🔍 CHECKING CREDENTIALS FILE")
    print("=" * 40)
    
    creds_path = Path.home() / '.aws' / 'credentials'
    config_path = Path.home() / '.aws' / 'config'
    
    if creds_path.exists():
        print(f"✅ Credentials file exists: {creds_path}")
        
        try:
            with open(creds_path, 'r') as f:
                content = f.read()
                if '[default]' in content:
                    print("✅ [default] profile found in credentials")
                    if 'aws_access_key_id' in content:
                        print("✅ aws_access_key_id found")
                    else:
                        print("❌ aws_access_key_id missing")
                    if 'aws_secret_access_key' in content:
                        print("✅ aws_secret_access_key found")
                    else:
                        print("❌ aws_secret_access_key missing")
                else:
                    print("❌ [default] profile not found in credentials")
        except Exception as e:
            print(f"❌ Error reading credentials file: {e}")
    else:
        print(f"❌ Credentials file not found: {creds_path}")
    
    if config_path.exists():
        print(f"✅ Config file exists: {config_path}")
    else:
        print(f"❌ Config file not found: {config_path}")
    
    return creds_path.exists()

def test_boto3_session():
    """Test boto3 session creation"""
    print("\n🔍 TESTING BOTO3 SESSION")
    print("=" * 40)
    
    try:
        # Test default session
        session = boto3.Session()
        print("✅ boto3.Session() created successfully")
        
        # Test getting credentials
        credentials = session.get_credentials()
        if credentials:
            print("✅ Credentials retrieved from session")
            print(f"   Access Key: {credentials.access_key[:8]}... (hidden)")
            if credentials.secret_key:
                print(f"   Secret Key: {credentials.secret_key[:8]}... (hidden)")
        else:
            print("❌ No credentials found in session")
            return False
        
        # Test STS call
        sts = session.client('sts')
        identity = sts.get_caller_identity()
        print("✅ AWS STS call successful")
        print(f"   Account: {identity.get('Account')}")
        print(f"   User ARN: {identity.get('Arn')}")
        
        return True
        
    except Exception as e:
        print(f"❌ boto3 session failed: {e}")
        return False

def test_ec2_connection():
    """Test EC2 connection"""
    print("\n🔍 TESTING EC2 CONNECTION")
    print("=" * 40)
    
    try:
        ec2 = boto3.client('ec2', region_name='us-east-1')
        response = ec2.describe_instances()
        
        instance_count = 0
        for reservation in response['Reservations']:
            instance_count += len(reservation['Instances'])
        
        print(f"✅ EC2 connection successful")
        print(f"   Found {instance_count} instances in us-east-1")
        
        if instance_count > 0:
            print("\n📋 Instance Summary:")
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    name = next((tag['Value'] for tag in instance.get('Tags', []) 
                               if tag['Key'] == 'Name'), 'N/A')
                    print(f"   • {instance['InstanceId']} ({name}) - {instance['State']['Name']}")
        
        return True
        
    except Exception as e:
        print(f"❌ EC2 connection failed: {e}")
        return False

def main():
    print("🌩️  AWS CREDENTIALS DIAGNOSTIC TOOL")
    print("=" * 50)
    print("This tool will help diagnose AWS credential issues\n")
    
    # Check all credential sources
    env_ok = check_environment_variables()
    file_ok = check_credentials_file()
    session_ok = test_boto3_session()
    
    if session_ok:
        ec2_ok = test_ec2_connection()
    
    print("\n" + "=" * 50)
    print("🎯 DIAGNOSTIC SUMMARY")
    print("=" * 50)
    
    if session_ok:
        print("✅ AWS credentials are working correctly!")
        print("   Your MCP server should be able to connect to AWS.")
        print("\n💡 If MCP is still showing demo data:")
        print("   1. Restart your MCP client completely")
        print("   2. Make sure you're using the updated aws_server.py")
        print("   3. Check that boto3 is installed: pip install boto3")
    else:
        print("❌ AWS credentials are not working")
        print("\n🔧 RECOMMENDED FIXES:")
        
        if not env_ok and not file_ok:
            print("   1. Run: aws configure")
            print("   2. Or set environment variables:")
            print("      export AWS_ACCESS_KEY_ID=your_key")
            print("      export AWS_SECRET_ACCESS_KEY=your_secret")
            print("      export AWS_DEFAULT_REGION=us-east-1")
        elif file_ok and not session_ok:
            print("   1. Check permissions on ~/.aws/credentials")
            print("   2. Verify the file format is correct")
            print("   3. Try: aws configure --profile default")

if __name__ == "__main__":
    main()
