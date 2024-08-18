from dagster import resource
from fumehood_project.Api import Api


@resource
def fumehood_api_resource():
    return Api()