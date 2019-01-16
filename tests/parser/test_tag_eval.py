import os

import pytest

from document import DocxDocument
from parser.render import document_tags, check_document_tags
from parser.tag_eval import _exponents_eval, is_int, is_float, _multiplication_eval, \
    _division_eval, _addition_eval, _subtraction_eval, text_as_datatype, eval_expression, eval_brackets

TEST_DIRECTORY = os.path.dirname(os.path.dirname(__file__))


def test_tags():
    """
    Checks whether all tag types are retrieved correctly
    """
    tag_document = DocxDocument(os.path.join(TEST_DIRECTORY, "tags.docx"))
    assert document_tags(tag_document) == ["{{ let a = 1 }}", "{{ if a }}", "{{ else }}", "{{end}}"]


def test_check_document_tags():
    """
    Checks whether the doc tag checker is identifying issues
    :return:
    """
    pytest.xfail("Needs fixing")  # TODO
    error_tag_document = DocxDocument(os.path.join(TEST_DIRECTORY, "error_tags.docx"))
    assert check_document_tags(error_tag_document) == {"error_tags": [
        {"para_id": None, "error": "Count of opening tags does not match count of closing tags in paragraph",
         "text": "{{Error 1: no closer"},
        {"para_id": None, "error": "Count of opening tags does not match count of closing tags in paragraph",
         "text": "Error 2: no opener}}"}
    ]}


def test_datatype_convert():
    test_text = [
        "3",
        "'3'",
        "3.0",
    ]
    assert [text_as_datatype(x) for x in test_text] == [3, "3", 3.0]


# TODO: Add all is_ and as_ functions
def test_is_int():
    test_text = [
        "2",
        "Hello",
    ]
    assert [is_int(x) for x in test_text] == [True, False]


def test_is_float():
    test_text = [
        "3.0",
        "a",
    ]
    assert [is_float(x) for x in test_text] == [True, False]


def test_eval_brackets():
    test_text = ['((2 + 3) * 5)',
                 '((2 * 3 / 4)']
    assert [eval_brackets(x) for x in test_text] == ["25", "(1.5"]


def test_eval_text():
    original = "2 ** 3 + 5 * 4"
    assert eval_expression(original) == '28'


def test_eval_text_with_string():
    original = "'2' * 4 + '5'"
    assert eval_expression(original) == '22225'


# TODO: Add testing for raises
def test_exponent_eval():
    test_text = [
        "2 ** 3",
        "4 ** 6 * 3",
        "4 ** 1.5",
    ]
    assert [_exponents_eval(x) for x in test_text] == ["8", "4096 * 3", "8.0"]


def test_multiplication_eval():
    test_text = [
        "3 * 4.5",
        "2 * 5",
        "2 * '3'"
    ]
    assert [_multiplication_eval(x) for x in test_text] == ["13.5", "10", "'33'"]


def test_division_eval():
    test_text = [
        "2 / 1",
        "5 / 2",
    ]
    assert [_division_eval(x) for x in test_text] == ["2.0", "2.5"]


def test_addition_eval():
    test_text = [
        "2 + 1",
        "5.2 + 2.4",
        "'2' + '3'",
    ]
    assert [_addition_eval(x) for x in test_text] == ["3", "7.6", "23"]


def test_subtraction_eval():
    test_text = [
        "3 - 2",
        "10.5 - 3.6",
    ]
    assert [_subtraction_eval(x) for x in test_text] == ["1", "6.9"]
