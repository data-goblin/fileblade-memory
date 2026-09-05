import QtQuick
import QtTest
import ".." as Memory

TestCase {
  name: "MemoryProviderService"
  Item { id: files }
  Component {
    id: providerComponent
    Memory.Service { manifest: ({id:"test.memory", __sourceDir:"/plugins/memory"}) }
  }

  function test_first_attach_loads_shared_inventory_and_observers_stay_bound() {
    var provider = createTemporaryObject(providerComponent, this)
    var view = { service: function() { return files }, ui: { url: function(name) {
      compare(name, "ArtifactInventory")
      return Qt.resolvedUrl("InventoryProbe.qml")
    } } }
    provider.attach(view)
    verify(provider.inventory !== null)
    compare(provider.inventory.files, files)
    compare(provider.inventory.providerId, "test.memory")
    compare(provider.inventory.providerRoot, "/plugins/memory")
    compare(provider.inventory.observers.length, 1)
    var runtime = provider.inventory
    provider.attach(view)
    compare(provider.inventory.observers.length, 1)
    provider.detach(view)
    compare(provider.inventory.observers.length, 0)
    provider.attach(view)
    compare(provider.inventory, runtime)
    compare(provider.inventory.observers.length, 1)
  }
}
