from flask import Flask, request, jsonify
from flask import render_template
import pika, json, uuid
import datetime

app = Flask(__name__, static_folder='static')

# RabbitMQ connection settings
rabbitmq_host = 'rabbitmq'
connection = None
channel = None

def connect_to_rabbitmq():
    """Establish a connection to RabbitMQ and open a channel with a longer heartbeat."""
    global connection, channel
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=rabbitmq_host,
        heartbeat=600  # Set a 10-minute heartbeat interval (600 seconds)
    ))
    channel = connection.channel()
    channel.queue_declare(queue='llama_queue')

connect_to_rabbitmq()

@app.route('/')
def index():
    return render_template('simplification_interface.html')  # Updated to the new template name

@app.route('/llama_simplify', methods=['POST'])
def llama_simplify():
    try:
        global connection, channel

        # Reconnect if the channel is closed
        if connection.is_closed or channel.is_closed:
            connect_to_rabbitmq()

        if not request.is_json:
            return jsonify({"error": "Unsupported Media Type. Expecting JSON data."}), 415

        data = request.get_json()
        input_text = data.get('text', '')

        if not input_text:
            return jsonify({"error": "Text field is empty."}), 400

        # Send task to the queue
        result = channel.queue_declare(queue='', exclusive=True)
        callback_queue = result.method.queue
        corr_id = str(uuid.uuid4())
        response = None

        def on_response(ch, method, props, body):
            nonlocal response
            if corr_id == props.correlation_id:
                response = body

        channel.basic_consume(queue=callback_queue, on_message_callback=on_response, auto_ack=True)

        # Send the simplification request
        channel.basic_publish(
            exchange='',
            routing_key='llama_queue',
            properties=pika.BasicProperties(reply_to=callback_queue, correlation_id=corr_id),
            body=json.dumps({"text": input_text})
        )

        while response is None:
            connection.process_data_events()

        simplified_text = response.decode('utf-8')
        return jsonify({"translation": simplified_text})

    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/get_help', methods=['GET'])
def get_help():
    try:
        with open('templates/help.txt', 'r') as file:
            help_content = json.load(file)
        
        lang = request.args.get('lang', 'en')  # Default to English
        content = help_content.get(lang, help_content['en'])  # Fallback to English if the language is missing
        return jsonify({"helpContent": content})
    except Exception as e:
        return jsonify({"error": "Error loading help content.", "details": str(e)}), 500

@app.route('/save_simplification', methods=['POST'])
def save_simplification():
    try:
        # Get client IP
        client_ip = request.remote_addr

        # Get data from request
        data = request.get_json()
        original_sentence = data.get('original_sentence', '')
        original_simplification = data.get('original', '')
        edited_simplification = data.get('edited', '')

        if not original_sentence or not original_simplification or not edited_simplification:
            return jsonify({"error": "Original sentence, original simplification, and edited simplification are required."}), 400

        # Log the data to a file
        with open('logs/simplifications_log.txt', 'a') as log_file:
            log_file.write(f"{datetime.datetime.now()} | IP: {client_ip} | Original Sentence: {original_sentence} | Original Simplification: {original_simplification} | Edited Simplification: {edited_simplification}\n")

        return jsonify({"message": "Simplification saved successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
