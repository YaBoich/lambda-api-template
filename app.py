"""
Module defining project infrastructure using the AWS CDK.

Environment variables are provided to the lambda functions here.
"""
from aws_cdk import (
    aws_lambda as alambda,
    aws_apigateway as apigw,
    aws_dynamodb as dynamodb,
    Stack,
    App,
    Environment,
    RemovalPolicy,
)
import config


# TODO change the names and ids of each resource as you require.


class MyStack(Stack):
    def __init__(self, scope, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create DynamoDB table
        table = dynamodb.Table(
            scope=self,
            id="MyTable",
            partition_key=dynamodb.Attribute(
                name="id",
                type=dynamodb.AttributeType.STRING,
            ),
            billing_mode=dynamodb.BillingMode.PROVISIONED,
            read_capacity=1,
            write_capacity=1,
            removal_policy=RemovalPolicy.DESTROY,  # WARN: makes `cdk destroy` work for this table.
        )

        # Enable read auto-scaling
        read_scaling = table.auto_scale_read_capacity(min_capacity=1, max_capacity=10)
        read_scaling.scale_on_utilization(target_utilization_percent=50)

        # Enable write auto-scaling
        write_scaling = table.auto_scale_write_capacity(min_capacity=1, max_capacity=10)
        write_scaling.scale_on_utilization(target_utilization_percent=50)

        # Create Lambda function
        lambda_function = alambda.Function(
            scope=self,
            id="MyLambdaFunction",
            runtime=alambda.Runtime.PYTHON_3_8,
            handler="handler.handle",
            code=alambda.Code.from_asset("bin/package.zip"),
            environment={
                "TABLE_NAME": table.table_name,
            },
        )

        # Grant Lambda function access to DynamoDB table
        table.grant_read_write_data(lambda_function)

        # Create API Gateway
        api = apigw.RestApi(
            scope=self,
            id="MyApiGateway",
            rest_api_name="API Name",
            description="API Gateway for my Lambda functions",
        )

        # Create API Gateway resource and associate with Lambda function
        api_resource = api.root.add_resource("endpoint")
        api_resource.add_method("ANY", apigw.LambdaIntegration(lambda_function))


app = App()

env = Environment(
    account=config.AWS_ACCOUNT,
    region=config.AWS_REGION,
)

stack = MyStack(app, "CdkTestStack", env=env)

app.synth()
