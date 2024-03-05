from fastapi.testclient import TestClient
from app import app


client = TestClient(app)


def test_profiles():
    reg_data = {
              "login": "pisunchik",
              "email": "pidoras1488@niga.ru",
              "password": "Qwerty1337)",
              "countryCode": "RU",
              "isPublic": True,
              "phone": "+7000000000",
              "image": "https://http.cat/images/100.jpg"
    }

    response = client.post('/api/auth/register', json=reg_data)
    assert response.status_code == 201 or response.status_code == 409
    if response.status_code == 201:
        assert response.json()['profile'] == {
                  "login": "pisunchik",
                  "email": "pidoras1488@niga.ru",
                  "countryCode": "RU",
                  "isPublic": True,
                  "phone": "+7000000000",
                  "image": "https://http.cat/images/100.jpg"
        }

    reg_data = {
        "login": "pisunchikZXC",
        "email": "pidoras14881@niga.ru",
        "password": "Qwerty1337)",
        "countryCode": "RU",
        "isPublic": False,
        "phone": "+7000030000",
        "image": "https://http.cat/images/100.jpg"
    }

    response = client.post('/api/auth/register', json=reg_data)
    assert response.status_code == 201 or response.status_code == 409

    reg_data = {
        "login": "pisunchik1212",
        "email": "pidoras1488@niga.ru",
        "countryCode": "RU",
        "isPublic": True,
        "phone": "+7000000000",
        "image": "https://http.cat/images/100.jpg"
    }
    response = client.post('/api/auth/register', json=reg_data)
    assert response.status_code == 400

    reg_data = {
        "login": "pisunchik1212",
        "email": "pidor",
        "countryCode": "Ru",
        "isPublic": True,
        "phone": "+7000000000asa",
        "image": "https://http.cat/images/100.jpg"
    }
    response = client.post('/api/auth/register', json=reg_data)
    assert response.status_code == 400

    reg_data = {
        "login": "pisunchik2",
        "email": "pidor",
        "countryCode": "Ru",
        "isPublic": True,
        "phone": "+7000000000asa",
        "image": "https://http.cat/images/100.jpg"
    }
    response = client.post('/api/auth/register', json=reg_data)
    assert response.status_code == 400

    auth_data = {
        "login": "pisunchik",
        "password": "Qwerty1337)"
    }
    response = client.post('/api/auth/sign-in', json=auth_data)

    assert response.status_code == 200
    assert 'token' in response.json()

    bearer = response.json()['token']
    headers = {
        "Authorization": f"Bearer {bearer}"
    }
    response = client.get('/api/me/profile', headers=headers)

    assert response.status_code == 200
    assert response.json() == {
              "login": "pisunchik",
              "email": "pidoras1488@niga.ru",
              "countryCode": "RU",
              "isPublic": True,
              "phone": "+7000000000",
              "image": "https://http.cat/images/100.jpg"
    }

    reg_data = {
        "login": "pisunchik2",
        "email": "pidoras1488@niga.ru2",
        "password": "Qwerty1337)",
        "countryCode": "RU",
        "isPublic": True,
        "phone": "+700000002",
        "image": "https://http.cat/images/100.jpg"
    }
    response = client.post('/api/auth/register', json=reg_data)

    assert response.status_code == 201 or response.status_code == 409
    if response.status_code == 201:
        assert len(response.json()['profile']) == 6

    auth_data = {
        "login": "pisunchik2",
        "password": "Qwerty1337)"
    }
    response = client.post('/api/auth/sign-in', json=auth_data)

    assert response.status_code == 200
    assert 'token' in response.json()

    bearer2 = response.json()['token']
    headers2 = {
        "Authorization": f"Bearer {bearer2}"
    }
    response = client.get('/api/me/profile', headers=headers2)
    assert response.status_code == 200

    patch_data = {
                  "countryCode": "RU",
                  "isPublic": True,
                  "phone": "+7000002000",
                  "image": "https://http.cat/images/101.jpg"
                }
    response = client.patch('/api/me/profile', json=patch_data, headers=headers2)

    assert response.status_code == 200
    assert response.json() == {
        "login": "pisunchik2",
        "email": "pidoras1488@niga.ru2",
        "countryCode": "RU",
        "isPublic": True,
        "phone": "+7000002000",
        "image": "https://http.cat/images/101.jpg"
    }

    response = client.get('/api/profiles/pisunchik2', headers=headers)

    assert response.status_code == 200
    assert response.json() == {
        "login": "pisunchik2",
        "email": "pidoras1488@niga.ru2",
        "countryCode": "RU",
        "isPublic": True,
        "phone": "+7000002000",
        "image": "https://http.cat/images/101.jpg"
    }


