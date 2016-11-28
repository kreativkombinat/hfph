# -*- coding: UTF-8 -*-
from Acquisition import aq_inner
from Acquisition import aq_parent
from five import grok
from operator import attrgetter
from plone import api
from plone.app.contentlisting.interfaces import IContentListing
from plone.app.textfield import RichText
from plone.app.z3cform.widget import RelatedItemsWidget
from plone.autoform import directives
from plone.dexterity.content import Container
from plone.directives import form
from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.indexer import indexer
from plone.namedfile.field import NamedBlobImage
from plone.namedfile.interfaces import IImageScaleTraversable
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from zope import schema
from zope.schema.vocabulary import getVocabularyRegistry

from hph.publications.publication import IPublication

from hph.faculty import MessageFactory as _


class IFacultyMember(form.Schema, IImageScaleTraversable):
    """
    A faculty staff member
    """
    lastname = schema.TextLine(
        title=_(u"Lastname"),
        description=_(u"Provide last name for better filtering and search"),
        required=True,
    )
    academicRole = schema.Choice(
        title=_(u"Accademic Role or Position"),
        vocabulary=u'hph.faculty.academicRole',
        required=True,
    )
    sidenote = schema.TextLine(
        title=_(u"Sidenote"),
        description=_(u"Optional additional information/sidenote"),
        required=False,
    )
    department = schema.TextLine(
        title=_(u"Department"),
        required=True,
    )
    street = schema.TextLine(
        title=_(u"Street"),
        required=False,
    )
    city = schema.TextLine(
        title=_(u"City"),
        required=False,
    )
    phone = schema.TextLine(
        title=_(u"Phone"),
        required=False,
    )
    fax = schema.TextLine(
        title=_(u"Fax"),
        required=False,
    )
    email = schema.TextLine(
        title=_(u"E-Mail"),
        required=False,
    )
    image = NamedBlobImage(
        title=_(u"Portrait Image"),
        required=False,
    )
    text = RichText(
        title=_(u"Body Text"),
        required=False,
    )
    directives.omitted('publications')
    publications = RelationList(
        title=u"Related Publication Items",
        default=[],
        value_type=RelationChoice(
            title=_(u"Publication"),
            source=ObjPathSourceBinder()),
        required=False,
    )
    # directives.mode(associatedPublications='hidden)
    associatedPublications = schema.List(
        title=_(u"Associated publications"),
        description=_(u"Content will be auto generated by assignment view"),
        value_type=schema.TextLine(
            title=_(u"Publication Unique Identifier")
        ),
        required=False
    )



@indexer(IFacultyMember)
def lastNameIndexer(obj):
    return obj.lastname
grok.global_adapter(lastNameIndexer, name="lastname")


@indexer(IFacultyMember)
def academicRoleIndexer(obj):
    return obj.academicRole
grok.global_adapter(academicRoleIndexer, name="academicRole")


class FacultyMember(Container):
    grok.implements(IFacultyMember)


class View(grok.View):
    """ Faculty member view """
    grok.context(IFacultyMember)
    grok.require('zope2.View')
    grok.name('view')

    def parent_url(self):
        context = aq_inner(self.context)
        parent = aq_parent(context)
        return parent.absolute_url()

    def item_owner(self):
        if api.user.is_anonymous():
            return False
        context = aq_inner(self.context)
        is_owner = False
        user = api.user.get_current()
        if user.getId() in context.listCreators():
            is_owner = True
        return is_owner

    def content_filter(self):
        context = aq_inner(self.context)
        container = aq_parent(context)
        tmpl = container.restrictedTraverse('@@content-filter-faculty')()
        return tmpl

    def filter_options(self):
        context = aq_inner(self.context)
        vr = getVocabularyRegistry()
        vocab = vr.get(context, 'hph.faculty.academicRole')
        return vocab

    def computed_klass(self, value):
        context = aq_inner(self.context)
        active_filter = getattr(context, 'academicRole', None)
        klass = 'nav-item-plain'
        if active_filter == value:
            klass = 'active'
        return klass

    def show_address(self):
        context = aq_inner(self.context)
        display = False
        if context.street or context.email:
            display = True
        return display


class Publications(grok.View):
    grok.context(IFacultyMember)
    grok.require('zope2.View')
    grok.name('publications')

    def update(self):
        self.has_publications = len(self.publications()) > 0

    def parent_url(self):
        context = aq_inner(self.context)
        parent = aq_parent(context)
        return parent.absolute_url()

    def filter_options(self):
        context = aq_inner(self.context)
        vr = getVocabularyRegistry()
        vocab = vr.get(context, 'hph.faculty.academicRole')
        return vocab

    def computed_klass(self, value):
        context = aq_inner(self.context)
        active_filter = getattr(context, 'academicRole', None)
        klass = 'app-nav-list-item'
        if active_filter == value:
            klass += 'app-nav-list-item-active'
        return klass

    def associated_publications(self):
        context = aq_inner(self.context)
        assigned = getattr(context, 'associatedPublications', None)
        return assigned

    def get_publication_details(self, uuid):
        item = api.content.get(UID=uuid)
        return item

    def publications(self):
        context = aq_inner(self.context)
        publications = [self.get_publication_details(item)
                        for item in self.associated_publications()]
        sorted_publications = sorted(
            publications,
            key=attrgetter('publicationYear'),
            reverse=True
        )
        return sorted_publications
