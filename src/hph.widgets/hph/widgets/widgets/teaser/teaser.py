# -*- coding: utf-8 -*-
"""Module providing site widget"""
import uuid as uuid_tool

import DateTime
from Acquisition import aq_inner, aq_parent
from Products.Five import BrowserView
from ade25.base.interfaces import IContentInfoProvider
from ade25.panelpage.page import IPage
from ade25.widgets.interfaces import IContentWidgets
from hph.sitecontent.eventitem import IEventItem
from hph.sitecontent.newsentry import INewsEntry
from plone import api
from plone.app.contenttypes.utils import replace_link_variables_by_paths


class WidgetTeaserNews(BrowserView):
    """ Base widget used as placeholder """

    def __call__(self,
                 widget_name='teaser-news',
                 widget_type='teaser-news',
                 widget_mode='view',
                 widget_data=None,
                 **kw):
        self.params = {
            'widget_name': widget_name,
            'widget_type': widget_type,
            'widget_mode': widget_mode,
            'widget_data': widget_data
        }
        return self.render()

    def render(self):
        return self.index()

    @property
    def edit_mode(self):
        if self.params['widget_mode'] == 'edit':
            return True
        return False

    @property
    def record(self):
        return self.params['widget_data']

    def has_content(self):
        if self.widget_content_items():
            return True
        return False

    def widget_uid(self):
        try:
            widget_id = self.record['id']
        except (KeyError, TypeError):
            widget_id = str(uuid_tool.uuid4())
        return widget_id

    def widget_content_items(self):
        return self.recent_news()

    def widget_custom_styles(self):
        if self.record and 'styles' in self.record:
            return self.record['styles']
        else:
            return None

    def widget_content_list_class(self):
        context = aq_inner(self.context)
        css_class = 'c-list c-list--gutter c-list--grid c-list--{}'.format(
            context.UID())
        custom_styles = self.widget_custom_styles()
        if custom_styles:
            class_container = custom_styles['class_container']
            for class_name in class_container.split(' '):
                css_class = '{0} c-list--{1}'.format(
                    css_class,
                    class_name
                )
            if 'custom' in custom_styles:
                css_class = '{0} {1}'.format(
                    css_class,
                    custom_styles['custom']
                )
        return css_class

    @staticmethod
    def time_stamp(item, date_time):
        content_info_provider = IContentInfoProvider(item)
        time_stamp = content_info_provider.time_stamp(date_time)
        return time_stamp

    @staticmethod
    def get_latest_news_items(limit=3):
        portal = api.portal.get()
        items = api.content.find(
            context=portal,
            object_provides=INewsEntry.__identifier__,
            review_state='published',
            sort_on='Date',
            sort_order='reverse',
            sort_limit=limit
        )[:limit]
        return items

    def recent_news(self):
        results = []
        brains = self.get_latest_news_items()
        for brain in brains:
            results.append({
                'title': brain.Title,
                'description': brain.Description,
                'url': brain.getURL(),
                'timestamp': brain.Date,
                'uuid': brain.UID,
                "css_classes": "o-card-list__item--{0}".format(
                    brain.UID
                ),
                'item_object': brain.getObject()
            })
        return results

    @staticmethod
    def widget_more_link():
        portal = api.portal.get()
        more_link = '{0}/nachrichten'.format(portal.absolute_url())
        return more_link