def test_profile_friends():
    auth_data = {
        "login": "pisunchik",
        "password": "Qwerty1337)"
    }
    response = client.post('/api/auth/sign-in', json=auth_data)
    bearer = response.json()['token']
    headers = {
        "Authorization": f"Bearer {bearer}"
    }

    fake_login = {'login': 'xyizxc'}
    response = client.post('/api/friends/add', headers=headers, json=fake_login)
    assert response.status_code == 404
    assert response.json() == {
        'reason': 'Пользователь с указанным логином не найден.'
    }

    response = client.post('/api/friends/add', json=auth_data)
    assert response.status_code == 401
    assert response.json() == {
        'reason': 'Переданный токен не существует либо некорректен'
    }

    add_friend_login = {
        "login": "pisunchik2"
    }
    response = client.post('/api/friends/add', json=add_friend_login, headers=headers)
    assert response.status_code == 200
    assert response.json() == {
        'status': 'ok'
    }

    add_friend_login = {
        "login": "pisunchik"
    }
    response = client.post('/api/friends/add', json=add_friend_login, headers=headers)
    assert response.status_code == 200
    assert response.json() == {
        'status': 'ok'
    }

    response = client.get('/api/friends', headers=headers)
    assert response.status_code == 200

    response = client.get('/api/friends')
    assert response.status_code == 401
    assert response.json() == {
        'reason': 'Переданный токен не существует либо некорректен'
    }

    fake_user = {
        "login": "fake_pisun"
    }
    response = client.post('/api/friends/remove', json=fake_user, headers=headers)
    assert response.status_code == 404

    invalid_form = {
        "zxcgg": "dota2",
        "login": "pisunchik",
        "huinya": "dolboeb?"
    }
    response = client.post('/api/friends/remove', json=invalid_form, headers=headers)
    assert response.status_code == 200

    invalid_token = {
        "token": "invalid"
    }
    response = client.post('/api/friends/remove', json=fake_user, headers=invalid_token)
    assert response.status_code == 401

    user = {
        "login": "pisunchik",
    }
    response = client.post('/api/friends/remove', json=user, headers=headers)
    assert response.status_code == 200

    user = {
        "login": "pisunchik2",
    }
    response = client.post('/api/friends/remove', json=user, headers=headers)
    assert response.status_code == 200


