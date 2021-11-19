# rumi.test_file_rumi.test_reader
# Test the reader for file-based translation monitoring
# 
# Author: Tianshu Li
# Created: Nov.19 2021

"""
Test the reader for file-based translation monitoring
"""

##########################################################################
# Imports
##########################################################################






##########################################################################
# FileReader Test Cases
##########################################################################


class TestFileReader():
    """
    FileReader Tests
    """

    def test_clean_filename(self):
        """
        Assert renaming path hack can be removed from a filename in git log.
        """
        pass

    def test_read_history(self):
        """
        Test reading git history from specified branch.
        """
        pass
    
    def test_parse_history(self):
        """
        Assert git history is correctly parsed into a commit dictionary.
        """
        pass

    def test_parse_base_lang(self):
        """
        Test parsing basename and language from a given file_name.
        """
        pass

    def test_get_langs(self):
        """
        Test getting languages from structured commit history.
        """
        pass

    def test_set_langs(self):
        """
        
        """
        pass

    def test_set_origins(self):
        """
        
        """
        pass

    def test_add_target(self):
        """
        Test adding single target file by name.
        """ 
        pass

    def test_del_target(self):
        """
        Test deleting single target file by name.
        """
        pass