# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# -------------------------------------------------------------------------
# This is a sample controller
# - index is the default action of any application
# - user is required for authentication and authorization
# - download is for downloading files uploaded in the db (does streaming)
# -------------------------------------------------------------------------
from nmapscanner import *
from pycsvasset import *
from pynessusasset import *
from pynmapasset import *


def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    return dict()


def manage():
    grid = SQLFORM.smartgrid(db.hosts,linked_tables=['ports'])
    return locals()


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()

# These next 2 might be moved to the reports controller at some point
def network_map():
    #TODO: Create a network map based on hops database!
    pass

@auth.requires_login()
@auth.requires_membership('auditor')
def review_scans():
    #TODO: Create a page which essentially just dumps the scans database out in a sql smart grid (use web2py built in)
    pass

# Below are all database editing pages.
@auth.requires_login()
@auth.requires_membership('editor')
def edit_hosts():
    # TODO: SQL smartgrid for hosts database
    pass
@auth.requires_login()
@auth.requires_membership('editor')
def edit_vulnerabilities():
    pass
@auth.requires_login()
@auth.requires_membership('editor')
def edit_ports():
    pass
@auth.requires_login()
@auth.requires_membership('editor')
def edit_softauth():
    pass
@auth.requires_login()
@auth.requires_membership('editor')
def edit_software():
    pass
@auth.requires_login()
@auth.requires_membership('editor')
def edit_hops():
    grid = SQLFORM.smartgrid(db.hops, headers={'hops.ip': 'Hop IP', 'hops.hostname': 'Hop Hostname',
                                                  'hops.scanner_ip': 'Origin Host IP',
                                                  'hops.dst_ip': 'Target IP', 'hops.rtt': 'Time to Hop Host (RTT)',
                                                  'hops.ttl': 'Distance from Origin (TTL)'})

    return dict(form=form)
