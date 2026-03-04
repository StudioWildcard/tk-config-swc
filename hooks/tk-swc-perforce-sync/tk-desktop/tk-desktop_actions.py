# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
Hook that loads defines all the available actions, broken down by publish type.
"""
import pprint
import sgtk
import tank

from tank_vendor import six

HookBaseClass = sgtk.get_hook_baseclass()

class ShellActions(HookBaseClass):
    """
    Stub implementation of the shell actions, used for testing.
    """

    def generate_actions(self, sg_publish_data, actions, ui_area):
        """
        Return a list of action instances for a particular publish.
        This method is called each time a user clicks a publish somewhere in the UI.
        The data returned from this hook will be used to populate the actions menu for a publish.

        The mapping between Publish types and actions are kept in a different place
        (in the configuration) so at the point when this hook is called, the loader app
        has already established *which* actions are appropriate for this object.

        The hook should return at least one action for each item passed in via the
        actions parameter.

        This method needs to return detailed data for those actions, in the form of a list
        of dictionaries, each with name, params, caption and description keys.

        Because you are operating on a particular publish, you may tailor the output
        (caption, tooltip etc) to contain custom information suitable for this publish.

        The ui_area parameter is a string and indicates where the publish is to be shown.
        - If it will be shown in the main browsing area, "main" is passed.
        - If it will be shown in the details area, "details" is passed.
        - If it will be shown in the history area, "history" is passed.

        Please note that it is perfectly possible to create more than one action "instance" for
        an action! You can for example do scene introspection - if the action passed in
        is "character_attachment" you may for example scan the scene, figure out all the nodes
        where this object can be attached and return a list of action instances:
        "attach to left hand", "attach to right hand" etc. In this case, when more than
        one object is returned for an action, use the params key to pass additional
        data into the run_action hook.

        :param sg_publish_data: Shotgun data dictionary with all the standard publish fields.
        :param actions: List of action strings which have been defined in the app configuration.
        :param ui_area: String denoting the UI Area (see above).
        :returns List of dictionaries, each with keys name, params, caption and description
        """
        app = self.parent
        #app.log_debug(
        #    "Generate actions called for UI element %s. "
        #    "Actions: %s. Publish Data: %s" % (ui_area, actions, sg_publish_data)
        #)

        action_instances = []

        # For the sake of easy test, we'll reuse Maya publish types.

        if "preview_create_folders" in actions:
            action_instances.append(
                {
                    "name": "preview_create_folders",
                    "params": "Preview Create Folders 'params'",
                    "caption": "Preview Create Folders",
                    "description": "Executes Preview Create Folders.",
                }
            )

        if "create_folders" in actions:
            action_instances.append(
                {
                    "name": "create_folders",
                    "params": "Create Folders 'params'",
                    "caption": "Create Folders",
                    "description": "Executes Create Folders.",
                }
            )
        if "unregister_folders" in actions:
            action_instances.append(
                {
                    "name": "unregister_folders",
                    "params": "Unregister Folders 'params'",
                    "caption": "Unregister Folders",
                    "description": "Unregisters folders for this Entity / Task.",
                }
            )            

        return action_instances

    def execute_multiple_actions(self, actions):
        """
        Executes the specified action on a list of items.

        The default implementation dispatches each item from ``actions`` to
        the ``execute_action`` method.

        The ``actions`` is a list of dictionaries holding all the actions to execute.
        Each entry will have the following values:

            name: Name of the action to execute
            sg_publish_data: Publish information coming from Shotgun
            params: Parameters passed down from the generate_actions hook.

        .. note::
            This is the default entry point for the hook. It reuses the ``execute_action``
            method for backward compatibility with hooks written for the previous
            version of the loader.

        .. note::
            The hook will stop applying the actions on the selection if an error
            is raised midway through.

        :param list actions: Action dictionaries.
        """
        app = self.parent
        app.log_info(f"Executing action '{actions}' on the selection")
        # Helps to visually scope selections
        # Execute each action.

        for single_action in actions:
            name = single_action["name"]
            sg_publish_data = single_action["sg_publish_data"]

            params = single_action["params"]
            self.execute_action(name, params, sg_publish_data)

    def execute_action(self, name, params, sg_publish_data):
        """
        Print out all actions. The data sent to this be method will
        represent one of the actions enumerated by the generate_actions method.

        :param name: Action name string representing one of the items returned by generate_actions.
        :param params: Params data, as specified by generate_actions.
        :param sg_publish_data: Shotgun data dictionary with all the standard publish fields.
        :returns: No return value expected.
        """
        app = self.parent
        engine = self.parent.engine
        app.log_debug(
            "Execute action called for action %s. "
            "Parameters: %s. Publish Data: %s" % (name, params, sg_publish_data)
        )

        # resolve path
        # toolkit uses utf-8 encoded strings internally and Maya API expects unicode
        # so convert the path to ensure filenames containing complex characters are supported
        # path = six.ensure_str(self.get_publish_path(sg_publish_data))

        if name == "preview_create_folders":  
            self.preview_create_folders(sg_publish_data['type'], [sg_publish_data['id']])            
        elif name == "create_folders":    
            self.create_folders(sg_publish_data['type'], [sg_publish_data['id']])                 
        elif name =="unregister_folders":
            self.unregister_folders(sg_publish_data['type'], [sg_publish_data['id']])           
            
    def preview_create_folders(self, entity_type, entity_ids):
        app = self.parent
        if len(entity_ids) == 0:
            app.log_error("No entities specified!")
            return
        app.log_info("--> Entity Type: %s" % entity_type)
        app.log_info("--> Entity IDs: %s" % entity_ids)

        paths = []
        try:
            paths.extend(
                app.tank.preview_filesystem_structure(entity_type, entity_ids)
            )

        except tank.TankError as tank_error:
            # tank errors are errors that are expected and intended for the user
            app.log_error(tank_error)

        except Exception:
            # other errors are not expected and probably bugs - here it's useful with a callstack.
            app.log_exception("Error when previewing folders!")

        else:
            # success! report back to user
            if len(paths) == 0:
                app.log_info("*No folders would be generated on disk for this item!*")

            else:
                app.log_info(
                    "*Creating folders would generate %d items on disk:*" % len(paths)
                )
                app.log_info("")
                for p in paths:
                    app.log_info(p.replace(r"\_", r"\\_"))
                app.log_info("")
                app.log_info(
                    "Note that some of these folders may exist on disk already."
                )

    def _add_plural(self, word, items):
        """
        appends an s if items > 1
        """
        if items > 1:
            return "%ss" % word
        else:
            return word

    def create_folders(self, entity_type, entity_ids):         
        app = self.parent
        if len(entity_ids) == 0:
            app.log_error("No entities specified!")
            return

        entities_processed = 0
        try:
            tk = sgtk.sgtk_from_entity(entity_type, entity_ids)   
            entities_processed = app.tank.create_filesystem_structure(
                entity_type, entity_ids
            )
            tk.synchronize_filesystem_structure()        

        except tank.TankError as tank_error:
            # tank errors are errors that are expected and intended for the user
            app.log_error(tank_error)

        except Exception:
            # other errors are not expected and probably bugs - here it's useful with a callstack.
            app.log_exception("Error when creating folders!")

        else:
            # report back to user
            app.log_info(
                "%d %s processed - "
                "Processed %d folders on disk."
                % (
                    len(entity_ids),
                    self._add_plural(entity_type, len(entity_ids)),
                    entities_processed,
                )
            )

    def unregister_folders(self, entity_type, entity_ids):    
        app = self.parent
        if len(entity_ids) == 0:
            app.log_error("No entities specified!")
            return

        try:

            uf = app.tank.get_command("unregister_folders")

            message = []
            for entity_id in entity_ids:
                tk = sgtk.sgtk_from_entity(entity_type, entity_id)   
                if entity_type == "Task":
                    parent_entity = self.parent.shotgun.find_one("Task",
                                        [["id", "is", entity_id]],
                                        ["entity"]).get("entity")
                    result = uf.execute({"entity": {"type": parent_entity["type"], "id": parent_entity["id"]}})      
                    message.append(result)                                  
                else:                
                    result = uf.execute({"entity": {"type": entity_type, "id": entity_id}})
                    message.append(result)
                tk.synchronize_filesystem_structure()        

        except tank.TankError as tank_error:
            # tank errors are errors that are expected and intended for the user
            app.log_error(tank_error)

        except Exception as error:
            # other errors are not expected and probably bugs - here it's useful with a callstack.
            app.log_exception("Error when unregiering folders: %s" % error)

        else:
            # report back to user
            app.log_info("Unregistered Folders: %s" % message)