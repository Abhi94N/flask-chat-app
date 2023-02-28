# flask-chat-app

# Setup 
1. `python3.11 -m venv venv --without-pip`
2. `source venv/bin/activate/`
3. `pip install flask flask-socketio`
4. run by `python main.py` where the flask app is running
5. templates must be in `template` folder in root. this is where your html templates will reside
6. templates must be in the `static` folder in root. This is where your static assets will reside
7. add cdnjs for socketio to head of html base page
8. add blocks to inject code
```html
        <div class="content">
            <!-- dynamically inject code -->
            {% block content %}

            {% endblock %}
        </div>
```
10. override blocks and inherit code using

```html
{% extends 'base.html' %}
```
11. 