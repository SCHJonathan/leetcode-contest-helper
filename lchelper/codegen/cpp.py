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
        return {
            # A header-only library for comparing outputs.
            "_testing.h": r"""
#ifndef TESTING_H
#define TESTING_H

#include <iostream>
#include <vector>
#include "_boilerplate.hpp"

template <typename T>
void print(const T &x) { std::cerr << x; }

template <typename T>
void print(const std::vector<T> &vec) {
    std::cerr << "{";
    for (int i = 0; i < vec.size(); ++i) {
        if (i > 0) std::cerr << ", ";
        print(vec[i]);
    }
    std::cerr << "}";
}

void print(ListNode* node) {
    std::cerr << "{";
    for (ListNode* thru = node; thru; thru = thru->next) {
        std::cerr << thru->val;
        if (thru->next) std::cerr << " -> ";
    }
    std::cerr << "}";
}

template <>
void print(const bool &x) { std::cerr << (x ? "true" : "false"); }

template <typename T>
inline bool _test(const T &a, const T &b) {
    return a == b;
}

template <typename T>
inline bool _test(const std::vector<T> &a, const std::vector<T> &b) {
    if (a.size() != b.size()) return false;
    for (int i = 0; i < a.size(); ++i)
        if (!_test(a[i], b[i])) return false;
    return true;
}

template <typename T>
inline void test(const char *msg, const T &a, const T &b) {
    if (_test(a, b)) {
        std::cerr << msg << "\033[1;32m [OK]\033[0m" << std::endl;
        std::cerr << "Expected: ";
        print(a);
        std::cerr << std::endl << "Received: ";
        print(b);
        std::cerr << std::endl;
    } else {
        std::cerr << msg << "\033[1;31m [WRONG]\033[0m" << std::endl;
        std::cerr << "Expected: ";
        print(a);
        std::cerr << std::endl << "Received: ";
        print(b);
        std::cerr << std::endl;
    }
}

#endif  // TESTING_H
""",
            # Boilerplate code for supporting LeetCode-specific constructs.
            "_boilerplate.hpp": r"""
#include <algorithm>
#include <bitset>
#include <complex>
#include <fstream>
#include <functional>
#include <iomanip>
#include <ios>
#include <iostream>
#include <map>
#include <numeric>
#include <queue>
#include <random>
#include <set>
#include <stack>
#include <string>
#include <tuple>
#include <utility>
#include <vector>

#include <cmath>
#include <climits>
#include <cstdarg>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <ctime>

using namespace std;

struct ListNode {
    int val;
    ListNode *next;
    ListNode() : val(0), next(nullptr) {}
    ListNode(int x) : val(x), next(nullptr) {}
    ListNode(int x, ListNode *next) : val(x), next(next) {}
};

struct TreeNode {
    int val;
    TreeNode *left;
    TreeNode *right;
    TreeNode(int x) : val(x), left(NULL), right(NULL) {}
    ~TreeNode() {
        if (left != NULL) delete left;
        if (right != NULL) delete right;
    }
};

const int NONE = INT_MIN;

TreeNode *_construct_tree(const vector<int> &parent) {
    queue<TreeNode *> q;
    int ptr = 0;

    auto _add_node = [&]() -> TreeNode * {
        if (ptr >= parent.size()) return nullptr;
        int val = parent[ptr++];
        if (val == NONE) return nullptr;
        auto *p = new TreeNode(val);
        q.push(p);
        return p;
    };

    TreeNode *root = _add_node();
    while (!q.empty()) {
        if (ptr >= parent.size()) break;
        TreeNode *p = q.front();
        q.pop();
        p->left = _add_node();
        p->right = _add_node();
    }
    return root;
}
""",
        }

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
        return r"""
#include <fstream>
#include <iostream>
#include <sstream>
#include <stack>
#include <queue>
#include <vector>
#include <array>
#include <map>
#include <unordered_map>
#include <set>
#include <unordered_set>
#include <algorithm>

#ifdef JONATHAN
#include "_testing.h"
#endif

using namespace std;

#define ll long long
#define ull unsigned long long

#define pll pair<ll, ll>
#define pull pair<ull, ull>
#define pint pair<int, int>

#define vint vector<int>
#define vll vector<ll>
#define vull vector<ull> 

void __print(int x) {cerr << x;}
void __print(long x) {cerr << x;}
void __print(long long x) {cerr << x;}
void __print(unsigned x) {cerr << x;}
void __print(unsigned long x) {cerr << x;}
void __print(unsigned long long x) {cerr << x;}
void __print(float x) {cerr << x;}
void __print(double x) {cerr << x;}
void __print(long double x) {cerr << x;}
void __print(char x) {cerr << '\'' << x << '\'';}
void __print(const char *x) {cerr << '\"' << x << '\"';}
void __print(const string &x) {cerr << '\"' << x << '\"';}
void __print(bool x) {cerr << (x ? "true" : "false");}

template<typename T, typename V>
void __print(const pair<T, V> &x) {cerr << '{'; __print(x.first); cerr << ','; __print(x.second); cerr << '}';}
template<typename T>
void __print(const T &x) {int f = 0; cerr << '{'; for (auto &i: x) cerr << (f++ ? "," : ""), __print(i); cerr << "}";}
void _print() {cerr << "]\n";}
template <typename T, typename... V>
void _print(T t, V... v) {__print(t); if (sizeof...(v)) cerr << ", "; _print(v...);}
#ifdef JONATHAN_DEBUG
#define debug(x...) cerr << "[" << #x << "] = ["; _print(x)
#else
#define debug(x...)
#endif

const int RANGE = 1e9+7;
"""

    def generate_code(self, problem: Problem, signature: Signature) -> Tuple[Code, Code]:
        # Generate solution code as the crawled template.
        solution_code = problem.code.copy()

        def to_str(val: Any) -> str:
            if isinstance(val, list):
                return "{" + ", ".join(to_str(x) for x in val) + "}"
            if isinstance(val, str):
                if len(val) == 1:
                    return f"'{val}'"
                return f'"{val}"'
            if isinstance(val, bool):  # bool is a subtype of int
                return "true" if val else "false"
            if isinstance(val, (int, float)):
                return str(val)
            assert False

        def to_tree(parent: List[Optional[int]]) -> str:
            return f"_construct_tree({{{', '.join('NONE' if x is None else str(x) for x in parent)}}})"

        def to_val(val: Any, type_name: str) -> str:
            if type_name.replace(' ', '') == "TreeNode*":
                if not isinstance(val, list):
                    val = [val]
                return to_tree(val)
            return to_str(val)

        def to_args(input: Dict[str, Any], func_sig: FunctionSignature) -> List[str]:
            # Return list of assignments.
            assignments = []
            for type_name, arg_name in func_sig.arguments:
                assignments.append(assign(f"{func_sig.name}_{arg_name}", to_val(input[arg_name], type_name)))
            return assignments

        def call(func_name: str, args: List[str]) -> str:
            return f"{func_name}({', '.join(args)})"

        def ctor(class_name: str, obj_name: str, args: List[str]) -> str:
            return f"{class_name} {call(obj_name, args)};"

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
