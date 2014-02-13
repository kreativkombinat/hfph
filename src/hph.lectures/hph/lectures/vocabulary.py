from five import grok

from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.interfaces import IVocabularyFactory

from hph.lectures import MessageFactory as _


class CourseDurationVocabulary(object):
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        TYPES = {
            _(u"1 hour"): '1-hour',
            _(u"2 hour"): '2-hour',
            _(u"3 hour"): '3-hour'
        }
        return SimpleVocabulary([SimpleTerm(value, title=title)
                                for title, value
                                in TYPES.iteritems()])
grok.global_utility(CourseDurationVocabulary,
                    name=u"hph.lectures.CourseDuration")


class CourseTypeVocabulary(object):
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        TYPES = {
            _(u"Advanced seminar"): 'advanced',
            _(u"Colloquium"): 'colloquium',
            _(u"Introductory seminar source"): 'introductory-seminar-course',
            _(u"Exercise"): 'exercise',
            _(u"Lecture"): 'lecture'
        }
        return SimpleVocabulary([SimpleTerm(value, title=title)
                                for title, value
                                in TYPES.iteritems()])
grok.global_utility(CourseTypeVocabulary, name=u"hph.lectures.CourseType")
