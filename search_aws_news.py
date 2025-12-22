import json
import urllib.request
import xml.etree.ElementTree as ET

def lambda_handler(event, context):
    # Get the search topic from the agent
    topic = ""
    for param in event.get("parameters", []):
        if param.get("name") == "topic":
            topic = param.get("value", "").lower()
    
    if not topic:
        return build_response(event, [])
    
    # Fetch the AWS News Blog RSS feed
    feed_url = "https://aws.amazon.com/blogs/aws/feed/"
    with urllib.request.urlopen(feed_url, timeout=10) as response:
        feed_data = response.read().decode("utf-8")
    
    # Parse and search
    root = ET.fromstring(feed_data)
    matching_posts = []
    topic_words = topic.split()
    
    # Adjust these values to control results (increases token usage)
    MAX_POSTS_TO_SEARCH = 20 # Number of recent posts to evaluate
    MAX_RESULTS = 5          # Maximum matching results to return
    DESC_LENGTH = 150        # Characters to include from description
    
    for item in root.findall(".//item")[:MAX_POSTS_TO_SEARCH]:
        title = item.find("title").text
        link = item.find("link").text
        description = item.find("description").text or ""
        
        if all(word in title.lower() or word in description.lower() for word in topic_words):
            matching_posts.append({
                "title": title,
                "link": link,
                "description": description[:DESC_LENGTH] + "..."
            })
        
        if len(matching_posts) >= MAX_RESULTS:
            break
    
    return build_response(event, matching_posts)


def build_response(event, posts):
    return {
        "messageVersion": "1.0",
        "response": {
            "actionGroup": event.get("actionGroup", ""),
            "apiPath": event.get("apiPath", ""),
            "httpMethod": event.get("httpMethod", ""),
            "httpStatusCode": 200,
            "responseBody": {
                "application/json": {
                    "body": json.dumps(posts) if posts else json.dumps({"message": "No matching posts found."})
                }
            }
        }
    }