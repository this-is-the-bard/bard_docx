import os
import re
from io import BytesIO
from shutil import make_archive
from tempfile import TemporaryDirectory
from zipfile import ZipFile

from bs4 import BeautifulSoup
from logzero import logger

TAG_OPEN = '{{'
TAG_CLOSE = '}}'
TAG_KEYWORDS = "let"

MODULE_DIRECTORY = os.path.dirname(__file__)


# TODO for odt support
class BaseDocument:
    pass


class Document:
    pass


class DocxDocument:
    def __init__(self, filepath=None):
        # TODO: Make it create its own file if no filepath specified

        # Open up the XML documents
        self.tmpdir = TemporaryDirectory()
        # Check if we need to create a blank docx

        if filepath is None:
            filepath = os.path.join(MODULE_DIRECTORY, "base_documents", "base.docx")
            logger.info("Using base.docx as no existing file specified")
        else:
            if not os.path.isfile(filepath):
                logger.error("{} is not a valid filepath".format(filepath))
                raise AttributeError

        with ZipFile(filepath, "r") as docx_package:
            docx_package.extractall(self.tmpdir.name)
            logger.debug("Extracted zip to %s" % self.tmpdir.name)

        # Document XML
        self._document_xml_path = os.path.join(self.tmpdir.name, "word", "document.xml")
        self.document_xml_buffer = BytesIO()
        with open(self._document_xml_path, "rb") as f:
            # TODO: Chunk
            self.document_xml_buffer.write(f.read())

        # Comments XML
        self._comments_xml_path = os.path.join(self.tmpdir.name, "word", "comments.xml")
        # If no comments in .docx it won't have a comments.xml
        if not os.path.isfile(self._comments_xml_path):
            with open(os.path.join(MODULE_DIRECTORY, "base_documents", "comments.xml"), "rb") as source, open(
                    self._comments_xml_path, "wb") as target:
                logger.info('No comments.xml found, creating new one')
                target.write(source.read())

        self.comments_xml_buffer = BytesIO()
        with open(self._comments_xml_path, "rb") as f:
            # TODO: Chunk
            self.comments_xml_buffer.write(f.read())

        with open(self._document_xml_path, "rb") as f:
            self.document_soup = BeautifulSoup(f.read(), "lxml-xml")

        # If no existing comments the extract won't have comments.xml
        with open(self._comments_xml_path, "rb") as f:
            self.comments_soup = BeautifulSoup(f.read(), "lxml-xml")

    def _document_comment_ids(self):
        _coms = []
        for row in self.document_soup.find_all('commentRangeStart'):
            _coms.append(row.get('w:id'))

        return _coms

    def _paragraph_has_comment(self, paraId):
        # TODO
        pass

    def add_comment(self, paraId, text):
        """
        Adds a comment with specified text to paragraph
        """
        para = self._paragraph_xml(paraId)
        pass  # TODO
        # Part 1: Add to document.xml

        # Part 2: Add to comments.xml

    def paragraph_paraid(self, xml) -> str:
        soup = BeautifulSoup(xml, "lxml-xml")
        return soup.find('p').get("w14:paraId")

    def paragraph_text(self, paraId) -> str:
        """
        Returns joined text from a paragraph
        """
        paragraph = self._paragraph_xml(paraId)

        return paragraph.get_text()

    def _paragraph_xml(self, paraId):
        return self.document_soup.find('p', attrs={"w14:paraId": paraId})

    def save(self, filepath: str) -> None:
        """
        Write the current Document to filepath
        """
        logger.debug('Saving .docx')
        with open(self._document_xml_path, "wb") as f:
            f.write(self.document_xml_buffer.read())

        with open(self._comments_xml_path, "wb") as f:
            f.write(self.comments_xml_buffer.read())

        make_archive(filepath, 'zip', self.tmpdir.name)
        os.rename(filepath + '.zip', filepath.rstrip('.zip'))

        logger.info("Saved Document to %s" % filepath)
        return

    def _save_documents_xml(self, filepath):
        """
        Used for debugging
        """
        with open(filepath, "wb") as target, open(self._document_xml_path, "rb") as source:
            target.write(source.read())
            logger.debug("Saved documents.xml to %s" % filepath)

        return

    def _save_comments_xml(self, filepath):
        """
        Used for debugging
        """
        with open(filepath, "wb") as target, open(self._comments_xml_path, "rb") as source:
            target.write(source.read())
            logger.debug("Saved comments.xml to %s" % filepath)

        return

    def paragraphs(self):
        """
        Retrieves all paragraphs in docx
        :return: list
        """
        for para in self.document_soup.find_all("w:p"):
            yield Paragraph(para)

    def document_tags(self):
        found_tags = []
        for paragraph in self.paragraphs():
            pass


def _document_from_tmpdir(directory: str) -> DocxDocument:
    """
    Creates a DocxDocument instance from a tmpdir path
    Mainly used for DocumentRender transactions
    :param directory:
    :return:
    """
    if not os.path.isdir(directory):
        message = "{} is not a valid directory".format(directory)
        logger.error(message)
        raise Exception(message)

    # Temp workaround... not very efficient
    arch = make_archive("temp.docx", "zip", directory)
    doc = DocxDocument(arch)
    return doc


class Paragraph:
    def __init__(self, xml):
        self.soup: BeautifulSoup = BeautifulSoup(str(xml), "lxml-xml")

    def __str__(self) -> str:
        return str(self.soup)

    def _text(self) -> str:
        return self.soup.get_text()

    def _para_id(self) -> str:
        return self.soup.find("p").get("paraId")

    @property
    def para_id(self):
        return self._para_id()

    @property
    def text(self):
        return self._text()

    def replace_text(self, original: str, new: str) -> None:
        text_matches = self.soup.find_all(text=re.compile(original))
        for match in text_matches:
            fixed_text = match.replace(original, new)
            match.replace_with(fixed_text)
        return
