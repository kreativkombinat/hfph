from five import grok

from z3c.form import group, field
from zope import schema
from zope.interface import invariant, Invalid
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from plone.dexterity.content import Container

from plone.directives import dexterity, form
from plone.app.textfield import RichText
from plone.namedfile.field import NamedImage, NamedFile
from plone.namedfile.field import NamedBlobImage, NamedBlobFile
from plone.namedfile.interfaces import IImageScaleTraversable

from z3c.relationfield.schema import RelationList, RelationChoice
from plone.formwidget.contenttree import ObjPathSourceBinder


from hph.membership import MessageFactory as _


class IWorkspace(form.Schema, IImageScaleTraversable):
    """
    Personal workspace container for members
    """


class Workspace(Container):
    grok.implements(IWorkspace)
    pass


class View(grok.View):
    grok.context(IWorkspace)
    grok.require('cmf.ModifyPortalContent')
    grok.name('view')
