"""Test connector item connectors."""

from gaphor import UML
from gaphor.tests import TestCase
from gaphor.UML.classes.dependency import DependencyItem
from gaphor.UML.classes.interface import Folded, InterfaceItem, Side
from gaphor.UML.classes.interfacerealization import InterfaceRealizationItem
from gaphor.UML.components import ComponentItem, ConnectorItem
from gaphor.UML.components.connectorconnect import ConnectorConnectBase


class ComponentConnectTestCase(TestCase):
    """Test connection of connector item to a component."""

    def test_glue(self):
        """Test gluing connector to component."""

        component = self.create(ComponentItem, UML.Component)
        line = self.create(ConnectorItem)

        glued = self.allow(line, line.head, component)
        assert glued

    def test_connection(self):
        """Test connecting connector to a component."""
        component = self.create(ComponentItem, UML.Component)
        line = self.create(ConnectorItem)

        self.connect(line, line.head, component)
        assert line.subject is None

    def test_glue_both(self):
        """Test gluing connector to component when one is connected."""

        c1 = self.create(ComponentItem, UML.Component)
        c2 = self.create(ComponentItem, UML.Component)
        line = self.create(ConnectorItem)

        self.connect(line, line.head, c1)
        glued = self.allow(line, line.tail, c2)
        assert not glued


class InterfaceConnectTestCase(TestCase):
    """Test connection with interface acting as assembly connector."""

    def test_non_folded_glue(self):
        """Test non-folded interface gluing."""

        iface = self.create(InterfaceItem, UML.Component)
        line = self.create(ConnectorItem)

        glued = self.allow(line, line.head, iface)
        assert glued

    def test_folded_glue(self):
        """Test folded interface gluing."""

        iface = self.create(InterfaceItem, UML.Component)
        line = self.create(ConnectorItem)

        iface.folded = Folded.REQUIRED
        glued = self.allow(line, line.head, iface)
        assert glued

    def test_glue_when_dependency_connected(self):
        """Test interface gluing, when dependency connected."""

        iface = self.create(InterfaceItem, UML.Component)
        dep = self.create(DependencyItem)
        line = self.create(ConnectorItem)

        self.connect(dep, dep.head, iface)

        iface.folded = Folded.REQUIRED
        glued = self.allow(line, line.head, iface)
        assert glued

    def test_glue_when_implementation_connected(self):
        """Test interface gluing, when implementation connected."""

        iface = self.create(InterfaceItem, UML.Component)
        impl = self.create(InterfaceRealizationItem)
        line = self.create(ConnectorItem)

        self.connect(impl, impl.head, iface)

        iface.folded = Folded.REQUIRED
        glued = self.allow(line, line.head, iface)
        assert glued

    def test_glue_when_connector_connected(self):
        """Test interface gluing, when connector connected."""

        iface = self.create(InterfaceItem, UML.Interface)
        comp = self.create(ComponentItem, UML.Component)
        iface.folded = Folded.REQUIRED

        line1 = self.create(ConnectorItem)
        line2 = self.create(ConnectorItem)

        self.connect(line1, line1.tail, comp)
        self.connect(line1, line1.head, iface)
        assert Folded.PROVIDED == iface.folded

        glued = self.allow(line2, line2.head, iface)
        assert glued

    def test_simple_connection(self):
        """Test simple connection to an interface."""
        iface = self.create(InterfaceItem, UML.Interface)
        comp = self.create(ComponentItem, UML.Component)
        line = self.create(ConnectorItem)

        self.connect(line, line.head, iface)
        self.connect(line, line.tail, comp)
        iface.request_update()
        self.diagram.update_now((iface, comp, line))

        # interface goes into assembly mode
        assert iface.folded == Folded.PROVIDED
        # no UML metamodel yet
        assert line.subject

    def test_simple_disconnection(self):
        """Test disconnection of simple connection to an interface."""
        iface = self.create(InterfaceItem, UML.Component)
        line = self.create(ConnectorItem)

        iface.folded = Folded.PROVIDED

        self.connect(line, line.head, iface)

        self.disconnect(line, line.head)
        assert Folded.PROVIDED == iface.folded
        assert iface.side == Side.N

        assert all(p.connectable for p in iface.ports())


