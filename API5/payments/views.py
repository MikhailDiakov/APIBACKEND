import stripe
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
import json
import requests

stripe.api_key = settings.STRIPE_SECRET_KEY
ORDER_SERVICE_URL = "http://127.0.0.1:8002/api/v1/order/"


@csrf_exempt
def create_checkout_session(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            order_id = data.get("order_id")
            cart_key = data.get("cart_key")

            token = request.headers.get("Authorization", "")

            headers = {
                "X-MICROSERVICE-API-KEY": settings.MICROSERVICE_API_KEY,
                "Authorization": token,
            }
            order_response = requests.post(
                f"{ORDER_SERVICE_URL}{order_id}/get_order_by_id/",
                headers=headers,
                json={"cart_key": cart_key},
            )

            if order_response.status_code != 200:
                return JsonResponse({"error": "Order not found"}, status=404)

            order_data = order_response.json()

            items = order_data.get("order", {}).get("items", [])

            line_items = []
            for item in items:
                product_name = item.get("product_name", "Unknown Product")
                quantity = item.get("quantity", 1)
                unit_price = float(item.get("unit_price", 0))

                line_items.append(
                    {
                        "price_data": {
                            "currency": "usd",
                            "unit_amount": int(unit_price * 100),
                            "product_data": {
                                "name": product_name,
                            },
                        },
                        "quantity": quantity,
                    }
                )

            success_url = request.build_absolute_uri(reverse("payments:completed"))
            cancel_url = request.build_absolute_uri(reverse("payments:canceled"))

            session = stripe.checkout.Session.create(
                mode="payment",
                client_reference_id=order_id,
                success_url=success_url,
                cancel_url=cancel_url,
                line_items=line_items,
            )

            return JsonResponse({"checkout_url": session.url})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
    event = None

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        if session["payment_status"] == "paid":
            order_id = session["client_reference_id"]
            payment_intent = session["payment_intent"]

            headers = {"X-MICROSERVICE-API-KEY": settings.MICROSERVICE_API_KEY}
            order_update_url = f"{ORDER_SERVICE_URL}update_order/"
            data = {
                "order_id": order_id,
                "is_paid": True,
                "payment_intent": payment_intent,
            }

            order_response = requests.put(order_update_url, json=data, headers=headers)
            if order_response.status_code == 200:
                return JsonResponse({"status": "success"})
            else:
                return JsonResponse(
                    {"error": "Failed to update order status"}, status=500
                )

    return HttpResponse(status=200)


def payment_completed(request):
    return JsonResponse({"status": "success"})


def payment_canceled(request):
    return JsonResponse({"status": "canceled"})
