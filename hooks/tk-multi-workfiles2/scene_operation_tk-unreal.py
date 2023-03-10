# Copyright (c) 2015 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import os
import unreal

import sgtk

from tank_vendor import six

HookClass = sgtk.get_hook_baseclass()


class SceneOperation(HookClass):
    """
    Hook called to perform an operation with the current scene
    """
    def __init__(self):
        self.unreal_util = unreal.EditorLoadingAndSavingUtils()

    def execute(
        self,
        operation,
        file_path,
        context,
        parent_action,
        file_version,
        read_only,
        **kwargs
    ):
        """
        Main hook entry point

        :param operation:       String
                                Scene operation to perform

        :param file_path:       String
                                File path to use if the operation
                                requires it (e.g. open)

        :param context:         Context
                                The context the file operation is being
                                performed in.

        :param parent_action:   This is the action that this scene operation is
                                being executed for.  This can be one of:
                                - open_file
                                - new_file
                                - save_file_as
                                - version_up

        :param file_version:    The version/revision of the file to be opened.  If this is 'None'
                                then the latest version should be opened.

        :param read_only:       Specifies if the file should be opened read-only or not

        :returns:               Depends on operation:
                                'current_path' - Return the current scene
                                                 file path as a String
                                'reset'        - True if scene was reset to an empty
                                                 state, otherwise False
                                all others     - None
        """
        # run the base class operations
        base_class = super(SceneOperation, self).execute(operation, file_path, context,
                                                         parent_action, file_version,
                                                         read_only, **kwargs)
        # if the base_class returns false, go no further-
        if not base_class:
            return False

        if operation == "current_path":
            return self.unreal_util.get_path()

        elif operation == "open":
            # give unreal forward slashes
            # file_path = file_path.replace(os.path.sep, "/")
            file_path = six.ensure_str(file_path)
            self.unreal_util.load_map(file_path)
            #self.unreal_util.load_map_with_dialog()

        elif operation == "save":
            self.unreal_util.save_current_level()

        elif operation == "save_as":
            # give unreal forward slashes
            # file_path = file_path.replace(os.path.sep, "/")
            file_path = six.ensure_str(file_path)
            self.unreal_util.save_map(file_path)

        elif operation == "reset":
            save_existing_map = True
            self.unreal_util.new_blank_map(save_existing_map)

            return True
