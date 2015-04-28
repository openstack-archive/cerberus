#
#   Copyright (c) 2014 EUROGICIEL
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#

import parser


class JsonSerializer(object):
    """A serializer that provides methods to serialize and deserialize JSON
    dictionaries.

    Note, one of the assumptions this serializer makes is that all objects that
    it is used to deserialize have a constructor that can take all of the
    attribute arguments. I.e. If you have an object with 3 attributes, the
    constructor needs to take those three attributes as keyword arguments.
    """

    __attributes__ = None
    """The attributes to be serialized by the seralizer.
    The implementor needs to provide these."""

    __required__ = None
    """The attributes that are required when deserializing.
    The implementor needs to provide these."""

    __attribute_serializer__ = None
    """The serializer to use for a specified attribute. If an attribute is not
    included here, no special serializer will be user.
    The implementor needs to provide these."""

    __object_class__ = None
    """The class that the deserializer should generate.
    The implementor needs to provide these."""

    serializers = dict(
        date=dict(
            serialize=lambda x: x.isoformat(),
            deserialize=lambda x: parser.parse(x)
        )
    )

    def deserialize(self, json, **kwargs):
        """Deserialize a JSON dictionary and return a populated object.

        This takes the JSON data, and deserializes it appropriately and then
        calls the constructor of the object to be created with all of the
        attributes.

        Args:
            json: The JSON dict with all of the data
            **kwargs: Optional values that can be used as defaults if they are
            not present in the JSON data
        Returns:
            The deserialized object.
        Raises:
            ValueError: If any of the required attributes are not present
        """
        d = dict()
        for attr in self.__attributes__:
            if attr in json:
                val = json[attr]
            elif attr in self.__required__:
                try:
                    val = kwargs[attr]
                except KeyError:
                    raise ValueError("{} must be set".format(attr))

            serializer = self.__attribute_serializer__.get(attr)
            if serializer:
                d[attr] = self.serializers[serializer]['deserialize'](val)
            else:
                d[attr] = val

        return self.__object_class__(**d)

    def serialize(self, obj):
        """Serialize an object to a dictionary.

        Take all of the attributes defined in self.__attributes__ and create
        a dictionary containing those values.

        Args:
            obj: The object to serialize
        Returns:
            A dictionary containing all of the serialized data from the object.
        """
        d = dict()
        for attr in self.__attributes__:
            val = getattr(obj, attr)
            if val is None:
                continue
            serializer = self.__attribute_serializer__.get(attr)
            if serializer:
                d[attr] = self.serializers[serializer]['serialize'](val)
            else:
                d[attr] = val

        return d
