# Copyright 2020 Soil, Inc.
# Copyright 2011 OpenStack Foundation
#
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import os

from oslo_config import cfg
from oslo_log import log as logging
from oslo_utils import importutils
import webob.dec
import webob.exc

from soil.api.server import wsgi
from soil import exception


extension_opts = [
    cfg.MultiStrOpt(
        'soil_api_extension',
        default=['soil.api.contrib.standard_extensions'],
        help='soil extension to load')]

CONF = cfg.CONF
LOG = logging.getLogger(__name__)
CONF.register_opts(extension_opts)


class ExtensionDescriptor(object):
    """Base class that defines the contract for extensions.

    Note that you don't have to derive from this class to have a valid
    extension; it is purely a convenience.

    """

    # The name of the extension, e.g., 'Fox In Socks'
    name = None

    # The alias for the extension, e.g., 'FOXNSOX'
    alias = None

    # Description comes from the docstring for the class

    # The timestamp when the extension was last updated, e.g.,
    # '2011-01-22T19:25:27Z'
    updated = None

    def __init__(self, ext_mgr):
        """Register extension with the extension manager."""

        ext_mgr.register(self)
        self.ext_mgr = ext_mgr

    def get_resources(self):
        """List of extensions.ResourceExtension extension objects.

        Resources define new nouns, and are accessible through URLs.

        """
        resources = []
        return resources

    def get_controller_extensions(self):
        """List of extensions.ControllerExtension extension objects.

        Controller extensions are used to extend existing controllers.
        """
        controller_exts = []
        return controller_exts

    def __repr__(self):
        return "<Extension: name=%s, alias=%s, updated=%s>" % (
            self.name, self.alias, self.updated)

    def is_valid(self):
        """Validate required fields for extensions.

        Raises an attribute error if the attr is not defined
        """
        for attr in ('name', 'alias', 'updated'):
            if getattr(self, attr) is None:
                raise AttributeError("%s is None, needs to be defined" % attr)
        return True


class ExtensionsResource(wsgi.Resource):

    def __init__(self, extension_manager):
        self.extension_manager = extension_manager
        super(ExtensionsResource, self).__init__(None)

    def _translate(self, ext):
        ext_data = {}
        ext_data['name'] = ext.name
        ext_data['alias'] = ext.alias
        ext_data['description'] = ext.__doc__
        ext_data['updated'] = ext.updated
        ext_data['links'] = []  # TODO(dprince): implement extension links
        return ext_data

    def index(self, req):
        extensions = []
        for _alias, ext in self.extension_manager.extensions.items():
            extensions.append(self._translate(ext))
        return dict(extensions=extensions)

    def show(self, req, id):
        try:
            # NOTE(dprince): the extensions alias is used as the 'id' for show
            ext = self.extension_manager.extensions[id]
        except KeyError:
            raise webob.exc.HTTPNotFound()

        return dict(extension=self._translate(ext))

    def delete(self, req, id):
        raise webob.exc.HTTPNotFound()

    def create(self, req, body):
        raise webob.exc.HTTPNotFound()


