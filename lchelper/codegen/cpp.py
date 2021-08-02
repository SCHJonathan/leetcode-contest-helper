import os
from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple, Union

from lchelper.codegen.base import Code, CodeGen, Signature
from lchelper.common import *
from lchelper.logging import log
from lchelper.utils import remove_affix

__all__ = [
    "CppCodeGen",
]


class CppCodeGen(CodeGen):
    @property
    def language(self) -> str:
        return "C++"

    @property
    def code_extension(self) -> str:
        return ".cc"

    @property
    def line_comment_symbol(self) -> str:
        return "//"

    @property
    def extra_files(self) -> Dict[str, str]:
        return {}

    @property
    def template_code(self) -> str:
        return r"""

// BEGIN SUBMIT

// BEGIN USER TEMPLATE

// END USER TEMPLATE

// BEGIN SOLUTION CLASS

// END SOLUTION CLASS

// END SUBMIT

// BEGIN TEST

// END TEST
"""

    @property
    def user_template_code(self) -> str:
        return r"""#ifdef JONATHAN
#include "_testing.h"
#else
#define debug(x...)
#endif

#define ll long long
#define ull unsigned long long

#define pll pair<ll, ll>
#define pull pair<ull, ull>
#define pint pair<int, int>

#define vint vector<int>
#define vll vector<ll>
#define vull vector<ull> 

const int RANGE = 1e9+7;
"""

    def generate_code(self, problem: Problem, signature: Signature) -> Tuple[Code, Code]:
        # Generate solution code as the crawled template.
        solution_code = problem.code.copy()

        def to_str(val: Any, type_name_input=None) -> str:
            if isinstance(val, list):
                type_name_input = type_name_input
                if type_name_input.startswith('vector<'):
                    type_name_input = type_name_input[7:-1]
                return "{" + ", ".join(to_val(x, type_name_input) for x in val) + "}"
            if isinstance(val, str):
                if type_name_input is None or type_name_input == 'string':
                    return f'"{val}"'
                return f"'{val}'"
            if isinstance(val, bool):  # bool is a subtype of int
                return "true" if val else "false"
            if isinstance(val, (int, float)):
                return str(val)
            assert False

        def to_tree(parent: List[Optional[int]]) -> str:
            return f"_construct_tree({{{', '.join('NONE' if x is None else str(x) for x in parent)}}})"

        def to_val(val: Any, type_name: str) -> str:
            type_name_no_ref = remove_cv_ref(type_name)
            type_name_no_space = type_name_no_ref.replace(' ', '')
            if type_name_no_space == "TreeNode*":
                if not isinstance(val, list):
                    val = [val]
                return to_tree(val)
            return to_str(val, type_name_no_space)

        def to_args(input: Dict[str, Any], func_sig: FunctionSignature) -> List[str]:
            # Return list of assignments.
            assignments = []
            for type_name, arg_name in func_sig.arguments:
                assignments.append(assign(f"{func_sig.name}_{arg_name}", to_val(input[arg_name], type_name)))
            return assignments

        def call(func_name: str, args: List[str]) -> str:
            return f"{func_name}({', '.join(args)})"

        def ctor(class_name: str, obj_name: str, args: List[str]) -> str:
            if len(args) > 0:
                return f"{class_name} {call(obj_name, args)};"
            else:
                return f"{class_name} {obj_name};"

        def remove_cv_ref(typ: str) -> str:
            while True:
                if typ.startswith("const"):
                    typ = typ[len("const"):]
                elif typ.startswith("volatile"):
                    typ = typ[len("volatile"):]
                elif typ.endswith("&"):
                    typ = typ[:-1]
                else:
                    break
                typ = typ.strip()
            return typ

        def decl(type_name: str, obj_name: Union[str, List[str]]) -> str:
            type_name = remove_cv_ref(type_name)
            if isinstance(obj_name, list):
                return f"{type_name} {', '.join(obj_name)};"
            return f"{type_name} {obj_name};"

        def assign(obj_name: str, value: str) -> str:
            return f"{obj_name} = {value};"

        def decl_assign(ret_type: str, obj_name: str, value: str) -> str:
            ret_type = remove_cv_ref(ret_type)
            return f"{ret_type} {obj_name} = {value};"

        # Generate test code as a function per example.
        test_functions = []
        instance_name = "_sol"
        if isinstance(signature, InteractiveProblemSignature):
            func_map: Dict[str, FunctionSignature] = {func_sig.name: func_sig for func_sig in signature.functions}
            for idx, example in enumerate(signature.examples):
                statements = []
                for ex_idx, ex in enumerate(example):
                    func_sig = func_map[ex.function]
                    statements.extend(to_args(ex.input, func_sig))
                    args = [f"{func_sig.name}_{arg_name}" for _, arg_name in func_sig.arguments]
                    if ex.function == signature.class_name:
                        ctor_stmt = ctor(signature.class_name, instance_name, args)
                        statements.append(ctor_stmt)
                    else:
                        ret_name = f"_ret{ex_idx}"
                        if func_sig.return_type != "void":
                            ret_ans_var = f"_ret_ans{ex_idx}"
                            stmts = [
                                decl_assign(func_sig.return_type, ret_ans_var, to_val(ex.output, func_sig.return_type)),
                                decl_assign(func_sig.return_type, ret_name,
                                            f"{instance_name}.{call(ex.function, args)}"),
                                # f"cout << \"Expected: \" << {ret_ans_var} << \" My Answer: \", {ret_name});"
                                # f"cout << \" Expected:\" << {ret_ans_var} << \" My Answer:\" << {ret_name} << endl;"
                                call("test", [to_str(f"Example - {idx} - Interaction {ex_idx}"),
                                              ret_ans_var, ret_name]) + ";",
                            ]
                            statements.extend(stmts)
                        else:
                            stmt = f"{instance_name}.{call(ex.function, args)};"
                            statements.append(stmt)
                declarations = defaultdict(list)
                for func_sig in signature.functions:
                    for type_name, arg_name in func_sig.arguments:
                        declarations[type_name].append(f"{func_sig.name}_{arg_name}")
                test_fn = [
                    f"void test_example_{idx}() {{",
                    *["    " + decl(type_name, objs) for type_name, objs in declarations.items()],
                    *["    " + line for line in statements],
                    "}"]
                test_functions.append(test_fn)

            main_code = [
                "int main() {",
                *["    " + f"test_example_{idx}();" for idx in range(len(signature.examples))],
                "}"]
        else:
            func_sig = signature.function
            for idx, example in enumerate(signature.examples):
                statements = []
                for type_name, arg_name in func_sig.arguments:
                    stmt = decl_assign(type_name, arg_name, to_val(example.input[arg_name], type_name))
                    statements.append(stmt)
                args = [arg_name for _, arg_name in func_sig.arguments]
                ret_name = "_ret"
                ret_ans_var = "_ret_ans"
                stmts = [
                    decl_assign(func_sig.return_type, ret_ans_var, to_val(example.output, func_sig.return_type)),
                    decl_assign(func_sig.return_type, ret_name, f"{instance_name}.{call(func_sig.name, args)}"),
                    # f"debug(\"Expected: \", {ret_ans_var}, \"My Answer: \", {ret_name});"
                    call("test", [to_str(f"Example - {idx}"), ret_ans_var, ret_name]) + ";",
                    # f"cout << \" Expected:\" << {ret_ans_var} << \" My Answer:\" << {ret_name} << endl;"
                ]
                statements.extend(stmts)

                test_fn = [
                    f"void test_example_{idx}(Solution &_sol) {{",
                    *["    " + line for line in statements],
                    "}"]
                test_functions.append(test_fn)

            main_code = [
                "int main() {",
                "    Solution _sol;",
                *[f"    test_example_{idx}(_sol);" for idx in range(len(signature.examples))],
                "}"]

        test_code = self.list_join(test_functions + [main_code], ["", ""])
        return solution_code, test_code

    def generate_additional_files(self, project_path: str, problems: List[Problem],
                                  signatures: List[Signature]) -> None:
        cmake = [
            "cmake_minimum_required(VERSION 3.12)",
            "project(leetcode)",
            "set(CMAKE_CXX_STANDARD 17)",
            'set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -DLEETCODE_LOCAL")',
        ]
        for idx, problem in enumerate(problems):
            file_name = self.get_problem_file_name(idx, problem)
            exec_name = remove_affix(file_name, suffix=self.code_extension)
            cmake.append(f"add_executable({exec_name} {file_name})")
        with open(os.path.join(project_path, "CMakeLists.txt"), "w") as f:
            f.write("\n".join(cmake))