class AssemblyConnectorTestCase(TestCase):
    """Test assembly connector.

    It is assumed that interface and component connection tests defined
    above are working correctly.
    """

    def create_interfaces(self, *args):
        """Generate interfaces with names specified by arguments.

        :Parameters:
         args
            List of interface names.
        """
        for name in args:
            interface = self.element_factory.create(UML.Interface)
            interface.name = name
            yield interface

    def provide(self, component, interface):
        """Change component's data so it implements interfaces."""
        impl = self.element_factory.create(UML.InterfaceRealization)
        component.interfaceRealization = impl
        impl.contract = interface

    def require(self, component, interface):
        """Change component's data so it requires interface."""
        usage = self.element_factory.create(UML.Usage)
        component.clientDependency = usage
        usage.supplier = interface

    def test_getting_component(self):
        """Test getting component."""
        conn1 = self.create(ConnectorItem)
        conn2 = self.create(ConnectorItem)

        c1 = self.create(ComponentItem, UML.Component)
        c2 = self.create(ComponentItem, UML.Component)

        # connect component
        self.connect(conn1, conn1.tail, c1)
        self.connect(conn2, conn2.head, c2)

        assert c1 is ConnectorConnectBase.get_component(conn1)
        assert c2 is ConnectorConnectBase.get_component(conn2)

    def test_connection(self):
        """Test basic assembly connection."""
        conn1 = self.create(ConnectorItem)
        conn2 = self.create(ConnectorItem)

        c1 = self.create(ComponentItem, UML.Component)
        c2 = self.create(ComponentItem, UML.Component)

        iface = self.create(InterfaceItem, UML.Interface)
        iface.folded = Folded.ASSEMBLY

        # first component provides interface
        # and the second one requires it
        self.provide(c1.subject, iface.subject)
        self.require(c2.subject, iface.subject)

        # connect component
        self.connect(conn1, conn1.head, c1)
        self.connect(conn2, conn2.head, c2)

        # make an assembly
        self.connect(conn1, conn1.tail, iface)
        self.connect(conn2, conn2.tail, iface)

        # test UML data model
        self.assertTrue(
            conn1.subject is conn2.subject, f"{conn1.subject} is not {conn2.subject}"
        )
        assembly = conn1.subject
        assert isinstance(assembly, UML.Connector)
        assert "assembly" == assembly.kind

        # there should be two connector ends
        self.assertEqual(2, len(assembly.end))

    def test_required_port_glue(self):
        """Test if required port gluing works."""

        conn1 = self.create(ConnectorItem)
        conn2 = self.create(ConnectorItem)

        c1 = self.create(ComponentItem, UML.Component)
        c2 = self.create(ComponentItem, UML.Component)

        iface = self.create(InterfaceItem, UML.Interface)
        iface.folded = Folded.ASSEMBLY
        rport = iface.ports()[2]

        self.provide(c1.subject, iface.subject)
        self.require(c2.subject, iface.subject)

        # connect components
        self.connect(conn1, conn1.head, c1)
        self.connect(conn2, conn2.head, c2)

        self.connect(conn1, conn1.tail, iface)
        glued = self.allow(conn2, conn2.tail, iface, rport)
        assert glued

    def test_connection_order(self):
        """Test connection order of assembly connection."""
        conn1 = self.create(ConnectorItem)
        conn2 = self.create(ConnectorItem)

        c1 = self.create(ComponentItem, UML.Component)
        c2 = self.create(ComponentItem, UML.Component)

        iface = self.create(InterfaceItem, UML.Interface)

        # both components provide interface only
        self.provide(c1.subject, iface.subject)
        self.provide(c2.subject, iface.subject)

        # connect components
        self.connect(conn1, conn1.head, c1)
        self.connect(conn2, conn2.head, c2)

        # connect to provided port
        self.connect(conn1, conn1.tail, iface)
        self.connect(conn2, conn2.tail, iface)
        # no UML data model yet (no connection on required port)
        assert conn1.subject
        assert conn2.subject

    def test_addtional_connections(self):
        """Test additional connections to assembly connection."""
        conn1 = self.create(ConnectorItem)
        conn2 = self.create(ConnectorItem)
        conn3 = self.create(ConnectorItem)

        c1 = self.create(ComponentItem, UML.Component)
        c2 = self.create(ComponentItem, UML.Component)
        c3 = self.create(ComponentItem, UML.Component)

        iface = self.create(InterfaceItem, UML.Interface)
        iface.folded = Folded.ASSEMBLY

        # provide and require interface by components
        self.provide(c1.subject, iface.subject)
        self.require(c2.subject, iface.subject)
        self.require(c3.subject, iface.subject)

        # connect components
        self.connect(conn1, conn1.head, c1)
        self.connect(conn2, conn2.head, c2)
        self.connect(conn3, conn3.head, c3)

        # create assembly
        self.connect(conn1, conn1.tail, iface)
        self.connect(conn2, conn2.tail, iface)

        # test precondition
        assert conn1.subject and conn2.subject

        #  additional connection
        self.connect(conn3, conn3.tail, iface)

        # test UML data model
        self.assertTrue(conn3.subject is conn1.subject)

        assembly = conn1.subject

        assert 3 == len(assembly.end)

    def test_disconnection(self):
        """Test assembly connector disconnection."""
        conn1 = self.create(ConnectorItem)
        conn2 = self.create(ConnectorItem)

        c1 = self.create(ComponentItem, UML.Component)
        c2 = self.create(ComponentItem, UML.Component)

        iface = self.create(InterfaceItem, UML.Interface)
        iface.folded = Folded.ASSEMBLY

        # first component provides interface
        # and the second one requires it
        self.provide(c1.subject, iface.subject)
        self.require(c2.subject, iface.subject)

        # connect component
        self.connect(conn1, conn1.head, c1)
        self.connect(conn2, conn2.head, c2)

        # make an assembly
        self.connect(conn1, conn1.tail, iface)
        self.connect(conn2, conn2.tail, iface)

        # test precondition
        assert conn1.subject is conn2.subject

        self.disconnect(conn1, conn1.head)

        assert conn1.subject is None
        assert conn2.subject is None

        assert len(self.kindof(UML.Connector)) == 0
        assert len(self.kindof(UML.ConnectorEnd)) == 0
        assert len(self.kindof(UML.Port)) == 0
