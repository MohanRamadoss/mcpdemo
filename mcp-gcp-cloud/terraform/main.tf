terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

# Variables
variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "GCP Zone"
  type        = string
  default     = "us-central1-a"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "mcp-demo"
}

# Enable required APIs
resource "google_project_service" "required_apis" {
  for_each = toset([
    "compute.googleapis.com",
    "storage.googleapis.com",
    "cloudfunctions.googleapis.com",
    "cloudbuild.googleapis.com",
    "sqladmin.googleapis.com",
    "bigquery.googleapis.com",
    "monitoring.googleapis.com",
    "logging.googleapis.com"
  ])
  
  project = var.project_id
  service = each.value
  
  disable_on_destroy = false
}

# VPC Network
resource "google_compute_network" "mcp_demo_network" {
  name                    = "${var.environment}-network"
  auto_create_subnetworks = false
  
  depends_on = [google_project_service.required_apis]
}

resource "google_compute_subnetwork" "mcp_demo_subnet" {
  name          = "${var.environment}-subnet"
  network       = google_compute_network.mcp_demo_network.id
  ip_cidr_range = "10.0.1.0/24"
  region        = var.region
}

# Firewall Rules
resource "google_compute_firewall" "mcp_demo_allow_ssh" {
  name    = "${var.environment}-allow-ssh"
  network = google_compute_network.mcp_demo_network.name

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["ssh-allowed"]
}

resource "google_compute_firewall" "mcp_demo_allow_http" {
  name    = "${var.environment}-allow-http"
  network = google_compute_network.mcp_demo_network.name

  allow {
    protocol = "tcp"
    ports    = ["80", "443", "8080"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["http-allowed"]
}

resource "google_compute_firewall" "mcp_demo_allow_internal" {
  name    = "${var.environment}-allow-internal"
  network = google_compute_network.mcp_demo_network.name

  allow {
    protocol = "tcp"
    ports    = ["0-65535"]
  }

  allow {
    protocol = "udp"
    ports    = ["0-65535"]
  }

  allow {
    protocol = "icmp"
  }

  source_ranges = ["10.0.0.0/16"]
}

# Compute Engine Instances
resource "google_compute_instance" "mcp_demo_web" {
  count = 2
  
  name         = "${var.environment}-web-server-${count.index + 1}"
  machine_type = "e2-micro"
  zone         = var.zone

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
      size  = 20
    }
  }

  network_interface {
    network    = google_compute_network.mcp_demo_network.id
    subnetwork = google_compute_subnetwork.mcp_demo_subnet.id
    
    access_config {
      // Ephemeral public IP
    }
  }

  metadata_startup_script = <<-EOF
    #!/bin/bash
    apt-get update
    apt-get install -y apache2
    systemctl start apache2
    systemctl enable apache2
    
    cat > /var/www/html/index.html << 'HTML'
    <html>
    <head><title>MCP Demo Web Server ${count.index + 1}</title></head>
    <body>
      <h1>MCP Demo Web Server ${count.index + 1}</h1>
      <p>Instance Name: ${var.environment}-web-server-${count.index + 1}</p>
      <p>Zone: ${var.zone}</p>
      <p>Environment: ${var.environment}</p>
      <p>Server Time: $(date)</p>
    </body>
    </html>
HTML
  EOF

  tags = ["ssh-allowed", "http-allowed"]

  labels = {
    environment = var.environment
    role        = "web-server"
  }

  depends_on = [google_project_service.required_apis]
}

resource "google_compute_instance" "mcp_demo_app" {
  name         = "${var.environment}-app-server"
  machine_type = "e2-small"
  zone         = var.zone

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
      size  = 30
    }
  }

  network_interface {
    network    = google_compute_network.mcp_demo_network.id
    subnetwork = google_compute_subnetwork.mcp_demo_subnet.id
    
    access_config {
      // Ephemeral public IP
    }
  }

  metadata_startup_script = <<-EOF
    #!/bin/bash
    apt-get update
    apt-get install -y python3 python3-pip git
    pip3 install google-cloud-storage google-cloud-functions flask
    
    echo "MCP Application Server Ready" > /home/debian/status.txt
    echo "Environment: ${var.environment}" >> /home/debian/status.txt
    echo "Initialized: $(date)" >> /home/debian/status.txt
  EOF

  tags = ["ssh-allowed", "http-allowed"]

  labels = {
    environment = var.environment
    role        = "app-server"
  }

  service_account {
    email  = google_service_account.mcp_demo_sa.email
    scopes = ["cloud-platform"]
  }

  depends_on = [google_project_service.required_apis]
}

