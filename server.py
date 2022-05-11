"""Entry point for the app."""

from flask import Flask, jsonify, request, redirect, url_for, render_template
from flask_login import login_required, current_user
from importlib import import_module

import flask
import flask_login
import json
import requests

from lib.core import config, exceptions
from lib.models.users import User
from lib.models import db, utils
import lib.core.utils

configuration = config.get_config()

app = Flask(__name__)
app.secret_key = configuration['secret_key']
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

CREATED = 201
BAD_REQUEST = 400
FORBIDDEN = 403
NOT_FOUND = 404

# ***
# Auth stuff
# ***


@login_manager.user_loader
def user_loader(id):
    """flask_login stuff."""
    user = User.query.get(id)
    if user is None:
        return
    return user


@login_manager.request_loader
def request_loader(request):
    """flask_login stuff."""
    username = request.form.get('username')
    password = request.form.get('password')

    user = User.query.filter(User.name == username).all()
    if user == []:
        return
    user = user[0]

    salt, hash = utils.hash_password(password, user.salt)
    if hash == user.hash:
        return user
    else:
        return

# ***
# Views and other endpoints
# ***


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User will be served the login page or will be logged in."""
    if request.method == 'GET':
        return _render_template('login.html')

    elif request.method == 'POST':
        data = request.get_json()
        username = data.get('username', None).lower()
        password = data.get('password', None)
        captcha_code = data.get('captcha_code', None)

        if not captcha_code:
            return jsonify({
                'success': False,
                'message': 'Captcha code was not solved.'
            })

        captcha_url = 'https://www.google.com/recaptcha/api/siteverify'
        data = {
            'secret': configuration['login_captcha_secret'],
            'response': captcha_code
        }
        captcha_verification = json.loads(requests.post(captcha_url,
                                                        data=data).text)
        if not captcha_verification['success']:
            return jsonify({
                'success': False,
                'message': 'Captcha verification failed. Please try again.'
            })

        user = User.query.filter(User.name == username).first()
        if not user:
            return jsonify({
                'success': False,
                'message': 'The username or password is incorrect.'
            })
        salt, hash = utils.hash_password(password, user.salt)
        if hash == user.hash:
            flask_login.login_user(user)
            return jsonify({'success': True})
        else:
            return jsonify({
                'success': False,
                'message': 'The username or password is incorrect.'
            })


@app.route('/logout')
@login_required
def logout():
    """The user is redirected to the login page after logging them out."""
    flask_login.logout_user()
    return redirect(url_for('root'))


@app.route('/')
def root():
    """Serve the home page of the web app."""
    if current_user.__dict__.get('id', None):
        return _render_template('home.html')
    else:
        return _render_template('landing_page.html')


@app.route('/signup', methods=['GET', 'POST'])
def singup():
    """Serve the home page of the web app."""
    if current_user.__dict__.get('id', None):
        return _render_template('home.html')

    if request.method == 'GET':
        return _render_template('signup.html')

    else:
        data = request.get_json()
        username = data.get('username', '').lower()
        password = data.get('password', '')
        email = data.get('emailId', '').lower()
        confirm_password = data.get('confirm_password', '')
        captcha_code = data.get('captcha_code', None)

        if not captcha_code:
            return jsonify({
                'success': False,
                'message': 'Captcha code was not solved.'
            })

        captcha_url = 'https://www.google.com/recaptcha/api/siteverify'
        data = {
            'secret': configuration['signup_captcha_secret'],
            'response': captcha_code
        }
        captcha_verification = json.loads(requests.post(captcha_url,
                                                        data=data).text)
        if not captcha_verification['success']:
            return jsonify({
                'success': False,
                'message': 'Captcha verification failed. Please try again.'
            })

        if len(username) < 5 or len(username) > 100:
            return jsonify({
                'success': False,
                'message': 'Username should be 5 to 100 characters long.'
            })

        if len(password) < 12 or len(password) > 100:
            return jsonify({
                'success': False,
                'message': 'Password should be 12 to 100 characters long.'
            })

        if password != confirm_password:
            return jsonify({
                'success': False,
                'message': 'Passwords do not match.'
            })

        user = User.query.filter(User.name == username).first()
        if user:
            return jsonify({
                'success': False,
                'message': 'This username is taken.'
            })

        new_user = User(password=password, name=username, email=email)
        db.db_session.add(new_user)
        db.db_session.commit()
        flask_login.login_user(new_user)
        return jsonify({
            'success': True
        })


# White list all functions that can be reached by an AJAX call.
INT_AJAX_REGISTRY = {
    'user': {
        'views': ['get_dashboard_data']
    },
    'audit': {
        'views': ['submit_for_audit', 'get_applications_list',
                  'get_application_details', 'cancel_application']
    },
    'profile': {
        'views': ['submit_for_password_change', 'submit_for_verify_email',
                  'get_emailid', 'get_email_verification_status']
    },
    'policy': {
        'views': ['get_approved_dapps', 'get_contract_info',
                  'submit_policy_application', 'get_policy_details',
                  'get_policies_list', 'check_fee_paid'],
    },
    'claim': {
        'views': ['get_claimable_policy_list', 'get_contract_info',
                  'raise_claim', 'get_claim_details', 'get_claims_list'],
    }
}

EXT_AJAX_REGISTRY = {
    'list_dapp': {
        # 'views': ['get_dapp_usage_data']
    },
    'profile': {
        'views': ['send_password_reset_mail', 'password_change',
                  'password_reset_verification', 'email_verification']
    },
    'policy': {
        'views': ['get_approved_dapps', 'get_contract_info',
                  'submit_policy_application', 'check_fee_paid',
                  'get_policy_details'],
    }
}


@app.route('/ajax', methods=['GET', 'POST'])
@login_required
def iajax():
    """Allowed only for logged in users."""
    return _ajax(INT_AJAX_REGISTRY)


@app.route('/eajax', methods=['GET', 'POST'])
def eajax():
    """Allowed for all users."""
    return _ajax(EXT_AJAX_REGISTRY)


def _ajax(registry):
    """Common entry point for all ajax calls.

    Query string must have 3 params:
        module: Module that you're interacting with.
        file: Where the function is present.
        method: Function being called.

    POST data should contain a stringified json object which and be available
    as kwargs to the registered function.

    Data returned by the function will be jsonified and returned to the client.
    """
    # import pudb; pudb.set_trace();
    module = request.args.get('module')
    file = request.args.get('file')
    method = request.args.get('method')
    try:
        kwargs = request.get_json()
    except:
        return jsonify({
            'success': False,
            'message': 'Could not parse request JSON'
        }), BAD_REQUEST

    try:
        if method not in registry[module][file]:
            raise Exception()
        function = getattr(import_module('.'.join(['lib', module, file])),
                           method)
    except:
        return jsonify({
            'success': False,
            'message': 'Method not found.'
        }), NOT_FOUND

    try:
        data = function(**kwargs)
        db.db_session.commit()
        return jsonify({'success': True, 'data': data})

    except exceptions.UserError as e:
        db.db_session.rollback()
        return jsonify(lib.core.utils.process_error(e))

    except Exception as e:
        # TODO: Log errors
        # Discard all changes if an error occurs
        if configuration['debug']:
            print(e)
        db.db_session.rollback()
        return jsonify({
            'success': False,
            'message': 'Unhandled exception, session rolled back.'
        }), BAD_REQUEST


INTERNAL_PAGE_REGISTRY = {
    'audit': 'dapp_developers.html',
    'buy_insurance': 'buy_insurance.html',
    'policies': 'policies.html',
    'claims': 'claims.html',
    'profile': 'profile.html',
    'contact': 'contact.html'
}


@app.route('/insurance/<file>')
@login_required
def internal_page(file):
    """Common handler for internal pages which can be used after logging in."""
    template_to_render = INTERNAL_PAGE_REGISTRY.get(file, None)
    if template_to_render:
        return _render_template(template_to_render)
    else:
        # TODO: Proper 404 page
        return _render_template('404.html'), NOT_FOUND


def _template_loader(registry, module, file):
    """Internal method to render templates that are registered."""
    if not (module in registry.keys() and
            file in registry[module]):
        return _render_template('404.html'), NOT_FOUND

    return _render_template(module + '/' + file + '.html')


INT_TEMPLATE_REGISTRY = {
    'developer': ['new_application', 'list_applications',
                  'application_details'],
    'insuree': ['new_policy', 'policy_details', 'list_policies',
                'new_claim', 'claim_details', 'list_claims'],
    'profile': ['edit_profile']
}


@app.route('/<module>/<file>')
@login_required
def template_loader(module, file):
    """Load templates of different modules."""
    return _template_loader(INT_TEMPLATE_REGISTRY, module, file)


EXT_TEMPLATE_REGISTRY = {
    # 'dapp': ['details'],
    'profile': ['email_verification', 'forgot_password', 'password_reset'],
    'insuree': ['external_policy', 'external_policy_details']
}


@app.route('/ext/<module>/<file>')
def external_template_loader(module, file):
    """Load pages that don't require users to be logged in."""
    return _template_loader(EXT_TEMPLATE_REGISTRY, module, file)

