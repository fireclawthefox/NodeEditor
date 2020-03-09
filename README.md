# Node Editor
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
Select one or more nodes and hit shift-D to copy all nodes and their connections. Drag them to the desired location and left click with the left mouse button to place them.

### Remove elements
Click X while having at least one node selected or use the Tools menu.

### Save and loading
To save and load a node setup, click on the File menu and select Save or Load and select a JSON file to store or load from. You may name the files however you want.

### Custom Nodes
To add your own Nodes, create a new python script in the /NodeCore/Nodes folder. These Nodes need to derive from NodeBase and should at least implement a logic method that handles the in and output of the node.

## Known Bugs and missing features
- Some more basic nodes
- Configurations
