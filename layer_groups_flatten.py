#!/usr/bin/env python

from gimpfu import *

def prepare_image(original_image):
    """
    Prepare a new image based on the specified one.
    """
    return gimp.Image(original_image.width, original_image.height, original_image.base_type)

def prepare_layer(image, original_layer):
    """
    Prepare a layer for the specified image, and based on specified layer.
    """
    result_layer = gimp.Layer(image, original_layer.name, original_layer.width, 
         original_layer.height, original_layer.type, original_layer.opacity,
         original_layer.mode)
    result_layer.set_offsets(*original_layer.offsets)
    return result_layer

def merge_down_layer_group(image, group_layer):
    """
    Merges down all the layers within the group and returns the resulting layer.
    """
    assert pdb.gimp_item_is_group(group_layer)
    result_layer = None
    if len(group_layer.layers) > 0:
       result_layer = group_layer.layers[0]
       for _x in range(len(group_layer.layers)-1):
          result_layer = pdb.gimp_image_merge_down(image, result_layer, 0)
    return result_layer

def copy_layer_contents(source_image, source_layer, target_image, target_layer, target_index):
    """
    Copies the content of one layer to the other. Returns the index of the copied layer.
    """
    target_image.add_layer(target_layer, target_index)
    # Before copying the layer contents clear any selection if needed
    if not pdb.gimp_selection_is_empty(source_image):
        pdb.gimp_selection_clear(source_image)
    pdb.gimp_edit_copy(source_layer)
    floating_sel = pdb.gimp_edit_paste(target_layer, 1)
    pdb.gimp_floating_sel_anchor(floating_sel)
    return target_layer

def layer_groups_flatten(source_image, _ign, as_new_image, autocrop):
    """
    Script entrypoint.
    """
    pdb.gimp_message_set_handler(MESSAGE_BOX)
    target_index = 0
    op_started = False
    image_touched = False
    target_image = None
    if as_new_image:
        target_image = prepare_image(source_image)
    # Use a baked copy of the image layers because we may need to
    # re-arrange / delete some layers.
    original_layers = list(source_image.layers)
    if not as_new_image:
        # Modifying current image. Register an undo group
        pdb.gimp_image_undo_group_start(source_image)
    for item in original_layers:
        if pdb.gimp_item_is_group(item):
            if len(item.layers) == 0:
                continue # Ignore empty layer groups
            if not op_started:
                # First group found
                op_started = True
            # Process the layer group
            if not as_new_image:
                target_layer = merge_down_layer_group(source_image, item)
                image_touched = True
                # Crop the layer if needed before anything else
                if autocrop:
                    pdb.plug_in_autocrop_layer(source_image, target_layer)
                target_name = item.name # Save the layer group name
                # Move the layer 
                pdb.gimp_image_reorder_item(source_image, target_layer, None, target_index)
                target_index += 1
                # We can get rid of the group layer now
                source_image.remove_layer(item)
                # Now rename the resulting layer
                target_layer.name = target_name
            else:
                target_layer = prepare_layer(target_image, item)
                target_layer = copy_layer_contents(source_image, item, target_image, target_layer, target_index)
                target_index += 1
                if autocrop:
                    pdb.plug_in_autocrop_layer(target_image, target_layer)
        else:
            # The non-group layers will move along in the same order they are found
            if not as_new_image:
                pdb.gimp_image_reorder_item(source_image, item, None, target_index)
                image_touched = True
                target_index += 1
                # Crop the layer if needed.
                if autocrop:
                    pdb.plug_in_autocrop_layer(source_image, item)
            else:
                target_layer = prepare_layer(target_image, item)
                target_layer = copy_layer_contents(source_image, item, target_image, target_layer, target_index)
                target_index += 1
                if autocrop:
                    pdb.plug_in_autocrop_layer(target_image, target_layer)

    # After processing all the groups
    if not as_new_image:
        pdb.gimp_image_undo_group_end(source_image)

    if not op_started and image_touched:
        pdb.gimp_message("Whoops! No groups were found but some layers may have been re-arranged.")
    elif not op_started:
        if target_image is not None:
            # We have created an un-needed image. We neeed to clean up.
            pdb.gimp_image_delete(target_image)
        pdb.gimp_message("No groups were found on the current image.")
    elif op_started and target_image is not None:
        # Process finished successfully. We need to show up the new image.
        pdb.gimp_display_new(target_image)
    return

register(
      "python_fu_layer_groups_flatten",
      "It will merge all the layers within the same group",
      ("It will merge all the layers within the same group and pop them out. "
        "It will preserve the same order and name for the resulting layers. "
        "It ignores empty layer groups."
      ),
      "Lordscales91",
      "Lordscales91",
      "July 2018",
      "<Image>/Layer/Layer Groups Flatten",
      "*", # It just organizes layers, image's type shouldn't be a problem
      [
         (PF_BOOL, "as_new", "Flatten to a new image?", True),
         (PF_BOOL, "autocrop", "Autocrop resulting layers?", True)
      ],
      [],
      layer_groups_flatten
)

main()