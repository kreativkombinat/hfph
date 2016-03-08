from Products.Archetypes.Marshall import PrimaryFieldMarshaller
from Products.Archetypes.TemplateMixin import TemplateMixin
from Products.Archetypes.SQLStorage import MySQLSQLStorage
try:
    from Products.CMFCore import permissions as CMFCorePermissions
except:
    from Products.CMFCore import CMFCorePermissions
from config import PROJECTNAME
from Products.LinguaPlone.public import *

schema = BaseSchema +  Schema((
#    StringField(
#        name='title',
#        required=1,
#        searchable=1,
#        default_method='getSurname',
#        accessor='Title',
#        widget=StringWidget(
#            label='Surname',
#            label_msgid='surname',
#            visible={'edit': 'visible','view' : 'invisible'},
#            i18n_domain='hfph',
#        ),
#    ),
    StringField('Name',
                default_output_type='image/jpeg',
                widget=StringWidget(label='Name',i18n_domain='hfph',label_msgid='name'),
                ),
    StringField('Surname',
                default_output_type='image/jpeg',
                #storage=MySQLSQLStorage(),
                widget=StringWidget(label='Surname',i18n_domain='hfph',label_msgid='surname'),
                ),
    StringField('akTitle',
                default_output_type='image/jpeg',
                #storage=MySQLSQLStorage(),
                widget=StringWidget(label='Title',i18n_domain='hfph',label_msgid='ak_title'),
                ),
    StringField('Profession',
                default_output_type='image/jpeg',
                #storage=MySQLSQLStorage(),
                widget=StringWidget(label='profession',i18n_domain='hfph',label_msgid='profession'),
                ),
    StringField('Country',
                default_output_type='image/jpeg',
                #storage=MySQLSQLStorage(),
                widget=StringWidget(label='Country',i18n_domain='hfph',label_msgid='country'),
                ),
    StringField('City',
                default_output_type='image/jpeg',
                #storage=MySQLSQLStorage(),
                widget=StringWidget(label='City',i18n_domain='hfph',label_msgid='city'),
                ),
    StringField('plz',
                default_output_type='image/jpeg',
                #storage=MySQLSQLStorage(),
                widget=StringWidget(label='zip',i18n_domain='hfph',label_msgid='plz'),
                ),
    StringField('tel1',
                default_output_type='image/jpeg',
                #storage=MySQLSQLStorage(),
                widget=StringWidget(label='tel1',i18n_domain='hfph',label_msgid='tel1'),
                ),
    StringField('tel',
                default_output_type='image/jpeg',
                #storage=MySQLSQLStorage(),
                widget=StringWidget(label='tel',i18n_domain='hfph',label_msgid='tel'),
                ),
    StringField('tel2',
                default_output_type='image/jpeg',
                #storage=MySQLSQLStorage(),
                widget=StringWidget(label='tel2',i18n_domain='hfph',label_msgid='tel2'),
                ),
    StringField('Email',
                default_output_type='image/jpeg',
                #storage=MySQLSQLStorage(),
                widget=StringWidget(label='e-mail',i18n_domain='hfph',label_msgid='email'),
                ),
    StringField('Street',
                default_output_type='image/jpeg',
                #storage=MySQLSQLStorage(),
                widget=StringWidget(label='Street',i18n_domain='hfph',label_msgid='street'),
                ),
    StringField('Street2',
                default_output_type='image/jpeg',
                #storage=MySQLSQLStorage(),
                widget=StringWidget(label='Street2',i18n_domain='hfph',label_msgid='street2'),
                ),
    StringField('Homepage',
                default_output_type='image/jpeg',
                #storage=MySQLSQLStorage(),
                widget=StringWidget(label='Homepage',i18n_domain='hfph',label_msgid='homepage'),
                ),
		
    StringField('Semester',
                default_output_type='image/jpeg',
                #storage=MySQLSQLStorage(),
                widget=StringWidget(label='Semester',i18n_domain='hfph',label_msgid='semester'),
                ),
    StringField('Degree',
                default_output_type='image/jpeg',
                #storage=MySQLSQLStorage(),
                widget=StringWidget(label='Degree',i18n_domain='hfph',label_msgid='degree'),
                ),
    StringField('Institution',
                default_output_type='image/jpeg',
                #storage=MySQLSQLStorage(),
                widget=StringWidget(label='Institution',i18n_domain='hfph',label_msgid='institution'),
                ),
    StringField('Position',
                default_output_type='image/jpeg',
                #storage=MySQLSQLStorage(),
                widget=StringWidget(label='Position',i18n_domain='hfph',label_msgid='position'),
                ),
    StringField('Workarea',
                default_output_type='image/jpeg',
                #storage=MySQLSQLStorage(),
                widget=StringWidget(label='Workarea',i18n_domain='hfph',label_msgid='workarea'),
                ),
    StringField('Degrees',
                default_output_type='image/jpeg',
                #storage=MySQLSQLStorage(),
                widget=StringWidget(label='Degrees',i18n_domain='hfph',label_msgid='degrees'),
                ),
    ),

                              )

class alumni(BaseContent):


    schema = schema
    archetype_name = "alumni"

registerType(alumni, PROJECTNAME)