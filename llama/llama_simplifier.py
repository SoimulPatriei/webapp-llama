import pika
import yaml
import json
import os
import torch
import time
from unsloth import FastLanguageModel

# Load configuration from config.yaml
with open("config.yaml", 'r') as config_file:
    config = yaml.safe_load(config_file)

# Assign config variables
model_name = config['model_name']
model_path = config['model_path']
max_seq_length = config['max_seq_length']
load_in_4bit = config['load_in_4bit']
rabbitmq_host = config['rabbitmq_host']
queue_name = config['queue_name']

# Load the Llama model and tokenizer
def load_model_and_tokenizer():
    model_full_path = os.path.join(os.path.dirname(__file__), model_path)
    print(f"Loading model from: {model_full_path}")
    
    start_time = time.time()
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=model_full_path,
        max_seq_length=max_seq_length,
        load_in_4bit=load_in_4bit
    )
    FastLanguageModel.for_inference(model)
    end_time = time.time()
    print(f"Model loaded in {end_time - start_time:.2f} seconds")
    
    return model, tokenizer

# Simplify a sentence based on the given template
def simplify_sentence(model, tokenizer, sentence):
    prompt = (
        f"system\n\n"
        f"You are a helpful AI assistant specializing in text simplification for Estonian sentences. "
        f"You will perform text simplification based on the input you receive.\n\n"
        f"user\n\n"
        f"Perform text simplification for the following Estonian sentence.\n\n"
        f"### Sentence:\n"
        f"{sentence}\n\n"
        f"assistant\n\n"
        f"### Simplified version:\n"
    )

    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
    outputs = model.generate(**inputs, max_new_tokens=100, use_cache=True, eos_token_id=tokenizer.eos_token_id, pad_token_id=tokenizer.eos_token_id)
    simplified_sentence = tokenizer.batch_decode(outputs, skip_special_tokens=True)[0].strip()

    if "### Simplified version:" in simplified_sentence:
        simplified_sentence = simplified_sentence.split("### Simplified version:")[1].strip()

    simplified_sentence = simplified_sentence.split("###")[0].strip()

    return simplified_sentence

# Connect to RabbitMQ
print(f"Connecting to RabbitMQ at {rabbitmq_host}...")
connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
channel = connection.channel()

# Declare the queue where Llama will listen for tasks
channel.queue_declare(queue=queue_name)

# Load the Llama model and tokenizer on startup
model, tokenizer = load_model_and_tokenizer()

# Function to process incoming messages from RabbitMQ
def on_message(channel, method, properties, body):
    try:
        message = json.loads(body)
        input_text = message.get('text', '')

        if not input_text:
            raise ValueError("Empty input text")

        # Simplify the sentence
        print(f"Received text for simplification: {input_text}")
        simplified_text = simplify_sentence(model, tokenizer, input_text)

        # Send the response back to the reply_to queue
        if properties.reply_to:
            channel.basic_publish(
                exchange='',
                routing_key=properties.reply_to,
                properties=pika.BasicProperties(correlation_id=properties.correlation_id),
                body=simplified_text
            )
        print(f"Simplified text sent to reply_to queue: {simplified_text}")

        # Acknowledge the message
        channel.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print(f"Error processing message: {e}")
        channel.basic_nack(delivery_tag=method.delivery_tag)

# Consume messages from RabbitMQ
print(f"Waiting for messages in queue: {queue_name}")
channel.basic_consume(queue=queue_name, on_message_callback=on_message)

# Start consuming tasks from RabbitMQ
channel.start_consuming()
