#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys

from keystoneclient.auth.identity import v2
from keystoneclient import session
from keystoneclient.v2_0 import client

DRY_RUN=True

protocol = 'http'
public = '192.168.11.100'  
internal = '10.0.0.1'
admin = '10.0.0.1'

user = os.getenv('OS_USERNAME')
password = os.getenv('OS_PASSWORD')
tenant = os.getenv('OS_TENANT_NAME')
region = os.getenv('OS_REGION_NAME')
auth_url = os.getenv('OS_AUTH_URL')

if user is None or password is None or tenant is None or region is None or auth_url is None:
    print("ERROR!")
    sys.exit(1)

#              publicURL, internalURL, adminURL の順
# サービス名: [(ポート, パス), ...]
new_endpoints = {
    "keystone": [(5000, "v2.0"), (5000, "v2.0"), (35357, "v2.0")],
    "ceilometer": [(8777, ""),(8777, ""),(8777, "")],
    "cinder": [(8776, "v1/%(tenant_id)s"),(8776, "v1/%(tenant_id)s"),(8776, "v1/%(tenant_id)s")],
    "cinderv2": [(8776, "v2/%(tenant_id)s"),(8776, "v2/%(tenant_id)s"),(8776, "v2/%(tenant_id)s")],
    "glance": [(9292, ""),(9292, ""),(9292, "")],
    "neutron": [(9696, ""),(9696, ""),(9696, "")],
    "nova": [(8774, "v2/%(tenant_id)s"),(8774, "v2/%(tenant_id)s"),(8774, "v2/%(tenant_id)s")],
    "nova_ec2": [(8773, "services/Cloud"),(8773, "services/Cloud"),(8773, "services/Admin")],
    "novav3": [(8774, "v3"),(8774, "v3"),(8774, "v3")],
    "swift": [(8080, "v1/AUTH_%(tenant_id)s"),(8080, "v1/AUTH_$(tenant_id)s"),(8080, "")],
    "swift_s3": [(8080, ""),(8080, ""),(8080, "")]
}

auth = v2.Password(auth_url=auth_url, username=user, password=password, tenant_name=tenant)
sess = session.Session(auth=auth, verify=False)

cli = client.Client(session=sess, region_name=region)

services = cli.services.list()

# 変更前の endpoint 情報を取得
old_endpoints = cli.endpoints.list()

# サービスごとに endpoint を変更
url_template = protocol + "://%s:%d/%s"
for service in services:
    endpoint = new_endpoints[service.name]
    publicURL = url_template % (public, endpoint[0][0], endpoint[0][1])
    internalURL = url_template % (internal, endpoint[1][0], endpoint[1][1])
    adminURL = url_template % (admin, endpoint[2][0], endpoint[2][1])
    if not DRY_RUN:
        cli.endpoints.create(
            region=region,
            service_id=service.id,
            publicURL=publicURL,
            internalURL=internalURL,
            adminURL=adminURL
        )
    print("[%s] public=%s internal=%s admin=%s" % (service.name, publicURL, internalURL, adminURL))

# 変更前の endpoint を削除
for endpoint in old_endpoints:
    if not DRY_RUN:
        cli.endpoints.delete(endpoint.id)
