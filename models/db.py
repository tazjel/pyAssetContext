from  datetime import datetime

# -*- coding: utf-8 -*-

# -------------------------------------------------------------------------
# This scaffolding model makes your app work on Google App Engine too
# File is released under public domain and you can use without limitations
# -------------------------------------------------------------------------

if request.global_settings.web2py_version < "2.14.1":
    raise HTTP(500, "Requires web2py 2.13.3 or newer")

# -------------------------------------------------------------------------
# if SSL/HTTPS is properly configured and you want all HTTP requests to
# be redirected to HTTPS, uncomment the line below:
# -------------------------------------------------------------------------
# request.requires_https()

# -------------------------------------------------------------------------
# app configuration made easy. Look inside private/appconfig.ini
# -------------------------------------------------------------------------
from gluon.contrib.appconfig import AppConfig

# -------------------------------------------------------------------------
# once in production, remove reload=True to gain full speed
# -------------------------------------------------------------------------
myconf = AppConfig(reload=True)

if not request.env.web2py_runtime_gae:
    # ---------------------------------------------------------------------
    # if NOT running on Google App Engine use SQLite or other DB
    # ---------------------------------------------------------------------
    db = DAL(myconf.get('db.uri'),
             pool_size=myconf.get('db.pool_size'),
             migrate_enabled=myconf.get('db.migrate'),
             check_reserved=['all'])
else:
    # ---------------------------------------------------------------------
    # connect to Google BigTable (optional 'google:datastore://namespace')
    # ---------------------------------------------------------------------
    db = DAL('google:datastore+ndb')
    # ---------------------------------------------------------------------
    # store sessions and tickets there
    # ---------------------------------------------------------------------
    session.connect(request, response, db=db)
    # ---------------------------------------------------------------------
    # or store session in Memcache, Redis, etc.
    # from gluon.contrib.memdb import MEMDB
    # from google.appengine.api.memcache import Client
    # session.connect(request, response, db = MEMDB(Client()))
    # ---------------------------------------------------------------------

# -------------------------------------------------------------------------
# by default give a view/generic.extension to all actions from localhost
# none otherwise. a pattern can be 'controller/function.extension'
# -------------------------------------------------------------------------
response.generic_patterns = ['*'] if request.is_local else []
# -------------------------------------------------------------------------
# choose a style for forms
# -------------------------------------------------------------------------
response.formstyle = myconf.get('forms.formstyle')  # or 'bootstrap3_stacked' or 'bootstrap2' or other
response.form_label_separator = myconf.get('forms.separator') or ''

# -------------------------------------------------------------------------
# (optional) optimize handling of static files
# -------------------------------------------------------------------------
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'

# -------------------------------------------------------------------------
# (optional) static assets folder versioning
# -------------------------------------------------------------------------
# response.static_version = '0.0.0'

# -------------------------------------------------------------------------
# Here is sample code if you need for
# - email capabilities
# - authentication (registration, login, logout, ... )
# - authorization (role based authorization)
# - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
# - old style crud actions
# (more options discussed in gluon/tools.py)
# -------------------------------------------------------------------------

from gluon.tools import Auth, Service, PluginManager

# host names must be a list of allowed host names (glob syntax allowed)
auth = Auth(db, host_names=myconf.get('host.names'))
service = Service()
plugins = PluginManager()

# -------------------------------------------------------------------------
# create all tables needed by auth if not custom tables
# -------------------------------------------------------------------------
auth.define_tables(username=True, signature=False)
auth.settings.extra_fields['auth_user']= [
  Field('address'),
  Field('city'),
  Field('zip'),
  Field('phone'),
  Field('organization'),
  Field('team'),
  Field('title'),
  Field('job_title')]

# -------------------------------------------------------------------------
# configure email
# -------------------------------------------------------------------------
mail = auth.settings.mailer
mail.settings.server = 'logging' if request.is_local else myconf.get('smtp.server')
mail.settings.sender = myconf.get('smtp.sender')
mail.settings.login = myconf.get('smtp.login')
mail.settings.tls = myconf.get('smtp.tls') or False
mail.settings.ssl = myconf.get('smtp.ssl') or False

# -------------------------------------------------------------------------
# configure auth policy
# -------------------------------------------------------------------------
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

