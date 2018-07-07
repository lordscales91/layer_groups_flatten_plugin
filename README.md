# GIMP plug-in Layer Groups Flatten
A simple plug-in for GIMP to merge all layers within the same layer group. It lets you choose whether you want to flatten all the layer groups into a new image or use the current one. It also has an option to autocrop the resulting layers.

Installation
===
The procedure varies depending on the operating system. The following URL explains the common ones: https://en.wikibooks.org/wiki/GIMP/Installing_Plugins

The file that you need to copy is `layer_groups_flatten.py`

Usage
===
You can launch this plug-in from: Layer > Layer Groups Flatten

It prompts you with two options. Flatten to a new image will leave the current opened image as it is and create a flattened version of it. Preserving the same names of the layer groups that contained the layers. The names will also be preserved if you choose to modify the current image instead. Non-layer groups will move along and preserve the same order.

Additionally, you may choose to autocrop the resulting layers as well (it will also auto crop non-layer groups).

It will complain if the current image doesn't have any layer groups (or they are empty).

Caveats
===

* Due to a bug in GIMP. This plug-in will fail if the current active layer is a layer group. See: https://github.com/efexgee/mapper/issues/1
* If there is a selection active and you choose to flatten to a new image. The selection will be cleared. This is because this script uses the standard copy and paste functions internally to copy the layer contents to the new image. Therefore, the selection needs to be cleared, otherwise only the contents within the selection would be copied.

Implementation Details
===
The implementation varies depending on whether the current image is used or a new one is created instead. When using the current one, it loops through all layers and for each non-empty group found it will merge down all layers inside that group, pop the resulting layer out of the group, remove the group itself and finally rename the resulting layer using the group's name. So, this is a 4-step operation per each layer group.

When using a new image the first step is to create the new image, with same properties as the current one. Then, it loops through all layers and for each group found it will create a new layer with the same properties (size, position and name), add it to the new image, and finally it copies the contents of the group (which will be the combination of all its layers) to the new layer.