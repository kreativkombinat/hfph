from Acquisition import aq_inner
from five import grok
from zope import schema
from zope.component import getUtility
from zope.lifecycleevent import modified

from plone.directives import form
from plone.dexterity.content import Container
from plone.namedfile.interfaces import IImageScaleTraversable
from Products.statusmessages.interfaces import IStatusMessage

from hph.membership.tool import IHPHMemberTool

from hph.membership import MessageFactory as _


class IMemberFolder(form.Schema, IImageScaleTraversable):
    """
    Container for member workspaces
    """
    importable = schema.TextLine(
        title=_(u"Importable API Records"),
        required=False,
    )


class MemberFolder(Container):
    grok.implements(IMemberFolder)
    pass


class View(grok.View):
    grok.context(IMemberFolder)
    grok.require('zope2.View')
    grok.name('view')


class UpdateRecords(grok.View):
    grok.context(IMemberFolder)
    grok.require('cmf.ManagePortal')
    grok.name('update-member-records')

    def render(self):
        new_records = self.get_importable_records()
        IStatusMessage(self.request).addStatusMessage(
            _(u"External records stored for import"),
            type='info')
        here_url = self.context.absolute_url()
        next_url = '{0}?imported_records={1}'.format(here_url, new_records)
        return self.request.response.redirect(next_url)

    def get_importable_records(self):
        context = aq_inner(self.context)
        tool = getUtility(IHPHMemberTool)
        records = tool.get()
        setattr(context, 'importable', records)
        modified(context)
        context.reindexObject(idxs='modified')
        return records
