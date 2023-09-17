from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
from ryanair import Ryanair
from ryanair.types import Flight, Trip

app = Flask(__name__)
CORS(app)

@app.route('/get-flight', methods=['POST'])
def get_flight():
    origin_airport = request.json['origin_airport']
    arrive_airport = request.json['arrive_airport']
    start = datetime.strptime(request.json['start'], '%Y-%m-%d').date()
    end = datetime.strptime(request.json['end'], '%Y-%m-%d').date()
    round_trip = request.json['round']  # Assuming this is a boolean
    print(origin_airport, arrive_airport, start, end, round_trip)
    api = Ryanair(currency="EUR")

    flights = None  # Initialize the flights variable to None

    try:
        if round_trip == "yes":
            flights = api.get_cheapest_return_flights(origin_airport, start, start, end, end, destination_airport=arrive_airport)
        if round_trip == "no":
            flights = api.get_cheapest_flights(origin_airport, start, end, destination_airport=arrive_airport)

        if not flights:
            return jsonify({
                'data': 'No flights found for the given criteria.'
            }), 200

        if round_trip == "yes":
            trip: Trip = flights[0]

            # Extract and process outbound and inbound flight details
            outbound_flight = {
                "departureTime": trip.outbound.departureTime.strftime('%Y-%m-%d %H:%M:%S'),  # Convert datetime to string
                "flightNumber": trip.outbound.flightNumber,
                "price": trip.outbound.price,
                "currency": trip.outbound.currency,
                "origin": trip.outbound.origin,
                "originFull": trip.outbound.originFull,
                "destination": trip.outbound.destination,
                "destinationFull": trip.outbound.destinationFull
            }

            inbound_flight = {
                "departureTime": trip.inbound.departureTime.strftime('%Y-%m-%d %H:%M:%S'),  # Convert datetime to string
                "flightNumber": trip.inbound.flightNumber,
                "price": trip.inbound.price,
                "currency": trip.inbound.currency,
                "origin": trip.inbound.origin,
                "originFull": trip.inbound.originFull,
                "destination": trip.inbound.destination,
                "destinationFull": trip.inbound.destinationFull
            }

            return jsonify({
                'totalPrice': trip.totalPrice,
                'outbound': outbound_flight,
                'inbound': inbound_flight
            })

        if round_trip == 'no':
            flight: Flight = flights[0]

            flight_data = {
                "departureTime": flight.departureTime.strftime('%Y-%m-%d %H:%M:%S'),  # Convert datetime to string
                "flightNumber": flight.flightNumber,
                "price": flight.price,
                "currency": flight.currency,
                "origin": flight.origin,
                "originFull": flight.originFull,
                "destination": flight.destination,
                "destinationFull": flight.destinationFull
            }

            return jsonify({
                "totalPrice": flight.price,
                "outbound": flight_data
            })


    except IndexError:  # Handle cases when there are no flights returned
        return jsonify({'data': 'No flights available.'}), 200

    except Exception as e:  # Generic exception handling
        return jsonify({'data': f'An error occurred: {str(e)}'}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)



    
