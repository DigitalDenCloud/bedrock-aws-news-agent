import json
import boto3

def lambda_handler(event, context):
    # Parse the request body
    try:
        if 'body' in event:
            body = event.get('body', '{}')
            if isinstance(body, str):
                body = json.loads(body)
        else:
            body = event
        message = body.get('message', '')
        session_id = body.get('sessionId', 'default-session')
    except Exception as e:
        return {
            'statusCode': 400,
            'headers': cors_headers(),
            'body': json.dumps({'error': f'Invalid request body: {str(e)}'})
        }

    if not message:
        return {
            'statusCode': 400,
            'headers': cors_headers(),
            'body': json.dumps({'error': 'No message provided'})
        }

    # Bedrock agent identifiers
    AGENT_ID = 'YOUR_AGENT_ID'
    AGENT_ALIAS_ID = 'TSTALIASID'

    try:
        client = boto3.client('bedrock-agent-runtime')
        response = client.invoke_agent(
            agentId=AGENT_ID,
            agentAliasId=AGENT_ALIAS_ID,
            sessionId=session_id,
            inputText=message
        )

        completion = ""
        for event in response.get('completion', []):
            if 'chunk' in event:
                completion += event['chunk']['bytes'].decode('utf-8')

        return {
            'statusCode': 200,
            'headers': cors_headers(),
            'body': json.dumps({'response': completion})
        }

    except Exception:
        return {
            'statusCode': 500,
            'headers': cors_headers(),
            'body': json.dumps({'error': 'Failed to get response from agent'})
        }

def cors_headers():
    return {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST, OPTIONS'
    }