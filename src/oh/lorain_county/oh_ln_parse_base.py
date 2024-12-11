from core.extractor.parse_base import Parse_Base
from core.utilities.normalise import normalise_object_value
import re


class LorainCountyParseBase(Parse_Base):
    def __init__(self, case_id):
        super(LorainCountyParseBase, self).__init__(case_id)
        # Regex
        # For Prefix and Suffix
        # todo: suppose you are sure that your county is bound to get prefix from start only or suffix from the end of
        #  fullname, add ^ or $ in the below regexes.
        self.prefix_match_regex = re.compile(r'(\s|^|,\s*)(?P<prefix_suffix>mr|mr\.|ms|ms\.|mrs|mrs\.|dr|d'
                                             r'\.r\.|dr\.|Honorable|Hon\.?|st\.?)(?P<post_match>\s|$|\s*,|;)', re.I)
        self.suffix_match_regex = re.compile(r'(\s|^|,\s*)(?P<prefix_suffix>PhD|II|I\s*I\s*I\s*|IV|VI|VII|VIII'
                                             r'|Esquire|esq\.?|apdc|jr|jr\.|sr|sr\.|A\.?\s?S\.?\s?A\.?\s?|m\.?d\.?|'
                                             r'A\.?\s?P\.?\s?D\.?\s?|A\.?\s?A\.?\s?G\.?\s?|S\.?\s?A\.?\s?A\.?\s?G\.?)'
                                             r'(?P<post_match>\s|$|\s*,|;)', re.I)
        self.multi_comma_post_prefix_suffix_replace_regex = re.compile(r',\s*,')
        # Name cleaning regex
        # 1. The below regex is used to clean any word that is known to occur in the beginning of a name.
        #    For example "IN RE: THE ESTATE OF VIOLET TERRY" can be reduced to "THE ESTATE OF VIOLET TERRY"
        #    Put keyword using | in the to_remove_keyword group
        self.name_preceding_word_cleaning_regex = re.compile(r'^(?P<to_remove_keyword>In\s*RE\b\s*)(?P<cleaned_name>.*)$', flags=re.I)
        # 2. If keywords are to be removed frstate_zip_patternom the end of a name.
        #    Example: "STILES, JAY ET AL" can be reduced to STILES, JAY
        self.name_ending_word_cleaning_regex = re.compile(r'^(?P<cleaned_name>.*)(?P<to_remove_keyword>\bET\s+AL)$', flags=re.I)
        # 3. This regex is meant to identify some keyword from maybe middle of the name and get cleaned name that is
        #    present before such keywords. For example
        #    "EPSTEIN JAMAN JILL AS CO-TRUSTEE OF THE NORMAN EPSTEIN" can b reduced to "EPSTEIN JAMAN JILL" by
        #    adding "AS\s*CO-TRUSTEE\s*OF"
        self.midway_name_cleaning_regex = re.compile(r'^(?P<cleaned_name>.*)(?P<to_remove_keyword>(?:as)?\s*AN IND|\bINDI$|Individually)', flags=re.I)
        # 4. AKA regex requires a separate entry as FW method has to be called to get the most complete name
        self.aka_individual_pattern_match_regx = re.compile(
            r'\bA\/?K\/?A\b|ALSO\sKNOWN\sAS|\bF\/?K\/?A\b|FORMERLY\sKNOWN\sAS|\bN\/?K\/?A\b|NOW\sKNOWN\sAS|\bD\/?B\/?A\/?\b|Doing\s*Business\s*As', flags=re.I)
        # 5. AKA regex for company
        self.aka_company_pattern_match_regx = re.compile(
            r'\bA\/?K\/?A\b|ALSO\sKNOWN\sAS|\bF\/?K\/?A\b|FORMERLY\sKNOWN\sAS|\bN\/?K\/?A\b|'
            r'NOW\sKNOWN\sAS|\bD\/?B\/?A\/?\b|Doing\s*Business\s*As|C\/O', re.I)
        # 6. Company name cleaning regex
        #    Add your regex keywords using |
        self.company_name_cleaning_regex = re.compile(r'^(?P<company_name>.*)(AS\s+TRUSTEE|As\s+assignee\s+of'
                                                      r'|On\s+behalf\s+of)', flags=re.I)  
        # 7.regex pattern to match and removes the question mark
        self.remove_question_mark_regex = re.compile(r'\?')    
        
        # 8 List of regex patterns for specific removals (data-cleaning)
        self.specific_removal_patterns = [
            # Pattern to substitute invalid characters from full name. Example "James #123 Corner" to "James Corner"
            re.compile(r'#|\d|:|-|\?'),
            # Pattern to match dots
            re.compile(r'\.'),
            # Pattern to match and remove any text within parentheses.
            re.compile(r'\([^)]*\)'),
            # Pattern to match and remove "UNKNOWN SPOUSE OF" at the beginning of the string
            re.compile(r'^UNKNOWN SPOUSE OF\s+'),
            # Pattern to match and remove "UNKN SPS OF" at the beginning of the string
            re.compile(r'^UNKN\s+SPS\s+OF\s*'),
            # Pattern to match and remove the entire phrase starting with "UNKNOWN SPOUSE OF" if it's not at the beginning of the string
            re.compile(r'(?<!^)UNKNOWN SPOUSE OF\s+[A-Z]+\s?(\w+\s?)*[A-Z]'),
            # Pattern to match and remove the entire phrase starting with "UNKN SPS OF" if it's not at the beginning of the string
            re.compile(r'(?<!^)UNKN\s+SPS\s+OF\s*'),
            # Pattern to match and remove "UNKNOWN SPOUSEOF" not at the beginning of the string, followed by any characters until the end of the string
            re.compile(r'(?<!^)UNKNOWN SPOUSEOF.*$'),
            # Pattern to match and remove "UNKNOWN SPOUSE OF" not at the beginning of the string, followed by any characters until the end of the string
            re.compile(r'\s+UNKNOWN SPOUSE OF.*'),
            # Pattern to match 'UNKNOWN HEIRS...OF' or 'UNKN HEIRS OF'
            re.compile(r'(UNKNOWN|UNKN)\s+HEIRS(?:\.\.\.)?\s+OF', flags=re.IGNORECASE),
            # Pattern to match and remove the question mark
            re.compile(r'\?'),
            # Pattern to match any invalid words
            re.compile(r'\bDOES\b')
        ]              
          

    # ******************************************* Resolving Party name *************************************************

    def resolve_party_name(self, fullname):
        """
        @Args:- fullname: string representing fullname to resolve
        @Return:- Tuple containing prefix_str, suffix_str, first_name, middle_name, last_name, is_company
        @Description:-
                This method resolves/segregates the given name into prefix, suffix, first_name, middle_name, last_name.
        """
        prefix_str = ''
        suffix_str = ''
        first_name = ''
        middle_name = ''
        last_name = ''
        is_company = False

        fullname = self.clean_fullname(fullname)    

        determine_company_regex_match = self.is_determine_company_name(fullname)

        if determine_company_regex_match:
            # Since given participant name is a company name, no name segregation is required
            is_company = True
            return prefix_str, suffix_str, first_name, middle_name, last_name, is_company

        # Full names can appear in one of the two formats.
        # 1. last_name suffix_str, prefix_str first_name middle_name
        # 2. prefix_str first_name middle_name last_name suffix_str
        # Prefixes and/or suffixes are optional

        # First get all prefixes and suffixes using FW method
        (suffix_str, fullname) = self.get_all_prefix_suffix(fullname)
        (prefix_str, fullname) = self.get_all_prefix_suffix(fullname, is_prefix=True)

        # The full name obtained after getting all prefixes/suffixes is devoid of the two, i.e now will not
        # have prefix or suffix in it.

        fullname_comma_split_list = fullname.strip().split(',')

        if len(fullname_comma_split_list) > 1:
            # If more than 1 string is present in fullname_comma_split_list, then the format of full name is
            # last_name, first_name middle_name
            last_name = fullname_comma_split_list.pop(0).strip()

            first_name_middle_name_string = ' '.join(fullname_comma_split_list)

            # split first name middle name string on space to get a list [first_name middle_name]
            first_name_middle_name_list = first_name_middle_name_string.strip().split()

            first_name = first_name_middle_name_list.pop(0).strip()

            # Since first name has been removed from the list, the list now holds only middle name words
            middle_name = ' '.join(first_name_middle_name_list).strip()

        else:
            # If this code is being executed, then the full name given is first_name middle_name last_name format
            first_name_middle_name_last_name_list = fullname.split()

            first_name = first_name_middle_name_last_name_list.pop(0).strip()

            if first_name_middle_name_last_name_list:
                # After removing first name from this list, if the list holds some word/string, the first string here is
                # last name
                last_name = first_name_middle_name_last_name_list.pop(-1).strip()

            # Whatever now left in first_name_middle_name_last_name_list is middle name.
            middle_name = ' '.join(first_name_middle_name_last_name_list)

        return prefix_str, suffix_str, first_name, middle_name, last_name, is_company

    def clean_fullname(self, fullname):
        """
        @Args:- fullname: string representing full name
        @Return:- fullname: cleaned up fullname string
        @Description:-
                This method cleans up the fullname string before name segregation starts
        """
        # Decode html entities(like &nbsp;, &amp;,etc.) to actual ascii characters.
        fullname = normalise_object_value(fullname)
        
        # Reducing multiple white spaces to 1
        fullname = self.white_spaces_regex.sub(" ", fullname)

        # Apply specific removal patterns to the fullname
        for pattern in self.specific_removal_patterns:
            fullname = pattern.sub("", fullname).strip()                            
            
        aka_regex_match = self.aka_individual_pattern_match_regx.search(fullname)

        if aka_regex_match:
            # Changing "John AKA Jonathan J" to "John <split-token> Jonathan J"
            fullname_token_str = self.aka_individual_pattern_match_regx.sub('<split-token>', fullname)
            # Getting a tuple containing ("John", "Jonathan J")
            name_token_tuple = tuple(fullname_token_str.split('<split-token>'))
            # Getting the best name from the tuple
            fullname = self.get_most_complete_name(name_token_tuple)
            # Reducing multiple white spaces to 1
            fullname = self.white_spaces_regex.sub(" ", fullname)
            # Recursively clean up the name until we don't find any of the above-mentioned text
            fullname = self.clean_fullname(fullname)

        name_ending_word_cleaning_regex_match = self.name_ending_word_cleaning_regex.match(fullname)
        midway_name_cleaning_regex_match = self.midway_name_cleaning_regex.match(fullname)
        name_preceding_word_cleaning_regex_match = self.name_preceding_word_cleaning_regex.match(fullname)

        if name_ending_word_cleaning_regex_match:
            cleaning_regex_match_object = name_ending_word_cleaning_regex_match
        elif midway_name_cleaning_regex_match:
            cleaning_regex_match_object = midway_name_cleaning_regex_match
        else:
            cleaning_regex_match_object = name_preceding_word_cleaning_regex_match

        if cleaning_regex_match_object:
            fullname = cleaning_regex_match_object.group('cleaned_name')

            # fullname = fullname.strip().strip(',').strip().strip(':').strip()
            fullname = fullname.strip().strip(',').strip()
            # remove the multiple white spaces and replace them by a single white space
            fullname = self.white_spaces_regex.sub(" ", fullname)
            # Recursively clean up the name
            fullname = self.clean_fullname(fullname)

        # Reducing multiple white spaces to 1
        fullname = self.white_spaces_regex.sub(" ", fullname).strip(' ,')

        return fullname

    def get_all_prefix_suffix(self, fullname, is_prefix=False):
        """
        This method will find suffixes in the fullname and will return
        suffixes and fullname without suffix
        Return (prefix_suffix, fullname)
        """
        if is_prefix:
            regex = self.prefix_match_regex
        else:
            regex = self.suffix_match_regex

        is_match = regex.search(fullname)

        prefix_suffix = None
        while is_match:
            # get the right most suffix
            matched_str = is_match.group('prefix_suffix')

            if not prefix_suffix:
                prefix_suffix = ""

            prefix_suffix += matched_str
            # fullname might still have a suffix
            # Remove the matched suffix from the fullname
            # suffix/prefix is at group 2, therefor, fullname should now have only group 1 and 3.
            fullname = regex.sub(r'\1 \3', fullname, 1)
            fullname = self.multi_comma_post_prefix_suffix_replace_regex.sub(',', fullname)
            is_match = regex.search(fullname)
            prefix_suffix += " "

        fullname = self.white_spaces_regex.sub(" ", fullname).strip(' ,')
        if prefix_suffix:
            prefix_suffix = prefix_suffix.strip()

        return prefix_suffix, fullname

    # *****************************************
    def resolve_company_name(self, company_name):
        """
        @Arg:- company_name: str representing company name
        @Return:- Cleaned/resolved company name
        @Description:-
                This method resolves given company name
        """
        company_name_list = []
        if self.aka_company_pattern_match_regx.search(company_name):
            company_full_name_with_token = self.aka_company_pattern_match_regx.sub("<split_token>", company_name)
            company_name_list = company_full_name_with_token.split('<split_token>')
        else:
            normalized_company_name = self.clean_company_name(company_name)
            company_name_list.append(normalized_company_name)
        return company_name_list

    def clean_company_name(self, company_name):
        """
        @Args:- company_name: str representing company name
        @Return:- normalized_company_name: string holding cleaned company name
        @Description:-
                This method cleans company name and returns company name to resolve
        """
        # Decode html entities(like &nbsp;, &amp;,etc.) to actual ascii characters.
        normalized_company_name = normalise_object_value(company_name)
        normalized_company_name = self.remove_question_mark_regex.sub('', normalized_company_name).strip()
        company_name_cleaning_regex = self.company_name_cleaning_regex.match(normalized_company_name)
        if company_name_cleaning_regex:
            normalized_company_name = company_name_cleaning_regex.group('company_name')
            normalized_company_name = normalized_company_name.strip()
            # Remove the multiple white spaces and replace them by a single white space
            normalized_company_name = self.white_spaces_regex.sub(" ", normalized_company_name)
            # Recursively clean up the name until we dont find any of the above mentioned text
            normalized_company_name = self.clean_company_name(normalized_company_name)

        return normalized_company_name
