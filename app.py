from flask import Flask, request, jsonify
import paypalrestsdk

app = Flask(__name__)

# PayPal SDK configuration
paypalrestsdk.configure({
    "mode": "sandbox",  # or "live" for production
    "client_id": "",
    "client_secret": ""
})

@app.route('/')
def index():
    return "PayPal Integration with Flask API"

# API endpoint to create a payment
@app.route('/create-payment', methods=['POST'])
def create_payment():
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "transactions": [{
            "amount": {
                "total": request.json['total'],
                "currency": request.json['currency']
            },
            "description": request.json['description']
        }],
        "redirect_urls": {
            "return_url": "http://localhost:5000/payment/execute",
            "cancel_url": "http://localhost:5000/payment/cancel"
        }
    })

    if payment.create():
        approval_url = None
        for link in payment.links:
            if link.rel == "approval_url":
                approval_url = link.href
                break

        return jsonify({
            "paymentID": payment.id,
            "approval_url": approval_url,
            "links": [{"rel": link.rel, "href": link.href, "method": link.method} for link in payment.links]
        })
    else:
        return jsonify({"error": payment.error}), 400

# API endpoint to execute a payment
@app.route('/payment/execute', methods=['GET'])
def payment_execute():
    # Get the payment ID and Payer ID from the query string
    payment_id = request.args.get('paymentId')
    payer_id = request.args.get('PayerID')

    # Find the payment object by its ID
    payment = paypalrestsdk.Payment.find(payment_id)

    if payment:
        return jsonify({
            "paymentID": payment_id,
            "payerID": payer_id
        })
    else:
        return jsonify({"error": "Payment not found"}), 404


if __name__ == '__main__':
    app.run(debug=True)