# Service Account for instances
resource "google_service_account" "mcp_demo_sa" {
  account_id   = "${var.environment}-service-account"
  display_name = "MCP Demo Service Account"
  description  = "Service account for MCP demo resources"
}

resource "google_project_iam_member" "mcp_demo_sa_roles" {
  for_each = toset([
    "roles/storage.admin",
    "roles/cloudsql.client",
    "roles/bigquery.user",
    "roles/monitoring.viewer",
    "roles/logging.viewer"
  ])
  
  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.mcp_demo_sa.email}"
}

# Cloud Storage Buckets
resource "google_storage_bucket" "mcp_demo_data" {
  name     = "${var.project_id}-${var.environment}-data-bucket"
  location = var.region

  uniform_bucket_level_access = true
  
  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "Delete"
    }
  }

  labels = {
    environment = var.environment
    purpose     = "data-storage"
  }

  depends_on = [google_project_service.required_apis]
}

resource "google_storage_bucket" "mcp_demo_logs" {
  name     = "${var.project_id}-${var.environment}-logs-bucket"
  location = var.region

  uniform_bucket_level_access = true

  labels = {
    environment = var.environment
    purpose     = "log-storage"
  }

  depends_on = [google_project_service.required_apis]
}

resource "google_storage_bucket" "mcp_demo_functions" {
  name     = "${var.project_id}-${var.environment}-functions-bucket"
  location = var.region

  uniform_bucket_level_access = true

  labels = {
    environment = var.environment
    purpose     = "function-source"
  }

  depends_on = [google_project_service.required_apis]
}

# Sample Storage Objects
resource "google_storage_bucket_object" "sample_config" {
  name   = "config/app-config.json"
  bucket = google_storage_bucket.mcp_demo_data.name
  content = jsonencode({
    application = "mcp-demo"
    environment = var.environment
    region      = var.region
    created_at  = timestamp()
    settings = {
      debug_mode = true
      log_level  = "INFO"
    }
  })
  content_type = "application/json"
}

resource "google_storage_bucket_object" "sample_data" {
  name   = "data/sample.txt"
  bucket = google_storage_bucket.mcp_demo_data.name
  content = "MCP Demo Sample Data\nCreated: ${timestamp()}\nEnvironment: ${var.environment}\n"
}

# Cloud Functions
data "archive_file" "function_source" {
  type        = "zip"
  output_path = "/tmp/function-source.zip"
  source {
    content = <<-EOF
import functions_framework
import json
from datetime import datetime
from google.cloud import storage

@functions_framework.http
def mcp_demo_function(request):
    """
    MCP Demo Cloud Function
    Processes HTTP requests and interacts with Cloud Storage
    """
    
    # Get request data
    request_json = request.get_json(silent=True)
    request_args = request.args
    
    # Prepare response
    response_data = {
        'function_name': 'mcp-demo-function',
        'timestamp': datetime.now().isoformat(),
        'environment': '${var.environment}',
        'message': 'MCP Demo function executed successfully'
    }
    
    # Process request data
    if request_json:
        response_data['received_data'] = request_json
        
        # Perform some demo processing
        if 'numbers' in request_json:
            numbers = request_json['numbers']
            response_data['calculations'] = {
                'sum': sum(numbers),
                'average': sum(numbers) / len(numbers) if numbers else 0,
                'count': len(numbers),
                'max': max(numbers) if numbers else None,
                'min': min(numbers) if numbers else None
            }
    
    # Add query parameters if any
    if request_args:
        response_data['query_params'] = dict(request_args)
    
    return json.dumps(response_data), 200, {'Content-Type': 'application/json'}

@functions_framework.http  
def mcp_data_processor(request):
    """
    MCP Data Processing Function
    Processes data and stores results in Cloud Storage
    """
    
    try:
        # Initialize storage client
        storage_client = storage.Client()
        bucket_name = '${var.project_id}-${var.environment}-data-bucket'
        
        response_data = {
            'function_name': 'mcp-data-processor',
            'timestamp': datetime.now().isoformat(),
            'environment': '${var.environment}',
            'status': 'success'
        }
        
        request_json = request.get_json(silent=True)
        if request_json and 'data' in request_json:
            # Process the data
            processed_data = {
                'original_data': request_json['data'],
                'processed_at': datetime.now().isoformat(),
                'processing_type': 'demo_processing'
            }
            
            # Store in Cloud Storage
            bucket = storage_client.bucket(bucket_name)
            blob_name = f"processed/{datetime.now().strftime('%Y/%m/%d')}/data_{datetime.now().strftime('%H%M%S')}.json"
            blob = bucket.blob(blob_name)
            blob.upload_from_string(json.dumps(processed_data))
            
            response_data['stored_file'] = blob_name
            response_data['bucket'] = bucket_name
        
        return json.dumps(response_data), 200, {'Content-Type': 'application/json'}
        
    except Exception as e:
        error_response = {
            'function_name': 'mcp-data-processor',
            'timestamp': datetime.now().isoformat(),
            'status': 'error',
            'error': str(e)
        }
        return json.dumps(error_response), 500, {'Content-Type': 'application/json'}
EOF
    filename = "main.py"
  }
  
  source {
    content = "functions-framework==3.*"
    filename = "requirements.txt"
  }
}