class WidgetTeaserEvents(BrowserView):
    """ Teaser widget for events """

    def __call__(self,
                 widget_name='teaser-events',
                 widget_type='teaser-events',
                 widget_mode='view',
                 widget_data=None,
                 **kw):
        self.params = {
            'widget_name': widget_name,
            'widget_type': widget_type,
            'widget_mode': widget_mode,
            'widget_data': widget_data
        }
        return self.render()

    def render(self):
        return self.index()

    @property
    def edit_mode(self):
        if self.params['widget_mode'] == 'edit':
            return True
        return False

    @property
    def record(self):
        return self.params['widget_data']

    @staticmethod
    def can_edit():
        return not api.user.is_anonymous()

    def has_content(self):
        if self.widget_has_data():
            return True
        return False

    def widget_uid(self):
        try:
            widget_id = self.record['id']
        except (KeyError, TypeError):
            widget_id = str(uuid_tool.uuid4())
        return widget_id

    def widget_content_items(self):
        return self.recent_events()

    def widget_custom_styles(self):
        if self.record and 'styles' in self.record:
            return self.record['styles']
        else:
            return None

    def widget_content_list_class(self):
        context = aq_inner(self.context)
        css_class = 'c-list c-list--gutter c-list--grid c-list--{}'.format(
            context.UID())
        custom_styles = self.widget_custom_styles()
        if custom_styles:
            class_container = custom_styles['class_container']
            for class_name in class_container.split(' '):
                css_class = '{0} c-list--{1}'.format(
                    css_class,
                    class_name
                )
            if 'custom' in custom_styles:
                css_class = '{0} {1}'.format(
                    css_class,
                    custom_styles['custom']
                )
        return css_class

    @staticmethod
    def time_stamp(item, date_time):
        content_info_provider = IContentInfoProvider(item)
        time_stamp = content_info_provider.time_stamp(date_time)
        return time_stamp

    def widget_has_data(self):
        return len(self.get_latest_event_items()) > 0

    def get_latest_event_items(self, limit=3):
        context = aq_inner(self.context)
        if IPage.providedBy(context):
            container = aq_parent(context)
        else:
            container = context
        date_range_query = {'query': DateTime.DateTime(), 'range': 'min'}
        items = api.content.find(
            context=container,
            object_provides=IEventItem.__identifier__,
            review_state='published',
            start=date_range_query,
            sort_on='start',
            sort_limit=limit
        )[:limit]
        return items

    def recent_events(self):
        results = list()
        brains = self.get_latest_event_items()
        for brain in brains:
            results.append({
                'title': brain.Title,
                'description': brain.Description,
                'url': brain.getURL(),
                'timestamp': brain.start,
                'uuid': brain.UID,
                "css_classes": "o-card-list__item--{0}".format(
                    brain.UID
                ),
                'item_object': brain.getObject()
            })
        return results

    @staticmethod
    def widget_more_link():
        portal = api.portal.get()
        more_link = '{0}/@@event-calendar'.format(portal.absolute_url())
        return more_link


class WidgetTeaserLinksInternal(BrowserView):
    """ Base widget used as placeholder """

    def __call__(self,
                 widget_name='teaser-links-internal',
                 widget_type='teaser-links-internal',
                 widget_mode='view',
                 widget_data=None,
                 **kw):
        self.params = {
            'widget_name': widget_name,
            'widget_type': widget_type,
            'widget_mode': widget_mode,
            'widget_data': widget_data
        }
        return self.render()

    def render(self):
        return self.index()

    @property
    def edit_mode(self):
        if self.params['widget_mode'] == 'edit':
            return True
        return False

    @property
    def record(self):
        return self.params['widget_data']

    def has_content(self):
        if self.widget_content_items():
            return True
        return False

    def widget_uid(self):
        try:
            widget_id = self.record['id']
        except (KeyError, TypeError):
            widget_id = str(uuid_tool.uuid4())
        return widget_id

    def widget_item_nodes(self):
        context = aq_inner(self.context)
        ordered_nodes = list()
        storage = IContentWidgets(context)
        stored_widget = storage.read_widget(
            self.widget_uid()
        )
        if stored_widget:
            ordered_nodes = stored_widget["item_order"]
        return ordered_nodes

    def has_widget_item_nodes(self):
        return len(self.widget_item_nodes()) > 0

    def widget_item_content(self, widget_node):
        context = aq_inner(self.context)
        item_content = {
            "uid": widget_node
        }
        storage = IContentWidgets(context)
        stored_widget = storage.read_widget(
            self.widget_uid()
        )
        if stored_widget:
            content_items = stored_widget["items"]
            if content_items:
                try:
                    item_content.update(content_items[widget_node])
                except KeyError:
                    item_content = None
        return item_content

    def get_link_action(self, link):
        context = aq_inner(self.context)
        link_action = replace_link_variables_by_paths(context, link)
        return link_action

    def widget_content_items(self):
        return self.widget_item_nodes()

    def widget_custom_styles(self):
        if self.record and 'styles' in self.record:
            return self.record['styles']
        else:
            return None

    def widget_content_list_class(self):
        context = aq_inner(self.context)
        css_class = 'c-list c-list--gutter c-list--grid c-list--{}'.format(
            context.UID())
        custom_styles = self.widget_custom_styles()
        if custom_styles:
            class_container = custom_styles['class_container']
            for class_name in class_container.split(' '):
                css_class = '{0} c-list--{1}'.format(
                    css_class,
                    class_name
                )
            if 'custom' in custom_styles:
                css_class = '{0} {1}'.format(
                    css_class,
                    custom_styles['custom']
                )
        return css_class

    @staticmethod
    def time_stamp(item, date_time):
        content_info_provider = IContentInfoProvider(item)
        time_stamp = content_info_provider.time_stamp(date_time)
        return time_stamp


