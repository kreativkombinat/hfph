from five import grok

from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.interfaces import IVocabularyFactory

from hph.publications import MessageFactory as _


class PublicationMediaVocabulary(object):
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        TYPES = {
            _(u"Book"): 'book',
            _(u"Magazine"): 'magazine',
            _(u"DVD/CD"): 'digital',
        }
        return SimpleVocabulary([SimpleTerm(value, title=title)
                                for title, value
                                in TYPES.iteritems()])
grok.global_utility(PublicationMediaVocabulary,
                    name=u"hph.pubications.publicationMedia")


class PublicationSeriesVocabulary(object):
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        TYPES = {
            _(u"Global Culture"): 'global-culture',
            _(u"Solidarity"): 'solidarity',
            _(u"Philosophy"): 'philosophy',
            _(u"Contexts"): 'contexts',
            _(u"Munich Philosophy"): 'munich',
            _(u"Theology"): 'theology',
        }
        return SimpleVocabulary([SimpleTerm(value, title=title)
                                for title, value
                                in TYPES.iteritems()])
grok.global_utility(PublicationSeriesVocabulary,
                    name=u"hph.pubications.publicationSeries")