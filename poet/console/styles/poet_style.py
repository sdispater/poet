# -*- coding: utf-8 -*-

from cleo.styles import CleoStyle
from cleo.helpers import QuestionHelper


class PoetStyle(CleoStyle):

    def ask_question(self, question):
        """
        Asks a question.

        :param question: The question to ask
        :type question: Question

        :rtype: str
        """
        answer = QuestionHelper().ask(self._input, self, question)

        return answer