class WidgetTeaserLinksExternal(BrowserView):
    """ Base widget used as placeholder """

    def __call__(self,
                 widget_name='teaser-links-external',
                 widget_type='teaser-links-external',
                 widget_mode='view',
                 widget_data=None,
                 **kw):
        self.params = {
            'widget_name': widget_name,
            'widget_type': widget_type,
            'widget_mode': widget_mode,
            'widget_data': widget_data
        }
        return self.render()

    def render(self):
        return self.index()

    @property
    def edit_mode(self):
        if self.params['widget_mode'] == 'edit':
            return True
        return False

    @property
    def record(self):
        return self.params['widget_data']

    def has_content(self):
        if self.widget_content_items():
            return True
        return False

    def widget_uid(self):
        try:
            widget_id = self.record['id']
        except (KeyError, TypeError):
            widget_id = str(uuid_tool.uuid4())
        return widget_id

    def widget_item_nodes(self):
        context = aq_inner(self.context)
        ordered_nodes = list()
        storage = IContentWidgets(context)
        stored_widget = storage.read_widget(
            self.widget_uid()
        )
        if stored_widget:
            ordered_nodes = stored_widget["item_order"]
        return ordered_nodes

    def has_widget_item_nodes(self):
        return len(self.widget_item_nodes()) > 0

    def widget_item_content(self, widget_node):
        context = aq_inner(self.context)
        item_content = {
            "uid": widget_node
        }
        storage = IContentWidgets(context)
        stored_widget = storage.read_widget(
            self.widget_uid()
        )
        if stored_widget:
            content_items = stored_widget["items"]
            if content_items:
                try:
                    item_content.update(content_items[widget_node])
                except KeyError:
                    item_content = None
        return item_content

    def get_link_action(self, link):
        context = aq_inner(self.context)
        link_action = replace_link_variables_by_paths(context, link)
        return link_action

    def widget_content_items(self):
        return self.widget_item_nodes()

    def widget_custom_styles(self):
        if self.record and 'styles' in self.record:
            return self.record['styles']
        else:
            return None

    def widget_content_list_class(self):
        context = aq_inner(self.context)
        css_class = 'c-list c-list--gutter c-list--grid c-list--{}'.format(
            context.UID())
        custom_styles = self.widget_custom_styles()
        if custom_styles:
            class_container = custom_styles['class_container']
            for class_name in class_container.split(' '):
                css_class = '{0} c-list--{1}'.format(
                    css_class,
                    class_name
                )
            if 'custom' in custom_styles:
                css_class = '{0} {1}'.format(
                    css_class,
                    custom_styles['custom']
                )
        return css_class

    @staticmethod
    def time_stamp(item, date_time):
        content_info_provider = IContentInfoProvider(item)
        time_stamp = content_info_provider.time_stamp(date_time)
        return time_stamp

    @staticmethod
    def has_stored_image(image_object):
        context = image_object
        try:
            lead_img = context.image
        except AttributeError:
            lead_img = None
        if lead_img is not None:
            return True
        return False

    def image_tag(self, image_uid):
        image = api.content.get(UID=image_uid)
        if self.has_stored_image(image):
            figure = image.restrictedTraverse('@@figure')(
                image_field_name='image',
                caption_field_name='image_caption',
                scale='ratio-4:3',
                aspect_ratio='4/3',
                lqip=True,
                lazy_load=True
            )
            return figure
        return None
