#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys

from keystoneclient.auth.identity import v2
from keystoneclient import session
from keystoneclient.v2_0 import client

base = 'https://helion-horizon.cu-mo.jp'

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
    "keystone": [(5000, "v2.0")],
    "nova": [],
    "neutron": [],
}

auth = v2.Password(auth_url=auth_url, username=user, password=password, tenant_name=tenant)
sess = session.Session(auth=auth, verify=False)

cli = client.Client(session=ss)

services = cli.services.list()

# 変更前の endpoint 情報を取得
old_endpoints = cli.endpoints.list()

# サービスごとに endpoint を変更
for service in services:
    endpoint = new_endpoints[service.name]
    publicURL = "%s:%d/%s" % (base, endpoint[0][0], endpoint[0][1])
    internalURL = "%s:%d/%s" % (base, endpoint[1][0], endpoint[1][1])
    adminURL = "%s:%d/%s" % (base, endpoint[2][0], endpoint[2][1])
    cli.endpoints.create(
        region=region,
        service_id=service.id,
        publicURL=publicURL,
        internalURL=internalURL,
        adminURL=adminURL
    )

# 変更前の endpoint を削除
for endpoint in old_endpoints:
    print(endpoint)
    cli.endpoints.delete(endpoint.id)
