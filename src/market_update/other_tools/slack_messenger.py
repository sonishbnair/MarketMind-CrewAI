import os
import requests
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

class SlackMessenger:
    def __init__(self, token=None, max_char_length=3000):
        """
        Initialize the SlackMessenger with a bot token.
        If no token is provided, it will try to get it from environment variables.
        
        Parameters:
        - token: Slack bot token (optional)
        - max_char_length: Maximum character length for message blocks (default: 5000)
        """
        self.token = token or os.getenv("SLACK_BOT_TOKEN")
        if not self.token:
            raise ValueError("No Slack token provided. Set SLACK_BOT_TOKEN environment variable or pass token to constructor.")
        
        self.base_url = "https://slack.com/api/"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        # Set the maximum character length for message blocks
        self.max_char_length = max_char_length
    
    def send_message(self, channel, message, blocks=None):
        """
        Send a message to a Slack channel.
        
        Parameters:
        - channel: The channel ID or name (with #) to send the message to
        - message: The text message to send
        - blocks: Optional blocks for advanced formatting (see Slack Block Kit)
        
        Returns:
        - Response from Slack API
        """
        endpoint = f"{self.base_url}chat.postMessage"
        payload = {
            "channel": channel,
            "text": message
        }
        
        if blocks:
            payload["blocks"] = blocks
            
        response = requests.post(endpoint, headers=self.headers, json=payload)
        response_data = response.json()
        
        if not response_data.get("ok"):
            error = response_data.get("error", "Unknown error")
            print(f"Error sending message: {error}")
        
        return response_data
    
    def send_markdown_snippet(self, channel, content, title=None, initial_comment=None):
        """
        Send markdown content as a snippet to a Slack channel.
        
        Parameters:
        - channel: The channel ID or name (with #) to send the snippet to
        - content: The markdown content to send
        - title: Optional title for the snippet
        - initial_comment: Optional message to accompany the snippet
        
        Returns:
        - Response from Slack API
        """
        endpoint = f"{self.base_url}chat.postMessage"
        
        # Format as a code block with markdown designation
        formatted_content = f"\n{content}\n"
        
        # Create the payload with just the text first - fallback if blocks fail
        payload = {
            "channel": channel,
            "text": initial_comment or "Report content:" 
        }
        
        # Add blocks if we have a title or initial comment
        if title or initial_comment:
            blocks = []
            
            if initial_comment:
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": initial_comment
                    }
                })
            
            if title:
                blocks.append({
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": title,
                        "emoji": True
                    }
                })
            
            # Make sure the content block doesn't exceed Slack's limits
            # Use the configurable max_char_length
            if len(formatted_content) <= self.max_char_length:
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": formatted_content
                    }
                })
            else:
                # Just use the text field if the content is too long
                payload["text"] = f"{initial_comment or 'Report content:'}\n\n{formatted_content}"
                # Don't add content to blocks to avoid the error
            
            # Only add blocks if we don't have oversized content
            if len(formatted_content) <= self.max_char_length:
                payload["blocks"] = blocks
        else:
            # If no title or comment, just use the formatted content as text
            payload["text"] = formatted_content
            
        # Send the message
        print(f"Sending markdown snippet to channel {channel}...")
        print("*********************")
        print(f"endpoint: {endpoint}")
        print("*********************")
        print(f"payload: {payload}")
        print("*********************")
        response = requests.post(endpoint, headers=self.headers, json=payload)
        response_data = response.json()
        
        if not response_data.get("ok"):
            error = response_data.get("error", "Unknown error")
            print(f"Error sending markdown snippet: {error}")
            print(f"Response details: {response_data}")
            
            # Fallback to sending as plain text if blocks fail
            if "blocks" in payload:
                del payload["blocks"]
                payload["text"] = f"{initial_comment or 'Report content:'}\n\n{formatted_content}"
                
                # Try again without blocks
                print("Trying to send message without blocks...")
                response = requests.post(endpoint, headers=self.headers, json=payload)
                response_data = response.json()
                
                if not response_data.get("ok"):
                    print(f"Fallback also failed: {response_data.get('error', 'Unknown error')}")
        
        return response_data

    def send_report(self, channel, report_file_path, max_part_length=None):
        """
        Sends a report markdown file to Slack as a formatted message.
        
        Parameters:
        - channel: The channel ID or name (with #) to send to
        - report_file_path: Path to the markdown report file
        - max_part_length: Optional override for max character length per part
        
        Returns:
        - True if successful, False otherwise
        """
        print(f"Attempting to send report: {report_file_path}")
        if not os.path.exists(report_file_path):
            print(f"Report file not found: {report_file_path}")
            return False
            
        try:
            # Read the markdown content
            with open(report_file_path, 'r') as file:
                markdown_content = file.read()
            
            # Get timestamp and filename for the message
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            filename = os.path.basename(report_file_path)
            
            # Send an introduction message
            self.send_message(
                channel, 
                f"🔔 *New Market Trends Report Available*\n"
            )
            
            # Use provided max_part_length or fall back to instance value
            part_length = max_part_length or self.max_char_length
            
            # Send the markdown content
            # Slack has message size limits
            if len(markdown_content) <= part_length:
                # Send as a single message
                response = self.send_markdown_snippet(
                    channel,
                    markdown_content,
                    title=f"Report: {filename}",
                    initial_comment="Here's the detailed report:"
                )
                
                success = response.get("ok", False)
            else:
                # Split into multiple messages if too long
                parts = [markdown_content[i:i+part_length] for i in range(0, len(markdown_content), part_length)]
                
                self.send_message(channel, f"The report is split into {len(parts)} parts due to length:")
                
                success = True
                for i, part in enumerate(parts):
                    response = self.send_markdown_snippet(
                        channel,
                        part,
                        title=f"Report Part {i+1}/{len(parts)}",
                        initial_comment=f"Report: {filename} (continued)"
                    )
                    if not response.get("ok", False):
                        success = False
                        print(f"Failed to send part {i+1}: {response.get('error', 'Unknown error')}")
                    else:
                        print(f"Successfully sent part {i+1}/{len(parts)}")
            
            if success:
                print(f"Successfully sent report to Slack channel {channel}")
                return True
            else:
                print(f"Failed to send report to Slack")
                return False
                
        except Exception as e:
            print(f"Error sending report to Slack: {str(e)}")
            return False
        

if __name__ == "__main__":
    # Example usage
    slack = SlackMessenger(max_char_length=3000)  # Configure with 5000 character limit
    # slack.send_message("#general", "Hello from Python!")
    # slack.send_markdown_snippet("#general", "This is a *bold* message with `code`.")
    slack.send_report("#stock-options-agent", "MyWorkspace/Playgroud/AI Agent/crewai/market_update/output/report_20250227_080406.md")