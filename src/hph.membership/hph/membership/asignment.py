# -*- coding: utf-8 -*-
"""Module providing responsible user selection and asignment"""

from Acquisition import aq_inner
from five import grok
from plone import api
from Products.CMFCore.interfaces import IContentish

from hph.membership import MessageFactory as _


class AsignmentView(grok.View):
    """ Group selection to provide prefiltering of users """
    grok.context(IContentish)
    grok.require('cmf.ManagePortal')
    grok.name('asignment-view')

    def selectable_groups(self):
        groups = [
            'Mediengruppe',
            'Lehrende',
            'HiWi',
            'Mediengruppe',
            'Tutoren'
        ]
        return groups


class AsignmentUsers(grok.View):
    """ User selection from preselected group """
    grok.context(IContentish)
    grok.require('cmf.ManagePortal')
    grok.name('asignment-users')

    @property
    def traverse_subpath(self):
        return self.subpath

    def publishTraverse(self, request, name):
        if not hasattr(self, 'subpath'):
            self.subpath = []
        self.subpath.append(name)
        return self

    def groupname(self):
        return self.traverse_subpath[0]

    def group_users(self):
        return api.user.get_users(groupname=self.groupname())

    def selectable_users(self):
        context = aq_inner(self.context)
        users = []
        idx = 0
        for record in self.group_users():
            idx += 1
            user = api.user.get(username=record.getId())
            userid = user.getId()
            info = {}
            info['idx'] = idx
            info['userid'] = userid
            info['fullname'] = user.getProperty('fullname', '') or userid
            info['email'] = user.getProperty('email', _(u"No email provided"))
            info['roles'] = api.user.get_roles(username=userid, obj=context)
            users.append(info)
        return users

    def get_asignment(self, userid):
        context = aq_inner(self.context)
        roles = api.user.get_roles(username=userid, obj=context)
        if 'Contributor' in roles:
            return True
        return False


class Asignment(grok.View):
    """ Process user asignment """
    grok.context(IContentish)
    grok.require('cmf.ManagePortal')
    grok.name('asignment')

    @property
    def traverse_subpath(self):
        return self.subpath

    def publishTraverse(self, request, name):
        if not hasattr(self, 'subpath'):
            self.subpath = []
        self.subpath.append(name)
        return self

    def render(self):
        context = aq_inner(self.context)
        user_roles = ['Reader', 'Editor', 'Contributor']
        userid = self.traverse_subpath[0]
        action = self.traverse_subpath[1]
        if action == 'revoke':
            api.user.revoke_roles(
                username=userid,
                roles=user_roles,
                obj=context,
            )
        else:
            api.user.grant_roles(
                username=userid,
                roles=user_roles,
                obj=context
            )
        next_url = '{0}/@asignment-view?updated=true'.format(
            context.absolute_url())
        api.portal.show_message(
            message=_(u"Responsible user asignment successfully updated"),
            request=self.request)
        return self.request.response.redirect(next_url)
