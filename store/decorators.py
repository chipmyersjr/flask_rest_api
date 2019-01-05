from functools import wraps
from flask import request, jsonify
import datetime

from store.models import Store, AccessToken


def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        app_id = request.headers.get('STORE-ID')
        access_token = request.headers.get('ACCESS-TOKEN')

        if app_id is None or access_token is None:
            return jsonify({}), 403

        store = Store.objects.filter(store_id=app_id).first()
        if not store:
            return jsonify({}), 403

        token = AccessToken.objects.filter(store_id=store).first()
        if not token:
            return jsonify({}), 403
        if token.token != access_token:
            return jsonify({}), 403
        if token.expires_at < datetime.datetime.utcnow():
            return jsonify({'error': "TOKEN_EXPIRED"}), 403

        return f(*args, **kwargs)
    return decorated_function