def test_posts():
    auth_data = {
        "login": "pisunchik",
        "password": "Qwerty1337)"
    }
    response = client.post('/api/auth/sign-in', json=auth_data)
    bearer = response.json()['token']
    headers = {
        "Authorization": f"Bearer {bearer}"
    }

    new_post_form = {
        "content": "string",
        "tags": [
            "string",
            "string1",
            "string2",
            "string3",
        ]
    }
    response = client.post('/api/posts/new', json=new_post_form, headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 7

    public_post_id = response.json()['id']

    response = client.post('/api/posts/new', json=new_post_form)
    assert response.status_code == 401

    invalid_post_form = {
        "content": 1,
        "tags": [
            "string",
            "string1",
            "string2",
            "string3",
        ],
        "zxc": "zxc"
    }
    response = client.post('/api/posts/new', json=invalid_post_form, headers=headers)
    assert response.status_code == 400

    invalid_post_form = {
        "content": 1,
        "tags": [
            "string",
            "string1",
            "string2",
            "string3",
        ],

    }
    response = client.post('/api/posts/new', json=invalid_post_form)
    assert response.status_code == 400

    invalid_post_form = {
        "tags": [
            "string",
            "string1",
            "string2",
            "string3",
        ],
        "zxc": "zxc"
    }
    response = client.post('/api/posts/new', json=invalid_post_form, headers=headers)
    assert response.status_code == 400

    auth_data = {
        "login": "pisunchikZXC",
        "password": "Qwerty1337)"
    }
    response = client.post('/api/auth/sign-in', json=auth_data)
    bearer = response.json()['token']
    headers = {
        "Authorization": f"Bearer {bearer}"
    }

    new_post_form = {
        "content": "string",
        "tags": [
            "string",
            "string1",
            "string2",
            "string3",
        ]
    }
    response = client.post('/api/posts/new', json=new_post_form, headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 7

    not_public_post_id = response.json()['id']

    invalid_post_form = {
        "content": 1,
        "tags": [
            "string",
            "string1",
            "string2",
            "string3",
        ],
        "zxc": "zxc"
    }
    response = client.post('/api/posts/new', json=invalid_post_form, headers=headers)
    assert response.status_code == 400

    invalid_post_form = {
        "content": 1,
        "tags": [
            "string",
            "string1",
            "string2",
            "string3",
        ],
        "zxc": "zxc"
    }
    response = client.post('/api/posts/new', json=invalid_post_form)
    assert response.status_code == 400

    invalid_post_form = {
        "tags": [
            "string",
            "string1",
            "string2",
            "string3",
        ],
        "zxc": "zxc"
    }
    response = client.post('/api/posts/new', json=invalid_post_form, headers=headers)
    assert response.status_code == 400

    auth_data = {
        "login": "pisunchikZXC",
        "password": "Qwerty1337)"
    }
    response = client.post('/api/auth/sign-in', json=auth_data)
    bearer = response.json()['token']
    headers = {
        "Authorization": f"Bearer {bearer}"
    }

    response = client.get(f'/api/posts/{not_public_post_id}', headers=headers)
    assert response.status_code == 200

    response = client.get(f'/api/posts/{public_post_id}', headers=headers)
    assert response.status_code == 200

    response = client.get('/api/posts/fake', params={'postId': 'fake'}, headers=headers)
    assert response.status_code == 404

    response = client.get(f'/api/posts/{None}', headers=headers)
    assert response.status_code == 404

    response = client.get('/api/posts/fake')
    assert response.status_code == 401

    response = client.get('/api/feed/my', headers=headers)
    assert response.status_code == 200

    response = client.get('/api/feed/my?limit=5&offset=2', headers=headers)
    assert response.status_code == 200

    response = client.get('/api/feed/my?limit=5&offset=120', headers=headers)
    assert response.status_code == 200
    assert response.json() == []

    response = client.get('/api/feed/my?limit=51&offset=0', headers=headers)
    assert response.status_code == 400

    response = client.get('/api/feed/my?limit=-1&offset=-1', headers=headers)
    assert response.status_code == 400

    response = client.get('/api/feed/my?limit=5&offset=0')
    assert response.status_code == 401

    response = client.get('/api/feed/my?limit=5', headers=headers)
    assert response.status_code == 200

    response = client.get('/api/posts/feed/pisunchik', headers=headers)
    assert response.status_code == 200

    response = client.get('/api/posts/feed/pisunchikZXC', headers=headers)
    assert response.status_code == 200

    response = client.get('/api/posts/feed/pisunchikZXC')
    assert response.status_code == 401

    auth_data = {
        "login": "pisunchik",
        "password": "Qwerty1337)"
    }
    response = client.post('/api/auth/sign-in', json=auth_data)
    bearer = response.json()['token']
    headers = {
        "Authorization": f"Bearer {bearer}"
    }

    response = client.get(f'/api/posts/{not_public_post_id}', headers=headers)
    assert response.status_code == 404

    response = client.get(f'/api/posts/{public_post_id}', headers=headers)
    assert response.status_code == 200

    response = client.get('/api/posts/feed/pisunchik', headers=headers)
    assert response.status_code == 200

    response = client.get('/api/posts/feed/pisunchikZXC', headers=headers)
    assert response.status_code == 404

    response = client.get('/api/posts/feed/pisunchikZXC')
    assert response.status_code == 401
