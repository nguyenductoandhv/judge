from typing import Any
import re

from dmoj.error import InternalError
from dmoj.result import CheckerResult
from dmoj.utils.helper_files import parse_helper_file_error


class ContribModule:
    AC = 0
    WA = 1
    PARTIAL = 2

    name = 'default'
    repartial = re.compile(br'^points ([-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?)', re.M)

    def catch_internal_error(f: Any) -> Any:
        def wrapper(*args, **kwargs) -> CheckerResult:
            try:
                return f(*args, **kwargs)
            except InternalError as e:
                proc = args[1]
                return CheckerResult(
                    False,
                    0,
                    feedback=f'Checker exitcode {proc.returncode}',
                    extended_feedback=str(e),
                )

        return wrapper

    @classmethod
    def get_checker_args_format_string(cls):
        return '{input_file} {output_file} {answer_file}'

    @classmethod
    def get_interactor_args_format_string(cls):
        return '{input_file} {answer_file}'

    @classmethod
    def parse_return_code(
        cls, proc, executor, point_value, time_limit, memory_limit, feedback, extended_feedback, name, stderr
    ):
        if proc.returncode == cls.AC:
            return CheckerResult(True, point_value, feedback=feedback, extended_feedback=extended_feedback)
        elif proc.returncode == cls.WA:
            return CheckerResult(False, 0, feedback=feedback, extended_feedback=extended_feedback)
        elif proc.returncode == cls.PARTIAL:
            match = cls.repartial.search(stderr)
            if not match:
                raise InternalError('Invalid stderr for partial points: %r' % stderr)
            points = float(match.group(1))
            if not 0 <= points <= 1:
                raise InternalError('Invalid partial points: %f, must be between [%f; %f]' % (points, 0, point_value))
            return CheckerResult(True, points * point_value, feedback=feedback, extended_feedback=extended_feedback)
        else:
            parse_helper_file_error(proc, executor, name, stderr, time_limit, memory_limit)
