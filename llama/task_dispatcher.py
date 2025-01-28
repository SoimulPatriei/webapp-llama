import pika
import uuid
import json
import yaml

# Load configuration from config.yaml
with open("config.yaml", 'r') as config_file:
    config = yaml.safe_load(config_file)

rabbitmq_host = config['rabbitmq_host']
queue_name = config['queue_name']

class SimplificationClient:
    def __init__(self):
        # Set up RabbitMQ connection using host from config.yaml
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
        self.channel = self.connection.channel()

        # Declare a callback queue for replies
        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue

        # Consume messages from the callback queue
        self.channel.basic_consume(queue=self.callback_queue, on_message_callback=self.on_response, auto_ack=True)

        # Store the correlation ID and response
        self.response = None
        self.corr_id = None

    def on_response(self, ch, method, props, body):
        """Handle the response from the Llama worker."""
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, text):
        """Send a task to the Llama worker and wait for the response."""
        self.response = None
        self.corr_id = str(uuid.uuid4())  # Generate a unique correlation ID
        self.channel.basic_publish(
            exchange='',
            routing_key=queue_name,  # The queue where the Llama worker listens (from config)
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,  # The queue to send the reply
                correlation_id=self.corr_id  # Correlation ID to match the response
            ),
            body=json.dumps({"text": text})
        )

        # Wait for the response from the worker
        while self.response is None:
            self.connection.process_data_events()  # Non-blocking wait

        return self.response.decode('utf-8')

def main():
    client = SimplificationClient()

    while True:
        # Ask for input from the user
        text = input("Enter a string to simplify (or enter '1' to exit): ")

        # Check if user wants to exit
        if text == "1":
            print("Exiting...")
            break

        # Send the string to RabbitMQ for simplification and wait for the result
        print("Sending task for simplification...")
        simplified_text = client.call(text)
        print(f"Simplified text: {simplified_text}")

if __name__ == "__main__":
    main()
