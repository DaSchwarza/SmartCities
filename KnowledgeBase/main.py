from flask import Flask, request, jsonify
from models import load_entities

# Load core data from MongoDB
sensors, plugs, parking_spaces, cars = load_entities()

app = Flask(__name__)


@app.route('/', methods=['GET'])
def list_cars():
    return jsonify([car.to_dict() for car in cars.values()])


@app.route('/emergency-charge', methods=['POST'])
def emergency_charge():
    data = request.json
    # Dummy MQTT publish, replace with real details as needed
    return jsonify({"success": True, "message": "Emergency charge initiated for car with license plate: " + data['license_plate']})


@app.route('/update-car', methods=['POST'])
def update_car():
    data = request.json
    car = cars.get(data['license_plate'])
    if not car:
        return jsonify({"error": "Car not found"}), 404
    car.manufacturer = data['manufacturer']
    car.model = data['model']
    car.battery_capacity = data['battery_capacity']
    car.parking_space_id = data['parking_space']
    # Update MongoDB as needed
    return jsonify({"success": True, "message": "Car updated successfully"})


if __name__ == '__main__':
    app.run(debug=True, port=8080)
