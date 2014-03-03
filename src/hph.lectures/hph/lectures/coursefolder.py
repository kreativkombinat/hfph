from Acquisition import aq_inner
from five import grok

from z3c.form import group, field
from zope import schema
from zope.interface import invariant, Invalid
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import getVocabularyRegistry

from plone.dexterity.content import Container

from plone.directives import dexterity, form
from plone.app.textfield import RichText
from plone.namedfile.field import NamedImage, NamedFile
from plone.namedfile.field import NamedBlobImage, NamedBlobFile
from plone.namedfile.interfaces import IImageScaleTraversable

from z3c.relationfield.schema import RelationList, RelationChoice
from plone.formwidget.contenttree import ObjPathSourceBinder


from hph.lectures import MessageFactory as _


class ICourseFolder(form.Schema, IImageScaleTraversable):
    """
    Manage lectures
    """


class CourseFolder(Container):
    grok.implements(ICourseFolder)
    pass


class View(grok.View):
    grok.context(ICourseFolder)
    grok.require('zope2.View')
    grok.name('view')

    def prettify_duration(self, value):
        context = aq_inner(self.context)
        vr = getVocabularyRegistry()
        vocab = vr.get(context, 'hph.lectures.CourseDuration')
        title = _(u"undefined")
        if value is not None:
            for term in vocab:
                if term.value == value:
                    title = term.title
        return title

    def filter_options(self):
        context = aq_inner(self.context)
        vr = getVocabularyRegistry()
        vocab = vr.get(context, 'hph.lectures.CourseType')
        return vocab

    def computed_klass(self, value):
        active_filter = self.request.get('courseType', None)
        klass = 'nav-item-plain'
        if active_filter == value:
            klass = 'active'
        return klass