# -------------------------------------------------------------------------
# Define your tables below (or better in another model file) for example
#
# >>> db.define_table('mytable', Field('myfield', 'string'))
#
# Fields can be 'string','text','password','integer','double','boolean'
#       'date','time','datetime','blob','upload', 'reference TABLENAME'
# There is an implicit 'id integer autoincrement' field
# Consult manual for more options, validators, etc.
#
# More API examples for controllers:
#
# >>> db.mytable.insert(myfield='value')
# >>> rows = db(db.mytable.myfield == 'value').select(db.mytable.ALL)
# >>> for row in rows: print row.id, row.myfield
# -------------------------------------------------------------------------

# -------------------------------------------------------------------------
# after defining tables, uncomment below to enable auditing
# -------------------------------------------------------------------------
# auth.enable_record_versioning(db)
ourtime = datetime.utcnow()

# Custom Databases
# Reference https://github.com/ShadeySecurity/pyAssetInventory/wiki/Database-Structure

db.define_table('scans', Field('username', db.auth_user, default=auth.user_id, writable=False, requires=IS_NOT_EMPTY()),
                Field('scan_type','string', requires=IS_IN_SET(['nessus', 'nmap', 'powershell', 'openvas', 'ssh','csv'])),
                Field('network','string', default='127.0.0.1/32',requires=IS_NOT_EMPTY()),
                Field('command','string'),
                Field('task_id', 'string'),
                Field('description','text'),
                Field('justification','text', requires=IS_NOT_EMPTY()),
                Field('approver','string'),
                Field('date_timestamp','date', default=ourtime,writable=False, requires=IS_NOT_EMPTY()),
                Field('scanner_ip', 'string',default='127.0.0.1', requires=IS_NOT_EMPTY()),
                Field('user_ip','string', default='127.0.0.1')
                )

db.define_table('hosts',
                Field('ip', 'string', requires=IS_NOT_EMPTY()),
                Field('netmask', 'string'),
                Field('mac', 'string', requires=IS_NOT_EMPTY()),
                Field('vendor', 'string'),
                Field('os', 'string', default="Other", requires=IS_IN_SET(['Linux','Windows','Mac','Unix','Other'])),
                Field('os_version'),
                Field('pingable', 'boolean', default=False, requires=IS_NOT_EMPTY()),
                Field('distance', 'integer', default=1, requires=IS_NOT_EMPTY()),
                Field('rtt', 'integer',  default=1, requires=IS_NOT_EMPTY()),
                Field('scan_id', requires=IS_NOT_EMPTY()),
                Field('host_type', requires=IS_NOT_EMPTY()),
                Field('firewall_state', requires=IS_IN_SET(['on','partial','off'])),
                singular="host",
                plural="hosts"
                )

db.define_table('hostnames',
                Field('ip', requires=IS_NOT_EMPTY()),
                Field('hostname', requires=IS_NOT_EMPTY()),
                Field('record_type', requires=IS_NOT_EMPTY()),
                Field('dns_source'),
                Field('scan_id', requires=IS_NOT_EMPTY())
                )
db.define_table('ports',
                Field('host_id', 'reference hosts'),
                Field('port', 'string', requires=IS_NOT_EMPTY()),
                Field('protocol', 'string', default='tcp', requires=IS_NOT_EMPTY()),
                Field('service', 'string', default='unk', requires=IS_NOT_EMPTY()),
                Field('scan_id', 'string', requires=IS_NOT_EMPTY()),
                Field('banner', 'string', requires=IS_NOT_EMPTY()),
                singular="port",
                plural="ports"
                )


db.define_table('software',
                Field('ip', 'string', requires=IS_NOT_EMPTY()),
                Field('software_name', 'string', requires=IS_NOT_EMPTY()),
                Field('software_version', 'string', requires=IS_NOT_EMPTY()),
                Field('install_user', 'string'),
                Field('install_date', 'string'),
                Field('scan_id', 'string', requires=IS_NOT_EMPTY())
                )
