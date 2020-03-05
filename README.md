# Noode Editor
A generic Node Editor

## Features
- Easily extensible
- Edit nodes similar to blenders node editor

## Screenshots

![Editor Window](/Screenshots/NodeEditor1.png?raw=true "The Editor")

## Requirements
- Python 3.x
- Panda3D 1.10.4.1+

## Manual
Add nodes by selecting the node from the Nodes menu

### Startup
To start the Node Editor, simply run the NodeEditor.py script

<code>python NodeEditor.py</code>

### Basic Editing
Adding Nodes
1. Select a Node from the menub
2. The node will be attached to your mouse, drag it wherever you want and left click to place it

To connecting Nodes simply click and drag from a nodes output socket to an input socket of another nodepath. The direction you drag doesn't matter here, you can also drag from out- to input socket.
To disconnect a connection between two sockets, simply repeat the same behaviour as when you want to connect them.

Selecting nodes can either be done by left clicking them or by draging a frame around them. Use shift-left click to add nodes to the selection. Right- or left-click anywhere on the editor to deselect the nodes.

Use the left mouse button and drag on any free space on the editor to move the editor area around

### Zooming
Use the mousewheel or the view menu to zoom in and out in the editor.

### Copying Nodes
Select one or more nodes and hit shift-D to copy all nodes. Drag them to the desired location and left click to place them.

### Remove elements
Click X while having at least one node selected or use the Tools menu.

### Save and loading
Saving and loading is currently not implemented

### Use exported scripts
The python script will always contain a class called Gui which you can pass a NodePath to be used as root parent element for the GUI. Simply instancing the class will make the GUI visible by default. If this is not desired, hide the root NodePath as given on initialization. As you shouldn't edit the exported class due to edits being overwritten with a new export, you should create another python module which will handle the connection of the apps logic with the gui. This dedicated module could for example implement a show and hide method to easily change the visibility of the gui or set and gather values of the GUI without having to change the actual GUI design module code.

### Custom Nodes
To add your own Nodes, create a new python script in the /NodeCore/Nodes folder. These Nodes need derive from NodeBase and at least should implement a logic method that handles the in and output of the node.

## Known Bugs and missing features
- Loading and saving
- Some more basic nodes
- Configurations