class ExtensionManager(object):
    """Load extensions from the configured extension path."""

    def __init__(self):
        LOG.info('Initializing extension manager.')

        self.cls_list = CONF.soil_api_extension
        self.extensions = {}
        self._load_extensions()

    def is_loaded(self, alias):
        return alias in self.extensions

    def register(self, ext):
        # Do nothing if the extension doesn't check out
        if not self._check_extension(ext):
            return

        alias = ext.alias
        LOG.info('Loaded extension: %s', alias)

        if alias in self.extensions:
            raise exception.Error("Found duplicate extension: %s" % alias)
        self.extensions[alias] = ext

    def get_resources(self):
        """Returns a list of ResourceExtension objects."""

        resources = []
        resources.append(ResourceExtension('extensions',
                                           ExtensionsResource(self)))

        for ext in self.extensions.values():
            try:
                resources.extend(ext.get_resources())
            except AttributeError:
                # NOTE(dprince): Extension aren't required to have resource
                # extensions
                pass
        return resources

    def get_controller_extensions(self):
        """Returns a list of ControllerExtension objects."""
        controller_exts = []
        for ext in self.extensions.values():
            try:
                get_ext_method = ext.get_controller_extensions
            except AttributeError:
                # NOTE(Vek): Extensions aren't required to have
                # controller extensions
                continue
            controller_exts.extend(get_ext_method())
        return controller_exts

    def _check_extension(self, extension):
        """Checks for required methods in extension objects."""
        try:
            LOG.debug('Ext name: %s', extension.name)
            LOG.debug('Ext alias: %s', extension.alias)
            LOG.debug('Ext description: %s',
                      ' '.join(extension.__doc__.strip().split()))
            LOG.debug('Ext updated: %s', extension.updated)
        except AttributeError:
            LOG.exception("Exception loading extension.")
            return False

        return True

    def load_extension(self, ext_factory):
        """Execute an extension factory.

        Loads an extension.  The 'ext_factory' is the name of a
        callable that will be imported and called with one
        argument--the extension manager.  The factory callable is
        expected to call the register() method at least once.
        """

        LOG.debug("Loading extension %s", ext_factory)

        # Load the factory
        factory = importutils.import_class(ext_factory)

        # Call it
        LOG.debug("Calling extension factory %s", ext_factory)
        factory(self)

    def _load_extensions(self):
        """Load extensions specified on the command line."""

        extensions = list(self.cls_list)

        for ext_factory in extensions:
            try:
                self.load_extension(ext_factory)
            except Exception as exc:
                LOG.warning('Failed to load extension %(ext_factory)s: '
                            '%(exc)s',
                            {'ext_factory': ext_factory, 'exc': exc})


class ControllerExtension(object):
    """Extend core controllers of Soil API.

    Provide a way to extend existing Soil API core
    controllers.
    """

    def __init__(self, extension, collection, controller):
        self.extension = extension
        self.collection = collection
        self.controller = controller


class ResourceExtension(object):
    """Add top level resources to the API in soil."""

    def __init__(self, collection, controller, parent=None,
                 collection_actions=None, member_actions=None,
                 custom_routes_fn=None):
        if not collection_actions:
            collection_actions = {}
        if not member_actions:
            member_actions = {}
        self.collection = collection
        self.controller = controller
        self.parent = parent
        self.collection_actions = collection_actions
        self.member_actions = member_actions
        self.custom_routes_fn = custom_routes_fn


def load_standard_extensions(ext_mgr, logger, path, package, ext_list=None):
    """Registers all standard API extensions."""

    # Walk through all the modules in our directory...
    our_dir = path[0]
    for dirpath, dirnames, filenames in os.walk(our_dir):
        # Compute the relative package name from the dirpath
        relpath = os.path.relpath(dirpath, our_dir)
        if relpath == '.':
            relpkg = ''
        else:
            relpkg = '.%s' % '.'.join(relpath.split(os.sep))

        # Now, consider each file in turn, only considering .py files
        for fname in filenames:
            root, ext = os.path.splitext(fname)

            # Skip __init__ and anything that's not .py
            if ext != '.py' or root == '__init__':
                continue

            # Try loading it
            classname = "%s%s" % (root[0].upper(), root[1:])
            classpath = ("%s%s.%s.%s" %
                         (package, relpkg, root, classname))

            if ext_list is not None and classname not in ext_list:
                logger.debug("Skipping extension: %s" % classpath)
                continue

            try:
                ext_mgr.load_extension(classpath)
            except Exception as exc:
                logger.warning('Failed to load extension %(classpath)s: '
                               '%(exc)s',
                               {'classpath': classpath, 'exc': exc})

        # Now, let's consider any subdirectories we may have...
        subdirs = []
        for dname in dirnames:
            # Skip it if it does not have __init__.py
            if not os.path.exists(os.path.join(dirpath, dname,
                                               '__init__.py')):
                continue

            # If it has extension(), delegate...
            ext_name = ("%s%s.%s.extension" %
                        (package, relpkg, dname))
            try:
                ext = importutils.import_class(ext_name)
            except ImportError:
                # extension() doesn't exist on it, so we'll explore
                # the directory for ourselves
                subdirs.append(dname)
            else:
                try:
                    ext(ext_mgr)
                except Exception as exc:
                    logger.warning('Failed to load extension %(ext_name)s: '
                                   '%(exc)s',
                                   {'ext_name': ext_name, 'exc': exc})

        # Update the list of directories we'll explore...
        dirnames[:] = subdirs
