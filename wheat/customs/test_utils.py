'''
Utils for test.

@Author Minchiuan <2016-May-9>
'''

from settings import API_VERSION
URL_PREFIX = '/api/%s/' % API_VERSION


def login_client(client, user_phone, password):
    url = URL_PREFIX + 'users/login/'
    post_data = {
        'phone': user_phone,
        'password': password
    }
    response = client.post(url, post_data)
    return response


def refresh_token(client, user_phone, password):
    response = login_client(user_phone, password)
    user_token = response.data['data']['token']['token']
    client.credentials(HTTP_AUTHORIZATION='Token ' + user_token)
    return user_token
