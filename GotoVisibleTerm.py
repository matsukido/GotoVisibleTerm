import sublime
import sublime_plugin


class GotoVisibleTermCommand(sublime_plugin.TextCommand):

    def run(self, edit):

        def focus_symbol(wordrgn):
            nonlocal KEY_ID, vw
            vw.add_regions(KEY_ID, [wordrgn], 
                                  flags=sublime.DRAW_NO_FILL,
                                  scope="invalid",
                                  icon="circle")

        def commit_symbol(wordrgns, idx):
            nonlocal KEY_ID, vw
            vw.erase_regions(KEY_ID)
            if idx >= 0:
                vw.sel().clear()
                vw.sel().add(wordrgns[idx])
        
        KEY_ID = "GotoVisibleTerm"
        punctset = frozenset("!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~")
        vw = self.view
        rgns = (rgn_scp[0]  for rgn_scp in 
                   vw.extract_tokens_with_scopes(vw.visible_region()))

        words = []
        wordrgns = []
        for rgn in rgns:
            word = vw.substr(rgn)
            if not (set(word) <= punctset or word.isspace()):
                words.append(word)
                wordrgns.append(rgn)

        vw.window().show_quick_panel(words, 
                on_highlight=lambda idx:focus_symbol(wordrgns[idx]),
                on_select=lambda idx:commit_symbol(wordrgns, idx),
                placeholder="=")

