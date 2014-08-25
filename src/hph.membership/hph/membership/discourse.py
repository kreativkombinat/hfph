# -*- coding: UTF-8 -*-
"""Module providing sso token consumer for external discourse installation"""

import base64
import hmac
import hashlib
import urlparse

try:  # py3
    from urllib.parse import unquote, urlencode
except ImportError:
    from urllib import unquote, urlencode

from requests.exceptions import HTTPError

from Acquisition import aq_inner
from DateTime import DateTime
from five import grok
from plone import api
from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.directives import form
from zope import schema
from zope.interface import Interface
from z3c.form import button
from z3c.form.interfaces import HIDDEN_MODE

from hph.membership import MessageFactory as _


class IDiscourseSigninForm(Interface):
    """ Login form schema """

    ac_name = schema.TextLine(
        title=_(u'Login Name'),
        required=True,
    )

    ac_password = schema.Password(
        title=_(u'Password'),
        required=True,
    )

    came_from = schema.TextLine(
        title=_(u'Came From'),
        required=False,
    )
    sso = schema.TextLine(
        title=_(u'SSO payload'),
        required=False,
    )
    sig = schema.TextLine(
        title=_(u'SSO Signature'),
        required=False,
    )


class DiscourseSigninForm(form.SchemaForm):
    """ Implementation of the login form """
    grok.context(INavigationRoot)
    grok.require('zope2.View')
    grok.name('signin-form')

    schema = IDiscourseSigninForm

    id = "LoginForm"
    label = _(u"Log in")
    description = _(u"Please enter your credentials to verify SSO login")

    ignoreContext = True

    # render = ViewPageTemplateFile('templates/login.pt')

    prefix = ""

    def update(self):
        self.request.set('disable_border', True)
        super(DiscourseSigninForm, self).update()

    def updateActions(self):
        super(DiscourseSigninForm, self).updateActions()
        self.actions['signin'].addClass("btn btn-primary")

    def updateWidgets(self):
        try:
            auth = self.context.acl_users.credentials_cookie_auth
        except:
            try:
                auth = self.context.cookie_authentication
            except:
                auth = None
        if auth:
            self.fields['ac_name'].__name__ = auth.get('name_cookie',
                                                       '__ac_name')
            self.fields['ac_password'].__name__ = auth.get('pw_cookie',
                                                           '__ac_password')
        else:
            self.fields['ac_name'].__name__ = '__ac_name'
            self.fields['ac_password'].__name__ = '__ac_password'

        super(DiscourseSigninForm, self).updateWidgets(prefix="")
        self.widgets['came_from'].mode = HIDDEN_MODE
        self.widgets['sso'].mode = HIDDEN_MODE
        self.widgets['sig'].mode = HIDDEN_MODE

    @button.buttonAndHandler(_('Log in'), name='signin')
    def handleLogin(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        membership_tool = api.portal.get_tool(name='portal_membership')
        if membership_tool.isAnonymousUser():
            self.request.response.expireCookie('__ac', path='/')
            email_login = api.portal.get_tool(name='portal_properties') \
                .site_properties.getProperty('use_email_as_login')
            if email_login:
                api.portal.show_message(
                    _(u'Login failed. Both email address and password are case'
                      u' sensitive, check that caps lock is not enabled.'),
                    self.request,
                    type='error')
            else:
                api.portal.show_message(
                    _(u'Login failed. Both login name and password are case '
                      u'sensitive, check that caps lock is not enabled.'),
                    self.request,
                    type='error')
            return

        member = membership_tool.getAuthenticatedMember()
        login_time = member.getProperty('login_time', '2000/01/01')
        if not isinstance(login_time, DateTime):
            login_time = DateTime(login_time)
        initial_login = login_time == DateTime('2000/01/01')
        if initial_login:
            # TODO: Redirect if this is initial login
            pass

        must_change_password = member.getProperty('must_change_password', 0)

        if must_change_password:
            # TODO: This user needs to change his password
            pass

        membership_tool.loginUser(self.request)

        api.portal.show_message(
            _(u"You are now logged in."), self.request, type="info")
        if data['came_from']:
            came_from = data['came_from']
        else:
            came_from = self.context.portal_url()
        self.request.response.redirect(came_from)


class DiscourseError(HTTPError):
    """ A generic error while attempting to communicate with Discourse """


class DiscourseSSOHandler(grok.View):
    """ Discourse SSO endpoint that handles user login
        and secret validation and digestion
    """
    grok.context(INavigationRoot)
    grok.require('zope2.View')
    grok.name('discourse-sso')

    def render(self):
        context = aq_inner(self.context)
        portal_url = api.portal.get().absolute_url()
        actual_url = self.request.get('ACTUAL_URL')
        if not actual_url.startswith('http://'):
            msg = _(u"The Discourse SSO endpoint can only be accessed via "
                    u"SSL since we do not support transfer of authentication "
                    u"tokens via unencrypted connections.")
            api.portal.show_message(msg, self.request, type='info')
            error_page = '{0}/@@discourse-sso-error'.format(portal_url)
            return self.request.response.redirect(error_page)
        discourse_url = self.get_stored_records(token='discourse_url')
        sso_secret = self.get_stored_records(token='discourse_sso_secret')
        if not discourse_url or not sso_secret:
            msg = _(u"The Discourse SSO endpoint has not been configured yet")
            api.portal.show_message(msg, self.request, type='info')
            error_page = '{0}/@@discourse-sso-error'.format(portal_url)
            return self.request.response.redirect(error_page)
        payload = self.request.get('sso')
        signature = self.request.get('sig')
        discourse_url = self.get_stored_records(token='discourse_url')
        sso_secret = self.get_stored_records(token='discourse_sso_secret')
        if api.user.is_anonymous():
            here_url = context.absolute_url() + '/@@discourse-sso'
            came_from = '{0}?sso={1}&sig={2}'.format(here_url,
                                                     payload,
                                                     signature)
            login_url = '{0}/@@signin-form?came_from={1}'.format(
                portal_url, came_from)
            return self.request.response.redirect(login_url)

        try:
            nonce = self.sso_validate(payload, signature, sso_secret)
        except DiscourseError as e:
            return 'HTTP400 Error {}'.format(e)  # Todo: implement handler
        user = api.user.get_current()
        url = self.sso_redirect_url(nonce,
                                    sso_secret,
                                    user.getProperty('email'),
                                    user.getId(),
                                    user.getProperty('fullname'))
        return self.request.response.redirect(discourse_url + url)

    def is_equal(self, a, b):
        """ Constant time comparison """
        if len(a) != len(b):
            return False
        result = 0
        for x, y in zip(a, b):
            result |= ord(x) ^ ord(y)
        return result == 0

    def get_stored_records(self, token):
        key_base = 'hph.membership.interfaces.IHPHMembershipSettings'
        key = key_base + '.' + token
        return api.portal.get_registry_record(key)

    def sso_validate(self, payload, signature, secret):
        """
            payload: provided by Discourse HTTP call as sso GET param
            signature: provided by Discourse HTTP call as sig GET param
            secret: the secret key you entered into Discourse sso secret

            return value: The nonce intended to validate the redirect URL
        """
        if None in [payload, signature]:
            raise DiscourseError('No SSO payload or signature.')

        if not secret:
            raise DiscourseError('Invalid secret..')

        payload = unquote(payload)
        if not payload:
            raise DiscourseError('Invalid payload..')

        decoded = base64.decodestring(payload)
        if 'nonce' not in decoded:
            raise DiscourseError('Invalid payload..')

        h = hmac.new(secret, payload, digestmod=hashlib.sha256)
        this_signature = h.hexdigest()

        if not self.is_equal(this_signature, signature):
            raise DiscourseError('Payload does not match signature.')

        # nonce = decoded.split('=')[1]

        sso = urlparse.parse_qs(payload.decode('base64'))
        nonce = sso['nonce'][0]

        return nonce

    def sso_redirect_url(self,
                         nonce,
                         secret,
                         email,
                         external_id,
                         username,
                         **kwargs):
        """
            nonce: returned by sso_validate()
            secret: the secret key you entered into Discourse sso secret
            user_email: email address of the user who logged in
            user_id: the internal id of the logged in user
            user_username: username of the logged in user (an email address)

            return value:
            URL to redirect users back to discourse, now logged in as username
        """
        kwargs.update({
            'nonce': nonce,
            'email': email,
            'external_id': external_id,
            'username': username
        })

        return_payload = base64.encodestring(urlencode(kwargs))
        h = hmac.new(secret, return_payload, digestmod=hashlib.sha256)
        query_string = urlencode({'sso': return_payload, 'sig': h.hexdigest()})

        return '/session/sso_login?%s' % query_string


class DiscourseSSOError(grok.View):
    """ Discourse SSO endpoint error page """
    grok.context(INavigationRoot)
    grok.require('zope2.View')
    grok.name('discourse-sso-error')
