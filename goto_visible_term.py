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

        def commit_term(termrgns, idx, event):
            nonlocal vw
            vw.erase_regions(self.KEY_ID)
            if idx < 0:
                return

            rgn = termrgns[idx]
            if event["modifier_keys"].get("shift", False):
                rgn = rgn.cover(vw.sel()[0])
                if termrgns[idx] < vw.sel()[0]:
                    rgn.a, rgn.b = rgn.b, rgn.a
                vw.sel().clear()
            
            elif event["modifier_keys"].get("ctrl", False):
                pass
            
            elif event["modifier_keys"].get("alt", False):
                emergency_rgn = sublime.Region(vw.sel()[0].b)
                try:
                    vw.sel().subtract(rgn)
                    vw.sel()[0]
                except IndexError:
                    vw.sel().add(emergency_rgn)
                return

            else:
                vw.sel().clear()

            vw.sel().add(rgn)
        
        vw = self.view
        punctset = frozenset("!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~")

        rgns = invert_region(vw.visible_region(), vw.folded_regions())
        rgn_scp = map(vw.extract_tokens_with_scopes, rgns)
        word_rgns, _ = zip(*itools.chain.from_iterable(rgn_scp))

        termrgns, qpitems = [], []
        index = itools.count(-1)
        tgtpt = vw.sel()[0].begin()

        for rgn in word_rgns:
            word = vw.substr(rgn)
            if set(word) <= punctset or word.isspace():
                continue

            termrgns.append(rgn)
            qpitems.append(sublime.QuickPanelItem(
                      trigger=word, 
                      annotation=html.escape(vw.substr(vw.line(rgn)), False)))
            (rgn.a <= tgtpt) and next(index)

        vw.window().show_quick_panel(
                items=qpitems, 
                on_highlight=lambda idx: focus_term(termrgns[idx], qpitems[idx].trigger),
                on_select=lambda idx, evt: commit_term(termrgns, idx, evt),
                flags=sublime.WANT_EVENT,
                selected_index=next(index),
                placeholder="=")
