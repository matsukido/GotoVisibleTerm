import sublime
import sublime_plugin
import html


class GotoVisibleTermCommand(sublime_plugin.TextCommand):

    KEY_ID = "GotoVisibleTerm"

    def run(self, edit):

        def focus_symbol(wordrgn, word):
            nonlocal vw
            vw.add_regions(key=self.KEY_ID, 
                           regions=[wordrgn], 
                           flags=sublime.DRAW_NO_FILL,
                           scope="invalid",
                           icon="circle",
                           annotations=[word],
                           annotation_color="#aa0")

        def commit_symbol(wordrgns, idx, event):
            nonlocal vw
            vw.erase_regions(self.KEY_ID)
            if idx < 0:
                return

            rgn = wordrgns[idx]
            if event["modifier_keys"].get("shift", False):
                rgn = rgn.cover(vw.sel()[0])
                if wordrgns[idx] < vw.sel()[0]:
                    rgn.a, rgn.b = rgn.b, rgn.a

            vw.sel().clear()
            vw.sel().add(rgn)
        
        vw = self.view
        punctset = frozenset("!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~")
        rgns = (rgn_scp[0]  for rgn_scp in 
                   vw.extract_tokens_with_scopes(vw.visible_region()))

        wordrgns = []
        qpitems = []
        for rgn in rgns:
            word = vw.substr(rgn)
            if set(word) <= punctset or word.isspace():
                continue

            wordrgns.append(rgn)
            qpitems.append(sublime.QuickPanelItem(
                      trigger=word, 
                      annotation=html.escape(vw.substr(vw.line(rgn)), False)))

        vw.window().show_quick_panel(
                items=qpitems, 
                on_highlight=lambda idx: focus_symbol(wordrgns[idx], qpitems[idx].trigger),
                on_select=lambda idx, evt: commit_symbol(wordrgns, idx, evt),
                flags=sublime.WANT_EVENT,
                placeholder="=")
