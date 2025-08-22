import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as apigwv2 from 'aws-cdk-lib/aws-apigatewayv2';
import * as integrations from 'aws-cdk-lib/aws-apigatewayv2-integrations';
import * as sm from 'aws-cdk-lib/aws-secretsmanager';
import * as path from 'path';

export class BackendStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const openAiSecret = new sm.Secret(this, 'OpenAIKey', {
      secretName: 'OPENAI_API_KEY',
      description: 'OpenAI API key for Mimosa backend'
    });

    const image = lambda.DockerImageCode.fromImageAsset(
      path.join(__dirname, '..', '..', 'lambda')
    );

    const fn = new lambda.DockerImageFunction(this, 'ApiFn', {
      code: image,
      memorySize: 1024,
      timeout: cdk.Duration.seconds(20),
      environment: {
        MODEL: 'gpt-5',
        OPENAI_SECRET_NAME: openAiSecret.secretName
      }
    });

    openAiSecret.grantRead(fn);

    const api = new apigwv2.HttpApi(this, 'HttpApi', {
      apiName: 'mimosa-backend',
      corsPreflight: {
        allowHeaders: ['*'],
        allowMethods: [apigwv2.CorsHttpMethod.ANY],
        allowOrigins: ['*']
      }
    });

    // Single Lambda proxy for all routes; FastAPI will route (/health,/chat)
    api.addRoutes({
      path: '/{proxy+}',
      methods: [apigwv2.HttpMethod.ANY],
      integration: new integrations.HttpLambdaIntegration('LambdaProxy', fn)
    });

    new cdk.CfnOutput(this, 'ApiUrl', { value: api.apiEndpoint });
    new cdk.CfnOutput(this, 'HealthUrl', { value: `${api.apiEndpoint}/health` });
    new cdk.CfnOutput(this, 'ChatUrl', { value: `${api.apiEndpoint}/chat` });
    new cdk.CfnOutput(this, 'SecretName', { value: openAiSecret.secretName });
  }
}
