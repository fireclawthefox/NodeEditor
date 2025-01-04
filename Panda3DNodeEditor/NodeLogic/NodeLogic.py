
from ast import *
import astor
import ast

class NodeLogic:

    def updateAllLeaveNodes(self):
        leaves = []
        for node in self.nodeList:
            if node.isLeaveNode():
                leaves.append(node)

        for leave in leaves:
            leave.logic()
            self.updateConnectedNodes(leave)

    def updateDisconnectedNodesLogic(self, plugA, plugB):
        """
        Updates the logic of the nodes of socket A and socket B.
        The respective input plug type sockets value will be set to None.
        """
        # Update logic of out socket node
        outSocketNode = plugA.socket.node if plugA.socket.type is OUTSOCKET else plugB.socket.node
        outSocketNode.logic()
        self.updateConnectedNodes(outSocketNode)

        # Update logic of in socket node
        inSocketNode = plugA.socket.node if plugA.socket.type is INSOCKET else plugB.socket.node
        inPlug = plugA if plugA.socket.type is INSOCKET else plugB
        print(inPlug.socket)
        print("CALL setValue of SOCKET?")
        inPlug.socket.setValue(inPlug, None)
        inSocketNode.logic()
        self.updateConnectedNodes(inSocketNode)

    def updateSocketNodeLogic(self, socket, plug):
        """Update the logic of the given node and all nodes connected
        down the given"""
        print("UPDATE LOGIC")
        if socket.type is INSOCKET:
            plug.setValue(None)
        socket.node.logic()
        self.updateConnectedNodes(socket.node)

    def updateConnectedNodes(self, leaveNode):
        self.processedConnections = []
        self.startNode = leaveNode
        self.__updateConnectedNodes(leaveNode)

    def __updateConnectedNodes(self, leaveNode):
        return
        """Update logic of all nodes connected the leave nodes
        out sockets recursively down to the last connected node."""
        print("Update leave node")
        for connector in self.connections:
            for outSocket in leaveNode.outputList:
                outSock = None
                outPlug = None
                inSock = None
                inPlug = None

                if connector.socketA is outSocket:
                    inSock = connector.socketB
                    inPlug = connector.plugB
                    outSock = connector.socketA
                    outPlug = connector.plugA
                elif connector.socketB is outSocket:
                    inSock = connector.socketA
                    inPlug = connector.plugA
                    outSock = connector.socketB
                    outPlug = connector.plugB
                else:
                    continue

                connector.setChecked()
                outSock.node.logic()
                print("SETTING VALUE OF PLUG NOE!")
                print("out", outSock.getValue())
                print("in", inSock.getValue())
                print("out sock:", outSock)
                print("in sock:", inSock)
                print("out plug:", outPlug)
                print("in plug:", inPlug)
                inSock.setValue(inPlug, outSock.getValue())
                inSock.node.logic()

                if connector in self.processedConnections:
                    # this connector is leading to a recursion
                    connector.setError(True)
                    continue
                self.processedConnections.append(connector)

                self.__updateConnectedNodes(inSock.node)

                if connector in self.processedConnections:
                    self.processedConnections.remove(connector)
                else:
                    print("SOMETHING WENT WRONG!")

    def run_logic(self, args=None):
        print("PYTHON:")

        """
        FunctionDef(
            name='myFunc',
            args=arguments(
                posonlyargs=[],
                args=[arg(arg='a'), arg(arg='b')],
                kwonlyargs=[],
                kw_defaults=[],
                defaults=[]),


            arguments(
                posonlyargs=[],
                args=[arg(arg='a'), arg(arg='b')],
                vararg=arg(arg='kw'),
                kwonlyargs=[],
                kw_defaults=[],
                kwarg=arg(arg='kwargs')


            body=[
                Expr(value=Constant(value=Ellipsis))],
            decorator_list=[])


        Module(
            body=[
                Expr(
                    value=Call(
                        func=Name(
                            id='print',
                            ctx=Load()
                        ),
                        args=[
                            Constant(value='Test')
                        ],
                        keywords=[]
                    )
                )
            ],
        type_ignores=[])


        Call(func=Name(id='print', ctx=Load()),args={Arguments}, keywords=[])
        """
        """
        Module([
            FunctionDef(
                name="MyFunc",
                args=arguments(
                    posonlyargs=[],
                    args=[],
                    kwonlyargs=[],
                    kw_defaults=[],
                    defaults=[]),
                body=[
                    Call(
                        func=Name(
                            id='print',
                            ctx=Load()
                        ),
                        args=[arg("Test")],
                        keywords=[]
                    )],
                decorator_list=[],
                returns=None,
                type_comment="")], [])
        """

        #astString = ast.dump(ast.parse("def myFunc(a, /, b, c:d, e=f, *g, **h):\n\tprint('Test')"))
        astString = self.getASTEval()
        print(astString)
        if astString is None:
            logging.error("No Entry Node found!")
            return
        astTree = eval(astString)
        print(astString)
        print(astTree)
        print(ast.dump(astTree, indent=4))
        ast.fix_missing_locations(astTree)
        print(ast.unparse(astTree))
        #print(self.getPythonScript())
        code = astor.to_source(astTree)
        print("PYTHON CODE:")
        print("")
        print(code)

    def replacePlaceholders(self, node, text):
        self.visitedNodes.append(node)
        print("PLACEHOLDERS ON NODE: ", node)
        print("MY TEXT: ", text)
        for socket in node.inputList:
            placeholderTypes = ["arguments:", "*", "?"]
            placeholders = [f"{socket.name}"]
            for pt in placeholderTypes:
                for placeholder in placeholders[:]:
                    placeholders.append(f"{pt}{placeholder}")
            for i in range(len(placeholders)):
                placeholders[i] = f"{{{placeholders[i]}}}"

            print("SOCKET: ", socket.name)
            print(placeholders)

            socketValue = socket.getValue()
            replText = str(socketValue)
            if type(socketValue) == str:
                replText = f"\"{replText}\""
            isStarred = False
            isOptional = False
            isArguments = False
            for placeholder in placeholders:
                if "*" in placeholder:
                    placeholder.replace("*", "")
                    isStarred = True
                if "?" in placeholder:
                    placeholder.replace("?", "")
                    isOptional = True

                if "arguments:" in placeholder:
                    placeholder.replace("arguments:", "")
                    isArguments = True

                if placeholder not in text:
                    continue

                if isOptional \
                and socket.getValue() == None:
                    replText = ""
                elif isArguments:
                    strValues = []
                    socketValue = socket.getValue()
                    if socketValue is not None:
                        if type(socketValue) == list:
                            for value in socketValue:
                                strValues.append(f"arg(\"{value}\")")
                            replText = ",".join(strValues)
                        else:
                            replText = f"arg(\"{socketValue}\")"
                elif isStarred:
                    strValues = []
                    if socket.getValue() is not None:
                        for value in socket.getValue():
                            strValues.append(str(value))
                    replText = ",".join(strValues)

                print("Replacing '", placeholder, "' with '", replText, "'")
                text = text.replace(placeholder, replText)
                break

        for socket in node.outputList:
            placeholder = f"{{{socket.name}}}"
            connections = self.getConnectionsOfSocket(socket)
            if len(connections) == 0: continue
            # since we only allow one connection per socket on those
            # nodes, we can savely take the first
            connector = connections[0]
            otherSocket = None
            if connector.socketA is socket:
                otherNode = connector.socketB.node
            else:
                otherNode = connector.socketA.node
            #if otherNode not in self.visitedNodes:
            template = self.replacePlaceholders(otherNode, otherNode.customAttributes["py"])
            #else:
            #    template = otherNode.customAttributes["py"]
            text = text.replace(placeholder, template)
        return text

    def getASTEval(self):
        self.visitedNodes = []
        for node in self.nodeList:
            if "isRoot" in node.customAttributes \
            and node.customAttributes["isRoot"]:
                print("FOUND ROOT")
                return self.replacePlaceholders(node, node.customAttributes["py"])

    def getAst(self):
        """Returns the Abstract Syntax Tree representation of this node"""

        pyScript = self.getPythonScript()
        try:
            print(f"pasre:\n{pyScript}")
            self.astRepr = ast.parse(pyScript, type_comments=True)
        except:
            pass

        return self.astRepr
