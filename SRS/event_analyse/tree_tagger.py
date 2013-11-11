import treetaggerwrapper


class TreeTagger:
    """
    This class allows you to parse a text and the grammar structure of it.
    An example : tags = TreeTagger().tag_text(..., TreeTagger.noun + TreeTagger.verb)
    """
    abbreviation = 'ABR'
    adjective = 'ADJ'
    adverb = 'ADV'
    determinant = 'DET:ART', 'DET:POS'
    interjection = 'INT'
    conjunction = 'KON'
    proper_name = 'NAM'
    noun = 'NOM'
    numeral = 'NUM'
    pronoun = 'PRO', 'PRO:DEM', 'PRO:IND', 'PRO:PER', 'PRO:POS', 'PRO:REL'
    preposition = 'RP', 'PRP:det'
    punctuation = 'PUN', 'PUN:cit'
    sentence_tag = 'SENT'
    symbol = 'SYM'
    verb = 'VER:cond', 'VER:futu', 'VER:impe', 'VER:impf', 'VER:infi', 'VER:pper', 'VER:ppre', 'VER:pres', \
           'VER:simp', 'VER:subi', 'VER:subp'
    not_correspondence_found = '<unknown>'

    tag_lang = 'fr'
    tag_dir = 'treetagger'
    tag_in_enc = 'utf-8'
    tag_out_enc = 'utf-8'

    def __init__(self):
        self.tagger = treetaggerwrapper.TreeTagger(TAGLANG=TreeTagger.tag_lang, TAGDIR=TreeTagger.tag_dir,
                                                   TAGINENC=TreeTagger.tag_in_enc, TAGOUTENC=TreeTagger.tag_out_enc)

    def tag_text(self, text, params=[], all_tags=False):
        """
        Parse a text with the tags in params. If params is empty, everything will be kept.
        For more information about the tags, please consult the following link :
        http://www.ims.uni-stuttgart.de/institut/mitarbeiter/schmid/french-tagset.html.
        """
        tags = self.tagger.TagText(text)
        out = list()
        all_tags_refuse = list(TreeTagger.punctuation) + list(TreeTagger.sentence_tag)

        for tag in tags:
            t = tag.split()
            try:
                if (all_tags and t[1] not in all_tags_refuse) or (not all_tags and (len(params) == 0 or t[1] in params)):
                    if t[2] != TreeTagger.not_correspondence_found:
                        out.append(t[2])
            except:
                pass

        return out
