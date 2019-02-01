from flask import Blueprint

from gift_card.api import GiftCardAPI

gift_card_app = Blueprint('gift_card_app', __name__)

gift_card_view = GiftCardAPI.as_view('gift_card_api')

gift_card_app.add_url_rule('/giftcard/', view_func=gift_card_view, methods=['POST', 'GET', ])
gift_card_app.add_url_rule('/giftcard/<gift_card_id>', view_func=gift_card_view, methods=['GET', ])