resource "google_storage_bucket_object" "function_source" {
  name   = "function-source.zip"
  bucket = google_storage_bucket.mcp_demo_functions.name
  source = data.archive_file.function_source.output_path
}

resource "google_cloudfunctions_function" "mcp_demo_function" {
  name        = "${var.environment}-demo-function"
  description = "MCP Demo Cloud Function"
  runtime     = "python39"
  region      = var.region

  available_memory_mb   = 256
  source_archive_bucket = google_storage_bucket.mcp_demo_functions.name
  source_archive_object = google_storage_bucket_object.function_source.name
  trigger {
    http_trigger {
      url = ""
    }
  }
  entry_point = "mcp_demo_function"

  environment_variables = {
    ENVIRONMENT = var.environment
    PROJECT_ID  = var.project_id
  }

  labels = {
    environment = var.environment
  }

  depends_on = [google_project_service.required_apis]
}

resource "google_cloudfunctions_function" "mcp_data_processor" {
  name        = "${var.environment}-data-processor"
  description = "MCP Data Processing Function"
  runtime     = "python39"
  region      = var.region

  available_memory_mb   = 512
  timeout               = 60
  source_archive_bucket = google_storage_bucket.mcp_demo_functions.name
  source_archive_object = google_storage_bucket_object.function_source.name
  trigger {
    http_trigger {
      url = ""
    }
  }
  entry_point = "mcp_data_processor"

  environment_variables = {
    ENVIRONMENT = var.environment
    PROJECT_ID  = var.project_id
  }

  labels = {
    environment = var.environment
  }

  depends_on = [google_project_service.required_apis]
}

# Cloud SQL Instance
resource "google_sql_database_instance" "mcp_demo_db" {
  name             = "${var.environment}-database"
  database_version = "MYSQL_8_0"
  region           = var.region

  settings {
    tier = "db-f1-micro"

    backup_configuration {
      enabled = true
    }

    ip_configuration {
      ipv4_enabled = true
      authorized_networks {
        value = "0.0.0.0/0"
        name  = "all"
      }
    }
  }

  deletion_protection = false

  depends_on = [google_project_service.required_apis]
}

resource "google_sql_database" "mcp_demo_database" {
  name     = "mcpdemo"
  instance = google_sql_database_instance.mcp_demo_db.name
}

resource "google_sql_user" "mcp_demo_user" {
  name     = "mcpuser"
  instance = google_sql_database_instance.mcp_demo_db.name
  password = "McpDemo123!"
}

# BigQuery Dataset
resource "google_bigquery_dataset" "mcp_demo_dataset" {
  dataset_id  = "${replace(var.environment, "-", "_")}_demo_dataset"
  description = "MCP Demo BigQuery Dataset"
  location    = "US"

  labels = {
    environment = var.environment
  }

  depends_on = [google_project_service.required_apis]
}

