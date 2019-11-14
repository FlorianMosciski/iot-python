# *****************************************************************************
# Copyright (c) 2019 IBM Corporation and other Contributors.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
# *****************************************************************************

from collections import defaultdict
import iso8601

from wiotp.sdk.api.common import RestApiDict
from wiotp.sdk.api.common import RestApiItemBase
from wiotp.sdk.api.dsc.destinations import Destinations
from wiotp.sdk.api.dsc.forwarding import ForwardingRules
from wiotp.sdk.exceptions import ApiException
from wiotp.sdk.api.common import IterableList

# See docs @ https://orgid.internetofthings.ibmcloud.com/docs/v0002/historian-connector.html


class Connector(RestApiItemBase):
    def __init__(self, apiClient, **kwargs):
        self._apiClient = apiClient

        self.destinations = Destinations(
            apiClient=self._apiClient, connectorId=kwargs["id"], connectorType=kwargs["type"]
        )
        self.rules = ForwardingRules(apiClient=self._apiClient, connectorId=kwargs["id"])
        dict.__init__(self, **kwargs)

    # Note - data accessor functions for common data items are defined in RestApiItemBase

    @property
    def serviceId(self):
        return self["serviceId"]

    @property
    def connectorType(self):
        return self["type"]

    @property
    def configuration(self):
        if "configuration" in self:
            return self["configuration"]
        else:
            return None

    @property
    def adminDisabled(self):
        return self["adminDisabled"]

    @property
    def enabled(self):
        return self["enabled"]

    @property
    def timezone(self):
        return self["timezone"]


class IterableConnectorList(IterableList):
    def __init__(self, apiClient, url, filters=None):
        # This API does not support sorting
        super(IterableConnectorList, self).__init__(
            apiClient, Connector, url, sort=None, filters=filters, passApiClient=True
        )


class Connectors(RestApiDict):

    allHistorianConnectorsUrl = "api/v0002/historianconnectors"
    oneHistorianConnectorUrl = "api/v0002/historianconnectors/%s"

    def __init__(self, apiClient):
        super(Connectors, self).__init__(apiClient, Connector, IterableConnectorList, self.allHistorianConnectorsUrl)

    def find(self, nameFilter=None, typeFilter=None, enabledFilter=None, serviceId=None):
        """
        Gets the list of Historian connectors, they are used to configure the Watson IoT Platform to store IoT data in compatible services.
        
        Parameters:
        
            - nameFilter(string) -      Filter the results by the specified name
            - typeFilter(string) -      Filter the results by the specified type, Available values : cloudant, eventstreams
            - enabledFilter(boolean) -  Filter the results by the enabled flag 
            - serviceId(string) -       Filter the results by the service id
            - limit(number) -           Max number of results returned, defaults 25
            - bookmark(string) -        used for paging through results
        
        Throws APIException on failure.
        """

        queryParms = {}
        if nameFilter:
            queryParms["name"] = nameFilter
        if typeFilter:
            queryParms["type"] = typeFilter
        if enabledFilter:
            queryParms["enabled"] = enabledFilter
        if serviceId:
            queryParms["serviceId"] = serviceId

        return IterableConnectorList(self._apiClient, self.allHistorianConnectorsUrl, filters=queryParms)

    def create(self, name, type, serviceId, timezone, description, enabled, configuration=None):
        """
        Create a connector for the organization in the Watson IoT Platform. 
        The connector must reference the target service that the Watson IoT Platform will store the IoT data in.
        Parameters:
            - name (string) - Name of the service
            - serviceId (string) - must be either eventstreams or cloudant
            - timezone (string) - 
            - description (string) - description of the service
            - enabled (boolean) - enabled
        Throws APIException on failure
        """

        connector = {
            "name": name,
            "type": type,
            "description": description,
            "serviceId": serviceId,
            "timezone": timezone,
            "enabled": enabled,
        }

        url = "api/v0002/historianconnectors"

        r = self._apiClient.post(url, data=connector)
        if r.status_code == 201:
            return Connector(apiClient=self._apiClient, **r.json())
        else:
            raise ApiException(r)

    def update(self, connectorId, serviceId, name, type, description, timezone, enabled, configuration=None):
        """
        Updates the connector with the specified uuid.
        if description is empty, the existing description will be removed.
        Parameters:
            - connector (String), Connnector Id which is a UUID
            - name (string) - Name of the service
            - timezone (json object) - Should have a valid structure for the service type.
            - description (string) - description of the service
            - enabled (boolean) - enabled
        Throws APIException on failure.
        """

        url = "api/v0002/historianconnectors/%s" % (connectorId)

        connectorBody = {}
        connectorBody["id"] = connectorId
        connectorBody["name"] = name
        connectorBody["type"] = type
        connectorBody["serviceId"] = serviceId
        connectorBody["description"] = description
        connectorBody["timezone"] = timezone
        connectorBody["enabled"] = enabled
        if configuration != None:
            connectorBody["configuration"] = configuration

        r = self._apiClient.put(url, data=connectorBody)

        if r.status_code == 200:
            return Connector(apiClient=self._apiClient, **r.json())
        else:
            raise ApiException(r)
