import os

from document import DocxDocument, _document_from_tmpdir
from parser.render import _clean_tag, code_tags

TEST_DIRECTORY = os.path.dirname(__file__)

debug_filename = os.path.join(TEST_DIRECTORY, "debug.docx")
base_filename = os.path.join(TEST_DIRECTORY, "base.docx")


def test_docx_from_no_filepath():
    """
    Test if doc created without filepath
    :return:
    """
    doc = DocxDocument()


def test_docx_open_and_save():
    save_target = os.path.join(TEST_DIRECTORY, "cache", "test_save.docx")
    doc = DocxDocument(debug_filename)
    doc.save(save_target)
    assert os.path.isfile(save_target) and save_target.endswith(".docx")
    os.remove(save_target)


def test_docx_create_comments_xml():
    """
    Test if creating a DocxDocument instance will create the blank comments.xml
    :return:
    """
    # Test will fail if exception raised
    doc = DocxDocument(base_filename)


def test_paragraph_iterator():
    doc = DocxDocument(debug_filename)
    for para in doc.paragraphs():
        a = para


def test_paragraph_str():
    doc = DocxDocument(debug_filename)
    for para in doc.paragraphs():
        a = str(para)


def test_paragraph_text():
    doc = DocxDocument(debug_filename)
    for para in doc.paragraphs():
        a = para.text


def test_paragraph_id():
    doc = DocxDocument(debug_filename)
    for para in doc.paragraphs():
        a = para.para_id


def test_tag_clean():
    tag = "{{ Hello:world}}"
    assert _clean_tag(tag) == "Hello:world"


def test_code_tag_retrieval():
    sample_text = """
    {{ Moustache tag 1 }}
    Hello test
    This should bring out
    {{ Two tags}}
    """
    assert code_tags(sample_text) == ["{{ Moustache tag 1 }}", "{{ Two tags}}"]


def test_docx_from_directory():
    doc = DocxDocument()
    new_doc = _document_from_tmpdir(doc.tmpdir.name)


def test_paragraph_replace_text():
    invalid_text = []
    doc = DocxDocument(debug_filename)
    for paragraph in doc.paragraphs():
        paragraph.replace_text("Good", "Bad")
        if "Good" in paragraph.text or paragraph.text == 'Bad':
            invalid_text.append(paragraph.text)

    assert not invalid_text