resource "google_bigquery_table" "mcp_demo_table" {
  dataset_id = google_bigquery_dataset.mcp_demo_dataset.dataset_id
  table_id   = "demo_table"

  schema = jsonencode([
    {
      name = "id"
      type = "INTEGER"
      mode = "REQUIRED"
    },
    {
      name = "name"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "created_at"
      type = "TIMESTAMP"
      mode = "REQUIRED"
    },
    {
      name = "data"
      type = "JSON"
      mode = "NULLABLE"
    }
  ])

  labels = {
    environment = var.environment
  }
}

# Sample BigQuery data
resource "google_bigquery_job" "mcp_demo_data_load" {
  job_id = "${var.environment}-demo-data-load-${formatdate("YYYYMMDD-hhmmss", timestamp())}"

  query {
    query = <<-EOF
      INSERT INTO `${var.project_id}.${google_bigquery_dataset.mcp_demo_dataset.dataset_id}.${google_bigquery_table.mcp_demo_table.table_id}`
      (id, name, created_at, data)
      VALUES
      (1, 'MCP Demo Record 1', CURRENT_TIMESTAMP(), JSON '{"type": "demo", "environment": "${var.environment}"}'),
      (2, 'MCP Demo Record 2', CURRENT_TIMESTAMP(), JSON '{"type": "test", "environment": "${var.environment}"}'),
      (3, 'MCP Demo Record 3', CURRENT_TIMESTAMP(), JSON '{"type": "sample", "environment": "${var.environment}"}'');
    EOF

    use_legacy_sql = false
  }

  depends_on = [google_bigquery_table.mcp_demo_table]
}

# Outputs
output "project_id" {
  description = "GCP Project ID"
  value       = var.project_id
}

output "region" {
  description = "GCP Region"
  value       = var.region
}

output "compute_instances" {
  description = "Compute Engine Instance Information"
  value = {
    web_servers = [
      for instance in google_compute_instance.mcp_demo_web : {
        name       = instance.name
        zone       = instance.zone
        public_ip  = instance.network_interface[0].access_config[0].nat_ip
        private_ip = instance.network_interface[0].network_ip
      }
    ]
    app_server = {
      name       = google_compute_instance.mcp_demo_app.name
      zone       = google_compute_instance.mcp_demo_app.zone
      public_ip  = google_compute_instance.mcp_demo_app.network_interface[0].access_config[0].nat_ip
      private_ip = google_compute_instance.mcp_demo_app.network_interface[0].network_ip
    }
  }
}

output "storage_buckets" {
  description = "Cloud Storage Bucket Names"
  value = {
    data_bucket      = google_storage_bucket.mcp_demo_data.name
    logs_bucket      = google_storage_bucket.mcp_demo_logs.name
    functions_bucket = google_storage_bucket.mcp_demo_functions.name
  }
}

output "cloud_functions" {
  description = "Cloud Function Information"
  value = {
    demo_function = {
      name = google_cloudfunctions_function.mcp_demo_function.name
      url  = google_cloudfunctions_function.mcp_demo_function.https_trigger_url
    }
    data_processor = {
      name = google_cloudfunctions_function.mcp_data_processor.name
      url  = google_cloudfunctions_function.mcp_data_processor.https_trigger_url
    }
  }
}

output "cloud_sql" {
  description = "Cloud SQL Instance Information"
  value = {
    instance_name    = google_sql_database_instance.mcp_demo_db.name
    connection_name  = google_sql_database_instance.mcp_demo_db.connection_name
    public_ip        = google_sql_database_instance.mcp_demo_db.public_ip_address
    database_name    = google_sql_database.mcp_demo_database.name
  }
  sensitive = true
}

output "bigquery" {
  description = "BigQuery Dataset Information"
  value = {
    dataset_id = google_bigquery_dataset.mcp_demo_dataset.dataset_id
    table_id   = google_bigquery_table.mcp_demo_table.table_id
  }
}

output "mcp_test_commands" {
  description = "Example MCP commands to test the infrastructure"
  value = [
    "List GCE instances: python3 gcp_server.py --http",
    "List Storage buckets: 'Show me all my Cloud Storage buckets'",
    "Check Cloud Functions: 'List all Cloud Functions'",
    "BigQuery datasets: 'List all BigQuery datasets'",
    "Run BigQuery query: 'Run query: SELECT * FROM ${google_bigquery_dataset.mcp_demo_dataset.dataset_id}.${google_bigquery_table.mcp_demo_table.table_id} LIMIT 5'"
  ]
}
