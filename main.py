from flask import Flask, request, jsonify
import boto3
from datetime import datetime, timedelta

app = Flask(__name__)
sessions = {}

# Authentication Endpoint
@app.route('/api/v1/auth/login', methods=['POST'])
def login():
    data = request.json
    aws_access_key = data.get("aws_access_key_id")
    aws_secret_key = data.get("aws_secret_access_key")
    aws_region = data.get("aws_region", "us-west-2")
    
    if not aws_access_key or not aws_secret_key:
        return jsonify({"error": "Missing AWS credentials"}), 400
    
    session_id = f"session_{len(sessions) + 1}"
    sessions[session_id] = {
        "aws_access_key": aws_access_key,
        "aws_secret_key": aws_secret_key,
        "aws_region": aws_region,
        "expires_at": datetime.utcnow() + timedelta(hours=1)
    }
    
    return jsonify({"session_id": session_id, "expires_at": sessions[session_id]["expires_at"].isoformat()})

# ECS Monitoring: List Clusters
@app.route('/api/v1/ecs/clusters', methods=['GET'])
def list_ecs_clusters():
    session_id = request.headers.get("Authorization")
    if session_id not in sessions:
        return jsonify({"error": "Unauthorized"}), 401

    session_data = sessions[session_id]
    ecs_client = boto3.client('ecs',
                              aws_access_key_id=session_data['aws_access_key'],
                              aws_secret_access_key=session_data['aws_secret_key'],
                              region_name=session_data['aws_region'])

    clusters = ecs_client.list_clusters()["clusterArns"]
    print("✅ Raw clusters:", clusters)  # <-- Print to debug

    cluster_details = []
    for cluster in clusters:
        try:
            info = ecs_client.describe_clusters(clusters=[cluster])['clusters'][0]
            cluster_details.append({
                "cluster_name": info['clusterName'],
                "cluster_arn": info['clusterArn'],
                "status": info['status'],
                "registered_container_instances_count": info['registeredContainerInstancesCount'],
                "running_tasks_count": info['runningTasksCount'],
                "pending_tasks_count": info['pendingTasksCount']
            })
        except Exception as e:
            print(f"❌ Failed to describe cluster {cluster}: {e}")

    return jsonify({"clusters": cluster_details})

# ECS Monitoring: List Services in a Cluster
@app.route('/api/v1/ecs/clusters/<cluster_name>/services', methods=['GET'])
def list_ecs_services(cluster_name):
    try:
        # Read credentials from request headers or query params
        aws_access_key = request.headers.get('aws_access_key_id')
        aws_secret_key = request.headers.get('aws_secret_access_key')
        aws_region = request.headers.get('aws_region')

        if not aws_access_key or not aws_secret_key or not aws_region:
            return jsonify({"error": "Missing AWS credentials"}), 400

        print("AWS Region:", aws_region)
        print("Cluster Name from URL:", cluster_name)

        ecs_client = boto3.client(
            'ecs',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=aws_region
        )

        # Validate cluster exists
        clusters = ecs_client.list_clusters()["clusterArns"]
        print("Found clusters:", clusters)

        full_cluster_arn = f"arn:aws:ecs:{aws_region}:{boto3.client('sts').get_caller_identity()['Account']}:cluster/{cluster_name}"
        if full_cluster_arn not in clusters:
            return jsonify({"error": f"Cluster '{cluster_name}' not found."}), 404

        # Get services
        services = ecs_client.list_services(cluster=cluster_name)["serviceArns"]
        service_details = []
        for service in services:
            info = ecs_client.describe_services(cluster=cluster_name, services=[service])["services"][0]
            service_details.append({
                "service_name": info["serviceName"],
                "status": info["status"],
                "desired_count": info["desiredCount"],
                "running_count": info["runningCount"]
            })

        return jsonify({"services": service_details})

    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": str(e)}), 500


# S3 Monitoring: List Buckets
@app.route('/api/v1/s3/buckets', methods=['GET'])
def list_s3_buckets():
    
    session_id = request.headers.get("Authorization")
    if session_id not in sessions:
        return jsonify({"error": "Unauthorized"}), 401
    
    session_data = sessions[session_id]
    s3_client = boto3.client('s3', aws_access_key_id=session_data['aws_access_key'],
                             aws_secret_access_key=session_data['aws_secret_key'],
                             region_name=session_data['aws_region'])
    
    buckets = s3_client.list_buckets()["Buckets"]
    bucket_list = [{"name": bucket["Name"], "creation_date": bucket["CreationDate"].isoformat()} for bucket in buckets]
    
    return jsonify({"buckets": bucket_list})

# EBS Monitoring: List Volumes
@app.route('/api/v1/ebs/volumes', methods=['GET'])
def list_ebs_volumes():
    session_id = request.headers.get("Authorization")
    if session_id not in sessions:
        return jsonify({"error": "Unauthorized"}), 401
    
    session_data = sessions[session_id]
    ec2_client = boto3.client('ec2', aws_access_key_id=session_data['aws_access_key'],
                              aws_secret_access_key=session_data['aws_secret_key'],
                              region_name=session_data['aws_region'])
    
    volumes = ec2_client.describe_volumes()["Volumes"]
    volume_list = []
    for volume in volumes:
        volume_list.append({
            "volume_id": volume['VolumeId'],
            "size": volume['Size'],
            "volume_type": volume['VolumeType'],
            "state": volume['State'],
            "iops": volume.get('Iops', 0),
            "throughput": volume.get('Throughput', 0),
            "attached_instance": volume['Attachments'][0]['InstanceId'] if volume['Attachments'] else None,
            "device": volume['Attachments'][0]['Device'] if volume['Attachments'] else None,
            "availability_zone": volume['AvailabilityZone'],
            "encrypted": volume['Encrypted']
        })
    
    return jsonify({"volumes": volume_list})

if __name__ == '__main__':
    app.run(debug=True)