db.define_table('software_auth', Field('software_vendor'),
                Field('software_name', requires=IS_NOT_EMPTY()),
                Field('software_version', requires=IS_NOT_EMPTY()),
                Field('auth_uid', requires=IS_NOT_EMPTY()),
                Field('win_auth','boolean', default=False, requires=IS_NOT_EMPTY()),
                Field('nix_auth','boolean', default=False, requires=IS_NOT_EMPTY()),
                Field('mac_auth','boolean', default=False, requires=IS_NOT_EMPTY()),
                Field('contract','string'),
                Field('last_updated','string', requires=IS_NOT_EMPTY()),
                Field('description','text')
                )

db.define_table('vulnerabilities', Field('software_vendor'),
                Field('software_name','string', requires=IS_NOT_EMPTY()),
                Field('software_version', requires=IS_NOT_EMPTY()),
                Field('os', requires=IS_NOT_EMPTY()),
                Field('os_version', requires=IS_NOT_EMPTY()),
                Field('cve',requires=IS_NOT_EMPTY()),
                Field('ip', requires=IS_NOT_EMPTY()),
                Field('criticality', requires=IS_IN_SET(['Critical','High','Medium','Low'])),
                Field('scan_id', requires=IS_NOT_EMPTY()),
                Field('description')
                )

db.define_table('hops', Field('ip', requires=IS_NOT_EMPTY()),
                Field('hostname'),
                Field('scanner_ip', requires=IS_NOT_EMPTY()),
                Field('dst_ip', requires=IS_NOT_EMPTY()),
                Field('rtt', requires=IS_NOT_EMPTY()),
                Field('ttl', requires=IS_NOT_EMPTY()),
                Field('scan_id', requires=IS_NOT_EMPTY())
                )

db.define_table('interfaces',
                Field('ip', requires=IS_NOT_EMPTY()),
                Field('interface', requires=IS_NOT_EMPTY()),
                Field('description'),
                Field('speed'),
                Field('interface_network'),
                Field('vlan'),
                Field('port_type'),
                Field('host_type'),
                Field('scan_id', requires=IS_NOT_EMPTY()),
                Field('next_device')
                )
db.define_table('vlans',
                Field('vlan_id', requires=IS_NOT_EMPTY()),
                Field('vlan_desc'),
                Field('interface', requires=IS_NOT_EMPTY()),
                Field('is_native', 'boolean', default=False, requires=IS_NOT_EMPTY())
                )
db.define_table('routes',
                Field('route_type', requires=IS_NOT_EMPTY()),
                Field('is_default', 'boolean',default=False, requires=IS_NOT_EMPTY()),
                Field('src_network', requires=IS_NOT_EMPTY()),
                Field('dst_network', requires=IS_NOT_EMPTY()),
                Field('interface', requires=IS_NOT_EMPTY()),
                Field('metric'),
                Field('next_hop', requires=IS_NOT_EMPTY())
                )

db.define_table('host_users',
                Field('username', requires=IS_NOT_EMPTY()),
                Field('creation_date'),
                Field('privilege_level', requires=IS_NOT_EMPTY()),
                Field('scan_id')
                )

db.define_table('auth_groups',
                Field('group_name', requires=IS_NOT_EMPTY()),
                Field('username'),
                Field('creation_date'),
                Field('scan_id')
                )

db.define_table('fw_acl',
                Field('rule_name'),
                Field('traffic_action', requires=IS_IN_SET(['deny','accept','reject'])),
                Field('src_net', requires=IS_NOT_EMPTY()),
                Field('dst_net', requires=IS_NOT_EMPTY()),
                Field('interface', requires=IS_NOT_EMPTY()),
                Field('src_port', requires=IS_NOT_EMPTY()),
                Field('dst_port', requires=IS_NOT_EMPTY()),
                Field('protocol', requires=IS_IN_SET(['tcp','udp','icmp'])),
                Field('service', requires=IS_NOT_EMPTY()),
                Field('hostname', requires=IS_NOT_EMPTY()),
                Field('fw_name', requires=IS_IN_SET(['cisco-acl','iptables','winfw','ufw','ipchains','other'])),
                Field('state_type', requires=IS_IN_SET(['stateful','stateless'])),
                Field('scan_id', requires=IS_NOT_EMPTY()),
                Field('description', 'text', requires=IS_NOT_EMPTY()),
                Field('logged', 'boolean', default=False, requires=IS_NOT_EMPTY()),
                Field('other_args', requires=IS_NOT_EMPTY()),
                Field('scan_id', requires=IS_NOT_EMPTY())
                )
