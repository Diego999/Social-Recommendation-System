from models import User
from Graph import Graph
from django.core.exceptions import ObjectDoesNotExist


def user_process(_token):
    """
    Add the user if he's a new facebook user of the application. Otherwise, change the current values
    """

    me = Graph(_token).get_me()
    current_user = None
    try:
        current_user = User.objects.get(external_id=me['id'])
        current_user.name = me['name']
        current_user.token = _token
    except ObjectDoesNotExist:
        current_user = User(external_id=me['id'], name=me['name'], token=_token)

    current_user.save()