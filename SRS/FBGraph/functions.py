from models import User
from Graph import Graph

def user_process(_token):
    """
    Add the user if he's a new facebook user of the application. Otherwhise, change the current values
    """
    current_user = None
    me = Graph(_token).get_me()

    try:
        current_user = User.objects.filter(external_id__exact=me['id'])[0]
        current_user.name = me['name']
        current_user.token = _token
    except IndexError:
        current_user = User(external_id=me['id'],name=me['name'],token=_token)

    current_user.save()