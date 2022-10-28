import json
import os.path
import random
from typing import Iterable


class Puzzle:

    def __init__(self,
                 _id: int,
                 problem: str,
                 options: list,
                 key_idx: int):
        self._id = _id
        self.problem = problem
        self.options = options
        self._key_idx = key_idx

    def shuffle(self):
        pairs = [[i, item] for i, item in enumerate(self.options)]
        random.shuffle(pairs)
        idx, self.options = list(zip(*pairs))
        self._key_idx = idx.index(self._key_idx)

    @property
    def key(self):
        return self.options[self._key_idx]

    @property
    def id(self):
        return self._id


class PuzzleSet:
    """问题集类。

    提供了基本的导入问题，追加问题，打乱选项，返回答案的功能。
    """

    def __init__(self, filepath: str, *, name="", shuffle=False):
        """构造问题集。
        参数 filepath 与 shuffle 只需要提供一个

        :param filepath: 问题的路径。只支持 json 格式。若filepath为 “”，问题集为空。
        :param name: 问题集的名字。
        :param shuffle: 是否打乱题目选项的顺序
        """

        self.puzzles = set()
        self.used = set()
        self.name = name
        if filepath != "":
            self.import_puzzles(filepath)
        if shuffle:
            self.shuffle()

    def __iter__(self):
        return iter(self.puzzles)

    def shuffle(self) -> None:
        """打乱问题集中所有题目选项的顺序。"""

        for p in self.puzzles:
            p.shuffle()

    def pop(self):
        one = self.puzzles.pop()
        self.used.add(one)
        return one

    def append(self, filepath: str, shuffle=False) -> None:
        """
        从文件中导入题目并追加到已有问题集中。

        :param filepath: 文件路径。
        :param shuffle: 是否打乱新加入题目选项的顺序。
        """

        new_puzzles = PuzzleSet(filepath, shuffle=shuffle)
        self.puzzles.update(new_puzzles.puzzles)

    def update(self, puzzles: Iterable[Puzzle]):
        self.puzzles.update(puzzles)

    def import_puzzles(self, filepath: str) -> None:
        """
        从json文件导入题目。

        :param filepath: 文件路径。
        """

        print("log")
        filename = os.path.basename(filepath)
        if not filename.endswith("json"):
            raise ValueError("问题文件只支持json格式，详细格式见文档...")
        if not os.path.exists(filepath):
            raise FileExistsError(f"{filepath}不存在，请检查路径和文件名是否正确。")

        with open(filepath, "r") as _f:
            tmp_set = json.load(_f, cls=PuzzleSetJSONDecoder)
            self.puzzles = tmp_set.puzzles
            if self.name == "":
                self.name = tmp_set.name


class PuzzleJSONEncoder(json.JSONEncoder):

    def default(self, o: Puzzle) -> dict:
        if isinstance(o, Puzzle):
            # JSON object would be a dictionary.
            return {
                "_id": o.id,
                "problem": o.problem,
                "options": o.options,
                "key_idx": o._key_idx,
            }
        else:
            # Base class will raise the TypeError.
            return super().default(o)


class PuzzleJSONDecoder(json.JSONDecoder):

    def __init__(self, *, parse_float=None, parse_int=None, parse_constant=None,
                 strict=True, object_pairs_hook=None):
        super(PuzzleJSONDecoder, self).__init__(
            object_hook=self.puzzle_hook, parse_float=parse_float,
            parse_int=parse_int, parse_constant=parse_constant, strict=strict,
            object_pairs_hook=object_pairs_hook)

    @staticmethod
    def puzzle_hook(o: dict):
        if "_id" in o:
            return Puzzle(
                o.get('_id'),
                o.get('problem'),
                o.get('options'),
                o.get('key_idx'),
            )
        return o


class PuzzleSetJSONEncoder(json.JSONEncoder):

    def __init__(self, *, skipkeys=False, ensure_ascii=True,
                 check_circular=True, allow_nan=True, sort_keys=False,
                 indent=None, separators=None, default=None):
        super(PuzzleSetJSONEncoder, self).__init__(
            skipkeys=skipkeys, ensure_ascii=ensure_ascii,
            check_circular=check_circular, allow_nan=allow_nan, sort_keys=sort_keys,
            indent=indent, separators=separators, default=default)
        self.puzzle_encoder = PuzzleJSONEncoder(
            skipkeys=skipkeys, ensure_ascii=ensure_ascii,
            check_circular=check_circular, allow_nan=allow_nan, sort_keys=sort_keys,
            indent=indent, separators=separators, default=default)

    def default(self, o: PuzzleSet):
        if isinstance(o, PuzzleSet):
            # JSON object would be a dictionary.
            return {
                "name": o.name,
                "content": [self.puzzle_encoder.default(p) for p in o.puzzles]
            }
        else:
            # Base class will raise the TypeError.
            return super().default(o)


class PuzzleSetJSONDecoder(json.JSONDecoder):

    def __init__(self, *, parse_float=None, parse_int=None,
                 parse_constant=None, strict=True, object_pairs_hook=None):
        super(PuzzleSetJSONDecoder, self).__init__(
            object_hook=self.puzzleset_hook, parse_float=parse_float,
            parse_int=parse_int, parse_constant=parse_constant, strict=strict,
            object_pairs_hook=object_pairs_hook)
        self.puzzle_decoder = PuzzleJSONDecoder(parse_float=parse_float, parse_int=parse_int,
                                                parse_constant=parse_constant, strict=strict,
                                                object_pairs_hook=object_pairs_hook)

    def puzzleset_hook(self, o: dict):
        if "name" in o:
            ps = PuzzleSet("", name=o.get("name"))
            content = o.get("content")
            if content is None:
                raise RuntimeError(f"问题集``{ps.name}``中未找到 ``content`` 字段。")
            ps.update(map(self.puzzle_decoder.puzzle_hook, content))
            return ps
        return o
