#!/usr/bin/env python3
"""
Prefect Setup Script
Khởi tạo và deploy Prefect workflows
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run shell command với error handling"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return None

def setup_prefect():
    """Setup Prefect server và deployments"""

    print("🚀 Setting up Prefect for SaaS Analytics API")
    print("=" * 50)

    # 1. Install dependencies nếu chưa có
    print("\n1. Checking Prefect installation...")
    try:
        import prefect
        print(f"✅ Prefect {prefect.__version__} is installed")
    except ImportError:
        print("❌ Prefect not found. Installing...")
        run_command("pip install prefect==2.14.0 prefect-sqlalchemy==0.4.1",
                   "Installing Prefect dependencies")

    # 2. Start Prefect server (local development)
    print("\n2. Starting Prefect server...")
    run_command("prefect server start --host 0.0.0.0 &", "Starting Prefect server")

    # 3. Create work pool
    print("\n3. Setting up work pool...")
    run_command("prefect work-pool create --type process analytics-pool",
               "Creating work pool")

    # 4. Set API URL
    print("\n4. Configuring Prefect API...")
    run_command("prefect config set PREFECT_API_URL=http://localhost:4200/api",
               "Setting Prefect API URL")

    # 5. Deploy workflows
    print("\n5. Deploying workflows...")

    # Change to project directory
    project_dir = Path(__file__).parent.parent
    os.chdir(project_dir)

    # Deploy daily ETL flow
    deploy_command = """
    python -c "
from app.orchestration.prefect_workflows import daily_analytics_etl_flow, data_quality_check_flow
from prefect.deployments import Deployment
from prefect.server.schemas.schedules import CronSchedule

# Deploy daily ETL
daily_deployment = Deployment.build_from_flow(
    flow=daily_analytics_etl_flow,
    name='daily-analytics-etl',
    schedule=CronSchedule(cron='0 2 * * *'),
    work_pool_name='analytics-pool',
    tags=['analytics', 'etl', 'daily']
)
daily_deployment.apply()

# Deploy quality check
quality_deployment = Deployment.build_from_flow(
    flow=data_quality_check_flow,
    name='data-quality-check',
    schedule=CronSchedule(cron='0 */6 * * *'),
    work_pool_name='analytics-pool',
    tags=['data-quality', 'monitoring']
)
quality_deployment.apply()

print('✅ Deployments created successfully!')
"
    """

    run_command(deploy_command, "Deploying workflows")

    # 6. Start worker
    print("\n6. Starting Prefect worker...")
    print("💡 Run this in a separate terminal:")
    print("   prefect worker start --pool analytics-pool")

    print("\n" + "=" * 50)
    print("🎉 Prefect setup completed!")
    print("\n📊 Access Prefect UI at: http://localhost:4200")
    print("🔗 API endpoints available at:")
    print("   - GET  /prefect/flows/status")
    print("   - POST /prefect/flows/daily-etl/run")
    print("   - POST /prefect/flows/data-quality/run")
    print("   - GET  /prefect/analytics/cached")
    print("   - GET  /prefect/monitoring/system")

    return True

if __name__ == "__main__":
    setup_prefect()