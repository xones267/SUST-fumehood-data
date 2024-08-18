from dagster import (
    load_assets_from_modules,
    Definitions,
    define_asset_job,
    ScheduleDefinition,
    build_schedule_from_partitioned_job,
    DefaultScheduleStatus
)
from fumehood_project import assets
# Define normal asset job

normal_asset_job = define_asset_job(name="hourly_refresh", selection="*")


# Load assets from modules
asset_defs = load_assets_from_modules([assets])

# Define schedules for both normal and partitioned assets
defs = Definitions(
    assets=asset_defs,
    schedules=[
        ScheduleDefinition(
            job=normal_asset_job,
            cron_schedule="*/60 * * * *",
            default_status=DefaultScheduleStatus.RUNNING  # Example cron schedule for normal asset
        ),
        
    ],
)






