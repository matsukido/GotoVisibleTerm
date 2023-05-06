import sublime
import sublime_plugin
import html
import itertools as itools


def invert_region(region, regions):
    rgns = (region.intersection(rgn)  for rgn in regions if region.intersects(rgn))
    flatten = itools.chain([region.a], itools.chain(*rgns), [region.b])
    invrgns = itools.starmap(sublime.Region, zip(flatten, flatten))

    return (rgn  for rgn in invrgns if rgn.a < rgn.b)


class GotoVisibleTermCommand(sublime_plugin.TextCommand):

    KEY_ID = "GotoVisibleTerm"

    def run(self, edit):

        def focus_term(wordrgn, word):
            nonlocal vw
            vw.add_regions(key=self.KEY_ID, 
                           regions=[wordrgn], 
                           flags=sublime.DRAW_NO_FILL,
                           scope="invalid",
                           icon="circle",
                           annotations=[word],
                           annotation_color="#aa0")

        def commit_term(wordrgns, idx, event):
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
            
            elif event["modifier_keys"].get("ctrl", False):
                pass
            else:
                vw.sel().clear()

            vw.sel().add(rgn)
        
        vw = self.view
        punctset = frozenset("!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~")

        rgns = invert_region(vw.visible_region(), vw.folded_regions())
        rgn_scp = map(vw.extract_tokens_with_scopes, rgns)
        term_rgns, _ = zip(*itools.chain.from_iterable(rgn_scp))

        wordrgns = []
        qpitems = []
        for rgn in term_rgns:
            word = vw.substr(rgn)
            if set(word) <= punctset or word.isspace():
                continue

            wordrgns.append(rgn)
            qpitems.append(sublime.QuickPanelItem(
                      trigger=word, 
                      annotation=html.escape(vw.substr(vw.line(rgn)), False)))

        vw.window().show_quick_panel(
                items=qpitems, 
                on_highlight=lambda idx: focus_term(wordrgns[idx], qpitems[idx].trigger),
                on_select=lambda idx, evt: commit_term(wordrgns, idx, evt),
                flags=sublime.WANT_EVENT,
                placeholder="=")