# @app.route('/templates/components/<string:name>.html')
# def component_loader(name):
#     """Load KO components."""
#     allowed_components = {
#         'cocoon-input',
#         'list-receivers',
#         'receiver-input',
#         'token-input',
#     }
#     if name in allowed_components:
#         return _render_template('components/' + name + '.html')
#     return 'Component not found', 404


@app.route('/robots.txt')
def robots():
    """If you want a file to be served from the root directory add a route here.

    The file should be placed in the static directory.
    """
    from lib.models.misc import Setting
    live_status = Setting.get_value_by_section_option('global',
                                                      'live_status',
                                                      cast=int
                                                      )
    if live_status != 0:
        return '''
User-agent: *
Disallow: /
Crawl-delay: 12000000
'''

    return flask.send_from_directory(app.static_folder, request.path[1:])


@app.route('/sitemap.xml')
def sitemap():
    """Return sitemap."""
    return flask.send_from_directory(app.static_folder, request.path[1:])


@app.route('/join_us', methods=['POST'])
def join_us():
    """Collect responses from the landing page.

    This is not under /ajax because we don't expect users to be logged in while
    filling this form.
    """
    from lib.models.users import JoinUs
    interests = request.form.getlist('interest[]')
    email = request.form.get('email')
    join_us = JoinUs.query.filter(JoinUs.email == email).first()

    if join_us:
        join_us.insuree = 'insuree' in interests or join_us.insuree
        join_us.auditor = 'auditor' in interests or join_us.auditor
        join_us.bounty_hunter = ('bounty_hunter' in interests or
                                 join_us.bounty_hunter)
        join_us.agent = 'agent' in interests or join_us.agent
        join_us.developer = 'developer' in interests or join_us.developer
    else:
        join_us = JoinUs(
            'insuree' in interests,
            'bounty_hunter' in interests,
            'auditor' in interests,
            'agent' in interests,
            'developer' in interests,
            email
        )
    db.db_session.add(join_us)
    db.db_session.commit()
    return jsonify({'success': True})


@app.route('/index.html')
def index():
    """Redirect /index.html to /."""
    return redirect(url_for('root'))


def _render_template(name):
    from lib.models.misc import Setting
    return render_template(name, Setting=Setting)


@app.errorhandler(404)
def page_not_found(e):
    """Return 404 error page if a route is not found.

    Change this to return a HTML Page in the future.
    """
    errors = {}
    errors['errors'] = True
    errors['type'] = 'Not found'
    return jsonify(errors), NOT_FOUND


@app.errorhandler(401)
def redirect_to_login(e):
    """Required for flask login."""
    return redirect(url_for('login'))


@app.teardown_appcontext
def shutdown_session(exception=None):
    """Required to ensure clean connection termination."""
    from lib.models import db
    db.db_session.remove()


@app.route('/status')
def status():
    """Load balancer health check endpoint."""
    return 'OK'


def setup():
    """Any processing that has to be performed before the server is started."""
    pass


if __name__ == '__main__':
    setup()
    print ('Using config: ', str(configuration['env']))
    app.run(
        host=configuration['host'],
        port=configuration['port'],
        threaded=True,
        debug=configuration['debug']
    )
