## Budget-service
<hr >

### Introduction
Budget-service is small Django REST applications, which helps to create simple budgets.

### Installation
Please follow below steps:
1) `git clone https://github.com/KonradMarzec1991/budget_service.git`
2) `docker-compose up --build`

Fixtures and migrations will be done automatically.
Fixtures will be applied to db only once.
If you do not need any inital data, please comment line `python manage.py load_fixtures` in `entrypoint_local.sh`.

### Usage

#### Authorization
Application uses `simple_jwt` for authorization.
To get token (valid for 1 day), post username and password on
`http://0.0.0.0:8000/api/token/`

![img_1.png](img_1.png)

#### API usage
After getting token, user gets access to endpoints.

![img_3.png](img_3.png)
