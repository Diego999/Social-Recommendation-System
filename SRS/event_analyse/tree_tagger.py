import treetaggerwrapper

class TreeTagger:
    """
    This class allows you to parse a text and the grammar structure of it.
    An example : tags = TreeTagger().tag_text(..., TreeTagger.noun + TreeTagger.verb)"""

    abbreviation = ['ABR']
    adjective = ['ADJ']
    adverb = ['ADV']
    determinant = ['DET:ART', 'DET:POS']
    interjection = ['INT']
    conjunction = ['KON']
    proper_name = ['NAM']
    noun = ['NOM']
    numeral = ['NUM']
    pronoun = ['PRO', 'PRO:DEM', 'PRO:IND', 'PRO:PER', 'PRO:POS', 'PRO:REL']
    preposition = ['RP', 'PRP:det']
    punctuation = ['PUN', 'PUN:cit']
    sentence_tag = 'SENT'
    symbol = ['SYM']
    verb = ['VER:cond', 'VER:futu', 'VER:impe', 'VER:impf', 'VER:infi', 'VER:pper', 'VER:ppre', 'VER:pres', 'VER:simp', 'VER:subi', 'VER:subp']
    not_correspondence_found = '<unknown>'

    def __init__(self):
        self.tagger = treetaggerwrapper.TreeTagger(TAGLANG='fr', TAGDIR='../treetagger', TAGINENC='utf-8', TAGOUTENC='utf-8')

    def tag_text(self, text, params=[]):
        """Parse a text with the tags in params. If params is empty, everything will be kept. For more information about the tags,
        please consult the following link : http://www.ims.uni-stuttgart.de/institut/mitarbeiter/schmid/french-tagset.html."""
        tags = self.tagger.TagText(text)
        out = list()

        for tag in tags:
            t = tag.split()
            if len(params) == 0 or t[1] in params:
                out.append(t)
        return out
