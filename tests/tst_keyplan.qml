import QtQuick
import QtTest
import "../blades/KeyPlan.js" as KeyPlan

TestCase {
  name: "MemoryKeyPlanRegression"

  function action(key, modifiers) {
    return KeyPlan.action(key, modifiers === undefined ? Qt.NoModifier : modifiers)
  }

  function test_shift_r_rescans() {
    compare(action(Qt.Key_R, Qt.ShiftModifier), "rescan")
  }

  function test_host_tab_chords_pass_through() {
    compare(action(Qt.Key_Tab, Qt.ControlModifier), "")
    compare(action(Qt.Key_Backtab, Qt.ControlModifier | Qt.ShiftModifier), "")
    compare(action(Qt.Key_PageDown, Qt.ControlModifier), "")
    compare(action(Qt.Key_PageUp, Qt.ControlModifier), "")
    compare(action(Qt.Key_BracketLeft, Qt.ControlModifier), "")
    compare(action(Qt.Key_BracketRight, Qt.ControlModifier), "")
    compare(action(Qt.Key_Z, Qt.AltModifier), "")
  }

  function test_shared_tree_keys_are_not_duplicated() {
    var keys = [Qt.Key_J, Qt.Key_K, Qt.Key_H, Qt.Key_L, Qt.Key_G, Qt.Key_Home,
                Qt.Key_End, Qt.Key_PageUp, Qt.Key_PageDown, Qt.Key_Slash,
                Qt.Key_Return, Qt.Key_Enter, Qt.Key_O, Qt.Key_R, Qt.Key_Escape,
                Qt.Key_Tab, Qt.Key_Backtab, Qt.Key_D, Qt.Key_U]
    var modifiers = [Qt.NoModifier, Qt.ControlModifier, Qt.AltModifier, Qt.MetaModifier]
    for (var k = 0; k < keys.length; k++)
      for (var m = 0; m < modifiers.length; m++)
        compare(action(keys[k], modifiers[m]), "")
  }

  function test_modified_shift_r_is_not_claimed() {
    compare(action(Qt.Key_R, Qt.ControlModifier | Qt.ShiftModifier), "")
    compare(action(Qt.Key_R, Qt.AltModifier | Qt.ShiftModifier), "")
    compare(action(Qt.Key_R, Qt.MetaModifier | Qt.ShiftModifier), "")
  }
}
