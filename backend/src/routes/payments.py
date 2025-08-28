from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.payment import Payment

payments_bp = Blueprint("payments", __name__)

@payments_bp.route("/payments", methods=["POST"])
def create_payment():
    data = request.get_json()
    new_payment = Payment(employee_id=data["employee_id"], amount=data["amount"], date=data["date"], description=data.get("description"))
    db.session.add(new_payment)
    db.session.commit()
    return jsonify(new_payment.to_dict()), 201

@payments_bp.route("/payments", methods=["GET"])
def get_payments():
    payments = Payment.query.all()
    return jsonify([payment.to_dict() for payment in payments]), 200

@payments_bp.route("/payments/<int:id>", methods=["DELETE"])
def delete_payment(id):
    payment = Payment.query.get_or_404(id)
    db.session.delete(payment)
    db.session.commit()
    return jsonify({"message": "Payment deleted"}), 200


