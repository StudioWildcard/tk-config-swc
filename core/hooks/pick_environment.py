# Copyright (c) 2018 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
Hook which chooses an environment file to use based on the current context.
"""

import sgtk

logger = sgtk.platform.get_logger(__name__)


class PickEnvironment(sgtk.Hook):
    def execute(self, context, **kwargs):
        """
        The default implementation assumes there are three environments, called shot, asset
        and project, and switches to these based on entity type.
        """

        if context.source_entity:
            if context.source_entity["type"] == "Version":
                return "version"
            elif context.source_entity["type"] == "PublishedFile":
                return "publishedfile"
            elif context.source_entity["type"] == "Playlist":
                return "playlist"

        if context.project is None:
            # Our context is completely empty. We're going into the site context.
            return "site"

        if context.entity is None:
            # We have a project but not an entity.
            return "project"

        if context.entity and context.step is None:
            # logger.info(">> We have an entity but no step.")
            if context.entity["type"] == "Asset":
                context_entity = context.sgtk.shotgun.find_one("Asset",
                                                               [["id", "is", context.entity["id"]]],
                                                               ["sg_asset_parent","sg_asset_library","sg_asset_type","sg_asset_section","sg_asset_category","sg_asset_class"])
                
                # Child Assets
                if context_entity.get("sg_asset_parent"):
                    if context_entity.get("sg_asset_type") == "Animations":
                        return "anim_asset"
                    elif context_entity.get("sg_asset_type") == "NoType":
                        return "notype_child"
                    else:
                        return "asset_child"
                else:

                    if context_entity.get("sg_asset_section") and context_entity.get("sg_asset_category") and context_entity.get("sg_asset_class"):           
                        return "asset_section_category_class"  
                    elif context_entity.get("sg_asset_section") and context_entity.get("sg_asset_category"):
                        return "asset_section_category"
                    elif context_entity.get("sg_asset_section"):
                        return "asset_section"

                    # Library Assets
                    if context_entity.get("sg_asset_library") == "Lib":
                        return "asset"

                    # Weapon Assets
                    if context_entity.get("sg_asset_type") == "NoType":
                        return "notype"                

                    return "asset"
            elif context.entity["type"] == "Sequence":
                return "sequence" 
            elif context.entity["type"] == "Shot":
                return "shot"                     

            elif context.entity["type"] == "CustomEntity03":
                context_entity = context.sgtk.shotgun.find_one("CustomEntity03",
                                                               [["id", "is", context.entity["id"]]],
                                                               ["sg_asset_type"])
                if context_entity.get("sg_asset_type") == "Campaigns":
                    return "pub_asset"
                return "prod_asset"                   

        if context.entity and context.step:
            # We have a step and an entity.
            # logger.info(">> We have a step and an entity.")
            if context.entity["type"] == "Asset":
                context_entity = context.sgtk.shotgun.find_one("Asset",
                                                               [["id", "is", context.entity["id"]]],
                                                               ["sg_asset_parent","sg_asset_library","sg_asset_type","sg_asset_section","sg_asset_category","sg_asset_class"])
                context_step = context.sgtk.shotgun.find_one("Step",
                                                             [["id", "is", context.step["id"]]],
                                                             ["sg_step_folder"])

                # Child Assets
                if context_entity.get("sg_asset_parent"):
                    if context_entity.get("sg_asset_type") == "Animations":
                        logger.info("Entity is an anim_asset_step")
                        return "anim_asset_step"
                    # NoType
                    elif context_entity.get("sg_asset_type") == "NoType":
                        logger.info("Entity is a notype_child_step")
                        return "notype_child_step"                    
                    else:
                        logger.info("Entity is an asset_child_step")
                        return "asset_child_step"
                else:
                    if not context_step.get("sg_step_folder"):
                        return "asset_step_flat"
                    
                    if context_entity.get("sg_asset_section") and context_entity.get("sg_asset_category") and context_entity.get("sg_asset_class"):           
                        logger.info("Entity is an asset_section_category_class_step")        
                        return "asset_section_category_class_step"  
                    elif context_entity.get("sg_asset_section") and context_entity.get("sg_asset_category"):
                        logger.info("Entity is an asset_section_category_step")
                        return "asset_section_category_step"
                    elif context_entity.get("sg_asset_section"):
                        logger.info("Entity is an asset_section_step")                    
                        return "asset_section_step"

                    if context_entity.get("sg_asset_library") == "Lib":
                        logger.info("Entity is a library asset")
                        return "asset"
                    
                    # NoType
                    if context_entity.get("sg_asset_type") == "NoType":
                        logger.info("Entity is a notype_step")
                        return "notype_step"
                    
                    logger.info("Entity is an asset_step")
                    return "asset_step"
            elif context.entity["type"] == "Sequence":
                logger.info("Entity is a sequence_step")
                return "sequence_step"  
            elif context.entity["type"] == "Shot":
                logger.info("Entity is a shot_step")
                return "shot_step"  

            elif context.entity["type"] == "CustomEntity03":
                context_entity = context.sgtk.shotgun.find_one("CustomEntity03",
                                                               [["id", "is", context.entity["id"]]],
                                                               ["sg_asset_type"])
                if context_entity.get("sg_asset_type") == "Campaigns":
                    logger.info("Entity is a pub_asset_step")
                    return "pub_asset_step"
                logger.info("Entity is a prod_asset_step")
                return "prod_asset_step"

        return None
